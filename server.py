"""
Wormhole (ApplyCopilot) Full-Stack Real-Time Agentic Web Server
Features:
- Live CDP Screencast WebSocket Stream with Wheel Scrolling & Precision Coordinates
- Multimodal File & PDF Upload with In-Memory Text Extraction (pypdfium2)
- Direct Emergency Abort (/api/abort)
- Real-Time Interactive Canvas with Seamless Human Takeover
- DOM-Aware Autonomous Agent Navigation & Form Filling
"""

import os
import sys
import json
import time
import base64
import asyncio
from pathlib import Path
from dotenv import load_dotenv

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

import pypdfium2 as pdfium
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

# Core Engine Imports
from agent_core import agent_core
from exorcist import heal_image
from dark_pattern import run_demo as run_dark_pattern_demo
from transit_rush import run_transit_rush

app = FastAPI(title="Wormhole Real-Time Agent Server")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

def extract_file_text(file_path: Path) -> str:
    """Extracts plain text from uploaded PDF or document files."""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        try:
            pdf = pdfium.PdfDocument(str(file_path))
            text_parts = []
            for page in pdf:
                tp = page.get_textpage()
                if tp:
                    text_parts.append(tp.get_text_range())
            return "\n".join(text_parts).strip()
        except Exception as e:
            print(f"[!] PDF extraction error on {file_path.name}: {e}")
            return ""
    elif suffix in [".txt", ".json", ".csv", ".md", ".py", ".html"]:
        try:
            return file_path.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception as e:
            return ""
    return ""

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

            # 2. User Wheel Scroll
            elif msg_type == "CANVAS_WHEEL":
                x_ratio = data.get("x", 0.5)
                y_ratio = data.get("y", 0.5)
                delta_x = data.get("deltaX", 0)
                delta_y = data.get("deltaY", 0)
                await agent_core.handle_user_canvas_wheel(x_ratio, y_ratio, delta_x, delta_y)

            # 3. User Keypress Forwarding (for Login / OTP / CAPTCHA / Forms)
            elif msg_type == "CANVAS_KEY":
                key = data.get("key", "")
                text = data.get("text", "")
                await agent_core.handle_user_canvas_key(key, text)

            # 4. Emergency Abort Agent
            elif msg_type == "ABORT_TASK":
                await agent_core.abort_current_task()

            # 5. User Resolved the Interrupt Modal
            elif msg_type == "RESOLVE_INTERRUPT":
                action = data.get("action", "RESUME")
                new_prompt = data.get("new_prompt")
                await agent_core.resolve_interrupt(action, new_prompt)

            # 6. User Finished Manual Handover (Login / CAPTCHA done)
            elif msg_type == "MANUAL_HANDOVER_DONE":
                await agent_core.resume_from_manual_handover()

    except WebSocketDisconnect:
        agent_core.active_websockets.discard(websocket)
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

@app.get("/uploads/{filename}")
async def serve_uploaded_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    return JSONResponse({"error": "Uploaded file not found"}, status_code=404)

# ==============================================================================
# FILE UPLOAD API WITH IN-MEMORY TEXT EXTRACTION
# ==============================================================================
@app.post("/api/upload")
async def handle_file_upload(req: Request):
    try:
        data = await req.json()
        files = data.get("files", [])
        saved_files = []
        for item in files:
            name = item.get("name", f"upload_{int(time.time())}.dat")
            raw_b64 = item.get("data", "")
            if "," in raw_b64:
                raw_b64 = raw_b64.split(",", 1)[1]
            raw_bytes = base64.b64decode(raw_b64)
            safe_name = name.replace(" ", "_")
            file_dest = UPLOAD_DIR / safe_name
            file_dest.write_bytes(raw_bytes)
            
            # Extract plain text if PDF or document
            extracted = extract_file_text(file_dest)

            file_info = {
                "name": name,
                "size": len(raw_bytes),
                "path": str(file_dest),
                "url": f"/uploads/{safe_name}",
                "extracted_text": extracted
            }
            saved_files.append(file_info)
            agent_core.session_files.append(file_info)
            if extracted:
                agent_core.session_context += f"\n--- RESUME / ATTACHED FILE CONTENT ({name}) ---\n{extracted}\n"
            print(f"[FILE UPLOAD] Saved '{name}' ({len(raw_bytes)} bytes, {len(extracted)} text chars) -> {file_dest}")
        return JSONResponse({"status": "SUCCESS", "files": saved_files})
    except Exception as e:
        print(f"[!] Upload error: {e}")
        return JSONResponse({"status": "ERROR", "message": str(e)}, status_code=500)

# ==============================================================================
# NEW CHAT SESSION RESET ENDPOINT
# ==============================================================================
@app.post("/api/chat/new")
async def create_new_chat():
    print("\n[SESSION] New Chat created by user. Resetting session memory and files...")
    agent_core.reset_session()
    return JSONResponse({"status": "SUCCESS", "message": "New chat initialized."})

# ==============================================================================
# EMERGENCY ABORT ENDPOINT
# ==============================================================================
@app.post("/api/abort")
async def abort_current_task_endpoint():
    print("\n[AGENT SERVER] Received Emergency Stop Command from User.")
    await agent_core.abort_current_task()
    return JSONResponse({"status": "ABORTED", "message": "Autonomous agent halted immediately."})

# ==============================================================================
# EMBEDDED BROWSER ADDRESS BAR NAVIGATION
# ==============================================================================
@app.post("/api/navigate")
async def direct_navigate(req: Request):
    data = await req.json()
    url = data.get("url", "").strip()
    if not url:
        return JSONResponse({"error": "URL required"}, status_code=400)
    
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    
    await agent_core.direct_goto(url)
    return JSONResponse({"status": "NAVIGATING", "url": url})

# ==============================================================================
# AGENTIC EXECUTION API
# ==============================================================================
@app.post("/api/execute")
async def execute_agent_command(req: Request):
    data = await req.json()
    prompt = data.get("prompt", "").strip()
    attached_files = data.get("files", [])
    
    if not prompt:
        return JSONResponse({"error": "Empty prompt"}, status_code=400)
    
    t_start = time.time()
    print(f"\n[AGENT SERVER] Received User Command: \"{prompt}\" (Attached Files: {len(attached_files)})")

    # 1. Compile User Profile & Attached Documents Context across turns
    for af in attached_files:
        txt = af.get("extracted_text", "")
        name = af.get("name", "document")
        if txt and txt not in agent_core.session_context:
            agent_core.session_context += f"\n--- RESUME / ATTACHED FILE CONTENT ({name}) ---\n{txt}\n"

    # Ingest candidate credentials from vault.json as default knowledge
    context_data = agent_core.session_context
    vault_file = BASE_DIR / "vault.json"
    if vault_file.exists():
        try:
            v_data = json.loads(vault_file.read_text(encoding="utf-8"))
            cand = v_data.get("candidate_profile", {})
            context_data += (
                f"\n--- SENDER CANDIDATE CREDENTIALS (FROM VAULT) ---\n"
                f"Full Name: {cand.get('name', 'Yashwanth K R')}\n"
                f"Email Address: {cand.get('email', 'yash2006kr@gmail.com')}\n"
                f"Phone: {cand.get('phone', '+91 98765 43210')}\n"
                f"Degree: {cand.get('education', {}).get('degree', 'B.E. Computer Science')}\n"
                f"College: {cand.get('education', {}).get('college', 'Don Bosco Institute of Technology')}\n"
                f"Skills: Backend Systems, Java, AI Agents, Python\n"
            )
        except Exception:
            pass

    # Store in agent core
    agent_core.attached_files = attached_files or agent_core.session_files
    agent_core.current_context = context_data

    # 2. Check if real website navigation / interaction / Q&A is requested
    if any(site in prompt.lower() for site in ["http://", "https://", ".com", ".org", ".in", ".app", "google", "wikipedia", "hackernews", "yash2006kr", "vercel", "portfolio", "about", "fetch", "who is", "what is", "tell me"]):
        print(f"[AGENT SERVER] Real Website Interaction & Q&A Task Detected!")
        await agent_core.start_autonomous_task(prompt, context=context_data)
        return {
            "status": "RUNNING",
            "protocol": "LIVE_WEB_NAVIGATION",
            "reason": f"Autonomous trajectory initiated on real browser for: {prompt}",
            "live_stream": True,
            "duration_ms": round((time.time() - t_start) * 1000, 1)
        }

    # 3. Protocol 04: Document Exorcist (Auto-heal photos)
    if "photo" in prompt.lower() or "gate" in prompt.lower() or "kb" in prompt.lower() or "image" in prompt.lower():
        input_test_file = BASE_DIR / "test_oversized_photo.jpg"
        if attached_files and Path(attached_files[0].get("path", "")).exists():
            input_test_file = Path(attached_files[0]["path"])
            print(f"[DOC EXORCIST] Healing user uploaded photo: {input_test_file}")

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

    # 4. Protocol 05: Anti-Dark-Pattern Fee Stripper
    elif "insurance" in prompt.lower() or "fee" in prompt.lower() or "clean" in prompt.lower() or "dark" in prompt.lower():
        telemetry = await asyncio.to_thread(run_dark_pattern_demo, "mock_checkout.html", True)
        return {
            "status": "COMPLETED",
            "protocol": "ANTI_DARK_PATTERN",
            "reason": "Anti-Dark-Pattern engine stripped deceptive fees.",
            "details": telemetry,
            "proof_image": "/proof/cleaned_checkout_proof.png",
            "payment_gate_active": True,
            "duration_ms": round((time.time() - t_start) * 1000, 1)
        }

    # 5. Protocol 01: Transit Rush KSRTC Reservation
    elif "ksrtc" in prompt.lower() or "bus" in prompt.lower() or "transit" in prompt.lower() or "sleeper" in prompt.lower():
        telemetry = await asyncio.to_thread(run_transit_rush, "mock_ksrtc.html", True)
        return {
            "status": "COMPLETED",
            "protocol": "TRANSIT_RUSH",
            "reason": "Transit Rush reserved berths 14A/14B and stripped dark-pattern fees.",
            "details": telemetry,
            "proof_image": "/proof/transit_rush_proof.png",
            "payment_gate_active": True,
            "duration_ms": round((time.time() - t_start) * 1000, 1)
        }

    # Default fallback: Execute as general browser goal
    await agent_core.start_autonomous_task(prompt, context=context_data)
    return {
        "status": "RUNNING",
        "protocol": "AUTONOMOUS_EXECUTION",
        "reason": f"Agent dispatched on goal: {prompt}",
        "live_stream": True,
        "duration_ms": round((time.time() - t_start) * 1000, 1)
    }

if __name__ == "__main__":
    import uvicorn
    print("\n=================================================================")
    print("  🌀 WORMHOLE / APPLYCOPILOT REAL-TIME AGENT SERVER")
    print("  * Local Web Cockpit: http://localhost:8000")
    print("  * Live WebSocket Stream: ws://localhost:8000/ws/screencast")
    print("=================================================================\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
