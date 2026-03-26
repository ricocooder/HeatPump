"""
GPIO relay output controller for the HeatPump system.

Controls 8 relay channels via GPIO. Pump speed is set using 3-bit binary
encoding across pins[0..2] — allowing 8 efficiency levels (0-7) with only
3 GPIO pins.

Relay logic:
  - NC (Normally Closed) relays: LOW = energised = circuit CLOSED = pump/device ON
  - NO (Normally Open) relay:   HIGH = energised = circuit CLOSED = valve switches position
  GPIO HIGH on an NC output turns the device OFF; LOW turns it ON.
"""

import logging
from typing import TYPE_CHECKING, List

from hardware.gpio_interface import gpio

if TYPE_CHECKING:
    from core.state import AppState

log = logging.getLogger(__name__)

# Pump efficiency levels 0-7 encoded as 3-bit values across pins[0..2].
# Tuple format: (bit0_LSB, bit1, bit2_MSB)
# NC relay logic: bit=0 → GPIO LOW → relay energised → pump stage ON
# Example: level 7 = (0,0,0) → all three stages active = maximum flow
_EFI_BITS: dict = {
    7: (0, 0, 0),   # 111 inverted → all stages ON = maximum
    6: (0, 0, 1),
    5: (0, 1, 0),
    4: (1, 0, 0),
    3: (0, 1, 1),
    2: (1, 0, 1),   # NOTE: original code had a bug here — tempPins[0]=0 instead of tempPins[1]=0
    1: (1, 1, 0),
    0: (1, 1, 1),   # all stages OFF = pump stopped
}


def apply_outputs(state: "AppState") -> float:
    """
    Write the current pump state to all GPIO relay outputs.

    In **auto** mode: sets the circulation pump, 3-way valve, furnace controller,
    and the 3-bit efficiency pins according to ``state.heat_object`` and ``state.pump_efi``.

    In **manual** mode: writes ``state.temp_pins`` directly to GPIO, bypassing all
    logic. Pin 6 (pompa obiegowa) is forced HIGH (OFF) in manual mode to prevent
    unintended circulation when the user is adjusting individual relays.

    Args:
        state: AppState instance — reads pump_efi, heat_object, pump_mode, temp_pins.

    Returns:
        float: Current pump efficiency as a percentage (0.0–100.0),
               or the previous value if a GPIO error occurred.
    """
    pins       = state.pins
    pump_efi   = state.pump_efi
    heat_object= state.heat_object
    pump_mode  = state.pump_mode
    temp_pins  = list(state.temp_pins)  # local copy — mutated then written back atomically

    base_efi_step = 100.0 / 7.0  # each efficiency level = ~14.3%

    try:
        gpio.setmode(gpio.BCM)
        for p in pins:
            gpio.setup(p, gpio.OUT)

        if pump_mode == 'auto':
            # Pompa obiegowa (NC) — always on in auto mode
            gpio.output(pins[6], gpio.LOW)
            temp_pins[6] = 0

            # Zawór 3-drogowy (NO): HIGH = energised = routes to bojler
            if heat_object == 1:
                gpio.output(pins[3], gpio.HIGH)
                temp_pins[3] = 1
            else:
                gpio.output(pins[3], gpio.LOW)
                temp_pins[3] = 0

            # Sterownik pieca (NC): HIGH = piec controller enabled
            if heat_object == 0:
                gpio.output(pins[4], gpio.LOW)
                temp_pins[4] = 0
            else:
                gpio.output(pins[4], gpio.HIGH)
                temp_pins[4] = 1

            if heat_object != 0 and pump_efi in _EFI_BITS:
                # Apply 3-bit binary efficiency encoding
                b0, b1, b2 = _EFI_BITS[pump_efi]
                gpio.output(pins[0], gpio.HIGH if b0 else gpio.LOW)
                temp_pins[0] = b0
                gpio.output(pins[1], gpio.HIGH if b1 else gpio.LOW)
                temp_pins[1] = b1
                gpio.output(pins[2], gpio.HIGH if b2 else gpio.LOW)
                temp_pins[2] = b2
                base_efi_percent = round(base_efi_step * pump_efi, 1)
            else:
                # heat_object == 0: turn all pump control pins OFF (HIGH = NC off)
                for i in range(3):
                    gpio.output(pins[i], gpio.HIGH)
                    temp_pins[i] = 1
                base_efi_percent = 0.0

        else:
            # Manual mode: write temp_pins directly, but keep obiegowa OFF for safety
            temp_pins[6] = 1
            gpio.output(pins[6], gpio.HIGH)
            for i, pin in enumerate(pins):
                gpio.output(pin, gpio.HIGH if temp_pins[i] == 1 else gpio.LOW)
            base_efi_percent = round(base_efi_step * pump_efi, 1) if heat_object != 0 else 0.0

        state.update(temp_pins=temp_pins)
        return base_efi_percent

    except Exception as e:
        log.error("GPIO output error: %s", e)
        return state.base_efi_percent  # keep last known good value on error
