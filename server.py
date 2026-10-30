"""
ApplyCopilot (Wormhole) Full-Stack Real-Time Agentic Web Server
Features:
- Live CDP Screencast WebSocket Stream
- Interactive User Cursor Click Forwarding
- Instant Human-in-the-Loop Interrupt Gate
- Protocol Engines: Transit Rush, Document Exorcist, Anti-Dark-Pattern
- Real Website Autonomous Navigation
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from groq import Groq

# Core Engine Imports
from agent_core import agent_core
from exorcist import heal_image
from dark_pattern import run_demo as run_dark_pattern_demo
from transit_rush import run_transit_rush

app = FastAPI(title="Wormhole Real-Time Agent Server")

BASE_DIR = Path(__file__).resolve().parent

# ==============================================================================
# LIFECYCLE EVENTS
# ==============================================================================
@app.on_event("startup")
async def startup_event():
    print("[SERVER STARTUP] Initializing real-time browser agent...")
    asyncio.create_task(agent_core.initialize())

# ==============================================================================
# WEBSOCKET: LIVE SCREENCAST & BIDIRECTIONAL CONTROL
# ==============================================================================
@app.websocket("/ws/screencast")
async def websocket_screencast(websocket: WebSocket):
    await websocket.accept()
    agent_core.active_websockets.add(websocket)
    print(f"[WS CONNECTED] Client joined screencast stream. Active viewers: {len(agent_core.active_websockets)}")
    
    # Send immediate initial frame snapshot if available
    try:
        init_frame = await agent_core.get_current_frame_base64()
        if init_frame:
            await websocket.send_text(json.dumps({
                "type": "FRAME",
                "data": init_frame,
                "state": agent_core.state,
                "url": agent_core.page.url if agent_core.page else ""
            }))
    except Exception as e:
        print(f"[!] Initial frame error: {e}")

    try:
        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            msg_type = data.get("type")

            # 1. User Click Inside Live Viewport
            if msg_type == "CANVAS_CLICK":
                x_ratio = data.get("x", 0.5)
                y_ratio = data.get("y", 0.5)
                await agent_core.handle_user_canvas_click(x_ratio, y_ratio)

            # 1b. User Keypress Forwarding (for Login / OTP / CAPTCHA)
            elif msg_type == "CANVAS_KEY":
                key = data.get("key", "")
                text = data.get("text", "")
                await agent_core.handle_user_canvas_key(key, text)

            # 2. User Resolved the Interrupt Modal
            elif msg_type == "RESOLVE_INTERRUPT":
                action = data.get("action", "RESUME")
                new_prompt = data.get("new_prompt")
                await agent_core.resolve_interrupt(action, new_prompt)

            # 3. User Finished Manual Handover (Login / CAPTCHA done)
            elif msg_type == "MANUAL_HANDOVER_DONE":
                await agent_core.resume_from_manual_handover()

    except WebSocketDisconnect:
        agent_core.active_websockets.remove(websocket)
        print(f"[WS DISCONNECTED] Client left screencast. Remaining: {len(agent_core.active_websockets)}")

# ==============================================================================
# STATIC & MOCK ROUTES
# ==============================================================================
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = BASE_DIR / "static" / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

@app.get("/mock/ksrtc", response_class=HTMLResponse)
async def serve_ksrtc_mock():
    mock_file = BASE_DIR / "mock_ksrtc.html"
    return HTMLResponse(content=mock_file.read_text(encoding="utf-8"))

@app.get("/mock/checkout", response_class=HTMLResponse)
async def serve_checkout_mock():
    mock_file = BASE_DIR / "mock_checkout.html"
    return HTMLResponse(content=mock_file.read_text(encoding="utf-8"))

@app.get("/proof/{filename}")
async def serve_proof_image(filename: str):
    file_path = BASE_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    return JSONResponse({"error": "Proof not found"}, status_code=404)

# ==============================================================================
# AGENTIC EXECUTION API
# ==============================================================================
@app.post("/api/execute")
async def execute_agent_command(req: Request):
    data = await req.json()
    prompt = data.get("prompt", "").strip()
    
    if not prompt:
        return JSONResponse({"error": "Empty prompt"}, status_code=400)
    
    t_start = time.time()
    print(f"\n[AGENT SERVER] Received User Command: \"{prompt}\"")

    # Detect if user is asking to navigate to a real website
    if any(site in prompt.lower() for site in ["http://", "https://", ".com", ".org", ".in", "google", "wikipedia", "hackernews"]):
        print(f"[AGENT SERVER] Real Website Navigation Request Detected!")
        # Trigger real browser autonomous loop
        await agent_core.start_autonomous_task(prompt)
        return {
            "status": "RUNNING",
            "protocol": "LIVE_WEB_NAVIGATION",
            "reason": f"Autonomous trajectory initiated on real browser for: {prompt}",
            "live_stream": True,
            "duration_ms": round((time.time() - t_start) * 1000, 1)
        }

    # Otherwise route to specialized offline/fast protocols
    if "photo" in prompt.lower() or "gate" in prompt.lower() or "kb" in prompt.lower():
        input_test_file = BASE_DIR / "test_oversized_photo.jpg"
        output_file = BASE_DIR / "test_healed_passport_photo.jpg"
        telemetry = await asyncio.to_thread(heal_image, str(input_test_file), str(output_file), 20, 48)
        return {
            "status": "COMPLETED",
            "protocol": "DOC_EXORCIST",
            "reason": "Document Exorcist healed upload to compliant 32KB.",
            "details": telemetry,
            "proof_image": "/proof/test_healed_passport_photo.jpg",
            "payment_gate_active": False,
            "duration_ms": round((time.time() - t_start) * 1000, 1)
        }

    elif "insurance" in prompt.lower() or "fee" in prompt.lower() or "clean" in prompt.lower():
        telemetry = await asyncio.to_thread(run_dark_pattern_demo, "mock_checkout.html", True)
        return {
            "status": "COMPLETED",
            "protocol": "ANTI_DARK_PATTERN",
            "reason": "Anti-Dark-Pattern engine stripped 3 deceptive fees.",
            "details": telemetry,
            "proof_image": "/proof/cleaned_checkout_proof.png",
            "payment_gate_active": True,
            "duration_ms": round((time.time() - t_start) * 1000, 1)
        }

    else:
        # Default to Transit Rush or Real Browser
        await agent_core.start_autonomous_task(prompt)
        return {
            "status": "RUNNING",
            "protocol": "TRANSIT_RUSH",
            "reason": f"Autonomous agent executing goal: {prompt}",
            "live_stream": True,
            "duration_ms": round((time.time() - t_start) * 1000, 1)
        }

@app.post("/api/interrupt/resolve")
async def resolve_interrupt_endpoint(req: Request):
    data = await req.json()
    action = data.get("action", "RESUME")
    new_prompt = data.get("new_prompt")
    await agent_core.resolve_interrupt(action, new_prompt)
    return {"status": "RESOLVED", "action": action}

# ==============================================================================
# SERVER ENTRYPOINT
# ==============================================================================
if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 65)
    print("  \U0001F300 WORMHOLE / APPLYCOPILOT REAL-TIME AGENT SERVER")
    print("  * Local Web Cockpit: http://localhost:8000")
    print("  * Live WebSocket Stream: ws://localhost:8000/ws/screencast")
    print("=" * 65 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
