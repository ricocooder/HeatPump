"""
Pump efficiency control algorithm.

Determines the active heat object (bojler / podłogówka / off) and adjusts
the pump efficiency level (0-7) based on the current season mode:

  **Lato (summer)** — schedule-driven boiler heating only:
    - Reads the weekly schedule grid (``godzina``) for the current hour and weekday.
    - If the schedule says ON and the boiler is below setpoint, activates the boiler (heat_object=1).
    - Otherwise turns the system off (heat_object=0).

  **Zima (winter)** — temperature-feedback with priority ordering:
    - If boiler is below setpoint − hysteresis → switch to boiler mode (heat_object=1).
    - If boiler is above setpoint + hysteresis → switch to floor heating (heat_object=2).
    - If both targets are satisfied (boiler AND floor above setpoint + hysteresis + 2°C margin)
      → turn system off (heat_object=0).

In both seasons the efficiency step is adjusted every ``interval[heat_object]`` seconds:
  - Temperature too high → decrease efi by 1 (save energy)
  - Temperature too low  → increase efi by 1 (heat faster)
  - Boiler mode always forces efi=7 (maximum) to fill the boiler quickly.
"""

import datetime
import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import AppState

log = logging.getLogger(__name__)


def check_pump_efi(state: "AppState") -> None:
    """
    Update pump efficiency (efi) and active heat object based on season and temperatures.

    Takes a snapshot of state at the start so all decisions use a consistent
    view of sensor readings — prevents race conditions with the 1-second GPIO job.

    Only runs in auto mode; returns immediately if pump_mode != 'auto'.

    Args:
        state: AppState instance — pump_efi, heat_object, and ac_time_plus_interval
               are updated at the end of a single atomic call.
    """
    # Snapshot once for consistency — avoid reading state mid-function while
    # the 1-second job might be writing GPIO state concurrently
    snap = state.snapshot()
    pump_mode         = snap['pump_mode']
    pump_efi          = snap['pump_efi']
    heat_object       = snap['heat_object']
    set_temp          = snap['set_temp']
    read_temp         = snap['read_temp']
    sensor_index_list = snap['sensor_index_list']
    offset            = snap['pump_temp_offset']
    interval          = snap['pump_interval']
    sezon             = snap['sezon']
    godzina           = snap['godzina']
    ac_time           = snap['ac_time_plus_interval']

    if pump_mode != 'auto':
        return

    now = time.time()
    new_efi          = pump_efi
    new_heat_object  = heat_object
    new_ac_time      = ac_time

    # --- Adjust efficiency level (runs every interval[heat_object] seconds) ---
    if now > ac_time + interval[heat_object]:
        new_ac_time = now
        if heat_object == 1:
            # Bojler always gets maximum flow to fill quickly
            new_efi = 7
        else:
            t_actual = read_temp[sensor_index_list[heat_object]] if heat_object < len(sensor_index_list) else 3.14
            t_set    = set_temp[heat_object]
            offs     = float(offset[heat_object])
            if t_actual > (t_set + offs) and pump_efi > 0:
                new_efi = pump_efi - 1   # too warm → reduce flow
            elif t_actual < (t_set - offs) and pump_efi < 7:
                new_efi = pump_efi + 1   # too cold → increase flow

    # --- Season logic: decide which heat object is active ---
    if sezon == 'Lato':
        now_dt    = datetime.datetime.now()
        hour      = now_dt.hour
        dow       = now_dt.weekday()  # 0=Monday, matches godzina column offset
        cell      = godzina[hour][dow + 1]   # +1 because column 0 is the hour label
        t_boiler  = read_temp[sensor_index_list[1]]
        t_set_b   = float(set_temp[1])
        log.debug("Lato: hour=%d dow=%d cell=%s t_boiler=%.1f t_set=%.1f",
                  hour, dow, cell, t_boiler, t_set_b)
        if cell == "ON" and t_set_b > t_boiler:
            new_heat_object = 1   # schedule active and boiler needs heating
        else:
            new_heat_object = 0   # schedule off or boiler already warm enough

    else:  # Zima — priority: boiler > floor > off
        t_boiler = read_temp[sensor_index_list[1]]
        t_floor  = read_temp[sensor_index_list[2]]
        t_set_b  = set_temp[1]
        t_set_f  = set_temp[2]
        off_b    = offset[1]
        off_f    = offset[2]

        # Boiler takes priority if it drops below setpoint − hysteresis
        if t_set_b - off_b > t_boiler:
            new_heat_object = 1
        # Switch to floor heating once boiler is satisfied
        if t_set_b + off_b < t_boiler:
            new_heat_object = 2
        # Turn off only when BOTH targets are comfortably exceeded
        # (+2°C extra margin on floor to avoid short-cycling)
        if (t_set_b + off_b < t_boiler) and (t_set_f + off_f + 2 < t_floor):
            new_heat_object = 0
            log.debug("Zima: pump off — both targets reached")

    state.update(
        pump_efi=new_efi,
        heat_object=new_heat_object,
        ac_time_plus_interval=new_ac_time,
    )
