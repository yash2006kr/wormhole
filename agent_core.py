"""
ApplyCopilot (Wormhole) Real-Time Agentic Web Engine
Features:
- Live CDP Screencast streaming to WebSockets with Wheel Scrolling & Mouse Movement
- DOM-Aware Autonomous Reasoning via Groq LPU (openai/gpt-oss-20b)
- Multi-Input Form Filling & Rich ContentEditable / Job Description Editor Support
- In-Memory Multi-Turn Session Memory (remembers resume & chat context across turns until New Chat)
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
        
        # Multi-Turn Session Memory (preserved across turns until user creates New Chat)
        self.session_history = []     # List of {"role": "user"|"agent", "text": "...", "time": "..."}
        self.session_files = []       # List of attached file dicts
        self.session_context = ""     # Accumulated text from resumes & attached documents
        
        self.interrupt_event = asyncio.Event()
        self.resume_event = asyncio.Event()
        self.interrupt_resolution = None # "RESUME", "REPLAN", "HANDOVER"
        self.new_instruction = None
        
        self.active_websockets = set()
        self.execution_task = None
        self.action_history = []
        self.viewport_size = {"width": 1280, "height": 800}

    async def reset_session(self):
        """Clears in-memory session history, uploaded files, and context when user clicks New Chat. Clears live browser to null."""
        print("[AGENT CORE] Resetting session memory for New Chat. Navigating browser to about:blank...")
        self.session_history = []
        self.session_files = []
        self.session_context = ""
        self.current_goal = None
        self.current_context = ""
        self.attached_files = []
        self.action_history = []
        self.state = "IDLE"
        if self.execution_task and not self.execution_task.done():
            self.execution_task.cancel()

        # Clear live webpage to null (about:blank)
        if self.page:
            try:
                await self.page.goto("about:blank", wait_until="domcontentloaded", timeout=8000)
                await self.broadcast({
                    "type": "URL_UPDATE",
                    "url": "",
                    "title": ""
                })
            except Exception as e:
                print(f"[!] Browser clear error on reset: {e}")

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
                await self.cdp.send("Input.dispatchMouseEvent", {
                    "type": "mouseMoved",
                    "x": actual_x,
                    "y": actual_y
                })
                await asyncio.sleep(0.02)
                await self.cdp.send("Input.dispatchMouseEvent", {
                    "type": "mousePressed",
                    "x": actual_x,
                    "y": actual_y,
                    "button": "left",
                    "clickCount": 1
                })
                await asyncio.sleep(0.04)
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
        """Extracts structured DOM: headings, navigation tabs, page & section text, forms, editors, buttons, and notices."""
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

                const cleanText = (t) => (t || '').replace(/\\s+/g, ' ').trim().slice(0, 100);

                // 1. Page Title & Headings (to understand context & topic)
                const headings = [];
                document.querySelectorAll('h1, h2, h3, h4').forEach((h, i) => {
                    if (i < 12) {
                        const txt = (h.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 90);
                        if (txt) headings.push(`${h.tagName}: "${txt}"`);
                    }
                });

                // 2. Navigation items (Header links, Nav links, Section tabs, Anchor links)
                const navItems = [];
                document.querySelectorAll('nav a, header a, a[href^="#"], [role="tab"], [data-page], [data-section], a.nav-link, a').forEach((el, i) => {
                    if (navItems.length < 25) {
                        const txt = cleanText(el.innerText || el.getAttribute('aria-label') || el.getAttribute('title'));
                        const href = el.getAttribute('href') || el.getAttribute('data-page') || '';
                        const id = el.id ? '#' + el.id : '';
                        if (txt && (href.startsWith('#') || href.includes('about') || href.includes('creation') || href.includes('project') || href.includes('skill') || href.includes('timeline') || href.includes('connect') || href.includes('contact') || href.includes('apply') || navItems.length < 8)) {
                            navItems.push(`NAV: a${id}[href="${href}"] text="${txt}" [${isVisible(el) ? 'visible' : 'hidden'}]`);
                        }
                    }
                });

                // 3. Page & Section Text Content (Crucial for Q&A, About details, Bio, Projects, Summaries)
                const sectionTexts = [];
                const knownSectionKeywords = ['about', 'bio', 'intro', 'summary', 'creations', 'projects', 'skills', 'experience', 'timeline', 'connect', 'contact', 'faq', 'overview'];
                knownSectionKeywords.forEach(k => {
                    const els = document.querySelectorAll(`section#${k}, #${k}, [data-section*="${k}"], [data-page*="${k}"], .${k}, [id*="${k}"]`);
                    els.forEach(el => {
                        const raw = (el.innerText || '').replace(/\\s+/g, ' ').trim();
                        if (raw.length > 25 && !sectionTexts.some(s => s.slice(0, 40) === raw.slice(0, 40))) {
                            sectionTexts.push(`[SECTION: #${el.id || k}]\\n` + raw.slice(0, 1600));
                        }
                    });
                });

                // Also extract visible paragraphs from active section or article
                const paragraphs = [];
                document.querySelectorAll('section.active p, .page-view.active p, main p, article p, p').forEach(p => {
                    if (paragraphs.length < 10) {
                        const pt = (p.innerText || '').replace(/\\s+/g, ' ').trim();
                        if (pt.length > 20 && isVisible(p) && !paragraphs.some(exist => exist.slice(0, 30) === pt.slice(0, 30))) {
                            paragraphs.push(pt.slice(0, 300));
                        }
                    }
                });

                // 4. Inputs, Textareas, Selects, and Rich ContentEditable Textboxes (Indeed, LinkedIn, Quill, ProseMirror)
                const formFields = [];
                document.querySelectorAll('input:not([type="hidden"]), textarea, select, [contenteditable="true"], [role="textbox"]').forEach((el, i) => {
                    if (formFields.length < 30) {
                        const tag = el.tagName.toLowerCase();
                        const id = el.id ? '#' + el.id : '';
                        const name = el.name ? `[name="${el.name}"]` : '';
                        const type = el.type ? `[type="${el.type}"]` : '';
                        const isRich = el.getAttribute('contenteditable') === 'true' || el.getAttribute('role') === 'textbox';
                        const richBadge = isRich ? ' (RichTextEditor/ContentEditable)' : '';
                        
                        let placeholder = el.placeholder || el.getAttribute('data-placeholder') || el.getAttribute('aria-placeholder') || '';
                        const placeholderStr = placeholder ? `placeholder="${cleanText(placeholder)}"` : '';
                        
                        // Associated Label / Heading
                        let labelText = el.getAttribute('aria-label') || '';
                        if (!labelText && el.id) {
                            const lbl = document.querySelector(`label[for="${el.id}"]`);
                            if (lbl) labelText = cleanText(lbl.innerText);
                        }
                        if (!labelText && el.closest('label')) {
                            labelText = cleanText(el.closest('label').innerText);
                        }
                        if (!labelText) {
                            const prev = el.previousElementSibling;
                            if (prev && (prev.tagName.startsWith('H') || prev.tagName === 'LABEL' || (prev.className && String(prev.className).includes('label')))) {
                                labelText = cleanText(prev.innerText);
                            }
                        }
                        const labelStr = labelText ? `label="${labelText}"` : '';
                        const vis = isVisible(el) ? 'visible' : 'hidden';
                        
                        let selectorHint = tag + id + name + type;
                        if (isRich && !id && !name) {
                            const testId = el.getAttribute('data-testid');
                            if (testId) selectorHint += `[data-testid="${testId}"]`;
                            else if (el.className) selectorHint += '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.');
                            else selectorHint += '[contenteditable="true"]';
                        }
                        
                        formFields.push(`FIELD: ${selectorHint}${richBadge} ${placeholderStr} ${labelStr} [${vis}]`.replace(/\\s+/g, ' ').trim());
                    }
                });

                // 5. Buttons & Interactive Clickables
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

                // 6. Active confirmation / Success / Error notices
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
                if (sectionTexts.length) output.push("=== PAGE & SECTION TEXT CONTENT ===\\n" + sectionTexts.join("\\n\\n"));
                else if (paragraphs.length) output.push("=== PAGE & SECTION TEXT CONTENT ===\\n" + paragraphs.join("\\n\\n"));
                if (formFields.length) output.push("=== FORM INPUT FIELDS & EDITORS ===\\n" + formFields.join("\\n"));
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

    async def _fill_any_input(self, selector, value):
        """Fills standard inputs, textareas, and rich contenteditable textboxes (Indeed, LinkedIn)."""
        if not self.page:
            return False

        loc = self.page.locator(selector).first
        if await loc.count() == 0:
            return False

        try:
            await loc.scroll_into_view_if_needed(timeout=2500)
            await loc.click(timeout=2500)
            await asyncio.sleep(0.15)

            # Check if element is a rich text editor or contenteditable
            is_rich = await loc.evaluate("""
                el => el.isContentEditable || 
                      el.getAttribute('contenteditable') === 'true' || 
                      el.getAttribute('role') === 'textbox' || 
                      el.classList.contains('ql-editor') ||
                      el.classList.contains('public-DraftEditor-content')
            """)

            if is_rich:
                print(f"  -> Filling rich contenteditable editor '{selector}'...")
                # Method 1: document.execCommand('insertHTML')
                await loc.evaluate("""
                    (el, val) => {
                        el.focus();
                        const htmlContent = val.split('\\n').map(p => p.trim() ? `<p>${p}</p>` : '<p><br></p>').join('');
                        document.execCommand('selectAll', false, null);
                        document.execCommand('insertHTML', false, htmlContent);
                        if (!el.innerText.trim()) {
                            el.innerHTML = htmlContent;
                        }
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                """, value)
                await asyncio.sleep(0.3)

                # Method 2: If still empty, use direct keyboard typing
                content_len = await loc.evaluate("el => el.innerText.trim().length")
                if content_len < 5:
                    await loc.focus()
                    await self.page.keyboard.insert_text(value)
                return True
            else:
                # Standard input or textarea
                await loc.fill(value, timeout=4000)
                return True
        except Exception as e:
            print(f"  [!] Fill error on '{selector}': {e}")
            # Fallback to direct keyboard insert
            try:
                await loc.focus()
                await self.page.keyboard.insert_text(value)
                return True
            except Exception:
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

        # Record prompt in multi-turn session history
        timestamp = time.strftime("%H:%M:%S")
        self.session_history.append({
            "role": "user",
            "text": goal,
            "time": timestamp
        })

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
        elif any(k in goal.lower() for k in ["portfolio", "yash2006kr", "yashwanth"]) and self.page:
            # If user refers to portfolio website without typing the full URL
            target_initial_url = "https://yash2006kr.vercel.app/"
            try:
                curr_host = urlparse(self.page.url or "").netloc
                if "yash2006kr" not in curr_host:
                    print(f"[AGENT CORE] Portfolio keyword detected. Navigating directly to {target_initial_url}...")
                    await self.broadcast({
                        "type": "LOG",
                        "message": f"Navigating to portfolio website: {target_initial_url}"
                    })
                    await self.page.goto(target_initial_url, wait_until="domcontentloaded", timeout=25000)
                    await asyncio.sleep(1.5)
            except Exception as e:
                print(f"[!] Portfolio navigation error: {e}")
        
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

                # Extract live interactive DOM elements (including rich editors)
                dom_elements = await self._get_interactive_dom_elements()

                # Ask Groq LPU for next action (providing full multi-turn session context & resume data)
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

                        # 2. Fill each input field with robust rich-text & candidate fallbacks
                        for f_sel, f_val in fields.items():
                            val_str = str(f_val)
                            print(f"  -> Filling field '{f_sel}' with: {val_str[:40]}...")
                            filled = await self._fill_any_input(f_sel, val_str)

                            # Heuristic Fallback based on field intent
                            if not filled:
                                f_lower = f_sel.lower()
                                fallback_candidates = []
                                if "description" in f_lower or "desc" in f_lower or "job" in f_lower:
                                    fallback_candidates = [
                                        "div[contenteditable='true']",
                                        "[role='textbox']",
                                        ".ql-editor",
                                        "textarea[name*='description' i]",
                                        "textarea[id*='description' i]",
                                        "div[aria-label*='description' i]",
                                        "textarea"
                                    ]
                                elif "name" in f_lower:
                                    fallback_candidates = ["#form-name", "input[name='name']", "input[placeholder*='name' i]", "input[type='text']"]
                                elif "email" in f_lower:
                                    fallback_candidates = ["#form-email", "input[type='email']", "input[name='email']", "input[placeholder*='email' i]"]
                                elif "message" in f_lower or "comment" in f_lower or "body" in f_lower:
                                    fallback_candidates = ["#form-message", "textarea[name='message']", "textarea", "div[contenteditable='true']"]

                                for cand in fallback_candidates:
                                    if await self._fill_any_input(cand, val_str):
                                        filled = True
                                        print(f"     [Fallback Success] Field filled via candidate '{cand}'")
                                        break

                            await asyncio.sleep(0.3)

                        # 3. Submit form if requested
                        submit_sel = action.get("submit_selector")
                        if submit_sel:
                            print(f"  -> Submitting form: {submit_sel}")
                            submitted = await self._smart_click(submit_sel)
                            if not submitted:
                                for s_cand in ["button:has-text('Send Message')", "button:has-text('Submit')", "button:has-text('Post')", "button[type='submit']"]:
                                    if await self._smart_click(s_cand):
                                        break
                        
                        await asyncio.sleep(1.5)

                        if action.get("finish_after", True):
                            print(f"  -> Form Complete: {reason}")
                            timestamp = time.strftime("%H:%M:%S")
                            self.session_history.append({
                                "role": "agent",
                                "text": f"Successfully filled form: {reason}",
                                "time": timestamp
                            })
                            await self.broadcast({"type": "COMPLETE", "reason": f"Form populated: {reason}", "has_chat_response": True})
                            break

                    elif action_type == "type":
                        target_selector = selector or "input, textarea, div[contenteditable='true']"
                        print(f"  -> Typing into '{target_selector}'...")
                        typed = await self._fill_any_input(target_selector, text_val)
                        if not typed:
                            # Try general contenteditable or input
                            for cand in ["[contenteditable='true']", "[role='textbox']", "textarea", "input[type='text']"]:
                                if await self._fill_any_input(cand, text_val):
                                    break
                        if action.get("press_enter"):
                            await self.page.keyboard.press("Enter")
                        await asyncio.sleep(1)

                    elif action_type == "click":
                        raw_sel = selector or text_val
                        print(f"  -> Clicking element: {raw_sel}")
                        await self._smart_click(raw_sel, text=text_val)
                        await asyncio.sleep(1.5)

                    elif action_type == "scroll":
                        print("  -> Scrolling down page...")
                        await self.page.evaluate("window.scrollBy(0, 600)")
                        await asyncio.sleep(0.8)

                    elif action_type in ["respond", "answer", "reply"]:
                        msg_text = action.get("message") or action.get("text") or action.get("response") or reason
                        print(f"  -> Agent Answering User in Chat:\n{msg_text}\n")
                        
                        # Record response in session memory
                        timestamp = time.strftime("%H:%M:%S")
                        self.session_history.append({
                            "role": "agent",
                            "text": msg_text,
                            "time": timestamp
                        })

                        # Broadcast answer to chat feed
                        await self.broadcast({
                            "type": "CHAT_RESPONSE",
                            "text": msg_text,
                            "reason": reason
                        })
                        
                        await asyncio.sleep(0.5)
                        if action.get("finish", True):
                            await self.broadcast({
                                "type": "COMPLETE",
                                "reason": reason,
                                "has_chat_response": True
                            })
                            break

                    elif action_type == "finish":
                        msg_text = action.get("message") or action.get("response") or reason or "Task completed successfully."
                        timestamp = time.strftime("%H:%M:%S")
                        self.session_history.append({
                            "role": "agent",
                            "text": msg_text,
                            "time": timestamp
                        })
                        await self.broadcast({
                            "type": "CHAT_RESPONSE",
                            "text": msg_text,
                            "reason": reason
                        })

                        print(f"  -> Task Complete: {reason}")
                        await self.broadcast({"type": "COMPLETE", "reason": reason, "has_chat_response": True})
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
        """Queries Groq LPU with cognitive policy, DOM context, multi-turn history, and resume data."""
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
            "You are Jarvis-Wormhole, an elite autonomous web navigation, form-filling, and web intelligence agent operating in an active multi-turn session.\n"
            "You MUST remember all previous user requests and your previous responses in this session. If the user asks a follow-up question (e.g. 'tell me more', 'what degree did you mention', 'add job description based on resume', 'change that', 'what else'), you must refer to and build upon the earlier conversation context.\n"
            "Your objective is to inspect the active web page, understand the user's intent, and execute the exact right sequence of browser actions or directly formulate intelligent responses in chat.\n\n"
            "=== COGNITIVE PROTOCOLS ===\n"
            "1. INFORMATION EXTRACTION & CHAT Q&A PROTOCOL (HIGH PRIORITY):\n"
            "   - If the user asks a question, requests information, or asks to 'fetch about details', 'tell me about', 'what does the page say', 'summarize', 'who is...', 'what skills...', or 'give it in chat':\n"
            "     * Check the text provided under '=== PAGE & SECTION TEXT CONTENT ==='.\n"
            "     * If on an SPA where a relevant section (e.g. `a[href='#about']`, `text=About`) is not active, you can click it so it displays in the live screencast, OR if the section text is already present in '=== PAGE & SECTION TEXT CONTENT ===', synthesize the answer immediately!\n"
            "     * Synthesize a rich, professional, well-formatted response (using markdown bolding `**` and bullet points `•`) providing the exact details, philosophy, bio, skills, education, or facts extracted from the page.\n"
            "     * Return action 'respond' with your synthesized answer in the 'message' field:\n"
            "       {\"action\": \"respond\", \"message\": \"Here are the About details from the portfolio:\\n\\n• **Core Philosophy**: ...\\n• **Education & Background**: ...\\n• **Key Specialization**: ...\", \"reason\": \"Extracted requested details from the website and presented to the user in chat.\", \"finish\": true}\n\n"
            "2. JOB DESCRIPTION / RESUME SYNTHESIS PROTOCOL:\n"
            "   - If the user asks to 'add job description', 'describe the job', 'fill description', or 'post job', AND a candidate resume or profile is provided in context:\n"
            "     * Extract the candidate's core role, domain, technical stack, skills, and qualifications from the uploaded resume.\n"
            "     * Synthesize a comprehensive, professional, complete Job Description tailored to that role (including Role Overview, Key Responsibilities, Required Skills, and Qualifications).\n"
            "     * Target the Job Description editor on the page (e.g. `div[contenteditable='true']`, `[role='textbox']`, `textarea[name*='description' i]`, or `[aria-label*='Job description']`).\n"
            "     * Use action 'fill_form' or 'type' with the complete synthesized job description text to populate the field!\n\n"
            "3. CONTACT & APPLICATION PROTOCOL:\n"
            "   - If the user wants to contact, connect, or hire, map name, email, and message into the fields.\n"
            "   - In Single-Page Applications (SPAs), sections like Contact are often hidden until you click their navigation tab (e.g. `a[href='#connect']`).\n\n"
            "4. SUPPORTED ACTIONS (JSON):\n"
            "   1. respond: {\"action\": \"respond\", \"message\": \"synthesized comprehensive markdown text response to answer user question in chat\", \"reason\": \"...\", \"finish\": true}\n"
            "   2. fill_form: {\"action\": \"fill_form\", \"fields\": {\"field_selector\": \"text_content_to_insert\"}, \"submit_selector\": \"optional_btn\", \"finish_after\": true, \"reason\": \"...\"}\n"
            "   3. click: {\"action\": \"click\", \"selector\": \"a[href='#...'] or button_selector\", \"reason\": \"...\"}\n"
            "   4. type: {\"action\": \"type\", \"selector\": \"selector\", \"text\": \"string\", \"press_enter\": false, \"reason\": \"...\"}\n"
            "   5. navigate: {\"action\": \"navigate\", \"text\": \"https://...\", \"reason\": \"...\"}\n"
            "   6. scroll: {\"action\": \"scroll\", \"reason\": \"...\"}\n"
            "   7. finish: {\"action\": \"finish\", \"reason\": \"...\"}\n\n"
            "Always return valid JSON only."
        )

        # Construct true OpenAI / Groq multi-turn conversation messages array
        messages = [
            {"role": "system", "content": sys_prompt}
        ]

        # Add earlier turns in current session so the model natively remembers past prompts and answers
        if len(self.session_history) > 1:
            for item in self.session_history[:-1]:
                if item["role"] == "user":
                    messages.append({
                        "role": "user",
                        "content": f"[Previous User Request]: {item['text']}"
                    })
                elif item["role"] == "agent":
                    messages.append({
                        "role": "assistant",
                        "content": json.dumps({
                            "action": "respond",
                            "message": item["text"],
                            "reason": "Previous response in this conversation."
                        })
                    })

        # Current turn payload
        user_msg = (
            f"Current User Goal: {goal}\n\n"
            f"Active Web Page: {curr_url} ('{curr_title}')\n\n"
            f"Attached Document / Candidate Resume Data:\n{context_info}\n\n"
            f"Structured DOM Elements on Page:\n{dom_elements}\n\n"
            f"Note: Maintain continuous memory of all previous turns. If the user refers to past responses, earlier questions, or resume details, use that conversation history to answer or act accurately."
        )
        messages.append({"role": "user", "content": user_msg})

        # Try active models with fallback in case of rate limits
        models_to_try = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
        last_error = None
        for model_name in models_to_try:
            try:
                res = groq_client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                return json.loads(res.choices[0].message.content)
            except Exception as e:
                last_error = e
                print(f"[!] Groq decision error with model {model_name}: {e}")
                continue

        print(f"[!] All Groq models failed. Last error: {last_error}")
        return {"action": "finish", "reason": "Completed trajectory."}

# Global Singleton Instance
agent_core = AgentCore()
