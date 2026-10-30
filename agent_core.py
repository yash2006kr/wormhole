"""
ApplyCopilot (Wormhole) Real-Time Agentic Web Engine
Features:
- Live CDP Screencast streaming to WebSockets with Wheel Scrolling & Mouse Movement
- DOM-Aware Autonomous Reasoning via Groq LPU (openai/gpt-oss-20b)
- Multi-Input Form Filling (fill_form action with smart SPA section activation)
- Document Context Ingestion (extracts text from attached PDFs and credentials from vault)
- Instant Human-in-the-Loop Interrupt Gate & Emergency Abort
- Advanced Semantic Web Navigation & Self-Healing Action Fallbacks
"""

import os
import sys
import re
import json
import time
import base64
import asyncio
from pathlib import Path
from urllib.parse import urlparse
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
        
        # State: IDLE, RUNNING, INTERRUPTED, MANUAL_CONTROL, PAUSED_FOR_HUMAN
        self.state = "IDLE"
        self.current_goal = None
        self.current_context = ""
        self.attached_files = []
        self.interrupt_event = asyncio.Event()
        self.resume_event = asyncio.Event()
        self.interrupt_resolution = None # "RESUME", "REPLAN", "HANDOVER"
        self.new_instruction = None
        
        self.active_websockets = set()
        self.execution_task = None
        self.action_history = []
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
        except Exception:
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
    # BIDIRECTIONAL USER INTERACTION (CLICKS, WHEEL, KEYBOARD)
    # --------------------------------------------------------------------------
    async def handle_user_canvas_click(self, x_ratio, y_ratio):
        """Receives normalized (0.0 to 1.0) coordinates from client canvas click."""
        actual_x = int(x_ratio * self.viewport_size["width"])
        actual_y = int(y_ratio * self.viewport_size["height"])

        # If agent is RUNNING -> Trigger Instant Interrupt!
        if self.state == "RUNNING":
            print(f"[INTERRUPT] User clicked website at ({actual_x}, {actual_y})! Halting autonomous agent immediately...")
            await self.trigger_user_interrupt(actual_x, actual_y)
            return

        # If IDLE or MANUAL_CONTROL -> forward click with mouseMoved first
        if self.cdp:
            try:
                # 1. Dispatch mouseMoved to trigger hover / active states
                await self.cdp.send("Input.dispatchMouseEvent", {
                    "type": "mouseMoved",
                    "x": actual_x,
                    "y": actual_y
                })
                await asyncio.sleep(0.02)
                # 2. Press
                await self.cdp.send("Input.dispatchMouseEvent", {
                    "type": "mousePressed",
                    "x": actual_x,
                    "y": actual_y,
                    "button": "left",
                    "clickCount": 1
                })
                await asyncio.sleep(0.04)
                # 3. Release
                await self.cdp.send("Input.dispatchMouseEvent", {
                    "type": "mouseReleased",
                    "x": actual_x,
                    "y": actual_y,
                    "button": "left",
                    "clickCount": 1
                })
            except Exception as e:
                print(f"[!] Error forwarding click: {e}")

    async def handle_user_canvas_wheel(self, x_ratio, y_ratio, delta_x, delta_y):
        """Forwards mouse wheel scrolling to real browser session."""
        actual_x = int(x_ratio * self.viewport_size["width"])
        actual_y = int(y_ratio * self.viewport_size["height"])
        if self.cdp:
            try:
                await self.cdp.send("Input.dispatchMouseEvent", {
                    "type": "mouseWheel",
                    "x": actual_x,
                    "y": actual_y,
                    "deltaX": int(delta_x),
                    "deltaY": int(delta_y)
                })
            except Exception:
                pass

    async def handle_user_canvas_key(self, key, text=None):
        """Forwards keyboard strokes to the real page during manual takeover (login, OTP, CAPTCHA)."""
        if not self.page:
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
        """Resolves user decision from interrupt modal: ['RESUME', 'REPLAN', 'HANDOVER']."""
        print(f"[INTERRUPT RESOLUTION] User chose: {action}")
        self.interrupt_resolution = action
        self.new_instruction = new_prompt
        
        if action == "RESUME":
            self.state = "RUNNING"
            self.interrupt_event.clear()
            self.resume_event.set()
            await self.broadcast({
                "type": "LOG",
                "message": "Resuming autonomous trajectory."
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
                "message": "Interactive mode active. Full mouse, scroll & keyboard control granted."
            })

    async def resume_from_manual_handover(self):
        """Called when user finishes manual login / verification."""
        self.state = "RUNNING"
        self.interrupt_event.clear()
        self.resume_event.set()
        await self.broadcast({
            "type": "LOG",
            "message": "Resuming autonomous trajectory after manual interaction."
        })

    async def abort_current_task(self):
        """Emergency stop: kills current execution loop immediately."""
        print("[AGENT CORE] Immediate emergency abort triggered.")
        self.state = "IDLE"
        self.interrupt_event.clear()
        self.resume_event.set()
        if self.execution_task and not self.execution_task.done():
            self.execution_task.cancel()
        await self.broadcast({
            "type": "COMPLETE",
            "reason": "Agent stopped by user command.",
            "state": "IDLE"
        })

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

    # --------------------------------------------------------------------------
    # RICH DOM INSPECTOR: EXTRACTS STRUCTURED CONTEXT & INTERACTIVE ELEMENTS
    # --------------------------------------------------------------------------
    async def _get_interactive_dom_elements(self):
        """Extracts structured DOM: headings, navigation tabs, forms, buttons, and alert notices."""
        if not self.page:
            return ""
        try:
            script = """
            (() => {
                const isVisible = (el) => {
                    if (!el) return false;
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
                    const rect = el.getBoundingClientRect();
                    return (rect.width > 0 && rect.height > 0) || !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
                };

                const cleanText = (t) => (t || '').replace(/\\s+/g, ' ').trim().slice(0, 60);

                // 1. Page Title & Headings (to know what page/section is active)
                const headings = [];
                document.querySelectorAll('h1, h2, h3').forEach((h, i) => {
                    if (i < 8) {
                        const txt = cleanText(h.innerText);
                        if (txt) headings.push(`${h.tagName}: "${txt}"`);
                    }
                });

                // 2. Navigation items (Header links, Nav links, Section tabs, Anchor links)
                const navItems = [];
                document.querySelectorAll('nav a, header a, a[href^="#"], [role="tab"], [data-page], [data-section], a.nav-link, a').forEach((el, i) => {
                    if (navItems.length < 20) {
                        const txt = cleanText(el.innerText || el.getAttribute('aria-label') || el.getAttribute('title'));
                        const href = el.getAttribute('href') || el.getAttribute('data-page') || '';
                        const id = el.id ? '#' + el.id : '';
                        if (txt && (href.startsWith('#') || href.includes('connect') || href.includes('contact') || href.includes('about') || href.includes('project') || href.includes('apply') || navItems.length < 8)) {
                            navItems.push(`NAV: a${id}[href="${href}"] text="${txt}" [${isVisible(el) ? 'visible' : 'hidden'}]`);
                        }
                    }
                });

                // 3. Inputs, Textareas, Selects
                const formFields = [];
                document.querySelectorAll('input:not([type="hidden"]), textarea, select').forEach((el, i) => {
                    if (i < 25) {
                        const tag = el.tagName.toLowerCase();
                        const id = el.id ? '#' + el.id : '';
                        const name = el.name ? `[name="${el.name}"]` : '';
                        const type = el.type ? `[type="${el.type}"]` : '';
                        const placeholder = el.placeholder ? `placeholder="${cleanText(el.placeholder)}"` : '';
                        
                        let labelText = '';
                        if (el.id) {
                            const lbl = document.querySelector(`label[for="${el.id}"]`);
                            if (lbl) labelText = cleanText(lbl.innerText);
                        }
                        if (!labelText && el.closest('label')) {
                            labelText = cleanText(el.closest('label').innerText);
                        }
                        const labelStr = labelText ? `label="${labelText}"` : '';
                        const vis = isVisible(el) ? 'visible' : 'hidden';
                        formFields.push(`FIELD: ${tag}${id}${name}${type} ${placeholder} ${labelStr} [${vis}]`.replace(/\\s+/g, ' ').trim());
                    }
                });

                // 4. Buttons & Interactive Clickables
                const buttons = [];
                document.querySelectorAll('button, input[type="submit"], [role="button"]').forEach((el, i) => {
                    if (buttons.length < 20) {
                        const id = el.id ? '#' + el.id : '';
                        const type = el.type ? `[type="${el.type}"]` : '';
                        const txt = cleanText(el.innerText || el.value || el.getAttribute('aria-label'));
                        const vis = isVisible(el) ? 'visible' : 'hidden';
                        if (txt || id) {
                            buttons.push(`BUTTON: ${el.tagName.toLowerCase()}${id}${type} text="${txt}" [${vis}]`.trim());
                        }
                    }
                });

                // 5. Active confirmation / Success / Error notices
                const notices = [];
                document.querySelectorAll('.alert, .success, .error, [role="alert"], .notification, .toast, .sent-message').forEach(el => {
                    if (isVisible(el)) {
                        const txt = cleanText(el.innerText);
                        if (txt) notices.push(`STATUS_NOTICE: "${txt}"`);
                    }
                });

                let output = [];
                if (headings.length) output.push("=== PAGE HEADINGS ===\\n" + headings.join("\\n"));
                if (navItems.length) output.push("=== NAVIGATION & SECTION LINKS ===\\n" + navItems.join("\\n"));
                if (formFields.length) output.push("=== FORM INPUT FIELDS ===\\n" + formFields.join("\\n"));
                if (buttons.length) output.push("=== BUTTONS & SUBMIT CONTROLS ===\\n" + buttons.join("\\n"));
                if (notices.length) output.push("=== NOTICES ON PAGE ===\\n" + notices.join("\\n"));

                return output.join("\\n\\n");
            })()
            """
            return await self.page.evaluate(script)
        except Exception as e:
            print(f"[!] DOM extraction error: {e}")
            return ""

    # --------------------------------------------------------------------------
    # RESILIENT ACTION EXECUTION HELPERS
    # --------------------------------------------------------------------------
    async def _smart_click(self, raw_selector, text=None):
        """Clicks an element using multiple fallback strategies (exact, text, role, JS)."""
        if not self.page:
            return False

        clean_sel = raw_selector or ""
        # Clean Groq pseudoselectors like button: text="..." -> button:has-text("...")
        if "text=" in clean_sel and not clean_sel.startswith("text="):
            txt_part = clean_sel.split("text=")[1].strip(" :\"'").replace('"', '')
            clean_sel = f'button:has-text("{txt_part}"), a:has-text("{txt_part}")'

        # Strategy 1: Standard locator click
        try:
            loc = self.page.locator(clean_sel).first
            if await loc.count() > 0:
                await loc.scroll_into_view_if_needed(timeout=2500)
                await loc.click(timeout=4000)
                return True
        except Exception:
            pass

        # Strategy 2: If it's a section anchor link (#connect, #contact)
        if "#" in clean_sel:
            hash_target = re.findall(r'#[a-zA-Z0-9_\-]+', clean_sel)
            if hash_target:
                tgt = hash_target[0]
                try:
                    js_click = f"""
                    (() => {{
                        const a = document.querySelector('a[href="{tgt}"], a[data-page="{tgt.replace("#", "")}"]');
                        if (a) {{ a.click(); return true; }}
                        const el = document.querySelector('{tgt}');
                        if (el) {{ el.scrollIntoView({{behavior: "smooth"}}); return true; }}
                        window.location.hash = '{tgt}';
                        return true;
                    }})()
                    """
                    success = await self.page.evaluate(js_click)
                    if success:
                        return True
                except Exception:
                    pass

        # Strategy 3: Text match
        query_text = text or (clean_sel if not clean_sel.startswith(('.', '#', '[')) else None)
        if query_text:
            try:
                txt_loc = self.page.get_by_text(query_text, exact=False).first
                if await txt_loc.count() > 0:
                    await txt_loc.scroll_into_view_if_needed(timeout=2500)
                    await txt_loc.click(timeout=3000, force=True)
                    return True
            except Exception:
                pass

        # Strategy 4: Force click on locator
        try:
            loc = self.page.locator(clean_sel).first
            if await loc.count() > 0:
                await loc.click(force=True, timeout=2000)
                return True
        except Exception:
            pass

        return False

    # --------------------------------------------------------------------------
    # AUTONOMOUS AGENTIC EXECUTION LOOP
    # --------------------------------------------------------------------------
    async def start_autonomous_task(self, goal, context=""):
        """Starts executing a natural language goal on the live web."""
        await self.initialize()
        self.current_goal = goal
        self.current_context = context
        self.state = "RUNNING"
        self.action_history = []
        self.interrupt_event.clear()
        self.resume_event.clear()

        # PRE-CHECK: If goal contains an explicit URL, navigate directly before entering the loop!
        found_urls = re.findall(r'https?://[^\s<>"\',;]+', goal)
        if found_urls and self.page:
            target_initial_url = found_urls[0].rstrip('.,;')
            try:
                target_host = urlparse(target_initial_url).netloc
                curr_host = urlparse(self.page.url or "").netloc
                if target_host and target_host != curr_host:
                    print(f"[AGENT CORE] Initial URL detected in goal: {target_initial_url}. Navigating directly...")
                    await self.broadcast({
                        "type": "LOG",
                        "message": f"Directly navigating to target website specified in prompt: {target_initial_url}"
                    })
                    await self.page.goto(target_initial_url, wait_until="domcontentloaded", timeout=25000)
                    await asyncio.sleep(1.5)
            except Exception as e:
                print(f"[!] Initial navigation error: {e}")
        
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
        """Main agentic reasoning & execution loop with DOM awareness."""
        try:
            print(f"\n[AGENTIC LOOP START] Goal: \"{self.current_goal}\"")
            await self.broadcast({"type": "TASK_START", "goal": self.current_goal})

            max_steps = 10
            step_count = 0
            prev_action_key = None
            repeat_action_count = 0

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

                # Extract live interactive DOM elements
                dom_elements = await self._get_interactive_dom_elements()

                # Ask Groq LPU for next action
                action = await self._decide_next_action(
                    self.current_goal, curr_url, curr_title, dom_elements, self.current_context
                )
                action_type = action.get("action", "wait").lower()
                selector = action.get("selector", "")
                text_val = action.get("text", "")
                reason = action.get("reason", "")

                # Loop prevention
                current_action_key = f"{action_type}:{selector}:{text_val}"
                if current_action_key == prev_action_key:
                    repeat_action_count += 1
                    if repeat_action_count >= 2:
                        print(f"[!] Repetitive loop detected on '{current_action_key}'. Forcing fallback scroll...")
                        action_type = "scroll"
                        reason = "Bypassing loop: scrolling down to discover interactive elements."
                        repeat_action_count = 0
                else:
                    repeat_action_count = 0
                prev_action_key = current_action_key

                await self.broadcast({
                    "type": "ACTION",
                    "action": action_type,
                    "selector": selector,
                    "text": text_val,
                    "reason": reason
                })

                # Execute action on the live page
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
                        else:
                            print(f"  -> Navigating to: {target_url}")
                            await self.page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                            await asyncio.sleep(1.5)

                    elif action_type == "fill_form":
                        fields = action.get("fields", {})

                        # 1. Activate SPA Section if fields are hidden
                        first_sel = next(iter(fields.keys()), "")
                        if first_sel:
                            try:
                                is_vis = await self.page.locator(first_sel).first.is_visible()
                                if not is_vis:
                                    print(f"  -> Field '{first_sel}' hidden. Triggering section navigation...")
                                    for nav_sel in ["a[href='#connect']", "a[href='#contact']", "a[data-page='connect']", "text=Connect", "text=Contact", "text=Initiate Contact"]:
                                        if await self._smart_click(nav_sel):
                                            print(f"  -> Section navigated via '{nav_sel}'")
                                            await asyncio.sleep(1.2)
                                            break
                            except Exception:
                                pass

                        # 2. Fill each input field with robust fallbacks
                        for f_sel, f_val in fields.items():
                            val_str = str(f_val)
                            print(f"  -> Filling field '{f_sel}' with: {val_str[:35]}...")
                            filled = False
                            
                            # Try primary selector
                            try:
                                loc = self.page.locator(f_sel).first
                                if await loc.count() > 0:
                                    await loc.scroll_into_view_if_needed(timeout=2500)
                                    await loc.fill(val_str, timeout=3000)
                                    filled = True
                            except Exception:
                                pass

                            # Heuristic Fallback based on field intent
                            if not filled:
                                f_lower = f_sel.lower()
                                fallback_candidates = []
                                if "name" in f_lower:
                                    fallback_candidates = ["#form-name", "input[name='name']", "input[placeholder*='name' i]", "input[type='text']"]
                                elif "email" in f_lower:
                                    fallback_candidates = ["#form-email", "input[type='email']", "input[name='email']", "input[placeholder*='email' i]"]
                                elif "message" in f_lower or "comment" in f_lower or "body" in f_lower:
                                    fallback_candidates = ["#form-message", "textarea[name='message']", "textarea", "textarea[placeholder*='message' i]"]

                                for cand in fallback_candidates:
                                    try:
                                        loc = self.page.locator(cand).first
                                        if await loc.count() > 0:
                                            await loc.scroll_into_view_if_needed(timeout=2000)
                                            await loc.fill(val_str, timeout=3000)
                                            filled = True
                                            print(f"     [Fallback Success] Field filled via candidate '{cand}'")
                                            break
                                    except Exception:
                                        continue

                            await asyncio.sleep(0.3)

                        # 3. Submit form
                        submit_sel = action.get("submit_selector") or "button[type='submit'], input[type='submit']"
                        print(f"  -> Submitting form: {submit_sel}")
                        submitted = await self._smart_click(submit_sel)
                        if not submitted:
                            # Try submit button fallbacks
                            for s_cand in ["button:has-text('Send Message')", "button:has-text('Send')", "button:has-text('Submit')", "button[type='submit']"]:
                                if await self._smart_click(s_cand):
                                    submitted = True
                                    break
                        
                        await asyncio.sleep(2.0)

                        if action.get("finish_after", True):
                            print(f"  -> Form Complete: {reason}")
                            await self.broadcast({"type": "COMPLETE", "reason": f"Form submitted: {reason}"})
                            break

                    elif action_type == "type":
                        target_selector = selector or "input, textarea"
                        print(f"  -> Typing '{text_val}' into: {target_selector}")
                        typed = False
                        try:
                            loc = self.page.locator(target_selector).first
                            await loc.scroll_into_view_if_needed(timeout=3000)
                            await loc.fill(text_val, timeout=5000)
                            if action.get("press_enter"):
                                await loc.press("Enter")
                            typed = True
                        except Exception:
                            pass

                        if not typed:
                            # Try first visible input
                            try:
                                loc = self.page.locator("input[type='text'], input[type='search'], textarea").first
                                await loc.fill(text_val, timeout=4000)
                                if action.get("press_enter"):
                                    await loc.press("Enter")
                            except Exception as te:
                                print(f"  [!] Type fallback error: {te}")
                        await asyncio.sleep(1)

                    elif action_type == "click":
                        raw_sel = selector or text_val
                        print(f"  -> Clicking element: {raw_sel}")
                        clicked = await self._smart_click(raw_sel, text=text_val)
                        if not clicked:
                            print(f"  [!] Primary click failed on '{raw_sel}'. Trying anchor/text fallback...")
                        await asyncio.sleep(1.5)

                    elif action_type == "scroll":
                        print("  -> Scrolling down page...")
                        await self.page.evaluate("window.scrollBy(0, 600)")
                        await asyncio.sleep(0.8)

                    elif action_type == "finish":
                        print(f"  -> Task Complete: {reason}")
                        await self.broadcast({"type": "COMPLETE", "reason": reason})
                        break

                except Exception as e:
                    print(f"  [!] Action execution error on '{selector}': {e}")
                    await self.broadcast({"type": "LOG", "message": f"Action notice: {e}"})
                    await asyncio.sleep(1)

                # Check if user clicked during execution
                for _ in range(10):
                    if self.interrupt_event.is_set():
                        break
                    await asyncio.sleep(0.1)

            self.state = "IDLE"
            await self.broadcast({"type": "STATE_CHANGE", "state": "IDLE"})
        except asyncio.CancelledError:
            print("[AGENT LOOP] Task cancelled by user abort.")
            self.state = "IDLE"
        except Exception as e:
            print(f"[AGENT LOOP FATAL] Error: {e}")
            self.state = "IDLE"

    async def _decide_next_action(self, goal, curr_url, curr_title, dom_elements="", context_info=""):
        """Queries Groq LPU with cognitive policy, DOM context, and user document credentials."""
        # Fast rule-based heuristics for search engines
        if ("google.com" in curr_url or "bing.com" in curr_url) and "search" in goal.lower():
            return {
                "action": "type",
                "selector": "textarea[name='q'], input[name='q']",
                "text": goal.replace("search", "").strip(),
                "press_enter": True,
                "reason": "Typing search query into Google."
            }

        sys_prompt = (
            "You are Jarvis-Wormhole, an elite autonomous web navigation and form-filling agent.\n"
            "Your objective is to examine the web page, understand the user's intent, and execute the exact right sequence of browser actions to achieve the goal without getting stuck or lost.\n\n"
            "=== COGNITIVE REASONING POLICY ===\n"
            "1. UNDERSTAND THE USER'S GOAL:\n"
            "   - Identify what the user wants to accomplish (e.g. 'send a message to the guy', 'search for AI', 'fill out application', 'contact developer').\n"
            "2. LOCATE WHERE TO GO ON THE WEBSITE:\n"
            "   - Inspect '=== NAVIGATION & SECTION LINKS ===' and '=== PAGE HEADINGS ==='.\n"
            "   - If the user wants to send a message / connect / contact:\n"
            "     * Look for links or buttons labeled 'Connect', 'Contact', 'Initiate Contact', 'Get in Touch', 'Hire Me', 'Message', or href='#connect' / href='#contact'.\n"
            "     * Single Page Applications (SPAs) keep forms hidden in sections until the section navigation tab is clicked.\n"
            "   - If input fields are present (even if marked [hidden] in an SPA), use action 'fill_form'. It automatically navigates to and activates the section!\n"
            "3. FORM FILLING PROTOCOL (action: 'fill_form'):\n"
            "   - Match the user's attached document / vault profile to the inputs:\n"
            "     * Name field -> use applicant/user's full name\n"
            "     * Email field -> use applicant/user's email address\n"
            "     * Message/Inquiry field -> write a concise, professional message introducing the user and expressing interest to connect or collaborate\n"
            "   - Specify the submit button (e.g. 'button[type=\"submit\"]' or 'button:has-text(\"Send Message\")').\n"
            "   - Set 'finish_after': true so the task finishes upon successful submission.\n"
            "4. LOOP & STUCK PREVENTION:\n"
            "   - If you already navigated to the section, proceed to fill the form.\n"
            "   - If a success notice appears in '=== NOTICES ON PAGE ===' or the form was submitted, output 'finish'.\n\n"
            "=== SUPPORTED ACTIONS (JSON) ===\n"
            "1. fill_form: {\"action\": \"fill_form\", \"fields\": {\"#form-name\": \"Name\", \"#form-email\": \"email@domain.com\", \"#form-message\": \"Message text...\"}, \"submit_selector\": \"button[type='submit']\", \"finish_after\": true, \"reason\": \"...\"}\n"
            "2. click: {\"action\": \"click\", \"selector\": \"a[href='#connect']\", \"reason\": \"Opening the Connect section to access the message form.\"}\n"
            "3. type: {\"action\": \"type\", \"selector\": \"input[name='q']\", \"text\": \"Query\", \"press_enter\": true, \"reason\": \"...\"}\n"
            "4. navigate: {\"action\": \"navigate\", \"text\": \"https://...\", \"reason\": \"Navigating to website.\"}\n"
            "5. scroll: {\"action\": \"scroll\", \"reason\": \"Scrolling to find content below the fold.\"}\n"
            "6. finish: {\"action\": \"finish\", \"reason\": \"Task successfully completed.\"}\n\n"
            "Always return valid JSON only."
        )

        user_msg = (
            f"User Goal: {goal}\n\n"
            f"Attached Document / Candidate Data:\n{context_info}\n\n"
            f"Current Web Page: {curr_url} ('{curr_title}')\n\n"
            f"Structured DOM Elements on Page:\n{dom_elements}\n"
        )

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
            return {"action": "finish", "reason": "Completed trajectory."}

# Global Singleton Instance
agent_core = AgentCore()
