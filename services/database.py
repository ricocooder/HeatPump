"""
SQLite persistence for time-series sensor data.

Each measurement type has its own table to keep queries simple and avoid
schema migrations when new sensor types are added.

Table schema (all tables): (rDatetime TEXT, rDate TEXT, value REAL)
  - rDatetime: 'YYYY-MM-DD HH:MM:SS' in local time (used for range queries)
  - rDate:     always '1' (legacy field, kept for schema compatibility)
  - value:     the measured value

Change detection: ``check_values()`` compares each new reading against a
module-level cache of the previous reading. A row is only inserted if at least
one value has changed by more than ``threshold``. This prevents filling the DB
with identical rows during periods of inactivity.

DB path: defaults to ``myDB.db`` next to app.py, overridable via the
``HEATPUMP_DB_PATH`` environment variable for testing or custom deployments.
"""

import logging
import os
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import AppState

log = logging.getLogger(__name__)

# Resolve DB path relative to the project root (parent of services/)
_DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "myDB.db"
)
DB_PATH = os.environ.get("HEATPUMP_DB_PATH", _DEFAULT_DB)


def _connect() -> sqlite3.Connection:
    """Open and return a new SQLite connection to DB_PATH."""
    return sqlite3.connect(DB_PATH)


def log_values(state: "AppState") -> None:
    """
    Insert one row per measurement table with the current sensor readings.

    Uses ``datetime(CURRENT_TIMESTAMP, 'localtime')`` so stored timestamps
    reflect wall-clock time rather than UTC — avoids confusion on the charts.

    Args:
        state: AppState instance — reads sensor_index_list, read_temp, pump_v,
               pump_i, and base_efi_percent.
    """
    snap = state.snapshot()
    sil  = snap['sensor_index_list']
    rt   = snap['read_temp']
    try:
        conn = _connect()
        c = conn.cursor()
        ts_expr = "datetime(CURRENT_TIMESTAMP, 'localtime')"
        c.execute(f"INSERT INTO temp1 VALUES({ts_expr},?,?)", ("1", rt[sil[0]]))
        c.execute(f"INSERT INTO temp2 VALUES({ts_expr},?,?)", ("1", rt[sil[1]]))
        c.execute(f"INSERT INTO temp3 VALUES({ts_expr},?,?)", ("1", rt[sil[2]]))
        c.execute(f"INSERT INTO volt  VALUES({ts_expr},?,?)", ("1", snap['pump_v']))
        c.execute(f"INSERT INTO cur   VALUES({ts_expr},?,?)", ("1", snap['pump_i']))
        c.execute(f"INSERT INTO efi   VALUES({ts_expr},?,?)", ("1", snap['base_efi_percent']))
        conn.commit()
    except Exception as e:
        log.error("DB write error: %s", e)
    finally:
        conn.close()


def check_values(state: "AppState", threshold: float = 1.0) -> None:
    """
    Write to DB only when a measured value has changed by at least *threshold*.

    Compares current readings against a module-level cache (_prev_values).
    If any single channel has changed by >= threshold, all channels are logged
    together so chart timestamps stay consistent across all series.

    Args:
        state:     AppState instance to read current values from.
        threshold: Minimum change (in sensor units) required to trigger a write.
                   Default 1.0 works for both °C and % — adjust if needed.
    """
    snap = state.snapshot()
    sil  = snap['sensor_index_list']
    rt   = snap['read_temp']

    # Module-level cache avoids a SELECT query for change detection
    prev = _prev_values

    changed = False
    if abs(rt[sil[0]] - prev['t0']) >= threshold:
        changed = True
    if abs(rt[sil[1]] - prev['t1']) >= threshold:
        changed = True
    if abs(rt[sil[2]] - prev['t2']) >= threshold:
        changed = True
    if abs(snap['pump_v'] - prev['v']) >= threshold:
        changed = True
    if abs(snap['pump_i'] - prev['i']) >= threshold:
        changed = True
    if abs(snap['base_efi_percent'] - prev['efi']) >= threshold:
        changed = True

    if changed:
        log_values(state)
        # Update cache so next call compares against the just-logged values
        prev['t0']  = rt[sil[0]]
        prev['t1']  = rt[sil[1]]
        prev['t2']  = rt[sil[2]]
        prev['v']   = snap['pump_v']
        prev['i']   = snap['pump_i']
        prev['efi'] = snap['base_efi_percent']


# Module-level previous-value cache (intentionally not in AppState — DB concerns
# should not leak into application state)
_prev_values = {'t0': 2.14, 't1': 2.14, 't2': 2.14, 'v': 0.0, 'i': 0.0, 'efi': 0.0}


def get_data_from_db(from_dt: str, to_dt: str) -> dict:
    """
    Fetch time-series data for all channels within a datetime range.

    Args:
        from_dt: Start of range, format 'YYYY-MM-DD HH:MM'.
        to_dt:   End of range, format 'YYYY-MM-DD HH:MM'.

    Returns:
        dict: Keys are channel names ('temp1', 'temp2', 'temp3', 'volt', 'curr', 'efi').
              Each value is a list of dicts: [{"ts": "YYYY-MM-DD HH:MM:SS", "v": float}, ...]
              Empty list if no data or on error.
    """
    result = {k: [] for k in ('temp1', 'temp2', 'temp3', 'volt', 'curr', 'efi')}
    # Map result keys to actual SQLite table names ('curr' → 'cur' for legacy naming)
    table_map = {
        'temp1': 'temp1', 'temp2': 'temp2', 'temp3': 'temp3',
        'volt': 'volt', 'curr': 'cur', 'efi': 'efi'
    }
    try:
        conn = _connect()
        c = conn.cursor()
        for key, table in table_map.items():
            c.execute(
                f"SELECT * FROM {table} WHERE rDatetime BETWEEN ? AND ?",
                (from_dt, to_dt)
            )
            rows = c.fetchall()
            result[key] = [{"ts": r[0], "v": r[2]} for r in rows]
        conn.close()
    except Exception as e:
        log.error("DB read error: %s", e)
    return result
