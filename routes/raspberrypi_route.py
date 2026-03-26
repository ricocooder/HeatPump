"""
Raspberry Pi system settings route — GET/POST /raspberrypi.

Provides:
  - Disk usage report (reads df -h /) with a warning at 80% usage.
    A full SD card causes silent SQLite failures, so early warning is important.
  - Language toggle (English ↔ Polish), persisted to config.json.
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from services import disk_space

log = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/raspberrypi", response_class=HTMLResponse)
async def raspberrypi(request: Request):
    """
    Render the Raspberry Pi settings page.

    Shows current disk usage (if previously read), GPIO pin states,
    and language toggle.
    """
    state = request.app.state.pump_state
    snap  = state.snapshot()
    msg   = request.query_params.get("msg", "")
    level = request.query_params.get("level", "success")
    return templates.TemplateResponse("raspberrypi.html", {
        "request":       request,
        "diskSpaceList": snap["disk_space_list"],
        "sensFoundList": snap["read_temp"],
        "sensorIndexList": snap["sensor_index_list"],
        "pickedLang":    snap["picked_lang"],
        "lang":          snap["language"],
        "ledStrip":      snap["temp_pins"],
        "ledStripDiscription": snap["pins_desc"],
        "msg": msg, "level": level,
    })


@router.post("/raspberrypi")
async def raspberrypi_post(request: Request):
    """
    Handle system action buttons: read disk usage or change language.

    Disk threshold is hardcoded at 80% — above that the warning level
    changes to 'danger' and a Polish warning message is shown.
    """
    state  = request.app.state.pump_state
    config = request.app.state.config
    form   = await request.form()
    msg    = ""
    level  = "success"

    if form.get("SaveDB"):
        data, full = disk_space.check_disk_space(80)
        state.update(disk_space_list=data)
        if full:
            # Warn loudly — a full SD card silently kills DB writes
            msg   = "Karta pamieci ponad 80%! Zrob cos z tym!"
            level = "danger"
        else:
            msg = f"Odczytano: {' '.join(data)}"

    if form.get("LangChange"):
        # Toggle between Polish (1) and English (0)
        new_lang = 0 if state.picked_lang == 1 else 1
        state.update(picked_lang=new_lang)
        config.save_from(state)
        msg   = "Zmieniono język" if new_lang == 1 else "Language changed"
        level = "success"

    return RedirectResponse(
        f"/raspberrypi?msg={msg}&level={level}", status_code=303
    )
