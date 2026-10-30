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
import random
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
from fastapi.staticfiles import StaticFiles

# Core Engine Imports
from agent_core import agent_core
from exorcist import heal_image
from dark_pattern import run_demo as run_dark_pattern_demo
from transit_rush import run_transit_rush
from sentinel import fraud_sentinel, run_demo as run_sentinel_demo
from sos_sentinel import is_emergency_prompt, sos_engine
from api_pool import api_pool

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
    
    # Send immediate initial frame snapshot and tabs state if available
    try:
        init_frame = await agent_core.get_current_frame_base64()
        if init_frame:
            await websocket.send_text(json.dumps({
                "type": "FRAME",
                "data": init_frame,
                "state": agent_core.state,
                "url": agent_core.page.url if agent_core.page else ""
            }))
        
        # Broadcast initial open tabs
        tabs = await agent_core.get_tabs_info()
        curr_idx = next((t["index"] for t in tabs if t["active"]), 0)
        await websocket.send_text(json.dumps({
            "type": "TABS_UPDATE",
            "tabs": tabs,
            "active_index": curr_idx,
            "url": agent_core.page.url if agent_core.page else ""
        }))
    except Exception as e:
        print(f"[!] Initial frame/tabs error: {e}")

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

            # 7. Multi-Tab Operations
            elif msg_type == "TAB_OPEN":
                url = data.get("url", "about:blank")
                await agent_core.open_new_tab(url)

            elif msg_type == "TAB_SWITCH":
                target = data.get("index", data.get("target", 0))
                await agent_core.switch_to_tab(target)

            elif msg_type == "TAB_CLOSE":
                target = data.get("index", data.get("target"))
                await agent_core.close_tab(target)

    except WebSocketDisconnect:
        agent_core.active_websockets.discard(websocket)
        print(f"[WS DISCONNECTED] Client left screencast. Remaining: {len(agent_core.active_websockets)}")

# ==============================================================================
# STATIC & MOCK ROUTES
# ==============================================================================
# Mount Vite built frontend assets if present
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="dist_assets")
    if (FRONTEND_DIST / "draco").exists():
        app.mount("/draco", StaticFiles(directory=str(FRONTEND_DIST / "draco")), name="dist_draco")
    if (FRONTEND_DIST / "models").exists():
        app.mount("/models", StaticFiles(directory=str(FRONTEND_DIST / "models")), name="dist_models")
    if (FRONTEND_DIST / "images").exists():
        app.mount("/images", StaticFiles(directory=str(FRONTEND_DIST / "images")), name="dist_images")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    dist_index = BASE_DIR / "frontend" / "dist" / "index.html"
    if dist_index.exists():
        return HTMLResponse(content=dist_index.read_text(encoding="utf-8"))
    index_file = BASE_DIR / "static" / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

@app.get("/classic", response_class=HTMLResponse)
async def serve_classic_index():
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

# In-memory mock mail & OTP state
latest_mock_email = {
    "sender": "QuickHire Security System",
    "email_from": "security@quickhire.io",
    "subject": "Your Security Verification Code: 849201",
    "otp": "849201",
    "time": "Just now",
    "body": "Hello Yashwanth, your single-use verification code for QuickHire Portal is provided below."
}

@app.get("/mock/emergency", response_class=HTMLResponse)
async def serve_emergency_mock():
    mock_file = BASE_DIR / "mock_emergency.html"
    return HTMLResponse(content=mock_file.read_text(encoding="utf-8"))

@app.get("/api/api-pool-status")
async def get_api_pool_status():
    return JSONResponse(api_pool.get_telemetry())

@app.post("/api/api-pool/add-key")
async def add_api_pool_key(req: Request):
    data = await req.json()
    key = data.get("key", "").strip()
    if not key:
        return JSONResponse({"status": "ERROR", "message": "No key provided"}, status_code=400)
    added = api_pool.add_key(key)
    return JSONResponse({
        "status": "SUCCESS" if added else "ALREADY_EXISTS",
        "telemetry": api_pool.get_telemetry()
    })

@app.get("/mock/portal", response_class=HTMLResponse)
async def serve_portal_mock():
    mock_file = BASE_DIR / "mock_portal.html"
    return HTMLResponse(content=mock_file.read_text(encoding="utf-8"))

@app.get("/mock/mail", response_class=HTMLResponse)
async def serve_mail_mock():
    mock_file = BASE_DIR / "mock_mail.html"
    return HTMLResponse(content=mock_file.read_text(encoding="utf-8"))

@app.post("/api/mock/send_otp")
async def mock_send_otp(req: Request):
    global latest_mock_email
    try:
        data = await req.json()
    except Exception:
        data = {}
    email = data.get("email", "yashwanth.kr.dbit@gmail.com")
    new_otp = str(random.randint(100000, 999999))
    latest_mock_email = {
        "sender": "QuickHire Security System",
        "email_from": "security@quickhire.io",
        "subject": f"Your Security Verification Code: {new_otp}",
        "otp": new_otp,
        "time": "Just now",
        "body": f"Hello {email}, your single-use verification code for QuickHire Portal is {new_otp}. Valid for 10 minutes."
    }
    print(f"[MOCK AUTH] Generated new OTP {new_otp} for {email}")
    return JSONResponse({"status": "SENT", "email": email, "otp": new_otp})

@app.get("/api/mock/latest_mail")
async def mock_get_latest_mail():
    return JSONResponse({"status": "SUCCESS", "email": latest_mock_email})

@app.post("/api/mock/verify_otp")
async def mock_verify_otp(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    entered_otp = str(data.get("otp", "")).strip()
    expected_otp = str(latest_mock_email.get("otp", "")).strip()
    if entered_otp and entered_otp == expected_otp:
        print(f"[MOCK AUTH] Successfully verified OTP: {entered_otp}")
        return JSONResponse({"status": "VALID", "message": "Authenticated successfully"})
    else:
        print(f"[MOCK AUTH] Failed verification: entered '{entered_otp}', expected '{expected_otp}'")
        return JSONResponse({"status": "INVALID", "message": "Code mismatch"}, status_code=400)

# ==============================================================================
# HACKATHON SURPRISE HURDLE: CRASH-AFTER-SUBMIT & ORDER RECONCILIATION MOCK API
# ==============================================================================
mock_orders_db = {
    "ORD-9921": {
        "order_id": "ORD-9921",
        "route": "BLR -> DEL (Airavat Express)",
        "amount": 4650.0,
        "currency": "INR",
        "status": "PENDING",
        "paid_at": None,
        "receipt_number": None
    }
}

@app.post("/api/mock/process_payment")
async def mock_process_payment(req: Request):
    global mock_orders_db
    try:
        data = await req.json()
    except Exception:
        data = {}
    order_id = data.get("order_id", "ORD-9921")
    amount = float(data.get("amount", 4650.0))
    simulate_crash = bool(data.get("simulate_crash", False))

    receipt_no = f"REC-{random.randint(100000, 999999)}"
    mock_orders_db[order_id] = {
        "order_id": order_id,
        "route": "BLR -> DEL (Airavat Express)",
        "amount": amount,
        "currency": "INR",
        "status": "PAID",
        "paid_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "receipt_number": receipt_no
    }
    print(f"[MOCK PAYMENT] Order {order_id} processed: PAID ₹{amount:,.0f} (Receipt: {receipt_no}). Crash simulated: {simulate_crash}")
    return JSONResponse({
        "status": "SETTLED",
        "order_id": order_id,
        "receipt_number": receipt_no,
        "amount": amount,
        "crash_simulated": simulate_crash
    })

@app.get("/api/mock/order_status")
async def mock_get_order_status(order_id: str = "ORD-9921"):
    order = mock_orders_db.get(order_id)
    if order:
        return JSONResponse({"status": "FOUND", "order": order})
    return JSONResponse({"status": "NOT_FOUND", "message": f"Order {order_id} not found"}, status_code=404)

@app.get("/mock/orders", response_class=HTMLResponse)
async def serve_mock_orders():
    order = mock_orders_db.get("ORD-9921", {})
    status_color = "#4ade80" if order.get("status") == "PAID" else "#fb923c"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>AirTravel Express - Order Ledger & Reconciliation</title>
      <style>
        body {{ background: #0b0e1b; color: #fff; font-family: -apple-system, sans-serif; padding: 40px; }}
        .card {{ background: #13172c; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; max-width: 580px; margin: 0 auto; padding: 28px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }}
        .badge {{ background: {status_color}; color: #000; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px; }}
        .row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 14px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <h2 style="margin-top:0; color:#79e8f3;">Order Status & Reconciliation Ledger</h2>
        <div class="row"><span>Order Reference</span><strong>{order.get('order_id', 'ORD-9921')}</strong></div>
        <div class="row"><span>Status</span><span class="badge">{order.get('status', 'PENDING')}</span></div>
        <div class="row"><span>Route</span><span>{order.get('route', 'BLR -> DEL')}</span></div>
        <div class="row"><span>Amount Captured</span><strong>₹{order.get('amount', 4650.0):,.0f}</strong></div>
        <div class="row"><span>Payment Timestamp</span><span>{order.get('paid_at', 'Pending')}</span></div>
        <div class="row"><span>Bank Receipt No.</span><strong>{order.get('receipt_number', 'None')}</strong></div>
        <p style="font-size: 12px; color: #8b92b2; margin-top: 20px; line-height: 1.4;">
          🛡️ <strong>Idempotency Sentinel:</strong> In case of abrupt browser/client crashes, the agent queries this ledger before re-executing any payment to ensure zero duplicate charges.
        </p>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/download/test-guide")
async def download_test_guide_pdf():
    pdf_path = BASE_DIR / "ApplyCopilot_Test_Prompts_Guide.pdf"
    if pdf_path.exists():
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=ApplyCopilot_Test_Prompts_Guide.pdf"}
        )
    return JSONResponse({"error": "Test Guide PDF not found"}, status_code=404)

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
    print("\n[SESSION] New Chat created by user. Resetting session memory, files, and clearing browser...")
    await agent_core.reset_session()
    return JSONResponse({"status": "SUCCESS", "message": "New chat initialized and browser cleared to null."})

# ==============================================================================
# EMERGENCY ABORT ENDPOINT
# ==============================================================================
@app.post("/api/abort")
async def abort_current_task_endpoint():
    print("\n[AGENT SERVER] Received Emergency Stop Command from User.")
    await agent_core.abort_current_task()
    return JSONResponse({
        "status": "PAUSED_FOR_HUMAN",
        "message": "Autonomous agent halted immediately by user command.",
        "telemetry": {
            "action": "EMERGENCY_STOP",
            "state": "PAUSED_FOR_HUMAN",
            "timestamp": time.strftime("%H:%M:%S"),
            "reason": "Execution cancelled by operator."
        }
    })

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
# BROWSER MULTI-TAB CONTROLS
# ==============================================================================
@app.get("/api/tabs")
async def get_browser_tabs():
    tabs = await agent_core.get_tabs_info()
    curr_idx = next((t["index"] for t in tabs if t["active"]), 0)
    return JSONResponse({"status": "SUCCESS", "tabs": tabs, "active_index": curr_idx})

@app.post("/api/tabs/open")
async def open_browser_tab(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    url = data.get("url", "about:blank")
    await agent_core.open_new_tab(url)
    tabs = await agent_core.get_tabs_info()
    curr_idx = next((t["index"] for t in tabs if t["active"]), 0)
    return JSONResponse({"status": "SUCCESS", "tabs": tabs, "active_index": curr_idx})

@app.post("/api/tabs/switch")
async def switch_browser_tab(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    target = data.get("index", data.get("target", 0))
    await agent_core.switch_to_tab(target)
    tabs = await agent_core.get_tabs_info()
    curr_idx = next((t["index"] for t in tabs if t["active"]), 0)
    return JSONResponse({"status": "SUCCESS", "tabs": tabs, "active_index": curr_idx})

@app.post("/api/tabs/close")
async def close_browser_tab(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    target = data.get("index", data.get("target"))
    await agent_core.close_tab(target)
    tabs = await agent_core.get_tabs_info()
    curr_idx = next((t["index"] for t in tabs if t["active"]), 0)
    return JSONResponse({"status": "SUCCESS", "tabs": tabs, "active_index": curr_idx})

# ==============================================================================
# AGENTIC EXECUTION API
# ==============================================================================
@app.post("/api/execute")
async def execute_agent_command(req: Request):
    t_start = time.time()
    try:
        data = await req.json()
        prompt = data.get("prompt", "").strip()
        attached_files = data.get("files", [])
        
        if not prompt:
            return JSONResponse({"error": "Empty prompt"}, status_code=400)
        
        print(f"\n[AGENT SERVER] Received User Command: \"{prompt}\" (Attached Files: {len(attached_files)})")

        # 0. Protocol 08: Autonomous Medical Emergency & SOS Dispatch Sentinel
        if is_emergency_prompt(prompt):
            print(f"[SOS PROTOCOL ENGAGED] Acute Emergency Distress Signal Detected: {prompt}")
            telemetry = sos_engine.execute_sos_protocol(prompt)
            asyncio.create_task(agent_core.direct_goto("http://localhost:8000/mock/emergency"))
            amb = telemetry.get("ambulance_dispatch", {})
            hosp = telemetry.get("hospital_booking", {})
            kin = telemetry.get("kin_notification", {})
            emergency_msg = (
                f"{telemetry.get('clinical_guidance', '')}\n\n"
                f"🚨 **AUTONOMOUS EMERGENCY DISPATCH COMPLETED**:\n"
                f"• **Ambulance Dispatched**: `{amb.get('vehicle_registration')}` ({amb.get('vehicle_type')})\n"
                f"• **Unit Lead**: {amb.get('paramedic_lead')} · Call: `{amb.get('driver_contact')}`\n"
                f"• **Ambulance ETA**: **{amb.get('eta_minutes')} Minutes** (Priority Sirens)\n"
                f"• **Pre-Booked Hospital ER**: {hosp.get('hospital_name')}\n"
                f"• **Assigned ER Bay**: `{hosp.get('assigned_bay')}` (Zero Wait Reception)\n"
                f"• **Resuscitation Lead**: {hosp.get('on_duty_physician')} (Cath Lab & ECG on standby)\n"
                f"• **Next-of-Kin Notified**: `{kin.get('recipient_name')}` ({kin.get('phone')}) via priority SMS with live GPS link\n"
                f"• **Live Tracking Terminal**: Dispatched on browser screencast (/mock/emergency)"
            )
            await agent_core.broadcast({
                "type": "SOS_EMERGENCY_ACTIVATED",
                "condition": prompt,
                "telemetry": telemetry
            })
            await agent_core.broadcast({
                "type": "CHAT_RESPONSE",
                "text": emergency_msg,
                "reason": "Autonomous medical emergency triage, ambulance booking, hospital admission, and kin alert."
            })
            return JSONResponse({
                "status": "COMPLETED",
                "protocol": "SOS_MEDICAL_EMERGENCY",
                "reason": "Ambulance dispatched, hospital ER pre-booked, kin alerted, clinical first-aid delivered.",
                "details": telemetry,
                "emergency_portal": "http://localhost:8000/mock/emergency",
                "duration_ms": telemetry.get("processing_time_ms", 0)
            })

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
                prof = v_data.get("profile") or v_data.get("candidate_profile", {})
                acad = v_data.get("academic") or prof.get("academic", {})
                addr = v_data.get("address", {})
                transit = v_data.get("transit_preferences", {})
                context_data += (
                    f"\n--- SENDER CANDIDATE CREDENTIALS (FROM USER VAULT) ---\n"
                    f"Full Name: {prof.get('full_name') or prof.get('name', 'Yashwanth K R')}\n"
                    f"Date of Birth: {prof.get('dob', '2003-08-14')} (Age: {prof.get('age', 23)})\n"
                    f"Gender: {prof.get('gender', 'Male')}\n"
                    f"Masked ID / Aadhaar: {prof.get('aadhaar_masked', 'XXXX-XXXX-8921')}\n"
                    f"Email Address: {prof.get('email', 'yashwanth.kr.dbit@gmail.com')}\n"
                    f"Phone: {prof.get('phone', '+91 98450 12345')}\n"
                    f"Institution: {acad.get('institution', 'Don Bosco Institute of Technology (DBIT)')}\n"
                    f"Course / Branch: {acad.get('course', 'B.Tech')} in {acad.get('branch', 'Computer Science & Engineering')}\n"
                    f"Current Year: {acad.get('current_year', '4th Year / 8th Semester')}\n"
                    f"B.Tech CGPA: {acad.get('cgpa', '8.85')} (Top 5%)\n"
                    f"Class 10th Score: {acad.get('tenth_percentage', '92.4%')}\n"
                    f"Class 12th Score: {acad.get('twelfth_percentage', '89.6%')}\n"
                    f"Technical Skills: {', '.join(acad.get('skills', ['Python', 'FastAPI', 'Agentic AI', 'Playwright']))}\n"
                    f"Address: {addr.get('line1', 'Kumbalagodu, Mysore Road')}, {addr.get('city', 'Bengaluru')}, {addr.get('state', 'Karnataka')} - {addr.get('pincode', '560074')}\n"
                    f"Transit Origin: {transit.get('default_origin', 'Bengaluru')}, Destination: {transit.get('default_destination', 'Mysuru')}, Berth: {transit.get('preferred_berth', 'Lower Sleeper')}\n"
                )
            except Exception as e:
                print(f"[!] Error reading vault.json: {e}")

        # Store in agent core
        agent_core.attached_files = attached_files or agent_core.session_files
        agent_core.current_context = context_data

        p_lower = prompt.lower()

        # Explicit Mock Benchmark 1: Document Exorcist (photo healing)
        if any(k in p_lower for k in ["heal photo", "fix passport", "compress photo", "passport photo", "document exorcist test"]):
            input_test_file = BASE_DIR / "test_oversized_photo.jpg"
            if attached_files and Path(attached_files[0].get("path", "")).exists():
                input_test_file = Path(attached_files[0]["path"])
                print(f"[DOC EXORCIST] Healing user uploaded photo: {input_test_file}")

            output_file = BASE_DIR / "test_healed_passport_photo.jpg"
            telemetry = await asyncio.to_thread(heal_image, str(input_test_file), str(output_file), 20, 48)
            return JSONResponse({
                "status": "COMPLETED",
                "protocol": "DOC_EXORCIST",
                "reason": "Document Exorcist healed upload to compliant 32KB.",
                "details": telemetry,
                "proof_image": "/proof/test_healed_passport_photo.jpg",
                "payment_gate_active": False,
                "duration_ms": round((time.time() - t_start) * 1000, 1)
            })

        # Explicit Mock Benchmark 2: Anti-Dark-Pattern Fee Stripper
        elif any(k in p_lower for k in ["mock checkout", "test dark pattern", "test sneaky fee", "benchmark dark pattern", "demo dark pattern"]):
            telemetry = await asyncio.to_thread(run_dark_pattern_demo, "mock_checkout.html", True)
            return JSONResponse({
                "status": "COMPLETED",
                "protocol": "ANTI_DARK_PATTERN",
                "reason": "Anti-Dark-Pattern engine stripped deceptive fees.",
                "details": telemetry,
                "proof_image": "/proof/cleaned_checkout_proof.png",
                "payment_gate_active": True,
                "duration_ms": round((time.time() - t_start) * 1000, 1)
            })

        # Explicit Mock Benchmark 3: Transit Rush KSRTC Reservation Mock
        elif any(k in p_lower for k in ["mock ksrtc", "test transit rush", "benchmark transit", "demo transit rush", "test ksrtc"]):
            telemetry = await asyncio.to_thread(run_transit_rush, "mock_ksrtc.html", True)
            return JSONResponse({
                "status": "COMPLETED",
                "protocol": "TRANSIT_RUSH",
                "reason": "Transit Rush reserved berths 14A/14B and stripped dark-pattern fees.",
                "details": telemetry,
                "proof_image": "/proof/transit_rush_proof.png",
                "payment_gate_active": True,
                "duration_ms": round((time.time() - t_start) * 1000, 1)
            })

        # Explicit Mock Benchmark 4: Air-Gapped Fraud Sentinel Mock
        elif any(k in p_lower for k in ["mock sentinel", "test sentinel", "demo sentinel", "test fraud"]):
            target_check = "http://localhost:8000/mock/checkout"
            telemetry = await asyncio.to_thread(run_sentinel_demo, target_check, True)
            return JSONResponse({
                "status": "COMPLETED",
                "protocol": "FRAUD_SENTINEL",
                "reason": "Air-Gapped Fraud Sentinel intercepted financial payment gateway and froze state before payment.",
                "details": telemetry,
                "proof_image": "/proof/sentinel_halt_proof.png",
                "payment_gate_active": True,
                "duration_ms": round((time.time() - t_start) * 1000, 1)
            })

        # ALL OTHER COMMANDS (including 'open abhibus', 'suno ai', 'biryani', searches, real tasks):
        # Dispatch to live autonomous agent core on real browser
        print(f"[AGENT SERVER] Dispatching live autonomous task on real browser for: \"{prompt}\"")
        await agent_core.start_autonomous_task(prompt, context=context_data)
        return JSONResponse({
            "status": "RUNNING",
            "protocol": "AUTONOMOUS_EXECUTION",
            "reason": f"Agent dispatched on goal: {prompt}",
            "live_stream": True,
            "duration_ms": round((time.time() - t_start) * 1000, 1)
        })

    except Exception as e:
        print(f"[AGENT SERVER ERROR] Unexpected error in execute_agent_command: {e}")
        return JSONResponse({
            "status": "ERROR",
            "protocol": "SYSTEM_GUARDRAIL",
            "message": f"Execution notice: {str(e)}",
            "reason": str(e),
            "live_stream": True,
            "duration_ms": round((time.time() - t_start) * 1000, 1) if 't_start' in locals() else 0
        }, status_code=200)

if __name__ == "__main__":
    import uvicorn
    print("\n=================================================================")
    print("  🌀 WORMHOLE / APPLYCOPILOT REAL-TIME AGENT SERVER")
    print("  * Local Web Cockpit: http://localhost:8000")
    print("  * Live WebSocket Stream: ws://localhost:8000/ws/screencast")
    print("=================================================================\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
