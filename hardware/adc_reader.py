"""
MCP3008 SPI ADC reader for pump current and voltage measurement.

The MCP3008 is an 8-channel, 10-bit ADC connected via SPI bus (CE0).
Only two channels are used:
  - CH6: current sensor (prąd) — raw value 0-1023 mapped to 0-30 A in app.py
  - CH7: voltage sensor (napięcie) — raw value 0-1023 mapped to 0-250 V in app.py

The actual unit conversion (raw → A/V) happens in ``_job_1s`` in app.py using
``map_value.map_value()`` so the calibration ranges are in one place.

On non-Pi systems the mock implementation is a no-op — state.pump_i_read and
state.pump_v_read stay at 0, and app.py converts those to the default I/V values.
"""

import logging
from typing import TYPE_CHECKING

from hardware.gpio_interface import IS_PI

if TYPE_CHECKING:
    from core.state import AppState

log = logging.getLogger(__name__)

if IS_PI:
    import Adafruit_GPIO.SPI as SPI       # type: ignore
    import Adafruit_MCP3008               # type: ignore

    def read_curr_and_volt(state: "AppState") -> None:
        """
        Read current and voltage channels from the MCP3008 ADC and store raw values.

        A new MCP3008 instance is created each call because the SpiDev connection
        is not persistent across scheduler ticks.

        Args:
            state: AppState instance — pump_i_read and pump_v_read are updated.
        """
        try:
            mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(0, 0))
            i_raw = mcp.read_adc(6)  # CH6: prąd (current)
            v_raw = mcp.read_adc(7)  # CH7: napięcie (voltage)
            state.update(pump_i_read=i_raw, pump_v_read=v_raw)
            log.debug("ADC: I_raw=%d  V_raw=%d", i_raw, v_raw)
        except Exception as e:
            log.error("ADC read failed: %s", e)

else:
    def read_curr_and_volt(state: "AppState") -> None:  # type: ignore
        """Mock: no-op on non-Pi — leaves pump_i_read/pump_v_read at defaults (0)."""
        pass
