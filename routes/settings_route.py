"""
Settings route — GET/POST /settings.

Allows the user to configure temperature setpoints, pump intervals,
and temperature hysteresis amplitudes for bojler and podłogówka.

Each save button updates only the specific index in its list, leaving
other indices (index 0 is unused, kept for 1-based indexing) untouched.
Changes are persisted to config.json immediately.
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

log = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    """
    Render the settings page with current temperature and interval values.

    Args:
        request: FastAPI request — reads optional msg/level query params for toast.
    """
    state = request.app.state.pump_state
    snap = state.snapshot()
    msg   = request.query_params.get("msg", "")
    level = request.query_params.get("level", "success")
    return templates.TemplateResponse("settings.html", {
        "request":          request,
        "setTempList":      snap["set_temp"],
        "pumpIntervalList": snap["pump_interval"],
        "pumpTempOfsetList":snap["pump_temp_offset"],
        "sensFoundList":    snap["read_temp"],
        "sensorIndexList":  snap["sensor_index_list"],
        "pickedLang":       snap["picked_lang"],
        "lang":             snap["language"],
        "msg": msg, "level": level,
    })


@router.post("/settings")
async def settings_post(request: Request):
    """
    Save one setting at a time based on which submit button was pressed.

    Each list (set_temp, pump_interval, pump_temp_offset) uses index 0 as
    a placeholder — never written — so indexes 1 and 2 map directly to
    bojler and podłogówka without off-by-one arithmetic.

    Redirects back to GET /settings with a toast message on success or error.
    """
    state  = request.app.state.pump_state
    config = request.app.state.config
    form   = await request.form()
    msg    = ""

    try:
        if form.get("Save1"):
            # Podłogówka temperature setpoint (index 2)
            state.update(set_temp=[state.set_temp[0],
                                   state.set_temp[1],
                                   float(form["tempZad1"])])
            msg = "Zapisano temperaturę podłogówki"
        if form.get("Save2"):
            # Bojler temperature setpoint (index 1)
            state.update(set_temp=[state.set_temp[0],
                                   float(form["tempZad2"]),
                                   state.set_temp[2]])
            msg = "Zapisano temperaturę bojlera"
        if form.get("Save3"):
            iv = list(state.pump_interval)
            iv[2] = int(form["setInterval1"])   # podłogówka interval
            state.update(pump_interval=iv)
            msg = "Zapisano interwał podłogówki"
        if form.get("Save4"):
            iv = list(state.pump_interval)
            iv[1] = int(form["setInterval2"])   # bojler interval
            state.update(pump_interval=iv)
            msg = "Zapisano interwał bojlera"
        if form.get("Save5"):
            of = list(state.pump_temp_offset)
            of[2] = float(form["setAmplitude1"])  # podłogówka hysteresis
            state.update(pump_temp_offset=of)
            msg = "Zapisano amplitudę podłogówki"
        if form.get("Save6"):
            of = list(state.pump_temp_offset)
            of[1] = float(form["setAmplitude2"])  # bojler hysteresis
            state.update(pump_temp_offset=of)
            msg = "Zapisano amplitudę bojlera"
        if msg:
            config.save_from(state)
            level = "success"
        else:
            level = "secondary"
    except (ValueError, KeyError) as e:
        msg   = f"Błąd wartości: {e} — użyj kropki zamiast przecinka"
        level = "danger"

    return RedirectResponse(f"/settings?msg={msg}&level={level}", status_code=303)
