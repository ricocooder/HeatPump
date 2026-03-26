"""
Weekly heating schedule route — GET/POST /harmonogram.

The schedule is a 24×8 grid: 24 hours × (1 label + 7 days).
Each cell is either "ON" or "OFF". Clicking a cell in the browser
submits the form with that cell's key (format: "hour-day_index").

The POST handler toggles the clicked cell and saves the updated
schedule to config.json so it survives restarts.
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

log = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/harmonogram", response_class=HTMLResponse)
async def harmonogram(request: Request):
    """
    Render the weekly schedule grid.

    Args:
        request: FastAPI request — reads optional msg/level query params for toast.
    """
    state = request.app.state.pump_state
    snap  = state.snapshot()
    msg   = request.query_params.get("msg", "")
    level = request.query_params.get("level", "success")
    return templates.TemplateResponse("harmonogram.html", {
        "request":       request,
        "godzina":       snap["godzina"],
        "dni":           snap["dni"],
        "sensFoundList": snap["read_temp"],
        "sensorIndexList": snap["sensor_index_list"],
        "pickedLang":    snap["picked_lang"],
        "lang":          snap["language"],
        "msg": msg, "level": level,
    })


@router.post("/harmonogram")
async def harmonogram_post(request: Request):
    """
    Toggle the ON/OFF state of the clicked schedule cell.

    Form keys use the format "hour-day" (e.g. "7-3" = 07:00 on Wednesday).
    Hour is 0-23, day_index is 1-7 (column in the godzina grid).

    Any key without a '-' (e.g. submit button names) is silently ignored.
    """
    state  = request.app.state.pump_state
    config = request.app.state.config
    form   = await request.form()

    new_grid = [list(row) for row in state.godzina]
    changed  = False

    for key in form.keys():
        # Only process cell keys in "hour-day" format; skip button names etc.
        if '-' in key:
            parts = key.split('-')
            if len(parts) == 2:
                try:
                    hour = int(parts[0])
                    day  = int(parts[1])
                    if 0 <= hour <= 23 and 1 <= day <= 7:
                        current = new_grid[hour][day]
                        new_grid[hour][day] = "OFF" if current == "ON" else "ON"
                        changed = True
                except (ValueError, IndexError):
                    pass

    if changed:
        state.update(godzina=new_grid)
        config.save_from(state)

    return RedirectResponse("/harmonogram?msg=Harmonogram+zapisany&level=success",
                            status_code=303)
