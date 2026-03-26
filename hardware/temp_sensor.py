"""
DS18B20 1-Wire temperature sensor reader.

Reads all detected DS18B20 sensors from the Linux sysfs 1-Wire bus.
Sensors are identified by glob-matching ``28*`` directories under
``/sys/bus/w1/devices/`` — the order returned by glob() is the physical
sensor index used throughout the rest of the application.

On non-Pi systems this module is a no-op: ``read_temp()`` returns immediately
so the rest of the app continues with default placeholder values (3.14 °C).
"""

import glob
import logging
import time
from typing import TYPE_CHECKING

from hardware.gpio_interface import IS_PI

if TYPE_CHECKING:
    from core.state import AppState

log = logging.getLogger(__name__)

BASE_DIR = '/sys/bus/w1/devices/'
SLAVE_COUNT_PATH = BASE_DIR + 'w1_bus_master1/w1_master_slave_count'


def _read_raw(sensor_number: int):
    """
    Read two lines from a single DS18B20 sensor's sysfs file.

    Args:
        sensor_number: Zero-based index into the sorted list of ``28*`` device paths.

    Returns:
        tuple[str, str]: (crc_line, temp_line) — raw text from w1_slave.
            crc_line contains 'YES' when the CRC check passed and the reading is valid.
            temp_line contains the temperature in the form ``... t=XXXXX`` (millidegrees).
    """
    paths = glob.glob(BASE_DIR + '28*')
    device_path = paths[sensor_number]
    with open(device_path + '/w1_slave', 'r') as f:
        valid, temp = f.readlines()
    return valid, temp


def read_temp(state: "AppState") -> None:
    """
    Read all connected DS18B20 sensors and update state.read_temp.

    Sensors are read sequentially. Each read is retried up to 5 times if the
    CRC check fails ('YES' not in first line) — bad readings can occur if the
    bus is noisy or the sensor is still converting.

    Sensors that fail after all retries are skipped (their slot in read_temp
    keeps the last good value). This avoids a single bad sensor from blocking
    the entire scan.

    Args:
        state: AppState instance — read_temp and temp_sens_found_number are updated.
    """
    if not IS_PI:
        return

    try:
        with open(SLAVE_COUNT_PATH) as f:
            count = int(f.read().strip())
        state.update(temp_sens_found_number=count)

        new_temps = list(state.read_temp)
        for x in range(count):
            try:
                valid, temp = _read_raw(x)

                retries = 0
                # 'YES' in crc_line means the hardware CRC matched — reading is trustworthy
                while 'YES' not in valid and retries < 5:
                    time.sleep(0.2)
                    valid, temp = _read_raw(x)  # NOTE: was _read_raw() in original — missing arg caused infinite loop
                    retries += 1

                if 'YES' not in valid:
                    log.warning("Sensor %d: no valid reading after retries", x)
                    continue

                # Temperature is encoded as millidegrees after the 't=' marker
                pos = temp.index('t=')
                temp_c = round(float(temp[pos + 2:]) / 1000.0, 1)
                new_temps[x] = temp_c

            except Exception as e:
                log.error("Sensor %d read error: %s", x, e)

        state.update(read_temp=new_temps)

    except Exception as e:
        log.error("Temperature scan failed: %s", e)
