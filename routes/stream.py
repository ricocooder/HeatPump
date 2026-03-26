"""
Server-Sent Events (SSE) endpoint — GET /stream.

Pushes live system state to the browser dashboard every 4 seconds without
polling or page refresh. The browser's EventSource API reconnects automatically
if the connection drops.

SSE format: each event is a single ``data: <json>\n\n`` frame.

Headers:
  - Cache-Control: no-cache — prevents proxy/CDN from buffering events
  - X-Accel-Buffering: no — disables Nginx proxy_buffering for this response
                            (required when running behind a reverse proxy)
  - Connection: keep-alive — keeps the TCP connection open between events
"""

import asyncio
import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

log = logging.getLogger(__name__)
router = APIRouter()


async def _event_generator(request: Request, state):
    """
    Async generator that yields SSE-formatted events until the client disconnects.

    Checks for disconnection before each event to avoid accumulating stale
    generators when users close the browser tab. The 4-second sleep matches
    the ``_job_4s`` scheduler interval so the dashboard stays in sync.

    Args:
        request: FastAPI request — used to detect client disconnection.
        state:   AppState instance — snapshot taken fresh each cycle.

    Yields:
        str: SSE data frame in the form ``data: <json_payload>\n\n``.
    """
    while True:
        if await request.is_disconnected():
            break
        snap = state.snapshot()
        payload = {
            "temps":        snap["read_temp"],
            "heat_object":  snap["heat_object"],
            "pump_efi":     snap["base_efi_percent"],
            "pump_i":       snap["pump_i"],
            "pump_v":       snap["pump_v"],
            "pump_p":       snap["pump_p"],
            "temp_pins":    snap["temp_pins"],
            "sezon":        snap["sezon"],
            "pump_mode":    snap["pump_mode"],
            "descriptions": snap["descriptions"],
            "set_temp":     snap["set_temp"],
            "picked_lang":  snap["picked_lang"],
        }
        yield f"data: {json.dumps(payload)}\n\n"
        await asyncio.sleep(4)


@router.get("/stream")
async def stream(request: Request):
    """
    Open an SSE stream for the live dashboard.

    Returns a streaming response that stays open indefinitely.
    The browser's EventSource automatically reconnects on network errors.
    """
    state = request.app.state.pump_state
    return StreamingResponse(
        _event_generator(request, state),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # critical for Nginx reverse proxy
            "Connection": "keep-alive",
        },
    )
