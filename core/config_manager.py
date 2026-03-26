"""
Persistent configuration manager for the HeatPump control system.

Saves and loads a whitelist of user-configurable settings to/from a JSON file.
Only keys listed in PERSISTED_KEYS are written — runtime state (sensor readings,
GPIO pin states, ADC values) is deliberately excluded to keep the config file
clean and human-readable.
"""

import json
import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import AppState

log = logging.getLogger(__name__)

# Keys from AppState that survive restarts. Runtime-only attributes are excluded.
PERSISTED_KEYS = [
    "set_temp", "pump_interval", "pump_temp_offset",
    "sensor_index_list", "picked_lang", "sezon",
    "godzina", "descriptions",
]


class ConfigManager:
    """
    Loads and saves a subset of AppState to a JSON file on disk.

    The same instance is reused throughout the application lifetime and
    is called explicitly (not automatically) so that I/O only happens
    on startup, shutdown, and when the user changes a setting.
    """

    def __init__(self, path: str):
        """
        Args:
            path: Absolute path to the config JSON file (e.g. /home/pi/HeatPump/config.json).
        """
        self.path = path

    def load_into(self, state: "AppState") -> None:
        """
        Load persisted settings from disk into *state*.

        If the file does not exist (first run), state keeps its defaults.
        Silently ignores unknown keys so older config files remain forward-compatible.

        Args:
            state: The AppState instance to populate.
        """
        if not os.path.exists(self.path):
            log.info("config.json not found — using defaults")
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            # Only update keys we recognise; unknown keys from older versions are ignored
            updates = {k: data[k] for k in PERSISTED_KEYS if k in data}
            state.update(**updates)
            log.info("Config loaded from %s", self.path)
        except Exception as e:
            log.error("Failed to load config: %s", e)

    def save_from(self, state: "AppState") -> None:
        """
        Write the persisted subset of *state* to disk as JSON.

        Called on orderly shutdown and after any user-initiated setting change.

        Args:
            state: The AppState instance to read values from.
        """
        snap = state.snapshot()
        data = {k: snap[k] for k in PERSISTED_KEYS if k in snap}
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log.info("Config saved to %s", self.path)
        except Exception as e:
            log.error("Failed to save config: %s", e)
