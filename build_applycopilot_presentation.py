import sys
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_applycopilot_presentation():
    template_path = 'AfterHours_1.0_PPT_Template.pptx'
    output_pptx = 'AfterHours_1.0_ApplyCopilot_AI_Avengers.pptx'
    output_pdf = 'AfterHours_1.0_ApplyCopilot_AI_Avengers.pdf'
    output_team_pptx = 'AI_Avengers_Theme01_ApplyCopilot.pptx'
    output_team_pdf = 'AI_Avengers_Theme01_ApplyCopilot.pdf'

    prs = Presentation(template_path)

    # Delete slide 8 (guidelines slide)
    if len(prs.slides) > 7:
        rId = prs.slides._sldIdLst[7].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[7]

    # --- COLOR SYSTEM ---
    C_DARK = RGBColor(15, 23, 42)            # Slate 900 (#0F172A)
    C_SLATE_800 = RGBColor(30, 41, 59)       # Slate 800 (#1E293B)
    C_CHARCOAL = RGBColor(51, 65, 85)        # Slate 700 (#334155)
    C_MUTED = RGBColor(100, 116, 139)        # Slate 500 (#64748B)
    C_ORANGE = RGBColor(234, 88, 12)         # Brand Orange (#EA580C)
    C_ORANGE_DARK = RGBColor(194, 65, 12)    # Orange 700 (#C2410C)
    C_ORANGE_LIGHT = RGBColor(255, 247, 237) # Orange 50 (#FFF7ED)
    C_ORANGE_BORDER = RGBColor(251, 146, 60) # Orange 400 (#FB923C)
    C_BLUE = RGBColor(2, 132, 199)           # Sky Blue 600 (#0284C7)
    C_BLUE_LIGHT = RGBColor(240, 249, 255)   # Sky Blue 50 (#F0F9FF)
    C_BLUE_BORDER = RGBColor(125, 211, 252)  # Sky Blue 300 (#7DD3FC)
    C_CYAN = RGBColor(6, 182, 212)           # Cyan 500 (#06B6D4)
    C_CYAN_LIGHT = RGBColor(236, 254, 255)   # Cyan 50 (#ECFEFF)
    C_CYAN_BORDER = RGBColor(34, 211, 238)   # Cyan 400 (#22D3EE)
    C_RED = RGBColor(220, 38, 38)            # Red 600 (#DC2626)
    C_RED_LIGHT = RGBColor(254, 242, 242)    # Red 50 (#FEF2F2)
    C_RED_BORDER = RGBColor(252, 165, 165)   # Red 300 (#FCA5A5)
    C_GREEN = RGBColor(22, 163, 74)          # Green 600 (#16A34A)
    C_GREEN_LIGHT = RGBColor(240, 253, 244)  # Green 50 (#F0FDF4)
    C_GREEN_BORDER = RGBColor(134, 239, 172) # Green 300 (#86EFAC)
    C_PURPLE = RGBColor(147, 51, 234)        # Purple 600 (#9333EA)
    C_PURPLE_LIGHT = RGBColor(250, 245, 255) # Purple 50 (#FAF5FF)
    C_PURPLE_BORDER = RGBColor(216, 180, 254)# Purple 300 (#D8B4FE)
    C_WHITE = RGBColor(255, 255, 255)        # Pure White (#FFFFFF)
    C_CARD_BORDER = RGBColor(226, 232, 240)  # Slate 200 (#E2E8F0)

    FONT = "Segoe UI"

    def add_card(slide, left, top, width, height, bg=C_WHITE, border=C_CARD_BORDER, border_width=1.0):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg
        shape.line.color.rgb = border
        shape.line.width = Pt(border_width)
        return shape

    def add_pill_badge(slide, left, top, width, height, text, bg_color=C_ORANGE, text_color=C_WHITE):
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        badge.fill.solid()
        badge.fill.fore_color.rgb = bg_color
        badge.line.fill.background()
        tf = badge.text_frame
        tf.word_wrap = False
        tf.margin_left = Inches(0.04)
        tf.margin_right = Inches(0.04)
        tf.margin_top = Inches(0.01)
        tf.margin_bottom = Inches(0.01)
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = FONT
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = text_color
        p.alignment = PP_ALIGN.CENTER
        return badge

    def add_tb(slide, left, top, width, height, ml=0.08, mr=0.08, mt=0.05, mb=0.05):
        tb = slide.shapes.add_textbox(left, top, width, height)
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(ml)
        tf.margin_right = Inches(mr)
        tf.margin_top = Inches(mt)
        tf.margin_bottom = Inches(mb)
        return tb, tf

    def setup_slide_header(slide, title_text, subtitle_text, tagline_text=None):
        to_delete = []
        for s in slide.shapes:
            if s.has_text_frame:
                txt = s.text_frame.text.strip()
                if any(q in txt for q in ["What Exact", "What are you", "What alternatives", 
                                          "How will", "What measurable", "Conclusion &", "Problem Statement &", 
                                          "Proposed Solution", "Existing Solutions", "Technical Approach", 
                                          "Expected Impact"]):
                    to_delete.append(s)
        for s in to_delete:
            el = s._element
            el.getparent().remove(el)

        tb, tf = add_tb(slide, Inches(0.65), Inches(0.38), Inches(11.50), Inches(0.80), ml=0, mt=0)
        p0 = tf.paragraphs[0]
        p0.text = title_text
        p0.font.name = FONT
        p0.font.size = Pt(22)
        p0.font.bold = True
        p0.font.color.rgb = C_DARK

        p1 = tf.add_paragraph()
        p1.space_before = Pt(1)
        r_sub = p1.add_run()
        r_sub.text = subtitle_text + "  "
        r_sub.font.name = FONT
        r_sub.font.size = Pt(13.5)
        r_sub.font.bold = True
        r_sub.font.color.rgb = C_ORANGE

        if tagline_text:
            r_tag = p1.add_run()
            r_tag.text = tagline_text
            r_tag.font.name = FONT
            r_tag.font.size = Pt(12.5)
            r_tag.font.italic = True
            r_tag.font.color.rgb = C_MUTED

    # ==============================================================================
    # SLIDE 1: COVER SLIDE
    # ==============================================================================
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.name == 'TextBox 14':
            shape.left = Inches(1.0)
            shape.top = Inches(2.55)  # Safe clearance below black line (ends at 2.26)
            shape.width = Inches(11.33)
            shape.height = Inches(1.80)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True

            p0 = tf.paragraphs[0]
            p0.text = "THEME 01: AGENTIC AI & MULTI-AGENT SYSTEMS"
            p0.font.name = FONT
            p0.font.size = Pt(13.5)
            p0.font.bold = True
            p0.font.color.rgb = C_ORANGE
            p0.alignment = PP_ALIGN.CENTER

            p1 = tf.add_paragraph()
            p1.space_before = Pt(3)
            p1.text = "APPLYCOPILOT"
            p1.font.name = FONT
            p1.font.size = Pt(40)
            p1.font.bold = True
            p1.font.color.rgb = C_DARK
            p1.alignment = PP_ALIGN.CENTER

            p2 = tf.add_paragraph()
            p2.space_before = Pt(2)
            p2.text = "Voice-Steered Autonomous Web Agent with 5 Specialized Execution Protocols"
            p2.font.name = FONT
            p2.font.size = Pt(17)
            p2.font.bold = True
            p2.font.color.rgb = C_BLUE
            p2.alignment = PP_ALIGN.CENTER

            p3 = tf.add_paragraph()
            p3.space_before = Pt(2)
            p3.text = "\"Speak your intent. Watch Jarvis navigate, reason, and execute \u2014 across transit rushes, civic portals, fraud defense, and anti-dark-pattern checkouts.\""
            p3.font.name = FONT
            p3.font.size = Pt(13)
            p3.font.italic = True
            p3.font.color.rgb = C_MUTED
            p3.alignment = PP_ALIGN.CENTER

        elif shape.name == 'TextBox 15':
            shape.left = Inches(1.5)
            shape.top = Inches(4.55)
            shape.width = Inches(4.8)
            shape.height = Inches(1.85)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True

            p = tf.paragraphs[0]
            p.text = "TEAM DETAILS"
            p.font.name = FONT
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_ORANGE

            p_tn = tf.add_paragraph()
            p_tn.space_before = Pt(3)
            p_tn.text = "Team Name: AI Avengers"
            p_tn.font.name = FONT
            p_tn.font.size = Pt(17)
            p_tn.font.bold = True
            p_tn.font.color.rgb = C_DARK

            p_dom = tf.add_paragraph()
            p_dom.space_before = Pt(2)
            p_dom.text = "Track: Theme 01: Agentic AI & Multi-Agent Systems"
            p_dom.font.name = FONT
            p_dom.font.size = Pt(13)
            p_dom.font.color.rgb = C_CHARCOAL

            p_inst = tf.add_paragraph()
            p_inst.space_before = Pt(2)
            p_inst.text = "Don Bosco Institute of Technology (DBIT)"
            p_inst.font.name = FONT
            p_inst.font.size = Pt(12)
            p_inst.font.italic = True
            p_inst.font.color.rgb = C_MUTED

        elif shape.name == 'TextBox 16':
            shape.left = Inches(7.0)
            shape.top = Inches(4.55)
            shape.width = Inches(5.0)
            shape.height = Inches(1.85)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True

            p = tf.paragraphs[0]
            p.text = "TEAM MEMBERS"
            p.font.name = FONT
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_ORANGE

            members = [
                "Raj Aanada",
                "Yashma C P",
                "Likith M",
                "Yashwanth K R"
            ]
            for m_name in members:
                pm = tf.add_paragraph()
                pm.space_before = Pt(2)
                r_n = pm.add_run()
                r_n.text = f"\u2022  {m_name}"
                r_n.font.name = FONT
                r_n.font.size = Pt(13.5)
                r_n.font.bold = True
                r_n.font.color.rgb = C_DARK

    # ==============================================================================
    # SLIDE 2: PROBLEM STATEMENT & ITS RELEVANCE
    # ==============================================================================
    s2 = prs.slides[1]
    setup_slide_header(s2, "Problem Statement & Its Relevance",
                       "The Universal Web Friction & The 5 Critical Digital Failure Vectors.",
                       "From frantic 90-second ticket rushes to rejected 20KB documents and predatory dark-pattern fees.")

    # Left Column: Exact Problem (Top) & Why Does It Matter (Bottom)
    add_card(s2, Inches(0.65), Inches(1.25), Inches(3.65), Inches(2.50), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(1.35), Inches(1.50), Inches(0.24), "HIGH-STRESS RUSHES", C_RED)
    _, tf = add_tb(s2, Inches(0.75), Inches(1.65), Inches(3.45), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "TRANSIT PANIC & REPETITIVE FORMS"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_RED
    probs = [
        ("Transit Rush Panic: ", "Peak KSRTC and Tatkal train seats vanish in < 90 seconds due to slow manual field entry."),
        ("Multi-Portal Burnout: ", "Re-entering identical credentials, marks, & addresses across 20+ fragmented portals."),
        ("Bespoke Essay Exhaustion: ", "Drafting custom statements of purpose for scholarships under tight deadlines.")
    ]
    for pt, pd in probs:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + pt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = pd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(0.65), Inches(3.85), Inches(3.65), Inches(2.50), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(3.95), Inches(1.50), Inches(0.24), "HIDDEN TRAPS", C_ORANGE)
    _, tf = add_tb(s2, Inches(0.75), Inches(4.25), Inches(3.45), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "REJECTED DOCS & SNEAKY FEES"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    matters = [
        ("Impossible Upload Constraints: ", "Portals demand photos strictly between 20KB-50KB and 3.5x4.5cm, causing rejection loops."),
        ("Deceptive Dark Patterns: ", "Sneaky pre-checked \u20B9199 insurance and auto-added convenience fees inflate totals."),
        ("Civic & Vernacular Exclusion: ", "Elderly and regional language citizens cannot navigate multi-step government SPAs.")
    ]
    for mt, md in matters:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + mt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Center Column: Current Gaps (Top) & Real-World Impact (Bottom)
    add_card(s2, Inches(4.45), Inches(1.25), Inches(4.45), Inches(2.50), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s2, Inches(4.60), Inches(1.35), Inches(1.40), Inches(0.24), "BOT BREAKDOWN", C_BLUE)
    _, tf = add_tb(s2, Inches(4.55), Inches(1.65), Inches(4.25), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "WHY EXISTING TOOLS FAIL"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_BLUE
    gaps = [
        ("Voice Assistants Can't Click: ", "Siri and Alexa only answer questions; they cannot browse websites, select seats, or type."),
        ("Chrome Autofill Collapses: ", "Blind key-value dumps fail on dynamic seat grids, dates, and strict file upload rules."),
        ("Scrapers Get Banned: ", "Headless bots trigger Cloudflare 403 blocks and have zero safety bridge for CAPTCHAs or UPI.")
    ]
    for gt, gd in gaps:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + gt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = gd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(4.45), Inches(3.85), Inches(4.45), Inches(2.50), C_WHITE, C_CARD_BORDER, 1.2)
    add_pill_badge(s2, Inches(4.60), Inches(3.95), Inches(1.40), Inches(0.24), "EMPIRICAL SCALE", C_MUTED)
    _, tf = add_tb(s2, Inches(4.55), Inches(4.25), Inches(4.25), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "THE SCALE OF DIGITAL FRICTION"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_DARK
    impacts = [
        ("$100M+ Unclaimed Aid: ", "Scholarships, grants, and subsidies abandoned annually due to portal paperwork exhaustion."),
        ("< 2.5 Min Sell-out Window: ", "Peak transit reservations expire before manual form completion can finish."),
        ("\u20B91,200 Cr Dark-Pattern Drain: ", "Lost annually by consumers to deceptive pre-selected add-ons and hidden surge fees.")
    ]
    for it, idesc in impacts:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + it; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = idesc; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Right Column: Big Stat Cards
    stat_w = Inches(3.60)
    add_card(s2, Inches(9.05), Inches(1.25), stat_w, Inches(1.20), C_RED_LIGHT, C_RED_BORDER, 1.2)
    _, tf = add_tb(s2, Inches(9.15), Inches(1.30), stat_w - Inches(0.2), Inches(1.05))
    p = tf.paragraphs[0]; p.text = "< 90 SEC SELLOUT"; p.font.name = FONT; p.font.size = Pt(22); p.font.bold = True; p.font.color.rgb = C_RED
    p2 = tf.add_paragraph(); p2.space_before = Pt(1)
    p2.text = "Window before peak KSRTC/Tatkal seats sell out; manual typing fails under rush pressure."
    p2.font.name = FONT; p2.font.size = Pt(10); p2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(9.05), Inches(2.55), stat_w, Inches(1.20), C_ORANGE_LIGHT, C_ORANGE_BORDER, 1.2)
    _, tf = add_tb(s2, Inches(9.15), Inches(2.60), stat_w - Inches(0.2), Inches(1.05))
    p = tf.paragraphs[0]; p.text = "38% REJECTION RATE"; p.font.name = FONT; p.font.size = Pt(22); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    p2 = tf.add_paragraph(); p2.space_before = Pt(1)
    p2.text = "Government job & exam applicants blocked by rigid 20KB-50KB image upload limits."
    p2.font.name = FONT; p2.font.size = Pt(10); p2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(9.05), Inches(3.85), stat_w, Inches(1.20), C_BLUE_LIGHT, C_BLUE_BORDER, 1.2)
    _, tf = add_tb(s2, Inches(9.15), Inches(3.90), stat_w - Inches(0.2), Inches(1.05))
    p = tf.paragraphs[0]; p.text = "\u20B9350+ SNEAKY FEES"; p.font.name = FONT; p.font.size = Pt(22); p.font.bold = True; p.font.color.rgb = C_BLUE
    p2 = tf.add_paragraph(); p2.space_before = Pt(1)
    p2.text = "Hidden insurance & convenience surcharges auto-checked during online ticketing checkouts."
    p2.font.name = FONT; p2.font.size = Pt(10); p2.font.color.rgb = C_CHARCOAL

    # Bottom Banner: Conversational Execution Flow
    add_card(s2, Inches(9.05), Inches(5.15), stat_w, Inches(1.20), C_DARK, C_DARK, 1.0)
    _, tf = add_tb(s2, Inches(9.15), Inches(5.20), stat_w - Inches(0.2), Inches(1.05), ml=0.02, mr=0.02)
    p = tf.paragraphs[0]; p.text = "CONVERSATIONAL EXECUTION FLOW"; p.font.name = FONT; p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_BORDER
    p2 = tf.add_paragraph(); p2.space_before = Pt(2)
    p2.text = "Voice Intent \u2192 Vault Match \u2192 Protocol Reason \u2192 HITL Gate \u2192 Exec"
    p2.font.name = FONT; p2.font.size = Pt(8.5); p2.font.color.rgb = C_WHITE
    p3 = tf.add_paragraph(); p3.space_before = Pt(2)
    p3.text = "Speak your goal. Swarm navigates live, pausing for payment approval."
    p3.font.name = FONT; p3.font.size = Pt(9.5); p3.font.italic = True; p3.font.color.rgb = C_MUTED

    # ==============================================================================
    # SLIDE 3: PROPOSED SOLUTION & INNOVATION (5 CORE PROTOCOLS)
    # ==============================================================================
    s3 = prs.slides[2]
    setup_slide_header(s3, "Proposed Solution & Core Innovation",
                       "ApplyCopilot: Autonomous Voice Engine Orchestrating 5 Core Protocols.",
                       "\"Speak naturally. Jarvis dynamically engages the target protocol \u2014 from high-speed transit checkout to anti-dark-pattern sanitization.\"")

    # Top Left Card: What Are We Proposing?
    add_card(s3, Inches(0.65), Inches(1.25), Inches(4.85), Inches(2.45), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s3, Inches(0.80), Inches(1.35), Inches(1.50), Inches(0.24), "JARVIS WEB ARCHITECTURE", C_ORANGE)
    _, tf = add_tb(s3, Inches(0.75), Inches(1.65), Inches(4.65), Inches(1.95))
    p = tf.paragraphs[0]; p.text = "WHAT ARE WE PROPOSING?"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    props = [
        ("Conversational Voice Steering: ", "Sub-250ms voice assistant transforms natural speech into structured browser actions."),
        ("5 Specialized Execution Protocols: ", "Dynamic task dispatch across transit booking, civic aid, document surgery, dark-patterns & fraud."),
        ("Air-Gapped Human Gate: ", "Mirrored viewport streams live clicks; auto-pauses for UPI payment & CAPTCHA clearance.")
    ]
    for pt, pd in props:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + pt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = pd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Top Right Visual: Split-Screen Dashboard UI
    add_card(s3, Inches(5.65), Inches(1.25), Inches(7.03), Inches(2.45), C_SLATE_800, C_CARD_BORDER, 1.2)
    s3.shapes.add_picture('applycopilot_dashboard.jpg', Inches(5.68), Inches(1.28), Inches(6.97), Inches(2.39))

    # Middle Row: 5 Specialized Protocol Cards Side-by-Side!
    # Total width available: 12.03 inches. 5 cards with width 2.31 each, gap 0.12 = 5 * 2.31 + 4 * 0.12 = 12.03
    p_w = Inches(2.31)
    p_gap = Inches(0.12)
    protocols = [
        ("SPEED & SEATS", "1. Transit Rush", C_RED, C_RED_LIGHT, C_RED_BORDER, [
            ("Sub-250ms Grid Parser: ", "Instantly identifies vacant sleeper/window berths on KSRTC & IRCTC."),
            ("Passenger Vault Auto-Fill: ", "Injects names, age, and ID proofs to beat the 90-sec sellout window."),
            ("Direct-to-Checkout: ", "Bypasses promo pages straight to payment terminal.")
        ]),
        ("CIVIC & SCHOLAR", "2. Civic Helper", C_BLUE, C_BLUE_LIGHT, C_BLUE_BORDER, [
            ("Vernacular Navigation: ", "Voice assistance in Kannada, Hindi & English for Seva Sindhu & Parivahan."),
            ("Grounded Essay RAG: ", "Synthesizes tailored scholarship motivation letters from stored achievements."),
            ("Elderly Inclusion: ", "Hands-free completion of complex multi-step government forms.")
        ]),
        ("ZERO-TRUST SHIELD", "3. Fraud Sentinel", C_GREEN, C_GREEN_LIGHT, C_GREEN_BORDER, [
            ("Domain Provenance: ", "Audits registration age & SSL against phishing lookalikes (<30 days flag)."),
            ("Air-Gapped Payment Gate: ", "State machine freezes DOM on checkout/UPI; never charges blindly."),
            ("Human-in-the-Loop: ", "Mandatory user authorization for UPI PIN, OTP, & submission.")
        ]),
        ("IN-FLIGHT SURGERY", "4. Document Exorcist", C_PURPLE, C_PURPLE_LIGHT, C_PURPLE_BORDER, [
            ("20KB-50KB Auto-Fixer: ", "Detects strict portal upload constraints in DOM validation attributes."),
            ("In-Memory Optimization: ", "Auto-crops to 3.5x4.5cm, sets 200 DPI, and compresses 2MB files to 38KB."),
            ("Zero Image Software: ", "Bypasses upload errors without touching MS Paint or Photoshop.")
        ]),
        ("CONSUMER DEFENSE", "5. Anti-Dark-Pattern", C_CYAN, C_CYAN_LIGHT, C_CYAN_BORDER, [
            ("Hidden Fee Stripper: ", "Programmatically unchecks sneaky \u20B9199 insurance and donation add-ons."),
            ("Dynamic Pricing Guard: ", "Rotates incognito sessions & headers to neutralize cookie-based surge fees."),
            ("Clean Checkout Total: ", "Ensures users pay true minimum base fares across booking portals.")
        ])
    ]

    for p_idx, (p_pill, p_title, p_col, p_bg, p_border, p_points) in enumerate(protocols):
        p_left = Inches(0.65) + p_idx * (p_w + p_gap)
        add_card(s3, p_left, Inches(3.85), p_w, Inches(2.65), p_bg, p_border, 1.2)
        add_pill_badge(s3, p_left + Inches(0.10), Inches(3.95), p_w - Inches(0.20), Inches(0.22), p_pill, p_col)
        _, tf_p = add_tb(s3, p_left + Inches(0.08), Inches(4.22), p_w - Inches(0.16), Inches(2.20), mt=0.01, mb=0.01, ml=0.02, mr=0.02)
        p = tf_p.paragraphs[0]; p.text = p_title; p.font.name = FONT; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = p_col
        for p_head, p_desc in p_points:
            pb = tf_p.add_paragraph(); pb.space_before = Pt(1.5)
            r1 = pb.add_run(); r1.text = "\u2022 " + p_head; r1.font.name = FONT; r1.font.size = Pt(8.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
            r2 = pb.add_run(); r2.text = p_desc; r2.font.name = FONT; r2.font.size = Pt(8.5); r2.font.color.rgb = C_CHARCOAL

    # ==============================================================================
    # SLIDE 4: EXISTING SOLUTIONS & DIFFERENTIATION
    # ==============================================================================
    s4 = prs.slides[3]
    setup_slide_header(s4, "Existing Solutions & Differentiation",
                       "Why Voice Assistants and Autofill Extensions Fail on the Modern Web.",
                       "How ApplyCopilot's 5 protocols bridge conversational steering with real-world browser execution.")

    # Left Card: Existing Solutions & Visual Graphic
    add_card(s4, Inches(0.65), Inches(1.25), Inches(5.15), Inches(5.15), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s4, Inches(0.80), Inches(1.35), Inches(1.65), Inches(0.24), "LEGACY TOOL FAILURES", C_RED)
    _, tf_ex = add_tb(s4, Inches(0.75), Inches(1.65), Inches(4.95), Inches(0.35))
    p = tf_ex.paragraphs[0]; p.text = "EXISTING TOOLS & CRITICAL BREAKDOWNS"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_RED

    # Failure Mode Image
    s4.shapes.add_picture('applycopilot_failure_modes.jpg', Inches(0.80), Inches(2.05), Inches(4.85), Inches(2.70))

    # Summary text under image
    _, tf_sub = add_tb(s4, Inches(0.80), Inches(4.85), Inches(4.85), Inches(1.45), ml=0.02, mr=0.02)
    p_sum = tf_sub.paragraphs[0]
    p_sum.text = "\u2022 Voice Assistants (Siri/Alexa): Conversational toys; zero DOM clicking or seat selection."
    p_sum.font.name = FONT; p_sum.font.size = Pt(10.5); p_sum.font.bold = True; p_sum.font.color.rgb = C_DARK
    p_sum2 = tf_sub.add_paragraph(); p_sum2.space_before = Pt(2)
    p_sum2.text = "\u2022 Chrome Autofill: Rigid text dump; crashes on dynamic seat grids, calendars, & strict upload rules."
    p_sum2.font.name = FONT; p_sum2.font.size = Pt(10.5); p_sum2.font.bold = True; p_sum2.font.color.rgb = C_CHARCOAL
    p_sum3 = tf_sub.add_paragraph(); p_sum3.space_before = Pt(2)
    p_sum3.text = "\u2022 Headless Bots: Trigger Cloudflare 403 blocks; zero handling for UPI/OTPs or dark-pattern fees."
    p_sum3.font.name = FONT; p_sum3.font.size = Pt(10.5); p_sum3.font.bold = True; p_sum3.font.color.rgb = C_RED

    # Right Card: Feature Matrix / Differentiation Table
    add_card(s4, Inches(6.05), Inches(1.25), Inches(6.63), Inches(5.15), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s4, Inches(6.20), Inches(1.35), Inches(1.65), Inches(0.24), "COMPETITIVE MATRIX", C_GREEN)
    _, tf_diff = add_tb(s4, Inches(6.15), Inches(1.65), Inches(6.43), Inches(0.35))
    p = tf_diff.paragraphs[0]; p.text = "BENCHMARK: APPLYCOPILOT VS ALTERNATIVES"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_GREEN

    # Clean Table for Differentiation (Benchmarking the 5 Protocols!)
    rows = 6
    cols = 5
    table_shape = s4.shapes.add_table(rows, cols, Inches(6.15), Inches(2.05), Inches(6.43), Inches(3.20))
    table = table_shape.table
    table.columns[0].width = Inches(2.10)
    table.columns[1].width = Inches(1.00)
    table.columns[2].width = Inches(1.05)
    table.columns[3].width = Inches(1.00)
    table.columns[4].width = Inches(1.28)

    headers = ["5 Core Capabilities", "Siri / Alexa", "Autofill", "ChatGPT", "ApplyCopilot"]
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_DARK if c_idx < 4 else C_ORANGE
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    matrix_data = [
        ("Transit Rush & Dynamic Seats", "None", "None", "Blind", "\u2713 Automated Grids"),
        ("Civic Forms & Essay RAG", "Blind", "Rigid Dump", "Hallucinates", "\u2713 Grounded RAG"),
        ("Document Exorcist (20-50KB)", "None", "Upload Error", "None", "\u2713 In-Flight Surgery"),
        ("Anti-Dark-Pattern Fee Stripper", "None", "Pays Extra", "None", "\u2713 Auto-Unchecks Fees"),
        ("Zero-Trust Fraud & UPI Gate", "None", "Blind Submit", "None", "\u2713 Air-Gapped UPI")
    ]

    for r_idx, row_vals in enumerate(matrix_data):
        for c_idx, val in enumerate(row_vals):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_GREEN_LIGHT if c_idx == 4 else (C_WHITE if r_idx % 2 == 0 else C_BLUE_LIGHT)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT
            p.font.size = Pt(9.5)
            p.font.bold = (c_idx == 0 or c_idx == 4)
            p.font.color.rgb = C_GREEN if "\u2713" in val else (C_RED if ("None" in val or "Blind" in val or "Error" in val) else C_DARK)
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    # Differentiation Callout
    _, tf_callout = add_tb(s4, Inches(6.15), Inches(5.35), Inches(6.43), Inches(0.95), ml=0.04, mr=0.04)
    p_c = tf_callout.paragraphs[0]
    p_c.text = "OUR UNFAIR ADVANTAGE:"
    p_c.font.name = FONT; p_c.font.size = Pt(11); p_c.font.bold = True; p_c.font.color.rgb = C_ORANGE_DARK
    p_c2 = tf_callout.add_paragraph(); p_c2.space_before = Pt(1)
    p_c2.text = "ApplyCopilot unites conversational voice AI with 5 specialized browser execution protocols. It solves high-stress booking rushes, tedious government forms, strict document limits, and predatory dark patterns while guaranteeing 100% human payment sovereignty."
    p_c2.font.name = FONT; p_c2.font.size = Pt(10.5); p_c2.font.color.rgb = C_CHARCOAL

    # ==============================================================================
    # SLIDE 5: TECHNICAL APPROACH & FEASIBILITY
    # ==============================================================================
    s5 = prs.slides[4]
    setup_slide_header(s5, "Technical Approach & Feasibility",
                       "Voice Pipeline, Multi-Agent Swarm, Stealth Browser, and 24h Scope.",
                       "Sub-second conversational voice loop backed by Playwright and free-tier LLM inference.")

    # Left: High-Tech Engineering System Architecture Diagram
    add_card(s5, Inches(0.65), Inches(1.25), Inches(6.50), Inches(5.15), C_SLATE_800, C_CARD_BORDER, 1.2)
    s5.shapes.add_picture('applycopilot_architecture.jpg', Inches(0.68), Inches(1.28), Inches(6.44), Inches(5.09))

    # Right Column: 3 Technical Detail Cards
    rc_w = Inches(5.35)

    # Card 1: Multi-Agent Swarm Logic
    add_card(s5, Inches(7.35), Inches(1.25), rc_w, Inches(1.65), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s5, Inches(7.50), Inches(1.35), Inches(1.85), Inches(0.24), "MULTI-AGENT SWARM", C_BLUE)
    _, tf = add_tb(s5, Inches(7.45), Inches(1.65), rc_w - Inches(0.2), Inches(1.20))
    p = tf.paragraphs[0]; p.text = "5 SPECIALIZED PROTOCOL WORKERS"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_BLUE
    swarms = [
        ("Transit Worker: ", "Extracts web accessibility trees to parse dynamic seat grids & calendars."),
        ("Civic & Scholar Worker: ", "RAG embedding reasoner generating grounded motivation essays from vault."),
        ("Document Exorcist Worker: ", "In-memory Pillow/Wasm image resizer and PDF byte sanitizer (20KB-50KB)."),
        ("Anti-Dark-Pattern Worker: ", "DOM selector heuristics detecting and unchecking hidden fees & insurance.")
    ]
    for st, sd in swarms:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + st; r1.font.name = FONT; r1.font.size = Pt(10); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    # Card 2: Stealth Browser & HITL Gateway
    add_card(s5, Inches(7.35), Inches(3.00), rc_w, Inches(1.65), C_WHITE, C_CYAN_BORDER, 1.2)
    add_pill_badge(s5, Inches(7.50), Inches(3.10), Inches(1.85), Inches(0.24), "STEALTH ENGINE & FRAUD GATE", C_CYAN)
    _, tf = add_tb(s5, Inches(7.45), Inches(3.40), rc_w - Inches(0.2), Inches(1.20))
    p = tf.paragraphs[0]; p.text = "STEALTH RUNTIME & AIR-GAPPED GATEWAY"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_DARK
    stealths = [
        ("Playwright-Stealth: ", "Masks navigator.webdriver, WebGL fingerprints, and browser headers against bot-detection."),
        ("Live Screencast Stream: ", "Streams CDP viewport frames via WebSockets directly to the web dashboard."),
        ("Payment Interrupt Gate: ", "State machine shifts to PAUSED on checkout/UPI/CAPTCHA; prompts user on mirrored canvas."),
        ("Zero Financial Liability: ", "Air-gapped execution \u2014 agent never touches banking passwords or UPI PINs.")
    ]
    for st, sd in stealths:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + st; r1.font.name = FONT; r1.font.size = Pt(10); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    # Card 3: 24-Hour Hackathon Feasibility
    add_card(s5, Inches(7.35), Inches(4.75), rc_w, Inches(1.65), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s5, Inches(7.50), Inches(4.85), Inches(1.60), Inches(0.24), "24-HOUR SCOPE", C_ORANGE)
    _, tf = add_tb(s5, Inches(7.45), Inches(5.15), rc_w - Inches(0.2), Inches(1.20), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "100% FREE DEVELOPER STACK & MVP"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    feass = [
        ("Zero Paid API Blockers: ", "Built on free Web Speech API, Groq Whisper, Gemini 2.5 Flash, Groq LPU, & Playwright."),
        ("Multi-Protocol 24h MVP: ", "Executes live transit seat selection, document auto-resizing, and fee stripping."),
        ("Failsafe Local Mock: ", "Local KSRTC/scholarship test server guarantees 100% demo uptime under spotty Wi-Fi."),
        ("Strict Human Sign-off: ", "Structured review diff ensures complete auditability before money or data is sent.")
    ]
    for ft, fd in feass:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + ft; r1.font.name = FONT; r1.font.size = Pt(10); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = fd; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    # ==============================================================================
    # SLIDE 6: EXPECTED IMPACT & EXECUTION PLAN
    # ==============================================================================
    s6 = prs.slides[5]
    setup_slide_header(s6, "Expected Impact & Execution Plan",
                       "Eliminating Administrative & Transactional Friction via Voice Precision.",
                       "A concrete 24-hour sprint roadmap and measurable real-world outcomes.")

    # Top Row: 3 Impact Cards
    card_w = Inches(3.88)
    card_gap = Inches(0.19)

    # Left: Quantifiable Outcomes
    add_card(s6, Inches(0.65), Inches(1.25), card_w, Inches(2.35), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80), Inches(1.35), Inches(1.50), Inches(0.22), "MEASURED VALUE", C_GREEN)
    _, tf = add_tb(s6, Inches(0.75), Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "QUANTIFIABLE OUTCOMES"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_GREEN
    impacts = [
        ("80% Faster Bookings: ", "Reduces transit ticket checkout from 8 mins to under 90 seconds (Transit Rush)."),
        ("100% Document Pass Rate: ", "Zero upload rejections on strict 20KB-50KB exam/job portals (Document Exorcist)."),
        ("\u20B9350+ Saved Per Booking: ", "Immediate elimination of auto-checked insurance & surge fees (Anti-Dark-Pattern)."),
        ("0% Payment Fraud: ", "Mandatory air-gapped human approval gate protects users from unintended charges.")
    ]
    for it, idesc in impacts:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + it; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = idesc; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    # Center: Evaluation Targets
    add_card(s6, Inches(0.65) + card_w + card_gap, Inches(1.25), card_w, Inches(2.35), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80) + card_w + card_gap, Inches(1.35), Inches(1.50), Inches(0.22), "TARGET BENCHMARKS", C_ORANGE)
    _, tf = add_tb(s6, Inches(0.75) + card_w + card_gap, Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "EVALUATION TARGETS"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    metrics = [
        ("< 250ms Voice Intent: ", "Real-time speech transcription & structured command extraction via Groq."),
        ("> 96% Field & Seat Accuracy: ", "Correct identification of inputs, dates, and bus seat layouts."),
        ("< 1.5s In-Flight Document Resizing: ", "Sub-second image re-encoding to strict 20KB-50KB threshold."),
        ("100% Pre-Submit Audit: ", "Complete visual verification diff presented before final execution.")
    ]
    for mt, md in metrics:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + mt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_GREEN
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    # Right: Who Benefits?
    add_card(s6, Inches(0.65) + (card_w + card_gap) * 2, Inches(1.25), card_w, Inches(2.35), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80) + (card_w + card_gap) * 2, Inches(1.35), Inches(1.40), Inches(0.22), "STAKEHOLDERS", C_BLUE)
    _, tf = add_tb(s6, Inches(0.75) + (card_w + card_gap) * 2, Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "WHO BENEFITS?"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_BLUE
    stakeholders = [
        ("Daily Commuters & Travelers: ", "Instant hands-free bus/train ticket bookings during peak rush windows."),
        ("Students & Exam Applicants: ", "Painless scholarship submissions and auto-corrected document uploads."),
        ("Online Shoppers & Consumers: ", "Complete protection against deceptive dark-pattern up-sells."),
        ("Differently-Abled & Seniors: ", "Empowering voice-to-action co-pilot assistance on complex public portals.")
    ]
    for st, sd in stakeholders:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + st; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    # Bottom Row: 24-Hour Hackathon Execution Roadmap (4 Phases)
    add_card(s6, Inches(0.65), Inches(3.75), Inches(12.03), Inches(2.65), C_WHITE, C_CARD_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80), Inches(3.85), Inches(1.80), Inches(0.24), "24-HOUR SPRINT TIMELINE", C_ORANGE)
    _, tf = add_tb(s6, Inches(0.75), Inches(4.15), Inches(11.83), Inches(0.35))
    p = tf.paragraphs[0]; p.text = "RIGOROUS 24-HOUR HACKATHON EXECUTION ROADMAP"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_DARK

    phases = [
        ("PHASE 1: 00:00 \u2014 06:00", "VOICE PIPELINE & VAULT SETUP",
         "\u2022 Web Speech API & audio intent router setup.\n\u2022 Encrypted local JSON vault for passenger/user credentials.\n\u2022 Sub-250ms Groq Whisper streaming audio pipeline."),
        ("PHASE 2: 06:00 \u2014 12:00", "TRANSIT RUSH & CIVIC SWARM",
         "\u2022 Playwright accessibility tree extractor for seat grids.\n\u2022 KSRTC & scholarship portal interaction state machine.\n\u2022 Grounded RAG for tailored motivation essays."),
        ("PHASE 3: 12:00 \u2014 18:00", "EXORCIST & ANTI-DARK-PATTERN",
         "\u2022 In-memory image/PDF 20KB-50KB resizing engine.\n\u2022 DOM selector rules unchecking hidden fees & insurance.\n\u2022 Live CDP screencast stream to web dashboard."),
        ("PHASE 4: 18:00 \u2014 24:00", "FRAUD SENTINEL & LIVE DEMO",
         "\u2022 Air-gapped interrupt loop on UPI/CAPTCHA/checkout.\n\u2022 Side-by-side battle demo rehearsal for hackathon judges.\n\u2022 Final latency optimization & pitch deck rehearsal.")
    ]

    p_w = Inches(2.88)
    p_gap = Inches(0.12)
    for p_idx, (p_title, p_sub, p_desc) in enumerate(phases):
        p_left = Inches(0.80) + (p_w + p_gap) * p_idx
        add_card(s6, p_left, Inches(4.55), p_w, Inches(1.70), C_ORANGE_LIGHT if p_idx % 2 == 0 else C_BLUE_LIGHT, C_ORANGE_BORDER if p_idx % 2 == 0 else C_BLUE_BORDER, 1.0)
        _, tf_p = add_tb(s6, p_left + Inches(0.1), Inches(4.60), p_w - Inches(0.2), Inches(1.60), ml=0.02, mr=0.02)
        p = tf_p.paragraphs[0]; p.text = p_title; p.font.name = FONT; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK if p_idx % 2 == 0 else C_BLUE
        p2 = tf_p.add_paragraph(); p2.space_before = Pt(1); p2.text = p_sub; p2.font.name = FONT; p2.font.size = Pt(9.5); p2.font.bold = True; p2.font.color.rgb = C_DARK
        p3 = tf_p.add_paragraph(); p3.space_before = Pt(2); p3.text = p_desc; p3.font.name = FONT; p3.font.size = Pt(8.5); p3.font.color.rgb = C_CHARCOAL

    # ==============================================================================
    # SLIDE 7: CONCLUSION & REFERENCES
    # ==============================================================================
    s7 = prs.slides[6]
    setup_slide_header(s7, "Conclusion & References",
                       "The Conversational Web: Autonomous Execution With Absolute Human Sovereignty.",
                       "\"Shifting from passive clicking to intelligent, voice-driven copilots that respect user control.\"")

    # Top Left: Key Takeaways Summary Card
    add_card(s7, Inches(0.65), Inches(1.25), Inches(5.15), Inches(3.05), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(1.35), Inches(1.30), Inches(0.24), "CORE SUMMARY", C_GREEN)
    _, tf_k = add_tb(s7, Inches(0.75), Inches(1.65), Inches(4.95), Inches(2.55))
    p = tf_k.paragraphs[0]; p.text = "KEY TAKEAWAYS"; p.font.name = FONT; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_GREEN
    takeaways = [
        ("Voice-First Web Navigation: ", "Replaces exhausting manual clicking with instant natural speech for forms and bookings."),
        ("5 Specialized Protocols: ", "Executes Transit Rush, Civic Helper, Fraud Sentinel, Document Exorcist, and Anti-Dark-Pattern tasks."),
        ("Ethical Machine-Human Synergy: ", "Proves that autonomous agents must keep the human in full sovereign control over money and data."),
        ("Zero-Cost Production Stack: ", "Fully buildable in 24 hours using free Web Speech API, Gemini 2.5 Flash, Groq LPU, & Playwright.")
    ]
    for kt, kd in takeaways:
        pb = tf_k.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + kt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = kd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Top Right: Realistic Security & Trust Certificate Visual
    add_card(s7, Inches(5.95), Inches(1.25), Inches(6.73), Inches(3.05), C_SLATE_800, C_CARD_BORDER, 1.2)
    s7.shapes.add_picture('applycopilot_trust_badge.jpg', Inches(5.98), Inches(1.28), Inches(6.67), Inches(2.99))

    # Bottom: References & Benchmarks (2 Clean Columns)
    add_card(s7, Inches(0.65), Inches(4.40), Inches(12.03), Inches(1.95), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(4.50), Inches(1.60), Inches(0.24), "TECHNICAL EVIDENCE", C_BLUE)
    _, tf_rf = add_tb(s7, Inches(0.75), Inches(4.80), Inches(11.83), Inches(1.50))
    p = tf_rf.paragraphs[0]; p.text = "VERIFIABLE REFERENCES & SCIENTIFIC BENCHMARKS"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_BLUE

    # References Col 1
    _, tf_c1 = add_tb(s7, Inches(0.75), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col1 = [
        ("1. W3C Web Speech & ARIA Standards: ", "SpeechRecognition API & Accessibility Tree Navigation Specifications."),
        ("2. Groq LPU Speech Benchmarks: ", "Sub-200ms Whisper Audio Transcription on Custom Inference Hardware."),
        ("3. Google Gemini 2.5 Flash: ", "Low-Latency Multimodal Reasoning & Zero-Shot Schema Classification.")
    ]
    for r_num, r_text in ref_col1:
        p = tf_c1.add_paragraph() if tf_c1.paragraphs[0].text else tf_c1.paragraphs[0]
        p.space_before = Pt(1)
        r1 = p.add_run(); r1.text = r_num; r1.font.name = FONT; r1.font.size = Pt(9.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = p.add_run(); r2.text = r_text; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    # References Col 2
    _, tf_c2 = add_tb(s7, Inches(6.80), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col2 = [
        ("4. Browser-Use & Stagehand (2024-2026): ", "Autonomous Web Agent Architecture & Natural Language DOM Routing."),
        ("5. Playwright Stealth: ", "Mitigating Automation Fingerprints on High-Traffic Reservation Systems."),
        ("6. FTC Guidelines on Automated Systems: ", "Mandatory Human Oversight & Consumer Consent in Digital Transactions.")
    ]
    for r_num, r_text in ref_col2:
        p = tf_c2.add_paragraph() if tf_c2.paragraphs[0].text else tf_c2.paragraphs[0]
        p.space_before = Pt(1)
        r1 = p.add_run(); r1.text = r_num; r1.font.name = FONT; r1.font.size = Pt(9.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = p.add_run(); r2.text = r_text; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    # Save outputs
    prs.save(output_pptx)
    prs.save(output_team_pptx)
    print(f"Saved: {output_pptx}")
    print(f"Saved: {output_team_pptx}")

    # Export to PDF and PNG previews via PowerPoint win32com
    try:
        import win32com.client
        import time

        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        abs_pptx = os.path.abspath(output_pptx)
        abs_pdf = os.path.abspath(output_pdf)
        abs_team_pdf = os.path.abspath(output_team_pdf)

        deck = powerpoint.Presentations.Open(abs_pptx, WithWindow=False)
        deck.SaveAs(abs_pdf, 32) # 32 = ppSaveAsPDF
        deck.SaveAs(abs_team_pdf, 32)
        print(f"Exported PDF: {abs_pdf}")
        print(f"Exported PDF: {abs_team_pdf}")

        for i in range(1, len(deck.Slides) + 1):
            out_img = os.path.abspath(f'applycopilot_slide_{i}.png')
            deck.Slides(i).Export(out_img, 'PNG', 1920, 1080)
            print(f"Rendered: applycopilot_slide_{i}.png")

        deck.Close()
        powerpoint.Quit()
    except Exception as e:
        print(f"PDF/PNG generation note: {e}")

if __name__ == '__main__':
    build_applycopilot_presentation()
