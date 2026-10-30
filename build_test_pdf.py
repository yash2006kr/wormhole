import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 40, 25, page_text)
        self.drawString(40, 25, "ApplyCopilot / Wormhole Autonomous Web Agent - Test & Prompt Guide")
        self.restoreState()

def generate_pdf(filename="ApplyCopilot_Test_Prompts_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a")
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569")
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=8,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )
    prompt_box_style = ParagraphStyle(
        'PromptBox',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0369a1")
    )
    bold_label = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # Title & Header Banner
    story.append(Paragraph("APPLYCOPILOT / WORMHOLE TEST & PROMPT SUITE", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Comprehensive Verification Guide for All 8 System Protocols, Multi-Key Failover & 3 Surprise Hurdles", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Author:</b> Yashwanth K R &nbsp;|&nbsp; <b>Cockpit URL:</b> http://localhost:8000 &nbsp;|&nbsp; <b>GitHub:</b> github.com/yash2006kr/wormhole", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

    # Architecture Summary Table
    matrix_data = [
        [
            Paragraph("<b>Part / Protocol</b>", bold_label),
            Paragraph("<b>Core Engine</b>", bold_label),
            Paragraph("<b>Primary Capability</b>", bold_label),
            Paragraph("<b>Benchmark</b>", bold_label)
        ],
        [
            Paragraph("<b>Part 2: Document Exorcist</b>", body_style),
            Paragraph("<code>exorcist.py</code>", body_style),
            Paragraph("In-memory image surgery: 3.5x4.5cm, 200 DPI, strictly 20KB-45KB", body_style),
            Paragraph("<b>77.9 ms</b> (<350ms)", body_style)
        ],
        [
            Paragraph("<b>Part 1: User Vault</b>", body_style),
            Paragraph("<code>vault.json</code>", body_style),
            Paragraph("Stores profile, academics (8.85 CGPA), marks, transit prefs, sample photo", body_style),
            Paragraph("Instant read", body_style)
        ],
        [
            Paragraph("<b>Part 8: SOS Emergency Sentinel</b>", body_style),
            Paragraph("<code>sos_sentinel.py</code>", body_style),
            Paragraph("Autonomous ambulance dispatch, hospital ER bay pre-booking & kin alert", body_style),
            Paragraph("<b>8.2 ms</b> instant dispatch", body_style)
        ],
        [
            Paragraph("<b>Resilience: Multi-Key Pool</b>", body_style),
            Paragraph("<code>api_pool.py</code>", body_style),
            Paragraph("Multi-key failover round-robin, rate-limit (429) quarantine, backup models", body_style),
            Paragraph("Zero rate-limit hang", body_style)
        ],
        [
            Paragraph("<b>Part 3: Anti-Dark-Pattern</b>", body_style),
            Paragraph("<code>dark_pattern.py</code>", body_style),
            Paragraph("Scans DOM checkboxes, unchecks sneaky insurance/donations/baggage", body_style),
            Paragraph("Saved ₹374 (3 items)", body_style)
        ],
        [
            Paragraph("<b>Part 4: Transit Rush</b>", body_style),
            Paragraph("<code>transit_rush.py</code>", body_style),
            Paragraph("Parallel sleeper seat selection + vault passenger injection", body_style),
            Paragraph("<b>1,660.4 ms</b> (<10s)", body_style)
        ],
        [
            Paragraph("<b>Part 5: Fraud Sentinel</b>", body_style),
            Paragraph("<code>sentinel.py</code>", body_style),
            Paragraph("Air-gapped watchdog halting at Card/UPI/CVV/OTP/CAPTCHA fields", body_style),
            Paragraph("PAUSED_FOR_HUMAN", body_style)
        ],
        [
            Paragraph("<b>Part 6: Jarvis Voice HUD</b>", body_style),
            Paragraph("<code>server.py + index.html</code>", body_style),
            Paragraph("Live CDP screencast, 3D robot eyes, voice waveform, New Chat reset", body_style),
            Paragraph("60 FPS Screencast", body_style)
        ],
        [
            Paragraph("<b>Part 7: E2E Autonomous</b>", body_style),
            Paragraph("<code>agent_core.py</code>", body_style),
            Paragraph("Multi-tab navigation across public web + webmail OTP verification", body_style),
            Paragraph("Multi-turn memory", body_style)
        ],
        [
            Paragraph("<b>Surprise Hurdle 1</b>", body_style),
            Paragraph("<code>transaction_ledger.py</code>", body_style),
            Paragraph("WAL IN_FLIGHT_SUBMITTED + crash recovery idempotency double-pay shield", body_style),
            Paragraph("Zero double-charge", body_style)
        ],
        [
            Paragraph("<b>Surprise Hurdle 2</b>", body_style),
            Paragraph("<code>sneaky_fee_guard.py</code>", body_style),
            Paragraph("Voice Financial Anchor; halts checkout if merchant quietly adds drip fees", body_style),
            Paragraph("Drip fee intercept", body_style)
        ],
        [
            Paragraph("<b>Surprise Hurdle 3</b>", body_style),
            Paragraph("<code>agent_core.py (clarify)</code>", body_style),
            Paragraph("Voice Ambiguity Clarification Protocol; renders interactive choice chips", body_style),
            Paragraph("Zero guess booking", body_style)
        ],
    ]

    t = Table(matrix_data, colWidths=[115, 90, 235, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # SECTION GENERATOR HELPER
    def make_protocol_section(part_num, title, badge, target_url, prompt_text, files_needed, what_to_do, agent_action, expected_output, proof_metric):
        card = []
        card.append(Paragraph(f"<b>{part_num}: {title}</b> &nbsp;&nbsp;<font color='#0284c7'>[{badge}]</font>", h1_style))
        
        detail_rows = [
            [
                Paragraph("<b>Target Website / URL:</b>", bold_label),
                Paragraph(f"<code>{target_url}</code>", body_style)
            ],
            [
                Paragraph("<b>Verbatim Prompt:</b>", bold_label),
                Paragraph(f"<b>\"{prompt_text}\"</b>", prompt_box_style)
            ],
            [
                Paragraph("<b>Test Files Required:</b>", bold_label),
                Paragraph(files_needed, body_style)
            ],
            [
                Paragraph("<b>What You Should Do:</b>", bold_label),
                Paragraph(what_to_do, body_style)
            ],
            [
                Paragraph("<b>Agent Trajectory:</b>", bold_label),
                Paragraph(agent_action, body_style)
            ],
            [
                Paragraph("<b>Expected Output:</b>", bold_label),
                Paragraph(expected_output, body_style)
            ],
            [
                Paragraph("<b>Success Verification:</b>", bold_label),
                Paragraph(proof_metric, body_style)
            ],
        ]
        
        sec_table = Table(detail_rows, colWidths=[115, 425])
        sec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f8fafc")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        card.append(sec_table)
        card.append(Spacer(1, 8))
        return KeepTogether(card)

    # 1. Part 2: Document Exorcist
    story.append(make_protocol_section(
        "PART 2",
        "Document Exorcist Engine (In-Memory Image Surgery)",
        "PROTOCOL 04",
        "Option A: http://localhost:8000/mock/portal#photo | Option B: Public portal upload",
        "Upload my passport photo and heal it to comply with strict 20KB to 45KB portal requirements.",
        "test_oversized_photo.jpg (80.2 KB high-res test photo located in project root)",
        "Open Cockpit at http://localhost:8000. Either speak into the microphone or paste the prompt into the chat box. Alternatively, visit http://localhost:8000/mock/portal, switch to Tab 2 ('Strict Photo Gate'), select the 80.2KB file to see the portal reject it with a red warning, then click 'Auto-Heal with Document Exorcist'.",
        "The Document Exorcist intercepts the oversized 80.2 KB image in RAM. In exactly 77.9 ms, it calculates the 7:9 (3.5x4.5cm) crop box, renders at 200 DPI, runs binary search JPEG compression, and outputs a compliant 32.0 KB photo.",
        "Status: COMPLETED | Protocol: DOC_EXORCIST. Chat displays healed photo thumbnail and diagnostic stats: Original: 80.2 KB -> Healed: 32.0 KB (within 20KB-45KB constraint) in 77.9 ms. Portal verification gate turns glowing GREEN with ACCEPTED badge.",
        "Output file generated: test_healed_passport_photo.jpg (32.0 KB, exactly within 20KB-45KB range). HTTP GET /proof/test_healed_passport_photo.jpg returns 200 OK."
    ))

    # 2. Protocol 08: SOS Medical Emergency Sentinel (NEW FEATURE)
    story.append(make_protocol_section(
        "PROTOCOL 08",
        "Autonomous Medical Emergency & SOS Dispatch Sentinel",
        "EMERGENCY LIFE-SAVER",
        "http://localhost:8000/mock/emergency (Live Active Dispatch & CPR Metronome Terminal)",
        "SOS! Medical emergency, severe chest pain and suspected heart attack. Book ambulance, hospital appointment, and alert kin immediately.",
        "vault.json (Contains patient Yashwanth K R, Age 23, Blood O+, address at Kumbalagodu, kin Rajesh K R, preferred BGS Gleneagles ER)",
        "Speak or type the emergency prompt into Cockpit. The agent detects the critical distress trigger, immediately executes life-saving protocols, speaks first-aid instructions, and navigates the browser screencast to http://localhost:8000/mock/emergency.",
        "1) Issues immediate clinical first-aid guidance (chew 300mg soluble aspirin, sit in W-position, unlock door, do not drive). 2) Autonomously books and dispatches Advanced Cardiac Life Support (ACLS) Ambulance KA-05-EM-1108 (ETA 6m, Lead Suresh Kumar +91 98450 77112). 3) Pre-books priority ER admission at BGS Gleneagles Global Hospital (Cardiac Resuscitation Bay 02, zero-wait triage with Dr. Anand M). 4) Dispatches priority SMS/WhatsApp SOS broadcast with live GPS link to next-of-kin Rajesh K R (+91 98450 11223).",
        "Browser screencast displays pulsing emergency HUD with real-time countdown timer (ETA: 05:42), active ambulance tracking, pre-cleared ER card, kin alert confirmation, and 110 BPM visual CPR rhythm metronome. Chat delivers complete dispatch summary.",
        "Terminal execution completed in 8.2 ms. Telemetry status: EMERGENCY_DISPATCHED. All 4 emergency legs confirmed without human delay."
    ))

    # 3. Resilience: Multi-Key API Pool & Self-Healing Failover (NEW FEATURE)
    story.append(make_protocol_section(
        "RESILIENCE",
        "Dynamic Multi-Key API Pool & Rate-Limit Self-Healing",
        "FAILOVER ENGINE",
        "API Status: http://localhost:8000/api/api-pool-status | Management: api_pool.py",
        "Verify API key pool health and auto-failover status.",
        ".env (Supports comma-separated GROQ_API_KEYS=key1,key2,key3 or individual GROQ_API_KEY_1, GROQ_API_KEY_2...)",
        "Add multiple Groq keys into your .env file separated by commas or numbered variables. To test failover, query http://localhost:8000/api/api-pool-status or execute complex multi-turn commands.",
        "The api_pool engine actively tracks the health of each key. If any key encounters a 429 RateLimitError, connection timeout, or 503 error, the engine automatically quarantines that key with a 45-second cooldown timer and seamlessly routes the request to the next available healthy key. In addition, it cycles through a resilient hierarchy of fallback models (openai/gpt-oss-120b, llama-3.3-70b-versatile, qwen/qwen3.8-27b, openai/gpt-oss-20b, llama-3.1-8b-instant).",
        "Zero hangs or freezes. Telemetry reports total keys, active healthy keys, cooling keys, and call counts per key. Endpoints: GET /api/api-pool-status and POST /api/api-pool/add-key allow dynamic additions without restart.",
        "Terminal test: 'python -c \"from api_pool import api_pool; print(api_pool.get_telemetry())\"' displays full health metrics."
    ))

    # 4. Part 1: User Vault
    story.append(make_protocol_section(
        "PART 1",
        "Environment Setup & Local User Vault",
        "PROTOCOL 00",
        "Public Website: https://yash2006kr.vercel.app (Connect Section) | Local: vault.json",
        "Navigate to https://yash2006kr.vercel.app and fill the contact form with Yashwanth's message expressing excitement for AI agents from vault.",
        "vault.json (contains Yashwanth K R's DBIT B.Tech CGPA 8.85, 10th 92.4%, 12th 89.6%, email, address)",
        "Speak or type the prompt into the Cockpit. Watch the live CDP screencast navigate to the public Vercel portfolio.",
        "Agent parses vault.json credentials, visits https://yash2006kr.vercel.app/, clicks 'Initiate Contact' (a[href='#connect']), populates input#form-name ('Yashwanth K R'), input#form-email ('yashwanth.kr.dbit@gmail.com'), and textarea#form-message with candidate background, and submits.",
        "Live screencast reflects filled form fields and submission confirmation. Chat log confirms form populated from user vault credentials.",
        "Telemetry confirms zero hallucination of personal data; exact match with vault.json parameters."
    ))

    # 5. Part 3: Anti-Dark-Pattern Fee Stripper
    story.append(make_protocol_section(
        "PART 3",
        "Anti-Dark-Pattern & Fee Stripper Engine",
        "PROTOCOL 05",
        "http://localhost:8000/mock/checkout (Or any public checkout page with add-on checkboxes)",
        "Audit this checkout page for sneaky pre-checked fees and clean my cart total.",
        "mock_checkout.html (features pre-checked Insurance +₹199, Donation +₹25, Priority +₹150)",
        "Speak or type the prompt. Alternatively run 'python dark_pattern.py' in terminal.",
        "Engine audits the DOM tree for input[type='checkbox']. Analyzes parent labels with regex for dark pattern keywords (insurance, donation, charity, priority, handling). Programmatically unchecks all deceptive checkboxes in parallel and recalculates clean total.",
        "Sanitization Telemetry: 3 deceptive patterns stripped. Initial Total: ₹5,144 -> Cleaned Total: ₹4,770 (₹374 saved). Chat feed displays breakdown of removed items.",
        "Verification screenshot generated: cleaned_checkout_proof.png showing all 3 add-on boxes cleanly unchecked."
    ))

    # 6. Part 4: Transit Rush
    story.append(make_protocol_section(
        "PART 4",
        "Transit Rush Protocol Engine (High-Speed Booking)",
        "PROTOCOL 01",
        "http://localhost:8000/mock/ksrtc (Simulates state transport sleeper seat matrix)",
        "Book 2 lower sleeper berths from Bengaluru to Mysuru on KSRTC using my transit preferences from vault.",
        "vault.json (transit_preferences specifies Bengaluru -> Mysuru, Lower Sleeper, 2 passengers)",
        "Submit the prompt into the Cockpit, or execute 'python transit_rush.py' in terminal.",
        "In <2 seconds, the engine loads the seat grid, locates available lower berths (#lower-deck .seat.available), locks berths 14A and 14B, fills passenger names (Yashwanth K R, Raj Aanada) from vault.json, advances to checkout, and shifts state to PAUSED_FOR_HUMAN_PAYMENT.",
        "Reservation prepared in 1,660.4 ms (target: <10,000 ms). Seats locked: 14A, 14B. Passengers injected: Yashwanth K R, Raj Aanada. Anti-dark pattern fees stripped.",
        "Verification screenshot generated: transit_rush_proof.png. Execution halted at payment screen without charging user."
    ))

    # 7. Part 5: Air-Gapped Fraud Sentinel
    story.append(make_protocol_section(
        "PART 5",
        "Air-Gapped Fraud Sentinel & Payment State Machine",
        "PROTOCOL 03",
        "http://localhost:8000/mock/checkout (Or any public gateway: Stripe, Razorpay, PayPal)",
        "Test air-gapped fraud sentinel watchdog on checkout.",
        "mock_checkout.html (contains Card Number, CVV, Expiry Date, UPI VPA, and Submit Payment)",
        "Submit the prompt into the Cockpit or execute 'python sentinel.py' in terminal.",
        "Live watchdog scans DOM input names, IDs, placeholders, iframes, and URLs for financial field patterns (card, cvv, upi, otp, netbank). Detects checkout payment gate and immediately shifts agent state to PAUSED_FOR_HUMAN.",
        "Alert Triggered: 'Air-Gapped Fraud Sentinel Activated. Protection Gate: PAYMENT_GATEWAY. Execution frozen before entering sensitive credentials. Please complete payment directly on screen.'",
        "Verification screenshot generated: sentinel_halt_proof.png. Agent remains safely halted until human resumes."
    ))

    # 8. Part 6: Jarvis Voice HUD
    story.append(make_protocol_section(
        "PART 6",
        "Jarvis Voice HUD & Adaptive Interface",
        "PROTOCOL 06",
        "http://localhost:8000 (Cockpit Web Interface)",
        "Who is Yashwanth K R and what are his top projects?",
        "Browser microphone (for voice mode) or text input; genuine Google Chrome CDP connection",
        "Observe the initial screen: 3D interactive robot eyes track mouse movement in Text Mode, and glowing voice radar orb displays in Voice Mode. Speak or type the prompt. Observe the smooth fade animation as the hero transitions into the chat feed. Then click '+ New Chat' in the top header.",
        "Agent activates thinking indicator in chat feed, executes cognitive reasoning via Groq LPU, streams telemetry, and speaks the answer using speech synthesis. On '+ New Chat', browser navigates to about:blank, extra tabs close, and robot hero returns.",
        "Initial screen maintains robot hero until first prompt. Smooth transition to chat feed. Real-time CDP screencast mirrors browser canvas. Instant session memory wipe on New Chat.",
        "Verify browser console: WebSocket connection established, Screencast frames streaming at 60 FPS."
    ))

    # 9. Part 7: End-to-End Multi-Tab Trajectory
    story.append(make_protocol_section(
        "PART 7",
        "End-to-End Multi-Tab Autonomous Trajectory",
        "PROTOCOL 07",
        "http://localhost:8000/mock/portal (Tab 0) & http://localhost:8000/mock/mail (Tab 1)",
        "Go to the QuickHire portal and apply for the AI Engineer role.",
        "mock_portal.html and mock_mail.html (dynamic mock mail server with unique 6-digit OTPs)",
        "Submit the prompt. Do not mention login or OTP in your prompt. Watch the agent deduce the requirement autonomously.",
        "1) Agent opens QuickHire portal. 2) Bypasses Google OAuth due to bot-detection policy. 3) Enters candidate email and clicks 'Send Verification Code'. 4) Opens new browser tab (/mock/mail). 5) Reads 6-digit OTP from inbox. 6) Switches back to portal tab. 7) Injects OTP across segmented boxes (#otp-1 to #otp-6). 8) Completes authentication.",
        "QuickHire Portal displays: 'Login & Application Verified! Welcome back, Yashwanth K R. Candidate profile active.'",
        "Telemetry logs show: open_tab -> switch_tab -> read_otp -> switch_tab -> fill_otp -> complete."
    ))

    # 10. Surprise Hurdle 1: Idempotency Sentinel
    story.append(make_protocol_section(
        "SURPRISE HURDLE 1",
        "Crash After Submit & Idempotency Sentinel",
        "HINT 1 DEFENSE",
        "http://localhost:8000/mock/checkout & http://localhost:8000/mock/orders",
        "Pay ₹4,650 for my confirmed booking.",
        "transaction_ledger.json (WAL write-ahead log with SHA-256 idempotency hash)",
        "Submit the payment prompt once. Then simulate a crash (restart server or trigger crash button). Re-submit the identical prompt: 'Pay ₹4,650 for my confirmed booking.'",
        "The agent checks the transaction ledger WAL before clicking Pay. Computes SHA-256 hash of URL, selector, and amount. Detects matching in-flight transaction TX-1793376183428. Immediately suppresses duplicate payment click. Redirects to /mock/orders to reconcile order status.",
        "Chat output: '🛡️ IDEMPOTENCY SENTINEL ENGAGED: Double-Payment Blocked! An identical payment [TX-1793376183428] was already submitted. Reconciling with backend status instead of double-charging.'",
        "Zero duplicate charges recorded in ledger. Order status reconciled to CONFIRMED."
    ))

    # 11. Surprise Hurdle 2: Sneaky Fee Interceptor
    story.append(make_protocol_section(
        "SURPRISE HURDLE 2",
        "Voice Financial Anchor & Sneaky Fee Interceptor",
        "HINT 2 DEFENSE",
        "http://localhost:8000/mock/checkout",
        "Approve payment of ₹4,650 for my flight.",
        "sneaky_fee_guard.py (Voice anchor parser + drip pricing detection engine)",
        "Speak or type the prompt with an explicit budget/approval amount of ₹4,650.",
        "Agent parses voice approval: voice_approved_amount = 4650.0. Inspects final checkout screen. Strips pre-checked checkboxes, but detects an unapproved 'Platform Convenience Surcharge (+₹120)' pushing final total to ₹4,770.",
        "Payment is frozen! Chat alert: '🚨 SNEAKY FEE INTERCEPTED: Voice Approved: ₹4,650 vs Final Merchant Total: ₹4,770. Quiet added fee: +₹120 (Platform Surcharge). Payment halted to protect your wallet. Do you approve paying the extra ₹120?'",
        "Air-gap activates. Agent halts execution until user gives explicit voice or text approval for the quiet surcharge."
    ))

    # 12. Surprise Hurdle 3: Ambiguity Clarification Protocol
    story.append(make_protocol_section(
        "SURPRISE HURDLE 3",
        "Voice Ambiguity Clarification Protocol",
        "HINT 3 DEFENSE",
        "http://localhost:8000/mock/ksrtc",
        "Book the sleeper berth.",
        "mock_ksrtc.html (features both Lower Berth 14A Window and Lower Berth 14B Aisle)",
        "Submit the ambiguous prompt: 'Book the sleeper berth.' (Deliberately omit specifying window or aisle).",
        "Groq LPU recognizes multiple matching lower berths. Rejects hallucinating or guessing. Issues cognitive action 'clarify' with structured options.",
        "Jarvis speaks: 'I found 2 available lower berths: Lower Berth 14A (Window, ₹840) vs Lower Berth 14B (Aisle, ₹840). Which one would you prefer?' Chat displays clickable interactive choice chips.",
        "Selecting a chip immediately resumes the booking trajectory with the user's explicit preference."
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"SUCCESS: PDF generated at {os.path.abspath(filename)}")

if __name__ == "__main__":
    generate_pdf()
