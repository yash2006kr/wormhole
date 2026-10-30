"""
ApplyCopilot (Wormhole) Real-Time Agentic Web Engine
Features:
- Live CDP Screencast streaming to WebSockets
- Real website navigation & semantic reasoning via Groq LPU
- Bidirectional user interaction (clicks, mouse, typing directly on canvas)
- Instant Human-in-the-Loop Interrupt Gate (pauses on user click or CAPTCHA/Login)
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

from playwright.async_api import async_playwright
from groq import Groq

groq_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_key)

class AgentCore:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.cdp = None
        
        # State: IDLE, RUNNING, INTERRUPTED, PAUSED_FOR_HUMAN
        self.state = "IDLE"
        self.current_goal = None
        self.interrupt_event = asyncio.Event()
        self.resume_event = asyncio.Event()
        self.interrupt_resolution = None # "RESUME", "REPLAN", "HANDOVER"
        self.new_instruction = None
        
        self.active_websockets = set()
        self.execution_task = None
        self.action_history = []
        self.attached_files = []
        self.viewport_size = {"width": 1280, "height": 800}

    async def initialize(self):
        """Spins up Playwright Chromium with stealth configs and CDP session."""
        if self.browser:
            return

        print("[AGENT CORE] Launching Chromium Browser Engine...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars"
            ]
        )
        self.context = await self.browser.new_context(
            viewport=self.viewport_size,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()
        
        # Open default landing page
        await self.page.goto("https://en.wikipedia.org")

        # Establish Chrome DevTools Protocol Session
        self.cdp = await self.context.new_cdp_session(self.page)
        self.cdp.on("Page.screencastFrame", self._on_screencast_frame)
        
        await self.cdp.send("Page.startScreencast", {
            "format": "jpeg",
            "quality": 65,
            "maxWidth": self.viewport_size["width"],
            "maxHeight": self.viewport_size["height"],
            "everyNthFrame": 1
        })
        print("[AGENT CORE] CDP Screencast stream online.")

    async def _on_screencast_frame(self, event):
        """Pushes real-time JPEG screencast frames to all connected frontend clients."""
        try:
            frame_base64 = event["data"]
            session_id = event["sessionId"]
            
            # Acknowledge frame to keep CDP stream flowing
            await self.cdp.send("Page.screencastFrameAck", {"sessionId": session_id})
            
            # Broadcast to web dashboard
            if self.active_websockets:
                payload = json.dumps({
                    "type": "FRAME",
                    "data": frame_base64,
                    "state": self.state,
                    "url": self.page.url if self.page else ""
                })
                disconnected = set()
                for ws in self.active_websockets:
                    try:
                        await ws.send_text(payload)
                    except Exception:
                        disconnected.add(ws)
                self.active_websockets -= disconnected
        except Exception as e:
            pass

    async def broadcast(self, msg_dict):
        """Sends control/telemetry messages to all WebSocket clients."""
        payload = json.dumps(msg_dict)
        disconnected = set()
        for ws in self.active_websockets:
            try:
                await ws.send_text(payload)
            except Exception:
                disconnected.add(ws)
        self.active_websockets -= disconnected

    # --------------------------------------------------------------------------
    # BIDIRECTIONAL USER INTERACTION
    # --------------------------------------------------------------------------
    async def handle_user_canvas_click(self, x_ratio, y_ratio):
        """
        Receives normalized (0.0 to 1.0) coordinates from client's canvas click.
        """
        actual_x = int(x_ratio * self.viewport_size["width"])
        actual_y = int(y_ratio * self.viewport_size["height"])

        print(f"[USER INTERACTION] Click at ({actual_x}, {actual_y}) | Current State: {self.state}")

        # If agent is RUNNING -> Trigger Instant Interrupt!
        if self.state == "RUNNING":
            print(f"[INTERRUPT] User clicked website at ({actual_x}, {actual_y})! Halting autonomous agent immediately...")
            await self.trigger_user_interrupt(actual_x, actual_y)
            return

        # If IDLE or MANUAL_CONTROL -> forward click directly to real web page
        if self.cdp:
            try:
                await self.cdp.send("Input.dispatchMouseEvent", {
                    "type": "mousePressed",
                    "x": actual_x,
                    "y": actual_y,
                    "button": "left",
                    "clickCount": 1
                })
                await asyncio.sleep(0.05)
                await self.cdp.send("Input.dispatchMouseEvent", {
                    "type": "mouseReleased",
                    "x": actual_x,
                    "y": actual_y,
                    "button": "left",
                    "clickCount": 1
                })
                await self.broadcast({
                    "type": "LOG",
                    "message": f"User manual click forwarded to DOM at ({actual_x}, {actual_y})."
                })
            except Exception as e:
                print(f"[!] Error forwarding click: {e}")

    async def handle_user_canvas_key(self, key, text=None):
        """Forwards keyboard strokes to the real page during manual takeover (login, OTP, CAPTCHA)."""
        if not self.page or self.state not in ["MANUAL_CONTROL", "IDLE"]:
            return

        try:
            if key == "Backspace":
                await self.page.keyboard.press("Backspace")
            elif key == "Enter":
                await self.page.keyboard.press("Enter")
            elif key == "Tab":
                await self.page.keyboard.press("Tab")
            elif key == "Escape":
                await self.page.keyboard.press("Escape")
            elif text and len(text) == 1:
                await self.page.keyboard.insert_text(text)
            else:
                await self.page.keyboard.press(key)
        except Exception as e:
            print(f"[!] Error forwarding keystroke: {e}")

    async def direct_goto(self, url):
        """Direct navigation invoked by user entering URL in browser bar."""
        await self.initialize()
        if self.page:
            try:
                print(f"[DIRECT NAV] Navigating to: {url}")
                await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await self.broadcast({
                    "type": "URL_UPDATE",
                    "url": self.page.url,
                    "title": await self.page.title()
                })
            except Exception as e:
                print(f"[!] Direct goto error: {e}")

    async def trigger_user_interrupt(self, x=None, y=None):
        """Puts agent into INTERRUPTED state and notifies frontend."""
        self.state = "INTERRUPTED"
        self.interrupt_event.set()
        self.resume_event.clear()
        
        curr_title = ""
        curr_url = ""
        if self.page:
            try:
                curr_title = await self.page.title()
                curr_url = self.page.url
            except Exception:
                pass

        await self.broadcast({
            "type": "INTERRUPT_TRIGGERED",
            "state": "INTERRUPTED",
            "message": "User clicked inside the live website. Autonomous agent paused immediately.",
            "url": curr_url,
            "title": curr_title,
            "current_goal": self.current_goal,
            "click_coords": {"x": x, "y": y} if x and y else None
        })

    async def resolve_interrupt(self, action, new_prompt=None):
        """
        Resolves the user's decision from the interrupt modal:
        action in ['RESUME', 'REPLAN', 'HANDOVER']
        """
        print(f"[INTERRUPT RESOLUTION] User chose: {action}")
        self.interrupt_resolution = action
        self.new_instruction = new_prompt
        
        if action == "RESUME":
            self.state = "RUNNING"
            self.interrupt_event.clear()
            self.resume_event.set()
            await self.broadcast({
                "type": "LOG",
                "message": "Resuming autonomous trajectory (accidental click dismissed)."
            })

        elif action == "REPLAN":
            self.state = "RUNNING"
            self.current_goal = new_prompt
            self.interrupt_event.clear()
            self.resume_event.set()
            await self.broadcast({
                "type": "LOG",
                "message": f"Replanning trajectory with new instruction: '{new_prompt}'"
            })

        elif action == "HANDOVER":
            self.state = "MANUAL_CONTROL"
            await self.broadcast({
                "type": "LOG",
                "message": "Manual handover active. You can now click and log in / solve CAPTCHA directly on canvas."
            })

    async def resume_from_manual_handover(self):
        """Called when user finishes manual login / verification."""
        self.state = "RUNNING"
        self.interrupt_event.clear()
        self.resume_event.set()
        await self.broadcast({
            "type": "LOG",
            "message": "Human verification complete! Agent resuming autonomous flow."
        })

    # --------------------------------------------------------------------------
    # AUTONOMOUS AGENTIC EXECUTION LOOP
    # --------------------------------------------------------------------------
    async def start_autonomous_task(self, goal):
        """Starts executing a natural language goal on the live web."""
        await self.initialize()
        self.current_goal = goal
        self.state = "RUNNING"
        self.action_history = []
        self.interrupt_event.clear()
        self.resume_event.clear()
        
        if self.execution_task and not self.execution_task.done():
            self.execution_task.cancel()
            
        self.execution_task = asyncio.create_task(self._run_loop())

    async def get_current_frame_base64(self):
        """Captures an immediate frame for new WebSocket connections."""
        if self.page:
            try:
                frame_bytes = await self.page.screenshot(type="jpeg", quality=60)
                return base64.b64encode(frame_bytes).decode("ascii")
            except Exception:
                pass
        return None

    async def _run_loop(self):
        """Main agentic reasoning & execution loop."""
        try:
            print(f"\n[AGENTIC LOOP START] Goal: \"{self.current_goal}\"")
            await self.broadcast({"type": "TASK_START", "goal": self.current_goal})

            max_steps = 10
            step_count = 0

            while step_count < max_steps and self.state in ["RUNNING", "INTERRUPTED", "MANUAL_CONTROL"]:
                # Check for Interrupt Gate
                if self.interrupt_event.is_set() or self.state in ["INTERRUPTED", "MANUAL_CONTROL"]:
                    print("[AGENT LOOP] Agent paused at interrupt gate. Awaiting user resolution...")
                    await self.resume_event.wait()
                    print("[AGENT LOOP] Interrupt cleared! Proceeding...")

                step_count += 1
                curr_url = self.page.url
                curr_title = await self.page.title()
                
                print(f"\n--- STEP {step_count}/{max_steps} | URL: {curr_url} ---")
                await self.broadcast({"type": "STEP", "step": step_count, "url": curr_url, "title": curr_title})

                # Check for Human Verification / Login / Payment Gate
                is_human_gate = any(k in curr_url.lower() for k in [
                    "login", "signin", "checkout", "payment", "captcha", "recaptcha", "turnstile", "challenge", "verify", "auth"
                ]) or any(k in curr_title.lower() for k in [
                    "login", "sign in", "security check", "captcha", "verification", "one-time password", "otp"
                ])

                if is_human_gate:
                    print(f"[SAFETY TRIGGER] Human Verification / Login / CAPTCHA detected on '{curr_title}'. Pausing for user.")
                    self.state = "PAUSED_FOR_HUMAN"
                    await self.broadcast({
                        "type": "HUMAN_VERIFICATION_REQUIRED",
                        "state": "PAUSED_FOR_HUMAN",
                        "url": curr_url,
                        "title": curr_title,
                        "message": "Human verification or Login required. Please complete this step directly on the website."
                    })
                    await self.resume_event.wait()

                # Ask Groq LPU for next action
                action = await self._decide_next_action(self.current_goal, curr_url, curr_title)
                action_type = action.get("action", "wait").lower()
                selector = action.get("selector", "")
                text_val = action.get("text", "")
                reason = action.get("reason", "")

                await self.broadcast({
                    "type": "ACTION",
                    "action": action_type,
                    "selector": selector,
                    "text": text_val,
                    "reason": reason
                })

                # Execute the action on the live page
                try:
                    if action_type == "navigate":
                        url_cand = (action.get("url") or action.get("text") or action.get("selector") or "").strip()
                        if not url_cand or not ("http" in url_cand or "." in url_cand):
                            for token in self.current_goal.split():
                                clean_token = token.strip("',\"()<>")
                                if "http" in clean_token or ("." in clean_token and len(clean_token) > 3):
                                    url_cand = clean_token
                                    break
                        target_url = url_cand if url_cand.startswith("http") else f"https://{url_cand}"
                        
                        # If already at destination
                        if target_url.rstrip("/") in curr_url.rstrip("/") and len(curr_url) > 10:
                            print(f"  -> Arrived at target: {curr_url}")
                            await self.broadcast({"type": "COMPLETE", "reason": f"Successfully loaded {curr_url}"})
                            break

                        print(f"  -> Navigating to: {target_url}")
                        await self.page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                        await asyncio.sleep(1.5)

                    elif action_type == "type":
                        target_selector = selector or "input, textarea"
                        print(f"  -> Typing '{text_val}' into: {target_selector}")
                        await self.page.fill(target_selector, text_val, timeout=5000)
                        if action.get("press_enter"):
                            await self.page.press(target_selector, "Enter")
                        await asyncio.sleep(1)

                    elif action_type == "click":
                        target_selector = selector or text_val
                        print(f"  -> Clicking element: {target_selector}")
                        await self.page.click(target_selector, timeout=5000)
                        await asyncio.sleep(1.5)

                    elif action_type == "scroll":
                        print("  -> Scrolling down page...")
                        await self.page.evaluate("window.scrollBy(0, 500)")
                        await asyncio.sleep(0.5)

                    elif action_type == "finish":
                        print(f"  -> Task Complete: {reason}")
                        await self.broadcast({"type": "COMPLETE", "reason": reason})
                        break

                except Exception as e:
                    print(f"  [!] Action execution error on '{selector}': {e}")
                    await self.broadcast({"type": "LOG", "message": f"Action error: {e}"})
                    await asyncio.sleep(1)

                # Check if user clicked during execution
                for _ in range(10):
                    if self.interrupt_event.is_set():
                        break
                    await asyncio.sleep(0.1)

            self.state = "IDLE"
            await self.broadcast({"type": "STATE_CHANGE", "state": "IDLE"})
        except Exception as e:
            print(f"[AGENT LOOP FATAL] Error: {e}")
            import traceback
            traceback.print_exc()
            self.state = "IDLE"

    async def _decide_next_action(self, goal, curr_url, curr_title):
        """Queries Groq LPU to determine the next browser action."""
        # Fast rule-based heuristics for speed & reliability
        if "google.com" in curr_url or "bing.com" in curr_url:
            if "search" in goal.lower():
                return {
                    "action": "type",
                    "selector": "textarea[name='q'], input[name='q']",
                    "text": goal.replace("search", "").strip(),
                    "press_enter": True,
                    "reason": "Typing search query into Google."
                }

        # Otherwise query Groq LPU
        sys_prompt = (
            "You are an autonomous web agent executing actions on real websites.\n"
            "Given the user's goal, current URL, and page title, return the NEXT single action in valid JSON.\n"
            "Action options:\n"
            "- navigate: set 'text' to full URL (e.g. {\"action\": \"navigate\", \"text\": \"https://news.ycombinator.com\", \"reason\": \"Open HN\"})\n"
            "- click: set 'selector' to CSS or text selector (e.g. {\"action\": \"click\", \"selector\": \"text=Show HN\", \"reason\": \"Filter articles\"})\n"
            "- type: set 'selector' to input, 'text' to string, optional 'press_enter': true\n"
            "- scroll: {\"action\": \"scroll\", \"reason\": \"Browse content\"}\n"
            "- finish: when goal has been achieved or user is at destination\n"
            "JSON Format: {\"action\": \"...\", \"selector\": \"...\", \"text\": \"...\", \"reason\": \"...\", \"press_enter\": false}"
        )
        user_msg = f"Goal: {goal}\nCurrent URL: {curr_url}\nCurrent Page Title: {curr_title}"

        try:
            res = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return json.loads(res.choices[0].message.content)
        except Exception as e:
            print(f"[!] Groq decision error: {e}")
            if curr_url == "https://en.wikipedia.org":
                return {
                    "action": "navigate",
                    "text": "https://news.ycombinator.com",
                    "reason": "Navigating to tech portal."
                }
            return {"action": "finish", "reason": "Completed trajectory."}

# Global Singleton Instance
agent_core = AgentCore()
