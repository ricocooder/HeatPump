"""
History and chart data routes — GET /history and GET /api/data.

GET /history renders the Plotly chart page (new_history.html).
  The chart page fetches its own data via the JSON API endpoint below.

GET /api/data returns time-series data as JSON for all sensor channels.
  Query params: from_dt, to_dt — format 'YYYY-MM-DD HH:MM'.
  If params are missing or invalid, defaults to the last 24 hours.
"""

import datetime
import logging
import time

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services import database

log = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

_FMT = "%Y-%m-%d %H:%M"


def _validate_date(d: str) -> bool:
    """
    Check whether *d* matches the expected datetime format.

    Args:
        d: String to validate.

    Returns:
        bool: True if *d* parses cleanly as 'YYYY-MM-DD HH:MM'.
    """
    try:
        datetime.datetime.strptime(d, _FMT)
        return True
    except ValueError:
        return False


def _default_range(hours: int = 24):
    """
    Build a (from_dt, to_dt) tuple spanning the last *hours* hours.

    Args:
        hours: Number of hours to look back from now. Default 24.

    Returns:
        tuple[str, str]: (from_dt, to_dt) formatted as 'YYYY-MM-DD HH:MM'.
    """
    now  = datetime.datetime.now()
    frm  = now - datetime.timedelta(hours=hours)
    return frm.strftime(_FMT), now.strftime(_FMT)


@router.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    """
    Render the Plotly chart page.

    Accepts optional 'from' and 'to' query params to pre-set the date range.
    If from == to (e.g. fresh page load with default value), falls back to
    the last 24 hours to avoid rendering empty charts.
    """
    state = request.app.state.pump_state
    from_dt = request.query_params.get("from", time.strftime(_FMT))
    to_dt   = request.query_params.get("to",   time.strftime(_FMT))

    if not _validate_date(from_dt):
        from_dt = time.strftime("%Y-%m-%d 00:00")
    if not _validate_date(to_dt):
        to_dt = time.strftime(_FMT)

    # Identical from/to happens on a fresh page load — show last 24 h by default
    if from_dt == to_dt:
        from_dt, to_dt = _default_range(24)

    snap = state.snapshot()
    return templates.TemplateResponse("new_history.html", {
        "request":    request,
        "from_date":  from_dt,
        "to_date":    to_dt,
        "pickedLang": snap["picked_lang"],
        "lang":       snap["language"],
        "sensFoundList":    snap["read_temp"],
        "sensorIndexList":  snap["sensor_index_list"],
    })


@router.get("/api/data")
async def api_data(request: Request):
    """
    Return time-series data for all sensor channels as JSON.

    Used by the Plotly charts on the history page via ``fetch('/api/data?...')``.

    Query params:
        from_dt: Start datetime ('YYYY-MM-DD HH:MM'). Falls back to last 24h if invalid.
        to_dt:   End datetime ('YYYY-MM-DD HH:MM'). Falls back to last 24h if invalid.

    Returns:
        dict: Channel data + 'lang' key for the chart JS to use the correct labels.
    """
    from_dt = request.query_params.get("from_dt", "")
    to_dt   = request.query_params.get("to_dt",   "")

    if not _validate_date(from_dt) or not _validate_date(to_dt):
        from_dt, to_dt = _default_range(24)

    state = request.app.state.pump_state
    data  = database.get_data_from_db(from_dt, to_dt)
    # Append language preference so chart JS can switch axis/legend labels
    data["lang"] = state.snapshot()["picked_lang"]
    return data
