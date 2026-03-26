"""
Thread-safe application state for the HeatPump control system.

State is split into two groups:
  - Persisted: loaded from / saved to config.json across restarts
    (temperatures, intervals, schedule, language, season)
  - Runtime: reset on every startup
    (live sensor readings, GPIO pin states, ADC values)

Constants (PINS, DNI, LANGUAGE) are stored here as the single source of truth
and exposed read-only via AppState so templates and routes don't import them directly.
"""

import threading
from dataclasses import dataclass, field
from typing import List

# ---------------------------------------------------------------------------
# Default weekly schedule: 24 rows (hours) × 8 cols (label + 7 days)
# Row format: [hour_label, Mon, Tue, Wed, Thu, Fri, Sat, Sun]
# ---------------------------------------------------------------------------
DEFAULT_GODZINA = [
    ['0', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['1', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['2', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['3', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['4', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['5', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['6', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['7', 'ON',  'ON',  'ON',  'ON',  'ON',  'ON',  'ON' ],
    ['8', 'ON',  'ON',  'ON',  'ON',  'ON',  'ON',  'ON' ],
    ['9', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON',  'ON' ],
    ['10','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON',  'ON' ],
    ['11','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON',  'ON' ],
    ['12','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON',  'ON' ],
    ['13','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON',  'ON' ],
    ['14','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON',  'ON' ],
    ['15','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON',  'ON' ],
    ['16','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON',  'ON' ],
    ['17','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON',  'ON' ],
    ['18','ON',  'ON',  'ON',  'ON',  'ON',  'ON',  'ON' ],
    ['19','ON',  'ON',  'ON',  'ON',  'ON',  'ON',  'ON' ],
    ['20','ON',  'ON',  'ON',  'ON',  'ON',  'ON',  'ON' ],
    ['21','ON',  'ON',  'ON',  'ON',  'ON',  'ON',  'ON' ],
    ['22','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['23','OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
]

DEFAULT_DESCRIPTIONS = [
    'T1 - Zew', 'T2 - Bojler', 'T3 - Pompa wyjscie',
    'T4 - Pompa powrot', 'T5 - Temp. zewnetrzna', 'T6'
]

# ---------------------------------------------------------------------------
# GPIO pin numbers (BCM) and their roles
# Index corresponds to usage throughout set_outputs.py:
#   0-2: pump efficiency bits (3-bit binary, NC logic)
#   3:   zawór 3-drogowy (NO)
#   4:   sterownik pieca (NC)
#   5:   zasilanie 24V (NC)
#   6:   pompa obiegowa (NC)
#   7:   spare
# ---------------------------------------------------------------------------
PINS = [26, 5, 6, 12, 25, 24, 23, 16]
PINS_DESC = [
    '[1] Sterowanie pompy1 (NC)', '[2] Sterowanie pompy2 (NC)',
    '[3] Sterowanie pompy3 (NC)', '[4] Zawor trojdrogowy (NO)',
    '[5] Sterownik piec (NC)',    '[6] Zal/Wyl 24V (NC)',
    '[7] Pompa obiegowa (NC)',    '[8] Spare'
]
PINS_LOGIC = ['NC', 'NC', 'NC', 'NO', 'NC', 'NC', 'NC', 'TBD']

# ---------------------------------------------------------------------------
# Day names in English (index 0) and Polish (index 1)
# Keys are 1-based strings to match the schedule grid column indices
# ---------------------------------------------------------------------------
DNI = {
    "1": ["Time\\Day", "Godzina\\Dzień"],
    "2": ["Monday",    "Poniedziałek"],
    "3": ["Tuesday",   "Wtorek"],
    "4": ["Wednesday", "Środa"],
    "5": ["Thursday",  "Czwartek"],
    "6": ["Friday",    "Piątek"],
    "7": ["Saturday",  "Sobota"],
    "8": ["Sunday",    "Niedziela"],
}

# ---------------------------------------------------------------------------
# UI strings: each value is [English, Polish]
# Index matches state.picked_lang (0=EN, 1=PL)
# ---------------------------------------------------------------------------
LANGUAGE = {
    "home":                 ["Home", "Start"],
    "Settings":             ["Settings", "Nastawy"],
    "Schedule":             ["Schedule", "Harmonogram"],
    "History/Charts":       ["Charts", "Wykresy"],
    "Sensor configuration": ["Sensor config", "Konfig. czujnikow"],
    "RaspberryPi":          ["Raspberry Pi", "Raspberry Pi"],
    "Temperature":          ["Temperature", "Temperatura"],
    "Language":             ["Language", "Język"],
    "Lang":                 ["en", "pl"],
    "LangChange":           ["Change Language", "Zmiana Języka"],
    "OperatingMode":        ["Operating mode", "Tryb pracy"],
    "SetTemp":              ["set temp.", "temp. zadana"],
    "ActualVoltage":        ["Actual Voltage", "Napięcie pompy"],
    "ActualCurrent":        ["Actual Current", "Prąd pobierany"],
    "ActualPower":          ["Actual Power", "Moc pompy"],
    "External":             ["External", "Zewnętrzne"],
    "PumpBoiler":           ["Pump - boiler", "Pompa - bojler"],
    "PumpFloorHeating":     ["Pump - floor heating", "Pompa - ogrzewanie podłogowe"],
    "PumpOn":               ["Pump working", "Pompa pracuje"],
    "FiveOn":               ["Furnace working", "Piec pracuje"],
    "RaspPiSett":           ["Raspberry Pi settings", "Ustawienia Raspberry Pi"],
    "RaspPiDat":            ["Memory card data", "Dane karty pamieci"],
    "RaspPiMem":            ["Read Pi memory", "Odczyt pamieci Pi"],
    "SensConfig":           ["Sensor configuration", "Konfiguracja czujnikow"],
    "SensConfAssi":         ["Assign sensor numbers here.",
                             "Tu mozesz przypisac numer czujnika."],
    "SensConfDet":          ["Sensors detected", "Wykryta liczba czujnikow"],
    "SensConfigDetNr":      ["Sensor at index", "Sensor at index"],
    "SensConfIndic":        ["actual value", "wartosc aktualna"],
    "SensConfOrder":        ["Order: [outside, boiler, pumpOut, pumpIn]",
                             "Kolejnosc: [outside, boiler, pumpOut, pumpIn]"],
    "SensConfigCurr":       ["Currently", "Obecnie"],
    "SensConfig1":          ["Boiler sensor?", "Czujnik bojlera?"],
    "SensConfig2":          ["Floor heating sensor?", "Czujnik podlogi?"],
    "SensConfig3":          ["Outside temperature?", "Temperatura zewnetrzna?"],
    "SensConfig4":          ["Pump inlet (low temp)?", "Wejscie pompy (niska temp)?"],
    "SensConfig5":          ["Pump outlet (high temp)?", "Wyjscie pompy (wysoka temp)?"],
    "DataDBDegrees":        ["Degrees [°C]", "Stopnie [°C]"],
    "DataDBTempOut":        ["Outdoor temperature", "Temperatura zewnętrzna"],
    "DataDBBoilTemp":       ["Boiler temperature", "Temperatura bojlera"],
    "DataDBBPumpTemp":      ["Pump output temperature", "Temperatura wyjscie pompy"],
    "DataDBBPumpAmp":       ["Amperes [A]", "Ampery [A]"],
    "DataDBBPumpCurr":      ["Current", "Prąd"],
    "DataDBBPumpVolt":      ["Volt [V]", "Volt [V]"],
    "DataDBBPumpVoltage":   ["Voltage", "Napięcie"],
}


class AppState:
    """
    Central in-memory store for all application state.

    All attributes are divided into two groups:
    - **Persisted** (saved to config.json): user settings that must survive restarts.
    - **Runtime** (reset each startup): live sensor values, GPIO states, ADC readings.

    Thread safety: use ``update()`` for atomic writes from background scheduler threads.
    Use ``snapshot()`` to obtain a consistent copy for reading (e.g. in SSE or templates)
    without holding the lock while sleeping or doing I/O.
    """

    def __init__(self):
        self._lock = threading.Lock()

        # --- Persisted to config.json ---
        self.set_temp: List[float]         = [0, 45.0, 33.0]        # [unused, bojler, podłogówka] °C
        self.pump_interval: List[int]      = [0, 30, 60]            # [unused, bojler, podłogówka] seconds between efi steps
        self.pump_temp_offset: List[float] = [0, 2.0, 2.0]          # hysteresis band ±°C
        self.sensor_index_list: List[int]  = [0, 1, 3, 2]           # maps role→physical sensor index
        self.picked_lang: int              = 1                       # 0=English, 1=Polish
        self.sezon: str                    = 'Lato'                  # 'Lato' (summer) or 'Zima' (winter)
        self.godzina: List[List[str]]      = [list(row) for row in DEFAULT_GODZINA]
        self.descriptions: List[str]       = list(DEFAULT_DESCRIPTIONS)

        # --- Runtime only (not saved) ---
        self.read_temp: List[float]        = [3.14] * 6             # DS18B20 readings; 3.14 = no reading yet
        self.pump_efi: int                 = 1                       # current efficiency level 0-7
        self.pump_mode: str                = 'auto'                  # 'auto' or 'manual'
        self.heat_object: int              = 1                       # 0=off, 1=bojler, 2=podłogówka
        self.base_efi_percent: float       = 0.0                    # efi as percentage (0-100)
        self.temp_pins: List[int]          = [0] * 8                # GPIO output states (0=LOW, 1=HIGH)
        self.pump_i: float                 = 9.7                    # calculated current (A)
        self.pump_v: float                 = 232.0                  # calculated voltage (V)
        self.pump_p: float                 = 30.0                   # calculated power (kW)
        self.pump_i_read: int              = 0                      # raw ADC value for current (0-1023)
        self.pump_v_read: int              = 0                      # raw ADC value for voltage (0-1023)
        self.temp_sens_found_number: int   = 0                      # number of DS18B20 sensors detected
        self.disk_space_list: list         = []                     # output of `df -h /`
        self.ac_time_plus_interval: float  = 0.0                   # timestamp of last efi step change

        # --- Read-only constants exposed to templates ---
        self.pins       = PINS
        self.pins_desc  = PINS_DESC
        self.pins_logic = PINS_LOGIC
        self.dni        = DNI
        self.language   = LANGUAGE

    def update(self, **kwargs) -> None:
        """
        Atomically update one or more state attributes.

        Args:
            **kwargs: Attribute name → new value pairs.
                      Unknown keys are silently ignored to avoid crashes
                      from stale callers after a refactor.
        """
        with self._lock:
            for k, v in kwargs.items():
                if hasattr(self, k):
                    setattr(self, k, v)

    def snapshot(self) -> dict:
        """
        Return a shallow copy of all public state without holding the lock.

        Use this when you need a consistent view of state but will be doing
        I/O or sleeping afterwards (e.g. SSE generator, template rendering).
        Private attributes (starting with '_') are excluded.

        Returns:
            dict: Copy of all public attributes at the moment of the call.
        """
        with self._lock:
            return {
                k: v for k, v in self.__dict__.items()
                if not k.startswith('_')
            }
