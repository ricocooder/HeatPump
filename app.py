"""
HeatPump Control System — FastAPI entry point.

Architecture overview:
  - AsyncIOScheduler runs two background jobs via a ThreadPoolExecutor:
      * _job_4s: reads DS18B20 temperatures + runs pump control logic (every 4s)
      * _job_1s: writes GPIO outputs + reads ADC + logs to SQLite (every 1s)
  - Jobs run in a thread pool (not the event loop) so blocking hardware I/O
    does not stall SSE streams or HTTP request handling.
  - AppState is the single shared mutable object; all cross-thread writes
    go through state.update() which holds a threading.Lock.
  - workers=1 is mandatory — AppState lives in-process, not in shared memory.

Run on Raspberry Pi:
    uvicorn app:app --host 0.0.0.0 --port 8000

Run on dev machine (no hardware):
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.config_manager import ConfigManager
from core.state import AppState
from hardware import adc_reader, set_outputs, temp_sensor
from routes import (
    dashboard,
    harmonogram_route,
    history_route,
    raspberrypi_route,
    sensor_config,
    settings_route,
    stream,
)
from services import database, map_value, pump_efi

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

# Two workers: one for _job_4s and one for _job_1s.
# They must not overlap hardware access, so keep the pool small.
_executor = ThreadPoolExecutor(max_workers=2)


def _job_4s(state: AppState) -> None:
    """
    Slow sensor job — runs every 4 seconds.

    DS18B20 reads are slow (up to ~750ms per sensor) so this runs less
    frequently than the GPIO output job. Also recalculates pump efficiency
    so the output job always has an up-to-date efi level.
    """
    temp_sensor.read_temp(state)
    pump_efi.check_pump_efi(state)


def _job_1s(state: AppState) -> None:
    """
    Fast output job — runs every 1 second.

    Writes GPIO relay states, reads ADC (current/voltage), converts raw ADC
    values to physical units using linear mapping, and conditionally writes
    to the SQLite database if any value has changed by >= 1 unit.

    ADC mapping constants:
      - Current: 0-1023 raw → 0-30 A
      - Voltage: 0-1023 raw → 0-250 V
    """
    efi = set_outputs.apply_outputs(state)
    state.update(base_efi_percent=efi)

    adc_reader.read_curr_and_volt(state)

    pump_i = map_value.map_value(state.pump_i_read, 0, 1023, 0, 30)
    pump_v = map_value.map_value(state.pump_v_read, 0, 1023, 0, 250)
    state.update(
        pump_i=pump_i,
        pump_v=pump_v,
        pump_p=round(pump_i * pump_v / 1000, 2),  # kW
    )

    database.check_values(state, 1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager — handles startup and shutdown.

    Startup:
      1. Create AppState and load persisted config from disk.
      2. Attach state and config to app.state so all routes can access them.
      3. Start APScheduler with two interval jobs.

    Shutdown (on SIGTERM/SIGINT):
      1. Stop the scheduler (don't wait for running jobs to finish).
      2. Save config to disk.
      3. Clean up GPIO resources.
    """
    # ---- startup ----
    state  = AppState()
    config = ConfigManager(CONFIG_PATH)
    config.load_into(state)

    app.state.pump_state = state
    app.state.config     = config

    loop      = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler()

    async def job_4s_async():
        # run_in_executor offloads blocking I/O to the thread pool
        await loop.run_in_executor(_executor, _job_4s, state)

    async def job_1s_async():
        await loop.run_in_executor(_executor, _job_1s, state)

    scheduler.add_job(job_4s_async, "interval", seconds=4,  id="job_4s")
    scheduler.add_job(job_1s_async, "interval", seconds=1,  id="job_1s")
    scheduler.start()
    log.info("Scheduler started. DB path: %s", database.DB_PATH)

    yield

    # ---- shutdown ----
    scheduler.shutdown(wait=False)  # don't block — jobs will notice state is gone
    config.save_from(state)
    try:
        from hardware.gpio_interface import gpio
        gpio.cleanup()
    except Exception:
        pass
    log.info("Shutdown complete — config saved.")


app = FastAPI(title="HeatPump Control", lifespan=lifespan)

# Static files (CSS, JS, images)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)

# Register all route modules
app.include_router(dashboard.router)
app.include_router(stream.router)
app.include_router(settings_route.router)
app.include_router(harmonogram_route.router)
app.include_router(sensor_config.router)
app.include_router(raspberrypi_route.router)
app.include_router(history_route.router)


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        workers=1,  # MUST be 1 — AppState lives in-process, not in shared memory
    )
