"""
Temperature sensor configuration route — GET/POST /temp_sensor_config.

Allows the user to assign each physical DS18B20 sensor (detected by index 0-N)
to a logical role: outdoor temperature, bojler, podłogówka, pump inlet, etc.

The mapping is stored in state.sensor_index_list and persisted to config.json.
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

log = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Maps submit button name → (form field name containing new index, sensor_index_list slot)
# Note: setIndexBtn3 and setIndexBtn3_1 both map to sensor_index_list[2] and [3]
# because the original template had a duplicate btn name (3) that was later renamed to 3_1
_BTN_MAP = {
    "setIndexBtn0":   ("setValueSensorIndex0",   0),  # outdoor / temp. zewn.
    "setIndexBtn1":   ("setValueSensorIndex1",   1),  # bojler
    "setIndexBtn2":   ("setValueSensorIndex2",   2),  # podłogówka
    "setIndexBtn3":   ("setValueSensorIndex3",   2),  # FIXME: duplicate slot — legacy, kept for compatibility
    "setIndexBtn3_1": ("setValueSensorIndex3_1", 3),  # pump inlet
}


@router.get("/temp_sensor_config", response_class=HTMLResponse)
async def temp_sensor_config(request: Request):
    """
    Render the sensor assignment page.

    Shows all detected sensors with their current readings and allows
    the user to re-assign which physical sensor index corresponds to each role.
    """
    state = request.app.state.pump_state
    snap  = state.snapshot()
    msg   = request.query_params.get("msg", "")
    level = request.query_params.get("level", "success")
    return templates.TemplateResponse("temp_sensor_config.html", {
        "request":         request,
        "sensFoundNumber": snap["temp_sens_found_number"],
        "sensFoundList":   snap["read_temp"],
        "sensorIndexList": snap["sensor_index_list"],
        "pickedLang":      snap["picked_lang"],
        "lang":            snap["language"],
        "msg": msg, "level": level,
    })


@router.post("/temp_sensor_config")
async def temp_sensor_config_post(request: Request):
    """
    Save a new sensor index assignment.

    Only one button is submitted per POST (each row has its own Save button).
    Invalid index values redirect back with an error toast.
    """
    state  = request.app.state.pump_state
    config = request.app.state.config
    form   = await request.form()
    msg    = ""

    sil = list(state.sensor_index_list)
    for btn, (field, idx) in _BTN_MAP.items():
        if form.get(btn) == "Save":
            try:
                sil[idx] = int(form[field])
                msg = f"Zapisano indeks czujnika [{idx}]"
            except (ValueError, KeyError) as e:
                return RedirectResponse(
                    f"/temp_sensor_config?msg=Błąd:+{e}&level=danger",
                    status_code=303
                )

    if msg:
        state.update(sensor_index_list=sil)
        config.save_from(state)

    return RedirectResponse(
        f"/temp_sensor_config?msg={msg or 'Brak+zmian'}&level=success",
        status_code=303
    )
