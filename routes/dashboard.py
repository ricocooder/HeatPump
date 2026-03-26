"""
Main dashboard route — GET / and POST /result.

The dashboard renders the live system overview (new_index.html) with the SVG
system diagram and status panel. Data is also streamed in real-time via SSE
(see routes/stream.py), so the page load only needs to display initial values.

POST /result handles all control actions from the dashboard form:
  - Auto/manual mode toggle
  - Season (Lato/Zima) toggle
  - Individual GPIO pin toggles (manual mode)
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

log = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _render(request: Request, state, msg: str = "", level: str = "success"):
    """
    Build the template context and render new_index.html.

    Args:
        request: FastAPI request object (required by Jinja2Templates).
        state:   AppState instance.
        msg:     Optional toast notification message.
        level:   Bootstrap alert level ('success', 'danger', etc.).

    Returns:
        TemplateResponse for new_index.html.
    """
    snap = state.snapshot()
    return templates.TemplateResponse("new_index.html", {
        "request":       request,
        "pump_i":        snap["pump_i"],
        "pump_v":        snap["pump_v"],
        "pump_p":        round(snap["pump_p"], 2),
        "pump":          snap["base_efi_percent"],
        "sensFoundList": snap["read_temp"],
        "sensorIndexList": snap["sensor_index_list"],
        "discriptionList": snap["descriptions"],
        "heat_object":   snap["heat_object"],
        "setTempList":   snap["set_temp"],
        "sezon":         snap["sezon"],
        "pumpMode":      snap["pump_mode"],
        "pins":          snap["pins"],
        "pinsDisc":      snap["pins_desc"],
        "pinsLogic":     snap["pins_logic"],
        "tempPins":      snap["temp_pins"],
        "pickedLang":    snap["picked_lang"],
        "lang":          snap["language"],
        "msg": msg, "level": level,
    })


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Render the main dashboard page with current system state.

    Flash messages are passed via query parameters (msg, level) so they
    survive the POST → redirect → GET cycle without server-side sessions.
    """
    state = request.app.state.pump_state
    msg   = request.query_params.get("msg", "")
    level = request.query_params.get("level", "success")
    return _render(request, state, msg, level)


@router.post("/result")
async def result(request: Request):
    """
    Handle control form submissions from the dashboard.

    All actions redirect back to GET / with a toast message. Using
    303 See Other ensures the browser re-GETs the page instead of
    re-POSTing on refresh.
    """
    state  = request.app.state.pump_state
    config = request.app.state.config
    form   = await request.form()
    msg    = ""

    # --- Auto/manual mode toggle ---
    if form.get("Switch_mode"):
        if state.pump_mode == "manual":
            state.update(pump_mode="auto", heat_object=2)
            msg = "Tryb Auto"
        else:
            state.update(pump_mode="manual", heat_object=0)
            msg = "Tryb ręczny"

    if form.get("Turn ON Pump"):
        state.update(pump_mode="auto", heat_object=2)
        msg = "Tryb automatyczny"

    # --- Season toggle (persisted to config.json immediately) ---
    if form.get("sezonSwitch"):
        new_sezon = "Zima" if state.sezon == "Lato" else "Lato"
        state.update(sezon=new_sezon)
        config.save_from(state)
        msg = f"Zmieniono sezon na {new_sezon}"

    # --- Individual GPIO pin toggles (manual mode) ---
    pin_names = [
        "Sterowanie pompy1 (NC)", "Sterowanie pompy2 (NC)",
        "Sterowanie pompy3 (NC)", "Zawor trojdrogowy (NO)",
        "Sterownik piec (NC)",    "Zal/Wyl 24V (NC)",
        "Pompa obiegowa (NC)",    "Spare",
    ]
    for i in range(8):
        if form.get(str(i)):
            pins = list(state.temp_pins)
            pins[i] = 0 if pins[i] == 1 else 1
            state.update(temp_pins=pins)
            # Toggling pin 7 (Spare) also forces manual mode to prevent
            # the auto scheduler from immediately overwriting the pin state
            if i == 7:
                state.update(pump_mode="manual", heat_object=0)
                msg = f"Przełączono pin {i}: {pin_names[i]} — tryb ręczny"
            else:
                msg = f"Przełączono pin {i}: {pin_names[i]}"

    return RedirectResponse(
        f"/?msg={msg}&level=success" if msg else "/",
        status_code=303
    )
