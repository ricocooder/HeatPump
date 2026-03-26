"""
GPIO abstraction layer for the HeatPump control system.

Provides a unified ``GpioInterface`` class that works on both Raspberry Pi
(using RPi.GPIO) and development machines (using a no-op mock that logs calls).

Pi detection uses the 1-Wire sysfs path as a proxy: if ``/sys/bus/w1/devices/``
exists we assume we are on the Pi and attempt to import RPi.GPIO.
This avoids the need for a separate environment flag or config setting.
"""

import logging
import os

log = logging.getLogger(__name__)

# Use 1-Wire bus presence as a reliable Pi indicator.
# /sys/bus/w1/devices/ only exists after `modprobe w1-gpio` on a Pi.
IS_PI = os.path.exists('/sys/bus/w1/devices/')

if IS_PI:
    import RPi.GPIO as _GPIO  # type: ignore

    class GpioInterface:
        """Real GPIO interface — wraps RPi.GPIO for use on Raspberry Pi."""

        BCM  = _GPIO.BCM
        OUT  = _GPIO.OUT
        HIGH = _GPIO.HIGH
        LOW  = _GPIO.LOW

        def setmode(self, mode) -> None:
            """Set the pin numbering mode (BCM or BOARD)."""
            _GPIO.setmode(mode)

        def setup(self, pin: int, mode) -> None:
            """Configure a single pin as input or output."""
            _GPIO.setup(pin, mode)

        def output(self, pin: int, val) -> None:
            """Write HIGH or LOW to an output pin."""
            _GPIO.output(pin, val)

        def cleanup(self) -> None:
            """Release all GPIO resources — call on shutdown."""
            _GPIO.cleanup()

else:
    class GpioInterface:  # type: ignore
        """
        Mock GPIO interface for development machines without RPi.GPIO.

        All calls are logged at DEBUG level so they are silent by default
        (only visible when log level is set to DEBUG).
        """

        BCM  = "BCM"
        OUT  = "OUT"
        HIGH = 1
        LOW  = 0

        def setmode(self, mode) -> None:
            log.debug("[GPIO MOCK] setmode(%s)", mode)

        def setup(self, pin: int, mode) -> None:
            log.debug("[GPIO MOCK] setup(pin=%s, mode=%s)", pin, mode)

        def output(self, pin: int, val) -> None:
            log.debug("[GPIO MOCK] output(pin=%s, val=%s)", pin, val)

        def cleanup(self) -> None:
            log.debug("[GPIO MOCK] cleanup()")


# Singleton — imported everywhere as `from hardware.gpio_interface import gpio`
gpio = GpioInterface()
