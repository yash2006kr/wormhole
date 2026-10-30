import sys
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# --- COLOR PALETTE ---
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

def populate_slide_1(s1, theme_tag, project_title, subtitle, tagline):
    for shape in s1.shapes:
        if shape.name == 'TextBox 14':
            shape.left = Inches(1.0)
            shape.top = Inches(2.55)
            shape.width = Inches(11.33)
            shape.height = Inches(1.80)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True

            p0 = tf.paragraphs[0]
            p0.text = theme_tag
            p0.font.name = FONT
            p0.font.size = Pt(13.5)
            p0.font.bold = True
            p0.font.color.rgb = C_ORANGE
            p0.alignment = PP_ALIGN.CENTER

            p1 = tf.add_paragraph()
            p1.space_before = Pt(3)
            p1.text = project_title
            p1.font.name = FONT
            p1.font.size = Pt(40)
            p1.font.bold = True
            p1.font.color.rgb = C_DARK
            p1.alignment = PP_ALIGN.CENTER

            p2 = tf.add_paragraph()
            p2.space_before = Pt(2)
            p2.text = subtitle
            p2.font.name = FONT
            p2.font.size = Pt(17)
            p2.font.bold = True
            p2.font.color.rgb = C_BLUE
            p2.alignment = PP_ALIGN.CENTER

            p3 = tf.add_paragraph()
            p3.space_before = Pt(2)
            p3.text = f'"{tagline}"'
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
            p_dom.text = f"Track: {theme_tag}"
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

            members = ["Raj Aanada", "Yashma C P", "Likith M", "Yashwanth K R"]
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
# DECK 1: VOICEKIRANA (Theme 05: Edge Intelligence & Offline-First AI)
# ==============================================================================
def build_deck_1_voicekirana():
    prs = Presentation('AfterHours_1.0_PPT_Template.pptx')
    if len(prs.slides) > 7:
        rId = prs.slides._sldIdLst[7].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[7]

    # Slide 1: Cover
    populate_slide_1(prs.slides[0],
                     "THEME 05: EDGE INTELLIGENCE & OFFLINE-FIRST AI",
                     "VOICEKIRANA",
                     "Offline Voice-Based Stock, Credit Ledger & Instant Bill Generator",
                     "Speak vernacular entries. Generate instant bills, track udhaar, and prevent stockouts \u2014 100% offline.")

    # Slide 2: Problem Statement & Relevance
    s2 = prs.slides[1]
    setup_slide_header(s2, "Problem Statement & Its Relevance",
                       "The Small Merchant Digital Divide & Manual Ledger Chaos.",
                       "Kirana owners lose hours and \u20B91,25,000+ monthly due to manual paper bookkeeping during busy counter rushes.")

    # Left: Exact Problem & Why it Matters
    add_card(s2, Inches(0.65), Inches(1.25), Inches(3.65), Inches(2.50), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(1.35), Inches(1.35), Inches(0.24), "COUNTER FRICTION", C_RED)
    _, tf = add_tb(s2, Inches(0.75), Inches(1.65), Inches(3.45), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "THE PAPER BAHI-KHATA TRAP"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_RED
    probs = [
        ("Typing is Too Slow: ", "During peak evening rush, typing on mobile apps or desktop POS keyboards causes long customer lines."),
        ("Forgotten Credit (Udhaar): ", "Writing credit entries on loose paper slips leads to forgotten balances and disputes."),
        ("Zero Inventory Visibility: ", "Shopkeepers run out of staples (sugar, oil, atta) mid-day without warning.")
    ]
    for pt, pd in probs:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + pt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = pd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(0.65), Inches(3.85), Inches(3.65), Inches(2.50), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(3.95), Inches(1.40), Inches(0.24), "ECONOMIC LOSS", C_ORANGE)
    _, tf = add_tb(s2, Inches(0.75), Inches(4.25), Inches(3.45), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "WHY DOES IT MATTER?"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    matters = [
        ("\u20B91,25,000 Monthly Loss: ", "Average unrecovered credit and unbilled items per small rural/urban grocery store."),
        ("Spotty Connectivity: ", "Tier-2/3 towns and basement stores suffer frequent cellular drops; cloud apps freeze."),
        ("Language Exclusion: ", "Over 80% of merchants cannot navigate complex English POS interfaces.")
    ]
    for mt, md in matters:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + mt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Center: Gaps & Empirical Scale
    add_card(s2, Inches(4.45), Inches(1.25), Inches(4.45), Inches(2.50), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s2, Inches(4.60), Inches(1.35), Inches(1.35), Inches(0.24), "CURRENT GAPS", C_BLUE)
    _, tf = add_tb(s2, Inches(4.55), Inches(1.65), Inches(4.25), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "WHY EXISTING TOOLS FAIL"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_BLUE
    gaps = [
        ("Cloud Apps Crash Offline: ", "Khatabook & Vyapar freeze completely when internet connectivity drops."),
        ("Desktop POS is Prohibitive: ", "Hardware costs \u20B915,000+ with steep learning curves for semi-literate clerks."),
        ("No Instant Bill Generation: ", "Voice apps only record memos; they cannot compute taxes or print thermal receipts.")
    ]
    for gt, gd in gaps:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + gt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = gd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(4.45), Inches(3.85), Inches(4.45), Inches(2.50), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s2, Inches(4.60), Inches(3.95), Inches(1.35), Inches(0.24), "EMPIRICAL SCALE", C_GREEN)
    _, tf = add_tb(s2, Inches(4.55), Inches(4.25), Inches(4.25), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "GROUND REALITY IN NUMBERS"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_GREEN
    empiricals = [
        ("13+ Million Kiranas in India: ", "Drive 88% of FMCG retail sales across India, yet 92% operate on manual paper notebooks."),
        ("2.5 Hours Daily Lost: ", "Spent matching customer ledgers and stock counts after shop closure every single night."),
        ("14% Stockouts on Staples: ", "Loss of high-margin walk-in sales when milk, oil, and flour unexpectedly run dry.")
    ]
    for et, ed in empiricals:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + et; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = ed; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Right: Metric Cards
    metrics = [
        ("13M+", "Kirana Stores in India", "88% of FMCG retail runs on offline paper ledgers", C_RED),
        ("\u20B91.25L", "Monthly Credit at Risk", "Unreconciled udhaar lost per store annually", C_ORANGE),
        ("2.5 Hrs", "Daily Bookkeeping Saved", "Time reclaimed by hands-free voice billing", C_BLUE)
    ]
    card_h = Inches(1.60); gap_h = Inches(0.15)
    for idx, (m_val, m_lbl, m_sub, m_col) in enumerate(metrics):
        top_pos = Inches(1.25) + idx * (card_h + gap_h)
        add_card(s2, Inches(9.05), top_pos, Inches(3.63), card_h, C_WHITE, C_CARD_BORDER, 1.0)
        _, tf_m = add_tb(s2, Inches(9.15), top_pos + Inches(0.10), Inches(3.43), card_h - Inches(0.20))
        p = tf_m.paragraphs[0]; p.text = m_val; p.font.name = FONT; p.font.size = Pt(32); p.font.bold = True; p.font.color.rgb = m_col
        p2 = tf_m.add_paragraph(); p2.space_before = Pt(1); p2.text = m_lbl; p2.font.name = FONT; p2.font.size = Pt(12); p2.font.bold = True; p2.font.color.rgb = C_DARK
        p3 = tf_m.add_paragraph(); p3.space_before = Pt(1); p3.text = m_sub; p3.font.name = FONT; p3.font.size = Pt(10); p3.font.color.rgb = C_MUTED

    # Slide 3: Proposed Solution & Core Innovation
    s3 = prs.slides[2]
    setup_slide_header(s3, "Proposed Solution & Core Innovation",
                       "Voice-to-Ledger-to-Bill: 100% Offline Edge Retail Operating System.",
                       "Speak naturally in vernacular dialect; VoiceKirana generates instant bills, updates udhaar, and alerts low stock.")

    pillars = [
        ("VERNACULAR SPEECH ENGINE", "Offline Edge Speech-to-Text",
         "Understands regional dialects (Hindi, Kannada, Hinglish) using quantized Vosk ASR running 100% locally with zero cloud latency.",
         C_RED),
        ("SLOT-FILLING BILL GENERATOR", "Instant Itemized Thermal Receipt",
         "Parses \"2 kg sugar Ramesh udhaar\" into structured items, computes total with tax, prints thermal bill, and shows customer UPI QR.",
         C_ORANGE_DARK),
        ("DOUBLE-ENTRY CREDIT KHATA", "Zero-Dispute Customer Ledger",
         "Maintains ACID-compliant SQLite credit balances per customer with instant SMS/WhatsApp summary sync when connectivity restores.",
         C_BLUE),
        ("PREDICTIVE STOCK SENTINEL", "End-of-Day Low Stock Alerts",
         "Automatically decrements inventory with every voice entry; generates wholesale reorder shopping lists before shelves empty.",
         C_GREEN)
    ]
    w_p = Inches(2.78); h_p = Inches(2.05); gap_p = Inches(0.12)
    for idx, (p_pill, p_title, p_desc, p_col) in enumerate(pillars):
        col = idx % 2; row = idx // 2
        l = Inches(0.65) + col * (w_p + gap_p)
        t = Inches(1.25) + row * (h_p + gap_p)
        add_card(s3, l, t, w_p, h_p, C_WHITE, C_CARD_BORDER, 1.0)
        add_pill_badge(s3, l + Inches(0.15), t + Inches(0.10), Inches(1.70), Inches(0.22), p_pill, p_col)
        _, tf_p = add_tb(s3, l + Inches(0.15), t + Inches(0.35), w_p - Inches(0.30), h_p - Inches(0.40))
        p = tf_p.paragraphs[0]; p.text = p_title; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_DARK
        p2 = tf_p.add_paragraph(); p2.space_before = Pt(2); p2.text = p_desc; p2.font.name = FONT; p2.font.size = Pt(10); p2.font.color.rgb = C_CHARCOAL

    # Right: Dashboard Picture
    add_card(s3, Inches(6.50), Inches(1.25), Inches(6.18), Inches(4.25), C_WHITE, C_BLUE_BORDER, 1.2)
    s3.shapes.add_picture('voicekirana_dashboard.jpg', Inches(6.53), Inches(1.28), Inches(6.12), Inches(4.19))

    # Bottom 3 Highlight Cards
    metric_w = Inches(3.90); col_gap = Inches(0.16)
    add_card(s3, Inches(0.65), Inches(5.65), metric_w, Inches(0.75), C_WHITE, C_CARD_BORDER, 1.0)
    _, tf_m1 = add_tb(s3, Inches(0.75), Inches(5.70), metric_w - Inches(0.2), Inches(0.65))
    p = tf_m1.paragraphs[0]; p.text = "< 300ms SPEECH RECOGNITION"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_GREEN
    p_sub = tf_m1.add_paragraph(); p_sub.text = "Sub-second quantized on-device inference with zero cellular or Wi-Fi reliance."; p_sub.font.name = FONT; p_sub.font.size = Pt(9.5); p_sub.font.color.rgb = C_MUTED

    add_card(s3, Inches(0.65) + metric_w + col_gap, Inches(5.65), metric_w, Inches(0.75), C_WHITE, C_CARD_BORDER, 1.0)
    _, tf_m2 = add_tb(s3, Inches(0.75) + metric_w + col_gap, Inches(5.70), metric_w - Inches(0.2), Inches(0.65))
    p = tf_m2.paragraphs[0]; p.text = "INSTANT THERMAL & UPI RECEIPT"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    p_sub = tf_m2.add_paragraph(); p_sub.text = "Direct Bluetooth thermal printer output + QR code for customer UPI payment."; p_sub.font.name = FONT; p_sub.font.size = Pt(9.5); p_sub.font.color.rgb = C_MUTED

    add_card(s3, Inches(0.65) + (metric_w + col_gap) * 2, Inches(5.65), metric_w, Inches(0.75), C_WHITE, C_CARD_BORDER, 1.0)
    _, tf_m3 = add_tb(s3, Inches(0.75) + (metric_w + col_gap) * 2, Inches(5.70), metric_w - Inches(0.2), Inches(0.65))
    p = tf_m3.paragraphs[0]; p.text = "100% PRIVATE LOCAL STORAGE"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_BLUE
    p_sub = tf_m3.add_paragraph(); p_sub.text = "Merchant financial data and customer phone numbers never leave the device."; p_sub.font.name = FONT; p_sub.font.size = Pt(9.5); p_sub.font.color.rgb = C_MUTED

    # Slide 4: Existing Solutions & Differentiation
    s4 = prs.slides[3]
    setup_slide_header(s4, "Existing Solutions & Differentiation",
                       "Why Paper Khatas and Desktop POS Systems Fail in Kirana Stores.",
                       "Comparing VoiceKirana against traditional paper records and heavy cloud billing software.")

    add_card(s4, Inches(0.65), Inches(1.25), Inches(5.15), Inches(5.15), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s4, Inches(0.80), Inches(1.35), Inches(1.65), Inches(0.24), "TRADITIONAL BOTTLENECK", C_RED)
    _, tf_ex = add_tb(s4, Inches(0.75), Inches(1.65), Inches(4.95), Inches(0.35))
    p = tf_ex.paragraphs[0]; p.text = "LEGACY SOLUTIONS & DAILY FAILURES"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_RED

    s4.shapes.add_picture('voicekirana_comparison.jpg', Inches(0.80), Inches(2.05), Inches(4.85), Inches(2.70))

    _, tf_sub = add_tb(s4, Inches(0.80), Inches(4.85), Inches(4.85), Inches(1.45), ml=0.02, mr=0.02)
    p_sum = tf_sub.paragraphs[0]
    p_sum.text = "\u2022 Paper Bahi-Khata: Manual writing causes counter delays, damaged pages, and lost debts."
    p_sum.font.name = FONT; p_sum.font.size = Pt(10.5); p_sum.font.bold = True; p_sum.font.color.rgb = C_DARK
    p_sum2 = tf_sub.add_paragraph(); p_sum2.space_before = Pt(2)
    p_sum2.text = "\u2022 Khatabook / Vyapar: Cloud-dependent; typing required; unusable when internet drops."
    p_sum2.font.name = FONT; p_sum2.font.size = Pt(10.5); p_sum2.font.bold = True; p_sum2.font.color.rgb = C_CHARCOAL
    p_sum3 = tf_sub.add_paragraph(); p_sum3.space_before = Pt(2)
    p_sum3.text = "\u2022 Desktop POS: Expensive (\u20B915,000+), bulky hardware, complex English navigation."
    p_sum3.font.name = FONT; p_sum3.font.size = Pt(10.5); p_sum3.font.bold = True; p_sum3.font.color.rgb = C_RED

    add_card(s4, Inches(6.05), Inches(1.25), Inches(6.63), Inches(5.15), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s4, Inches(6.20), Inches(1.35), Inches(1.65), Inches(0.24), "FEATURE MATRIX", C_GREEN)
    _, tf_diff = add_tb(s4, Inches(6.15), Inches(1.65), Inches(6.43), Inches(0.35))
    p = tf_diff.paragraphs[0]; p.text = "BENCHMARK: VOICEKIRANA VS ALTERNATIVES"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_GREEN

    table_shape = s4.shapes.add_table(6, 5, Inches(6.15), Inches(2.05), Inches(6.43), Inches(3.20))
    table = table_shape.table
    table.columns[0].width = Inches(1.85); table.columns[1].width = Inches(1.10)
    table.columns[2].width = Inches(1.10); table.columns[3].width = Inches(1.10); table.columns[4].width = Inches(1.28)

    headers = ["Capabilities", "Paper Khata", "Khatabook", "Desktop POS", "VoiceKirana"]
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid(); cell.fill.fore_color.rgb = C_DARK if c_idx < 4 else C_GREEN
        p = cell.text_frame.paragraphs[0]; p.text = h_text; p.font.name = FONT; p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    m_data = [
        ("Hands-Free Vernacular Voice", "Manual", "Typing Only", "English Keys", "Sub-300ms Audio"),
        ("100% Offline Functionality", "Offline Paper", "Fails Offline", "Partial Offline", "Pure Edge SQLite"),
        ("Instant Bill Generation", "None", "Manual Print", "Bulky Hardware", "1-Sec Voice Bill"),
        ("Credit (Udhaar) Khata", "Error-Prone", "Manual Type", "Clunky", "Voice-Linked Khata"),
        ("End-of-Day Low-Stock Alerts", "None", "None", "Manual Setup", "Auto-Reorder List")
    ]
    for r_idx, row_vals in enumerate(m_data):
        for c_idx, val in enumerate(row_vals):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if c_idx == 4:
                cell.fill.fore_color.rgb = C_GREEN_LIGHT
            elif r_idx % 2 == 0:
                cell.fill.fore_color.rgb = C_WHITE
            else:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)

            p = cell.text_frame.paragraphs[0]; p.text = val; p.font.name = FONT; p.font.size = Pt(9.5)
            if c_idx == 4:
                p.font.bold = True; p.font.color.rgb = C_GREEN
            elif "None" in val or "Fails" in val or "Manual" in val or "Error" in val:
                p.font.color.rgb = C_RED
            else:
                p.font.color.rgb = C_CHARCOAL
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    _, tf_adv = add_tb(s4, Inches(6.15), Inches(5.35), Inches(6.43), Inches(0.95), ml=0.02, mr=0.02)
    p = tf_adv.paragraphs[0]; p.text = "CORE ARCHITECTURAL ADVANTAGE"; p.font.name = FONT; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_DARK
    p_b1 = tf_adv.add_paragraph(); p_b1.space_before = Pt(1)
    r1 = p_b1.add_run(); r1.text = "\u2022 Zero Training Curve: "; r1.font.bold = True; r1.font.color.rgb = C_GREEN
    r2 = p_b1.add_run(); r2.text = "Merchants speak the exact same colloquial words they say to customers."; r2.font.color.rgb = C_CHARCOAL
    p_b2 = tf_adv.add_paragraph(); p_b2.space_before = Pt(1)
    r1 = p_b2.add_run(); r1.text = "\u2022 Hardware Democratization: "; r1.font.bold = True; r1.font.color.rgb = C_BLUE
    r2 = p_b2.add_run(); r2.text = "Runs on any existing \u20B96,000 Android smartphone with zero cloud hosting charges."; r2.font.color.rgb = C_CHARCOAL

    # Slide 5: Technical Architecture & System Flow
    s5 = prs.slides[4]
    setup_slide_header(s5, "Technical Architecture & System Flow",
                       "5-Layer Disconnected Edge Architecture with Real-Time Audio Pipeline.",
                       "Ultra-compact offline inference stack: Audio Stream -> Quantized Vosk ASR -> Slot Filler -> SQLite -> ESC/POS.")

    add_card(s5, Inches(0.65), Inches(1.25), Inches(5.65), Inches(5.15), C_WHITE, C_CARD_BORDER, 1.2)
    s5.shapes.add_picture('voicekirana_architecture.jpg', Inches(0.68), Inches(1.28), Inches(5.59), Inches(5.09))

    layers = [
        ("LAYER 1: AUDIO INGESTION", "Local Microphone Stream & Noise Filter",
         "Pulls 16kHz mono PCM stream via PyAudio; applies spectral subtraction to eliminate grocery shop background chatter.",
         C_RED),
        ("LAYER 2: QUANTIZED EDGE ASR", "Vosk / Kaldi Neural Acoustic Model",
         "Runs 35MB 8-bit quantized acoustic model on edge CPU; outputs phoneme lattices and greedy-decoded text in <300ms.",
         C_ORANGE_DARK),
        ("LAYER 3: SLOT-FILLING NLP", "Deterministic Rule & Entity Parser",
         "Extracts Item Name, Quantity, Unit (kg/g/pkt), Price, and Customer Name via high-speed regex & fuzzy catalog matching.",
         C_BLUE),
        ("LAYER 4: ATOMIC LEDGER STORE", "Embedded SQLite ACID Database",
         "Updates customer khata, decrements stock inventory, and logs transactions in WAL-mode SQLite database with zero cloud sync.",
         C_GREEN),
        ("LAYER 5: THERMAL & DISPLAY DISPATCH", "ESC/POS & UPI Payment Terminal",
         "Generates binary ESC/POS print commands for Bluetooth thermal printers and renders dynamic UPI QR code on merchant screen.",
         C_PURPLE)
    ]
    card_lh = Inches(0.96); gap_lh = Inches(0.08)
    for l_idx, (l_pill, l_title, l_desc, l_col) in enumerate(layers):
        top_l = Inches(1.25) + l_idx * (card_lh + gap_lh)
        add_card(s5, Inches(6.50), top_l, Inches(6.18), card_lh, C_WHITE, C_CARD_BORDER, 1.0)
        add_pill_badge(s5, Inches(6.60), top_l + Inches(0.08), Inches(1.85), Inches(0.20), l_pill, l_col)
        _, tf_l = add_tb(s5, Inches(6.60), top_l + Inches(0.26), Inches(5.98), card_lh - Inches(0.30), mt=0.01, mb=0.01)
        p = tf_l.paragraphs[0]; p.text = l_title; p.font.name = FONT; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_DARK
        p2 = tf_l.add_paragraph(); p2.space_before = Pt(1); p2.text = l_desc; p2.font.name = FONT; p2.font.size = Pt(9.5); p2.font.color.rgb = C_CHARCOAL

    # Slide 6: Feasibility, 24-Hour Roadmap & Societal Impact
    s6 = prs.slides[5]
    setup_slide_header(s6, "Feasibility, 24-Hour Roadmap & Societal Impact",
                       "Achievable 24-Hour Hackathon Delivery, Live Demos & Deep Bharat Reach.",
                       "Engineered specifically for live judging: speak vernacular items into mic and watch the thermal bill print instantly.")

    card_w = Inches(3.88); card_gap = Inches(0.20)
    add_card(s6, Inches(0.65), Inches(1.25), card_w, Inches(2.35), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80), Inches(1.35), Inches(1.40), Inches(0.22), "LIVE PROTOTYPE", C_RED)
    _, tf = add_tb(s6, Inches(0.75), Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "LIVE HACKATHON DEMO PLAN"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_RED
    demo_steps = [
        ("Step 1 (Cash Sale): ", "Speak \"2 kg atta, 1 litre mustard oil\" -> Watch instant bill appear in 1.2 seconds."),
        ("Step 2 (Credit Khata): ", "Speak \"1 kg basmati rice Suresh udhaar\" -> Customer khata ledger debited automatically."),
        ("Step 3 (Low Stock): ", "Inventory falls below 5kg threshold -> Instant amber low-stock alert triggers on screen."),
        ("Step 4 (Thermal Print): ", "One-click print dispatches itemized slip to simulated ESC/POS thermal printer.")
    ]
    for st, sd in demo_steps:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + st; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    add_card(s6, Inches(0.65) + card_w + card_gap, Inches(1.25), card_w, Inches(2.35), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80) + card_w + card_gap, Inches(1.35), Inches(1.50), Inches(0.22), "TARGET BENCHMARKS", C_ORANGE)
    _, tf = add_tb(s6, Inches(0.75) + card_w + card_gap, Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "EVALUATION TARGETS"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    metrics = [
        ("< 300ms ASR Latency: ", "Sub-second speech-to-text response on local CPU hardware."),
        ("> 95% Entity Extraction: ", "Accurate extraction of quantity, product name, and price."),
        ("0 KB Cloud Dependence: ", "Complete standalone execution with Wi-Fi/cellular turned OFF."),
        ("< 35MB Model Footprint: ", "Ultra-lightweight quantized neural model runs on 1GB RAM.")
    ]
    for mt, md in metrics:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + mt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_GREEN
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    add_card(s6, Inches(0.65) + (card_w + card_gap) * 2, Inches(1.25), card_w, Inches(2.35), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80) + (card_w + card_gap) * 2, Inches(1.35), Inches(1.40), Inches(0.22), "STAKEHOLDERS", C_BLUE)
    _, tf = add_tb(s6, Inches(0.75) + (card_w + card_gap) * 2, Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "WHO BENEFITS?"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_BLUE
    stakeholders = [
        ("Kirana & Provision Stores: ", "Instant hands-free billing during peak morning and evening rush hours."),
        ("Vegetable & Fruit Vendors: ", "Rapid itemized calculation without paper notes or mental arithmetic errors."),
        ("Rural Customers: ", "Transparent itemized thermal printed receipts with clear credit records."),
        ("FMCG Wholesalers: ", "Timely stock replenishment orders generated automatically every night.")
    ]
    for st, sd in stakeholders:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + st; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    add_card(s6, Inches(0.65), Inches(3.75), Inches(12.03), Inches(2.65), C_WHITE, C_CARD_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80), Inches(3.85), Inches(1.80), Inches(0.24), "24-HOUR SPRINT TIMELINE", C_ORANGE)
    _, tf = add_tb(s6, Inches(0.75), Inches(4.15), Inches(11.83), Inches(0.35))
    p = tf.paragraphs[0]; p.text = "RIGOROUS 24-HOUR HACKATHON EXECUTION ROADMAP"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_DARK

    phases = [
        ("PHASE 1: 00:00 \u2014 06:00", "OFFLINE ASR & MODEL SETUP",
         "\u2022 Vosk quantized Indian English/Hindi model setup.\n\u2022 Local audio capture stream (PyAudio / SoundDevice).\n\u2022 Word error rate benchmarking on edge CPU."),
        ("PHASE 2: 06:00 \u2014 12:00", "NLP & SLOT-FILLING ENGINE",
         "\u2022 Entity regex parser (item, quantity, price, customer).\n\u2022 Currency & unit normalizer (kg, g, packet, litre).\n\u2022 Khata credit vs. cash classifier."),
        ("PHASE 3: 12:00 \u2014 18:00", "SQLITE LEDGER & THERMAL BILL",
         "\u2022 Schema design (products, customers, transactions).\n\u2022 Instant thermal receipt generator + UPI QR code.\n\u2022 Automated low-stock trigger logic."),
        ("PHASE 4: 18:00 \u2014 24:00", "UI POLISH & LIVE MIC REHEARSAL",
         "\u2022 Streamlit merchant dashboard with live audio waveform.\n\u2022 Multi-dialect testing (Hindi, Kannada, Hinglish).\n\u2022 Final live demo script rehearsal with 5 rapid entries.")
    ]
    p_w = Inches(2.88); p_gap = Inches(0.12)
    for p_idx, (p_title, p_sub, p_desc) in enumerate(phases):
        p_left = Inches(0.80) + (p_w + p_gap) * p_idx
        add_card(s6, p_left, Inches(4.55), p_w, Inches(1.70), C_GREEN_LIGHT if p_idx % 2 == 0 else C_ORANGE_LIGHT, C_GREEN_BORDER if p_idx % 2 == 0 else C_ORANGE_BORDER, 1.0)
        _, tf_p = add_tb(s6, p_left + Inches(0.1), Inches(4.60), p_w - Inches(0.2), Inches(1.60), ml=0.02, mr=0.02)
        p = tf_p.paragraphs[0]; p.text = p_title; p.font.name = FONT; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = C_GREEN if p_idx % 2 == 0 else C_ORANGE_DARK
        p2 = tf_p.add_paragraph(); p2.space_before = Pt(1); p2.text = p_sub; p2.font.name = FONT; p2.font.size = Pt(9.5); p2.font.bold = True; p2.font.color.rgb = C_DARK
        p3 = tf_p.add_paragraph(); p3.space_before = Pt(2); p3.text = p_desc; p3.font.name = FONT; p3.font.size = Pt(8.5); p3.font.color.rgb = C_CHARCOAL

    # Slide 7: Conclusion & References
    s7 = prs.slides[6]
    setup_slide_header(s7, "Conclusion & References",
                       "Dignity, Speed, and Financial Health for Bharat's Backbone Retailers.",
                       "\"Bringing edge intelligence to the kirana counter without requiring English or internet.\"")

    add_card(s7, Inches(0.65), Inches(1.25), Inches(5.15), Inches(3.05), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(1.35), Inches(1.30), Inches(0.24), "CORE SUMMARY", C_GREEN)
    _, tf_k = add_tb(s7, Inches(0.75), Inches(1.65), Inches(4.95), Inches(2.55))
    p = tf_k.paragraphs[0]; p.text = "KEY TAKEAWAYS"; p.font.name = FONT; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_GREEN
    takeaways = [
        ("Zero Typing Barrier: ", "Shopkeepers simply speak naturally; VoiceKirana generates itemized bills in under 3 seconds."),
        ("100% Offline Autonomy: ", "Complete immunity from cellular outages; merchant records stay private on the device."),
        ("Credit & Stock Clarity: ", "Eliminates \u20B91,25,000 monthly credit leaks and alerts merchants before staples run out of stock."),
        ("Zero Hardware Cost: ", "Runs on any budget Android phone or existing merchant tablet with zero subscription fees.")
    ]
    for kt, kd in takeaways:
        pb = tf_k.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + kt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = kd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s7, Inches(5.95), Inches(1.25), Inches(6.73), Inches(3.05), C_SLATE_800, C_CARD_BORDER, 1.2)
    s7.shapes.add_picture('voicekirana_badge.jpg', Inches(5.98), Inches(1.28), Inches(6.67), Inches(2.99))

    add_card(s7, Inches(0.65), Inches(4.40), Inches(12.03), Inches(1.95), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(4.50), Inches(1.60), Inches(0.24), "TECHNICAL EVIDENCE", C_BLUE)
    _, tf_rf = add_tb(s7, Inches(0.75), Inches(4.80), Inches(11.83), Inches(1.50))
    p = tf_rf.paragraphs[0]; p.text = "VERIFIABLE REFERENCES & EDGE AI BENCHMARKS"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_BLUE

    _, tf_c1 = add_tb(s7, Inches(0.75), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col1 = [
        ("1. Vosk Offline ASR Architecture: ", "Kaldi-Based Lightweight Speech Recognition for Embedded Devices (AlphaCephei)."),
        ("2. TensorFlow Lite Quantization: ", "Quantized Neural Network Inference for Microcontrollers and Edge Hardware."),
        ("3. SQLite Embedded Database: ", "ACID Compliance and Crash-Proof Storage in Disconnected Environments.")
    ]
    for r_num, r_text in ref_col1:
        p = tf_c1.add_paragraph() if tf_c1.paragraphs[0].text else tf_c1.paragraphs[0]
        p.space_before = Pt(1)
        r1 = p.add_run(); r1.text = r_num; r1.font.name = FONT; r1.font.size = Pt(9.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = p.add_run(); r2.text = r_text; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    _, tf_c2 = add_tb(s7, Inches(6.80), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col2 = [
        ("4. National Retail Federation Report: ", "Digitization and Informal Credit Dynamics in Indian Unorganized Retail."),
        ("5. ESC/POS Protocol Standard: ", "Binary Command Set for Point of Sale Thermal Printing Systems."),
        ("6. NPCI UPI Offline Specification: ", "Dynamic QR Code Generation for Contactless Merchant Payments.")
    ]
    for r_num, r_text in ref_col2:
        p = tf_c2.add_paragraph() if tf_c2.paragraphs[0].text else tf_c2.paragraphs[0]
        p.space_before = Pt(1)
        r1 = p.add_run(); r1.text = r_num; r1.font.name = FONT; r1.font.size = Pt(9.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = p.add_run(); r2.text = r_text; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    prs.save('AI_Avengers_Theme05_VoiceKirana.pptx')
    print("Saved: AI_Avengers_Theme05_VoiceKirana.pptx")


# ==============================================================================
# DECK 2: SCAMSENTRY (Theme 02: Trust, Privacy & Digital Provenance)
# ==============================================================================
def build_deck_2_scamsentry():
    prs = Presentation('AfterHours_1.0_PPT_Template.pptx')
    if len(prs.slides) > 7:
        rId = prs.slides._sldIdLst[7].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[7]

    # Slide 1: Cover
    populate_slide_1(prs.slides[0],
                     "THEME 02: TRUST, PRIVACY & DIGITAL PROVENANCE",
                     "SCAMSENTRY",
                     "Multi-Modal Provenance & Forensic Defense Against Job, Scholarship & UPI Fraud",
                     "Zero-trust verification for offer letters, UPI payment receipts, and viral WhatsApp forward scams.")

    # Slide 2: Problem Statement & Relevance
    s2 = prs.slides[1]
    setup_slide_header(s2, "Problem Statement & Its Relevance",
                       "The Rampant Epidemic of Digital Impersonation & Payment Spoofing.",
                       "Predatory scams exploit students, job seekers, and retailers \u2014 draining \u20B91,750+ Crores annually across India.")

    # Left: Exact Problem & Why it Matters
    add_card(s2, Inches(0.65), Inches(1.25), Inches(3.65), Inches(2.50), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(1.35), Inches(1.50), Inches(0.24), "RECRUITMENT SCAMS", C_RED)
    _, tf = add_tb(s2, Inches(0.75), Inches(1.65), Inches(3.45), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "PREDATORY JOB OFFERS"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_RED
    probs = [
        ("Bogus Offer Letters: ", "Fraudsters forge Tier-1 IT (TCS, Infosys) letters demanding \u20B91,500 - \u20B915,000 \"laptop security fees\"."),
        ("Typosquatted Domains: ", "Recruiters use spoofed domains like careers-tcs-india.net registered <30 days ago."),
        ("Targeting the Vulnerable: ", "Exploits fresh graduates desperate for campus placements and internships.")
    ]
    for pt, pd in probs:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + pt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = pd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(0.65), Inches(3.85), Inches(3.65), Inches(2.50), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(3.95), Inches(1.50), Inches(0.24), "PAYMENT & SCHEMES", C_ORANGE)
    _, tf = add_tb(s2, Inches(0.75), Inches(4.25), Inches(3.45), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "FORGED UPI & GHOST SCHEMES"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    matters = [
        ("Counterfeit UPI Receipts: ", "Spoof APKs generate pixel-perfect fake \"Payment Successful\" screens duping merchants."),
        ("Ghost Scholarships: ", "Phishing links mimicking National Scholarship Portal (NSP) harvest Aadhaar & bank OTPs."),
        ("Irreversible Loss: ", "Victims realize fraud only after giving away retail goods or seeing drained accounts.")
    ]
    for mt, md in matters:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + mt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Center: Gaps & Empirical Scale
    add_card(s2, Inches(4.45), Inches(1.25), Inches(4.45), Inches(2.50), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s2, Inches(4.60), Inches(1.35), Inches(1.40), Inches(0.24), "DEFENSE GAPS", C_BLUE)
    _, tf = add_tb(s2, Inches(4.55), Inches(1.65), Inches(4.25), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "WHY CURRENT TOOLS FAIL"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_BLUE
    gaps = [
        ("No Multi-Modal Ingestion: ", "Truecaller & SMS filters only check phone numbers; they cannot analyze PDFs or images."),
        ("HR Response Lag: ", "Corporate HR verification portals take 5 to 10 business days to confirm an offer."),
        ("Zero ELA Forensics: ", "Ordinary citizens cannot detect spliced fonts, edited timestamps, or fake UTR numbers.")
    ]
    for gt, gd in gaps:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + gt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = gd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(4.45), Inches(3.85), Inches(4.45), Inches(2.50), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s2, Inches(4.60), Inches(3.95), Inches(1.35), Inches(0.24), "EMPIRICAL SCALE", C_GREEN)
    _, tf = add_tb(s2, Inches(4.55), Inches(4.25), Inches(4.25), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "GROUND REALITY IN NUMBERS"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_GREEN
    empiricals = [
        ("\u20B91,750 Cr+ Annual Siphon: ", "Lost across India through fake employment onboarding drives and fraudulent portals."),
        ("4.2 Million Fake Offers: ", "Circulated annually via Telegram groups, WhatsApp recruiters, and spam emails."),
        ("68% Non-Reporting Rate: ", "Victims feel shame or lack evidence, allowing organized scam rings to thrive unchecked.")
    ]
    for et, ed in empiricals:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + et; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = ed; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Right: Metric Cards
    metrics = [
        ("\u20B91,750 Cr", "Annual Scam Loss", "Reported digital recruitment & payment fraud in India", C_RED),
        ("4.2M+", "Phishing Targets", "Students & fresh graduates targeted by fake job drives", C_ORANGE),
        ("< 30 Days", "Domain Lifespan", "Average operational lifespan of lookalike phishing sites", C_BLUE)
    ]
    card_h = Inches(1.60); gap_h = Inches(0.15)
    for idx, (m_val, m_lbl, m_sub, m_col) in enumerate(metrics):
        top_pos = Inches(1.25) + idx * (card_h + gap_h)
        add_card(s2, Inches(9.05), top_pos, Inches(3.63), card_h, C_WHITE, C_CARD_BORDER, 1.0)
        _, tf_m = add_tb(s2, Inches(9.15), top_pos + Inches(0.10), Inches(3.43), card_h - Inches(0.20))
        p = tf_m.paragraphs[0]; p.text = m_val; p.font.name = FONT; p.font.size = Pt(32); p.font.bold = True; p.font.color.rgb = m_col
        p2 = tf_m.add_paragraph(); p2.space_before = Pt(1); p2.text = m_lbl; p2.font.name = FONT; p2.font.size = Pt(12); p2.font.bold = True; p2.font.color.rgb = C_DARK
        p3 = tf_m.add_paragraph(); p3.space_before = Pt(1); p3.text = m_sub; p3.font.name = FONT; p3.font.size = Pt(10); p3.font.color.rgb = C_MUTED

    # Slide 3: Proposed Solution & Core Innovation
    s3 = prs.slides[2]
    setup_slide_header(s3, "Proposed Solution & Core Innovation",
                       "Zero-Trust Multi-Modal Forensics: Document, Domain & Image Provenance.",
                       "Upload an offer letter PDF, WhatsApp forward, or payment screenshot \u2014 receive an explainable verdict in seconds.")

    pillars = [
        ("MULTI-MODAL INGESTION", "Unified Document & Media Gateway",
         "Accepts PDF offer letters, email headers, WhatsApp forwards, and screenshot images through web drop and automated bots.",
         C_RED),
        ("DOMAIN PROVENANCE SENTINEL", "WHOIS & Infrastructure Intelligence",
         "Inspects sender domain creation date (<30 days = red flag), SPF/DKIM records, and corporate registry typosquatting.",
         C_ORANGE_DARK),
        ("IMAGE FORENSICS & ELA", "Error Level Analysis & Font Kerning",
         "Detects compression discontinuities and font baselines in UPI screenshots to expose edited transaction amounts.",
         C_BLUE),
        ("EXPLAINABLE EVIDENCE ENGINE", "Actionable Risk Score & Family Bot",
         "Delivers a 0-100% Risk Index citing legal violations (IPC 420) and provides an automated WhatsApp forward bot for families.",
         C_GREEN)
    ]
    w_p = Inches(2.78); h_p = Inches(2.05); gap_p = Inches(0.12)
    for idx, (p_pill, p_title, p_desc, p_col) in enumerate(pillars):
        col = idx % 2; row = idx // 2
        l = Inches(0.65) + col * (w_p + gap_p)
        t = Inches(1.25) + row * (h_p + gap_p)
        add_card(s3, l, t, w_p, h_p, C_WHITE, C_CARD_BORDER, 1.0)
        add_pill_badge(s3, l + Inches(0.15), t + Inches(0.10), Inches(1.70), Inches(0.22), p_pill, p_col)
        _, tf_p = add_tb(s3, l + Inches(0.15), t + Inches(0.35), w_p - Inches(0.30), h_p - Inches(0.40))
        p = tf_p.paragraphs[0]; p.text = p_title; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_DARK
        p2 = tf_p.add_paragraph(); p2.space_before = Pt(2); p2.text = p_desc; p2.font.name = FONT; p2.font.size = Pt(10); p2.font.color.rgb = C_CHARCOAL

    # Right: Dashboard Picture
    add_card(s3, Inches(6.50), Inches(1.25), Inches(6.18), Inches(4.25), C_WHITE, C_RED_BORDER, 1.2)
    s3.shapes.add_picture('scamsentry_dashboard.jpg', Inches(6.53), Inches(1.28), Inches(6.12), Inches(4.19))

    # Bottom 3 Highlight Cards
    metric_w = Inches(3.90); col_gap = Inches(0.16)
    add_card(s3, Inches(0.65), Inches(5.65), metric_w, Inches(0.75), C_WHITE, C_CARD_BORDER, 1.0)
    _, tf_m1 = add_tb(s3, Inches(0.75), Inches(5.70), metric_w - Inches(0.2), Inches(0.65))
    p = tf_m1.paragraphs[0]; p.text = "< 2.5s MULTI-MODAL VERDICT"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_RED
    p_sub = tf_m1.add_paragraph(); p_sub.text = "Sub-second OCR, domain lookup, and ELA image forensics running in parallel."; p_sub.font.name = FONT; p_sub.font.size = Pt(9.5); p_sub.font.color.rgb = C_MUTED

    add_card(s3, Inches(0.65) + metric_w + col_gap, Inches(5.65), metric_w, Inches(0.75), C_WHITE, C_CARD_BORDER, 1.0)
    _, tf_m2 = add_tb(s3, Inches(0.75) + metric_w + col_gap, Inches(5.70), metric_w - Inches(0.2), Inches(0.65))
    p = tf_m2.paragraphs[0]; p.text = "SPLICED UPI IMAGE DETECTION"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    p_sub = tf_m2.add_paragraph(); p_sub.text = "Pinpoints tampered digits and font mismatches generated by fake payment APKs."; p_sub.font.name = FONT; p_sub.font.size = Pt(9.5); p_sub.font.color.rgb = C_MUTED

    add_card(s3, Inches(0.65) + (metric_w + col_gap) * 2, Inches(5.65), metric_w, Inches(0.75), C_WHITE, C_CARD_BORDER, 1.0)
    _, tf_m3 = add_tb(s3, Inches(0.75) + (metric_w + col_gap) * 2, Inches(5.70), metric_w - Inches(0.2), Inches(0.65))
    p = tf_m3.paragraphs[0]; p.text = "WHATSAPP FAMILY SHIELD"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_GREEN
    p_sub = tf_m3.add_paragraph(); p_sub.text = "Zero friction: forward suspicious forwards directly to WhatsApp bot for check."; p_sub.font.name = FONT; p_sub.font.size = Pt(9.5); p_sub.font.color.rgb = C_MUTED

    # Slide 4: Existing Solutions & Differentiation
    s4 = prs.slides[3]
    setup_slide_header(s4, "Existing Solutions & Differentiation",
                       "Why Generic Anti-Spam Tools Fail Against Modern Socio-Technical Fraud.",
                       "Comparing ScamSentry against Truecaller, manual HR checks, and antivirus software.")

    add_card(s4, Inches(0.65), Inches(1.25), Inches(5.15), Inches(5.15), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s4, Inches(0.80), Inches(1.35), Inches(1.65), Inches(0.24), "TRADITIONAL BOTTLENECK", C_RED)
    _, tf_ex = add_tb(s4, Inches(0.75), Inches(1.65), Inches(4.95), Inches(0.35))
    p = tf_ex.paragraphs[0]; p.text = "LEGACY DEFENSES & BLIND SPOTS"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_RED

    s4.shapes.add_picture('scamsentry_comparison.jpg', Inches(0.80), Inches(2.05), Inches(4.85), Inches(2.70))

    _, tf_sub = add_tb(s4, Inches(0.80), Inches(4.85), Inches(4.85), Inches(1.45), ml=0.02, mr=0.02)
    p_sum = tf_sub.paragraphs[0]
    p_sum.text = "\u2022 Phone Blacklists (Truecaller): Only flags reported phone numbers; blind to PDFs and image files."
    p_sum.font.name = FONT; p_sum.font.size = Pt(10.5); p_sum.font.bold = True; p_sum.font.color.rgb = C_DARK
    p_sum2 = tf_sub.add_paragraph(); p_sum2.space_before = Pt(2)
    p_sum2.text = "\u2022 Manual HR Inquiries: Takes 5 to 10 days; fraudsters demand fees within 24 hours."
    p_sum2.font.name = FONT; p_sum2.font.size = Pt(10.5); p_sum2.font.bold = True; p_sum2.font.color.rgb = C_CHARCOAL
    p_sum3 = tf_sub.add_paragraph(); p_sum3.space_before = Pt(2)
    p_sum3.text = "\u2022 Merchant UPI Dilemma: Zero forensic tooling to verify fake Paytm / PhonePe screenshots."
    p_sum3.font.name = FONT; p_sum3.font.size = Pt(10.5); p_sum3.font.bold = True; p_sum3.font.color.rgb = C_RED

    add_card(s4, Inches(6.05), Inches(1.25), Inches(6.63), Inches(5.15), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s4, Inches(6.20), Inches(1.35), Inches(1.65), Inches(0.24), "FEATURE MATRIX", C_GREEN)
    _, tf_diff = add_tb(s4, Inches(6.15), Inches(1.65), Inches(6.43), Inches(0.35))
    p = tf_diff.paragraphs[0]; p.text = "BENCHMARK: SCAMSENTRY VS ALTERNATIVES"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_GREEN

    table_shape = s4.shapes.add_table(6, 5, Inches(6.15), Inches(2.05), Inches(6.43), Inches(3.20))
    table = table_shape.table
    table.columns[0].width = Inches(1.85); table.columns[1].width = Inches(1.10)
    table.columns[2].width = Inches(1.10); table.columns[3].width = Inches(1.10); table.columns[4].width = Inches(1.28)

    headers = ["Capabilities", "Truecaller", "HR Helplines", "Antivirus", "ScamSentry"]
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid(); cell.fill.fore_color.rgb = C_DARK if c_idx < 4 else C_GREEN
        p = cell.text_frame.paragraphs[0]; p.text = h_text; p.font.name = FONT; p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    m_data = [
        ("PDF Offer Letter Forensics", "None", "Manual Scan", "None", "Instant OCR+NLP"),
        ("Fake UPI Screenshot ELA", "None", "None", "None", "OpenCV Heatmap"),
        ("Domain Age Provenance", "None", "Manual Check", "Known URL Only", "Automated WHOIS"),
        ("WhatsApp Forward Shield", "SMS Only", "None", "None", "Instant Bot Reply"),
        ("Explainable Legal Red Flags", "Spam Tag", "Slow Memo", "Heuristic Tag", "Cited Law Evidence")
    ]
    for r_idx, row_vals in enumerate(m_data):
        for c_idx, val in enumerate(row_vals):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if c_idx == 4:
                cell.fill.fore_color.rgb = C_GREEN_LIGHT
            elif r_idx % 2 == 0:
                cell.fill.fore_color.rgb = C_WHITE
            else:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)

            p = cell.text_frame.paragraphs[0]; p.text = val; p.font.name = FONT; p.font.size = Pt(9.5)
            if c_idx == 4:
                p.font.bold = True; p.font.color.rgb = C_GREEN
            elif "None" in val or "Slow" in val or "Manual" in val:
                p.font.color.rgb = C_RED
            else:
                p.font.color.rgb = C_CHARCOAL
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    _, tf_adv = add_tb(s4, Inches(6.15), Inches(5.35), Inches(6.43), Inches(0.95), ml=0.02, mr=0.02)
    p = tf_adv.paragraphs[0]; p.text = "CORE COMPETITIVE ADVANTAGE"; p.font.name = FONT; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_DARK
    p_b1 = tf_adv.add_paragraph(); p_b1.space_before = Pt(1)
    r1 = p_b1.add_run(); r1.text = "\u2022 Multi-Modal Triangulation: "; r1.font.bold = True; r1.font.color.rgb = C_GREEN
    r2 = p_b1.add_run(); r2.text = "Simultaneously audits text semantics, image pixels, and server infrastructure."; r2.font.color.rgb = C_CHARCOAL
    p_b2 = tf_adv.add_paragraph(); p_b2.space_before = Pt(1)
    r1 = p_b2.add_run(); r1.text = "\u2022 Zero Installation Barrier: "; r1.font.bold = True; r1.font.color.rgb = C_BLUE
    r2 = p_b2.add_run(); r2.text = "Operates directly via web and WhatsApp without requiring specialized software."; r2.font.color.rgb = C_CHARCOAL

    # Slide 5: Technical Architecture & System Flow
    s5 = prs.slides[4]
    setup_slide_header(s5, "Technical Architecture & System Flow",
                       "5-Layer Multi-Modal Cybersecurity Pipeline with Explainable Telemetry.",
                       "Modular ingestion pipeline: Input Stream -> Multi-Modal Parser -> Forensic Engine -> Threat OSINT -> Risk Score.")

    add_card(s5, Inches(0.65), Inches(1.25), Inches(5.65), Inches(5.15), C_WHITE, C_CARD_BORDER, 1.2)
    s5.shapes.add_picture('scamsentry_architecture.jpg', Inches(0.68), Inches(1.28), Inches(5.59), Inches(5.09))

    layers = [
        ("LAYER 1: MULTI-MODAL GATEWAY", "File, Link & Webhook Ingestion",
         "Captures PDF documents, PNG/JPEG screenshots, raw email headers, and WhatsApp forward payloads via FastAPI.",
         C_RED),
        ("LAYER 2: TEXT & METADATA OCR", "PyMuPDF, Tesseract & Entity Extractor",
         "Extracts text layers, checks font embedded tables, parses banking details, and identifies fee demand clauses.",
         C_ORANGE_DARK),
        ("LAYER 3: VISUAL ELA FORENSICS", "OpenCV Error Level Analysis Engine",
         "Computes JPEG compression delta heatmaps and examines font baseline alignment to detect digitally altered text.",
         C_BLUE),
        ("LAYER 4: THREAT INTELLIGENCE", "WHOIS, DNS & Corporate Registry",
         "Performs live RDAP domain lookup, checks registration age (<30 days flag), MX record validity, and SPF/DMARC.",
         C_GREEN),
        ("LAYER 5: RISK SCORING ENGINE", "Ensemble Risk Scorer & PDF Reporter",
         "Fuses multi-modal signals into a 0-100% Risk Index with cited legal red flags and generates shareable PDF audit slips.",
         C_PURPLE)
    ]
    card_lh = Inches(0.96); gap_lh = Inches(0.08)
    for l_idx, (l_pill, l_title, l_desc, l_col) in enumerate(layers):
        top_l = Inches(1.25) + l_idx * (card_lh + gap_lh)
        add_card(s5, Inches(6.50), top_l, Inches(6.18), card_lh, C_WHITE, C_CARD_BORDER, 1.0)
        add_pill_badge(s5, Inches(6.60), top_l + Inches(0.08), Inches(1.85), Inches(0.20), l_pill, l_col)
        _, tf_l = add_tb(s5, Inches(6.60), top_l + Inches(0.26), Inches(5.98), card_lh - Inches(0.30), mt=0.01, mb=0.01)
        p = tf_l.paragraphs[0]; p.text = l_title; p.font.name = FONT; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_DARK
        p2 = tf_l.add_paragraph(); p2.space_before = Pt(1); p2.text = l_desc; p2.font.name = FONT; p2.font.size = Pt(9.5); p2.font.color.rgb = C_CHARCOAL

    # Slide 6: Feasibility, 24-Hour Roadmap & Societal Impact
    s6 = prs.slides[5]
    setup_slide_header(s6, "Feasibility, 24-Hour Roadmap & Societal Impact",
                       "Rapid Hackathon Implementation, Live Battle Testing & Citizen Protection.",
                       "Engineered for high-impact live judging: compare a genuine TCS offer vs a scam letter side-by-side.")

    card_w = Inches(3.88); card_gap = Inches(0.20)
    add_card(s6, Inches(0.65), Inches(1.25), card_w, Inches(2.35), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80), Inches(1.35), Inches(1.40), Inches(0.22), "LIVE PROTOTYPE", C_RED)
    _, tf = add_tb(s6, Inches(0.75), Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "LIVE HACKATHON DEMO PLAN"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_RED
    demo_steps = [
        ("Demo 1 (Fake Job Offer): ", "Upload forged TCS PDF demanding \u20B93,500 training fee -> 94% Risk Score + Domain Flag."),
        ("Demo 2 (Genuine Job Offer): ", "Upload genuine Infosys onboarding letter -> 4% Risk Score, Verified official domain."),
        ("Demo 3 (Fake UPI Screenshot): ", "Drop spoofed Paytm screenshot -> ELA highlights tampered amount and mismatched font."),
        ("Demo 4 (WhatsApp Bot): ", "Forward viral scholarship link via WhatsApp -> Instant 3-second safety advisory returned.")
    ]
    for st, sd in demo_steps:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + st; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    add_card(s6, Inches(0.65) + card_w + card_gap, Inches(1.25), card_w, Inches(2.35), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80) + card_w + card_gap, Inches(1.35), Inches(1.50), Inches(0.22), "TARGET BENCHMARKS", C_ORANGE)
    _, tf = add_tb(s6, Inches(0.75) + card_w + card_gap, Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "EVALUATION TARGETS"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    metrics = [
        ("< 2.5s Verification Time: ", "End-to-end multi-modal forensics pipeline turnaround."),
        ("98.4% Tamper Accuracy: ", "Detection rate on spliced UPI receipts and lookalike domains."),
        ("\u20B90 API Operational Cost: ", "Runs entirely on local open-source models & free OSINT feeds."),
        ("Zero False Positives: ", "Rigorous whitelisting ensures authentic corporate offers are cleared.")
    ]
    for mt, md in metrics:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + mt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_GREEN
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    add_card(s6, Inches(0.65) + (card_w + card_gap) * 2, Inches(1.25), card_w, Inches(2.35), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80) + (card_w + card_gap) * 2, Inches(1.35), Inches(1.40), Inches(0.22), "STAKEHOLDERS", C_BLUE)
    _, tf = add_tb(s6, Inches(0.75) + (card_w + card_gap) * 2, Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "WHO BENEFITS?"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_BLUE
    stakeholders = [
        ("Engineering Students: ", "Protection against fake recruitment drives, training fees, and lost deposits."),
        ("Retail Shopkeepers: ", "Instant detection of spoofed payment screenshots before handing over merchandise."),
        ("Non-Technical Families: ", "Frictionless WhatsApp forward checking for elderly parents and relatives."),
        ("College Placement Cells: ", "Automated batch screening of recruitment emails and company domains.")
    ]
    for st, sd in stakeholders:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + st; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    add_card(s6, Inches(0.65), Inches(3.75), Inches(12.03), Inches(2.65), C_WHITE, C_CARD_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80), Inches(3.85), Inches(1.80), Inches(0.24), "24-HOUR SPRINT TIMELINE", C_ORANGE)
    _, tf = add_tb(s6, Inches(0.75), Inches(4.15), Inches(11.83), Inches(0.35))
    p = tf.paragraphs[0]; p.text = "RIGOROUS 24-HOUR HACKATHON EXECUTION ROADMAP"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_DARK

    phases = [
        ("PHASE 1: 00:00 \u2014 06:00", "INGESTION & OCR PIPELINE",
         "\u2022 Streamlit upload UI + WhatsApp webhook listener.\n\u2022 PyMuPDF text & vector extraction engine.\n\u2022 Tesseract OCR pipeline for scanned images."),
        ("PHASE 2: 06:00 \u2014 12:00", "ELA FORENSICS & DOMAIN OSINT",
         "\u2022 OpenCV Error Level Analysis compression heatmaps.\n\u2022 WHOIS & RDAP domain creation date checker.\n\u2022 Font kerning and baseline alignment auditor."),
        ("PHASE 3: 12:00 \u2014 18:00", "RISK ENGINE & EXPLAINABILITY",
         "\u2022 Ensemble 0-100% Risk Score heuristic model.\n\u2022 Legal citation mapper (IPC 420, IT Act Section 66D).\n\u2022 Automated forensic evidence summary generator."),
        ("PHASE 4: 18:00 \u2014 24:00", "BENCHMARKING & LIVE BATTLE DEMO",
         "\u2022 Test suite: 10 authentic vs 10 spoofed test cases.\n\u2022 WhatsApp bot stress testing and latency tuning.\n\u2022 Live pitch deck rehearsal with side-by-side demo.")
    ]
    p_w = Inches(2.88); p_gap = Inches(0.12)
    for p_idx, (p_title, p_sub, p_desc) in enumerate(phases):
        p_left = Inches(0.80) + (p_w + p_gap) * p_idx
        add_card(s6, p_left, Inches(4.55), p_w, Inches(1.70), C_RED_LIGHT if p_idx % 2 == 0 else C_ORANGE_LIGHT, C_RED_BORDER if p_idx % 2 == 0 else C_ORANGE_BORDER, 1.0)
        _, tf_p = add_tb(s6, p_left + Inches(0.1), Inches(4.60), p_w - Inches(0.2), Inches(1.60), ml=0.02, mr=0.02)
        p = tf_p.paragraphs[0]; p.text = p_title; p.font.name = FONT; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = C_RED if p_idx % 2 == 0 else C_ORANGE_DARK
        p2 = tf_p.add_paragraph(); p2.space_before = Pt(1); p2.text = p_sub; p2.font.name = FONT; p2.font.size = Pt(9.5); p2.font.bold = True; p2.font.color.rgb = C_DARK
        p3 = tf_p.add_paragraph(); p3.space_before = Pt(2); p3.text = p_desc; p3.font.name = FONT; p3.font.size = Pt(8.5); p3.font.color.rgb = C_CHARCOAL

    # Slide 7: Conclusion & References
    s7 = prs.slides[6]
    setup_slide_header(s7, "Conclusion & References",
                       "Restoring Digital Trust for Students, Job Seekers & Merchants.",
                       "\"Defending vulnerable citizens against cyber predation through transparent, multi-modal forensics.\"")

    add_card(s7, Inches(0.65), Inches(1.25), Inches(5.15), Inches(3.05), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(1.35), Inches(1.30), Inches(0.24), "CORE SUMMARY", C_RED)
    _, tf_k = add_tb(s7, Inches(0.75), Inches(1.65), Inches(4.95), Inches(2.55))
    p = tf_k.paragraphs[0]; p.text = "KEY TAKEAWAYS"; p.font.name = FONT; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_RED
    takeaways = [
        ("Multi-Modal Protection: ", "Analyzes PDFs, images, WhatsApp forwards, and domain links in a unified zero-trust tool."),
        ("Spliced Payment Detection: ", "First accessible tool detecting fake UPI screenshots via Error Level Analysis."),
        ("Domain Age Intelligence: ", "Immediately catches 99% of job scams by flagging domains created under 30 days ago."),
        ("Frictionless Family Bot: ", "Empowers non-tech-savvy parents and students via direct WhatsApp forward checking.")
    ]
    for kt, kd in takeaways:
        pb = tf_k.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + kt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = kd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s7, Inches(5.95), Inches(1.25), Inches(6.73), Inches(3.05), C_SLATE_800, C_CARD_BORDER, 1.2)
    s7.shapes.add_picture('scamsentry_badge.jpg', Inches(5.98), Inches(1.28), Inches(6.67), Inches(2.99))

    add_card(s7, Inches(0.65), Inches(4.40), Inches(12.03), Inches(1.95), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(4.50), Inches(1.60), Inches(0.24), "TECHNICAL EVIDENCE", C_BLUE)
    _, tf_rf = add_tb(s7, Inches(0.75), Inches(4.80), Inches(11.83), Inches(1.50))
    p = tf_rf.paragraphs[0]; p.text = "VERIFIABLE REFERENCES & CYBER FORENSICS BENCHMARKS"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_BLUE

    _, tf_c1 = add_tb(s7, Inches(0.75), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col1 = [
        ("1. CERT-In Cyber Security Advisory: ", "Analysis of Recruitment Phishing and Digital Employment Fraud Patterns in India."),
        ("2. Error Level Analysis (ELA) Research: ", "Digital Image Tampering Detection via JPEG Compression Analysis (IEEE)."),
        ("3. Indian Penal Code & IT Act 2000: ", "Provisions on Impersonation (Sec 66D) and Fraudulent Financial Inducement (Sec 420).")
    ]
    for r_num, r_text in ref_col1:
        p = tf_c1.add_paragraph() if tf_c1.paragraphs[0].text else tf_c1.paragraphs[0]
        p.space_before = Pt(1)
        r1 = p.add_run(); r1.text = r_num; r1.font.name = FONT; r1.font.size = Pt(9.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = p.add_run(); r2.text = r_text; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    _, tf_c2 = add_tb(s7, Inches(6.80), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col2 = [
        ("4. ICANN RDAP & WHOIS Specification: ", "Automated Domain Registration Date Verification and Registrar Threat Intelligence."),
        ("5. National Cyber Crime Reporting Portal: ", "Annual Modus Operandi Report on UPI Spoofing and Fake Transaction Receipts."),
        ("6. Optical Character Recognition Standards: ", "LayoutLM & Tesseract Multimodal Information Extraction from Structured Documents.")
    ]
    for r_num, r_text in ref_col2:
        p = tf_c2.add_paragraph() if tf_c2.paragraphs[0].text else tf_c2.paragraphs[0]
        p.space_before = Pt(1)
        r1 = p.add_run(); r1.text = r_num; r1.font.name = FONT; r1.font.size = Pt(9.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = p.add_run(); r2.text = r_text; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    prs.save('AI_Avengers_Theme02_ScamSentry.pptx')
    print("Saved: AI_Avengers_Theme02_ScamSentry.pptx")


# ==============================================================================
# DECK 3: DATAHEAL (Theme 04: Self-Healing Systems & Autonomous Infrastructure)
# ==============================================================================
def build_deck_3_dataheal():
    prs = Presentation('AfterHours_1.0_PPT_Template.pptx')
    if len(prs.slides) > 7:
        rId = prs.slides._sldIdLst[7].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[7]

    # Slide 1: Cover
    populate_slide_1(prs.slides[0],
                     "THEME 04: SELF-HEALING SYSTEMS & AUTONOMOUS INFRASTRUCTURE",
                     "DATAHEAL",
                     "Autonomous Self-Healing Engine Rescuing Broken Spreadsheets & Silent ETL Failures",
                     "Zero-intervention schema repair, semantic re-mapping, and intelligent row quarantine for enterprise data pipelines.")

    # Slide 2: Problem Statement & Relevance
    s2 = prs.slides[1]
    setup_slide_header(s2, "Problem Statement & Its Relevance",
                       "The Fragile Data Ingestion Bottleneck & Silent Pipeline Failures.",
                       "Data engineering teams waste 40% of their sprints debugging unannounced schema shifts, broken CSV headers, and corrupted rows.")

    # Left: Exact Problem & Why it Matters
    add_card(s2, Inches(0.65), Inches(1.25), Inches(3.65), Inches(2.50), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(1.35), Inches(1.50), Inches(0.24), "SCHEMA DRIFT", C_RED)
    _, tf = add_tb(s2, Inches(0.75), Inches(1.65), Inches(3.45), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "UNANNOUNCED SCHEMA DRIFTS"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_RED
    probs = [
        ("Arbitrary Header Renaming: ", "Upstream departments rename Customer_ID to Cust# or Client_ID without notice, breaking SQL ETLs."),
        ("Swapped Column Positions: ", "CSV exports with shifted column orders cause numbers to flow into text columns undetected."),
        ("Crashing Nightly DAGs: ", "Hard-coded schema assertions crash Airflow jobs, delaying critical executive dashboards.")
    ]
    for pt, pd in probs:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + pt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = pd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(0.65), Inches(3.85), Inches(3.65), Inches(2.50), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(3.95), Inches(1.50), Inches(0.24), "DIRTY SPREADSHEETS", C_ORANGE)
    _, tf = add_tb(s2, Inches(0.75), Inches(4.25), Inches(3.45), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "HUMAN EXCEL CORRUPTION"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    matters = [
        ("Mixed Date Dialects: ", "Single columns combining DD/MM/YYYY, MM-DD-YY, and epoch stamps crash standard parsers."),
        ("Currency Glyphs in Floats: ", "Dollar/Rupee symbols and commas ($1,250.00) cause silent type-casting exceptions."),
        ("Trailing Whitespace: ", "Rogue spaces create phantom duplicate records and violate primary key constraints.")
    ]
    for mt, md in matters:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + mt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Center: Gaps & Empirical Scale
    add_card(s2, Inches(4.45), Inches(1.25), Inches(4.45), Inches(2.50), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s2, Inches(4.60), Inches(1.35), Inches(1.40), Inches(0.24), "CURRENT GAPS", C_BLUE)
    _, tf = add_tb(s2, Inches(4.55), Inches(1.65), Inches(4.25), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "WHY CURRENT TOOLS FAIL"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_BLUE
    gaps = [
        ("Airflow / dbt Fail Hard: ", "Pipelines halt completely when a single row has bad syntax, starving entire organizations."),
        ("Silent Row Dropping: ", "Permissive parsers silently discard dirty records without alerting data owners."),
        ("Prohibitive Enterprise SaaS: ", "Monte Carlo and Great Expectations require months of manual rule configuration.")
    ]
    for gt, gd in gaps:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + gt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = gd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s2, Inches(4.45), Inches(3.85), Inches(4.45), Inches(2.50), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s2, Inches(4.60), Inches(3.95), Inches(1.35), Inches(0.24), "EMPIRICAL SCALE", C_GREEN)
    _, tf = add_tb(s2, Inches(4.55), Inches(4.25), Inches(4.25), Inches(2.00))
    p = tf.paragraphs[0]; p.text = "ENTERPRISE DOWNTIME METRICS"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_GREEN
    empiricals = [
        ("$15M Average Annual Loss: ", "Poor data quality costs mid-to-large enterprise organizations over $15M annually (Gartner)."),
        ("40% Engineer Sprints Lost: ", "Data engineers spend nearly half their working hours investigating schema breakages."),
        ("6-Hour Mean Time to Repair: ", "Average latency required to manually debug, repair, and re-trigger a failed ingestion batch.")
    ]
    for et, ed in empiricals:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + et; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = ed; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Right: Metric Cards
    metrics = [
        ("40%", "Engineer Time Lost", "Wasted on pipeline maintenance and broken CSV debugging", C_RED),
        ("6 Hours", "Average MTTR", "Time required to manually debug and replay failed ETL jobs", C_ORANGE),
        ("99.9%", "Target Resilience", "Operational pipeline uptime maintained via autonomous healing", C_BLUE)
    ]
    card_h = Inches(1.60); gap_h = Inches(0.15)
    for idx, (m_val, m_lbl, m_sub, m_col) in enumerate(metrics):
        top_pos = Inches(1.25) + idx * (card_h + gap_h)
        add_card(s2, Inches(9.05), top_pos, Inches(3.63), card_h, C_WHITE, C_CARD_BORDER, 1.0)
        _, tf_m = add_tb(s2, Inches(9.15), top_pos + Inches(0.10), Inches(3.43), card_h - Inches(0.20))
        p = tf_m.paragraphs[0]; p.text = m_val; p.font.name = FONT; p.font.size = Pt(32); p.font.bold = True; p.font.color.rgb = m_col
        p2 = tf_m.add_paragraph(); p2.space_before = Pt(1); p2.text = m_lbl; p2.font.name = FONT; p2.font.size = Pt(12); p2.font.bold = True; p2.font.color.rgb = C_DARK
        p3 = tf_m.add_paragraph(); p3.space_before = Pt(1); p3.text = m_sub; p3.font.name = FONT; p3.font.size = Pt(10); p3.font.color.rgb = C_MUTED

    # Slide 3: Proposed Solution & Core Innovation
    s3 = prs.slides[2]
    setup_slide_header(s3, "Proposed Solution & Core Innovation",
                       "Autonomous Schema Healing, Semantic Re-Mapping & Surgical Quarantine.",
                       "Ingest corrupted, drifting, or dirty CSV/Excel feeds \u2014 DataHeal repairs them on the fly with zero human downtime.")

    pillars = [
        ("SEMANTIC HEADER ALIGNMENT", "Embedding-Based Column Matcher",
         "Uses cosine similarity over column embeddings and fuzzy string matching to map renamed headers back to the golden schema.",
         C_RED),
        ("AUTOMATED TYPE COERCION", "Multi-Format Normalizer",
         "Strips currency symbols, harmonizes mixed date dialects using dateutil heuristics, and casts values to correct datatypes.",
         C_ORANGE_DARK),
        ("SURGICAL ROW QUARANTINE", "Non-Blocking Isolation Queue",
         "Routes unrecoverable outlier rows to quarantine.parquet with root-cause error logs, letting clean data flow uninterrupted.",
         C_BLUE),
        ("SELF-DOCUMENTING AUDIT", "Telemetry & Transformation Diffs",
         "Emits transparent JSON transformation audit diffs detailing every column re-map and value repair for compliance.",
         C_GREEN)
    ]
    w_p = Inches(2.78); h_p = Inches(2.05); gap_p = Inches(0.12)
    for idx, (p_pill, p_title, p_desc, p_col) in enumerate(pillars):
        col = idx % 2; row = idx // 2
        l = Inches(0.65) + col * (w_p + gap_p)
        t = Inches(1.25) + row * (h_p + gap_p)
        add_card(s3, l, t, w_p, h_p, C_WHITE, C_CARD_BORDER, 1.0)
        add_pill_badge(s3, l + Inches(0.15), t + Inches(0.10), Inches(1.70), Inches(0.22), p_pill, p_col)
        _, tf_p = add_tb(s3, l + Inches(0.15), t + Inches(0.35), w_p - Inches(0.30), h_p - Inches(0.40))
        p = tf_p.paragraphs[0]; p.text = p_title; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_DARK
        p2 = tf_p.add_paragraph(); p2.space_before = Pt(2); p2.text = p_desc; p2.font.name = FONT; p2.font.size = Pt(10); p2.font.color.rgb = C_CHARCOAL

    # Right: Dashboard Picture
    add_card(s3, Inches(6.50), Inches(1.25), Inches(6.18), Inches(4.25), C_WHITE, C_CYAN_BORDER, 1.2)
    s3.shapes.add_picture('dataheal_dashboard.jpg', Inches(6.53), Inches(1.28), Inches(6.12), Inches(4.19))

    # Bottom 3 Highlight Cards
    metric_w = Inches(3.90); col_gap = Inches(0.16)
    add_card(s3, Inches(0.65), Inches(5.65), metric_w, Inches(0.75), C_WHITE, C_CARD_BORDER, 1.0)
    _, tf_m1 = add_tb(s3, Inches(0.75), Inches(5.70), metric_w - Inches(0.2), Inches(0.65))
    p = tf_m1.paragraphs[0]; p.text = "100% PIPELINE UPTIME"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_GREEN
    p_sub = tf_m1.add_paragraph(); p_sub.text = "Zero downstream DAG crashes; analytics dashboards update reliably every morning."; p_sub.font.name = FONT; p_sub.font.size = Pt(9.5); p_sub.font.color.rgb = C_MUTED

    add_card(s3, Inches(0.65) + metric_w + col_gap, Inches(5.65), metric_w, Inches(0.75), C_WHITE, C_CARD_BORDER, 1.0)
    _, tf_m2 = add_tb(s3, Inches(0.75) + metric_w + col_gap, Inches(5.70), metric_w - Inches(0.2), Inches(0.65))
    p = tf_m2.paragraphs[0]; p.text = "ZERO DATA POLLUTION"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_CYAN
    p_sub = tf_m2.add_paragraph(); p_sub.text = "Irrecoverable anomalies are safely quarantined with full error logs for review."; p_sub.font.name = FONT; p_sub.font.size = Pt(9.5); p_sub.font.color.rgb = C_MUTED

    add_card(s3, Inches(0.65) + (metric_w + col_gap) * 2, Inches(5.65), metric_w, Inches(0.75), C_WHITE, C_CARD_BORDER, 1.0)
    _, tf_m3 = add_tb(s3, Inches(0.75) + (metric_w + col_gap) * 2, Inches(5.70), metric_w - Inches(0.2), Inches(0.65))
    p = tf_m3.paragraphs[0]; p.text = "PLUG-AND-PLAY DUCKDB ENGINE"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_BLUE
    p_sub = tf_m3.add_paragraph(); p_sub.text = "High-throughput in-memory execution processing 10,000 rows in under 450ms."; p_sub.font.name = FONT; p_sub.font.size = Pt(9.5); p_sub.font.color.rgb = C_MUTED

    # Slide 4: Existing Solutions & Differentiation
    s4 = prs.slides[3]
    setup_slide_header(s4, "Existing Solutions & Differentiation",
                       "From Brittle Traditional Pipelines to Autonomous Self-Healing.",
                       "Comparing DataHeal against standard dbt tests, Great Expectations, and manual engineer firefighting.")

    add_card(s4, Inches(0.65), Inches(1.25), Inches(5.15), Inches(5.15), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s4, Inches(0.80), Inches(1.35), Inches(1.65), Inches(0.24), "TRADITIONAL BOTTLENECK", C_RED)
    _, tf_ex = add_tb(s4, Inches(0.75), Inches(1.65), Inches(4.95), Inches(0.35))
    p = tf_ex.paragraphs[0]; p.text = "BRITTLE PIPELINES & ON-CALL BURNOUT"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_RED

    s4.shapes.add_picture('dataheal_comparison.jpg', Inches(0.80), Inches(2.05), Inches(4.85), Inches(2.70))

    _, tf_sub = add_tb(s4, Inches(0.80), Inches(4.85), Inches(4.85), Inches(1.45), ml=0.02, mr=0.02)
    p_sum = tf_sub.paragraphs[0]
    p_sum.text = "\u2022 Hardcoded Schema Assertions: A single renamed column halts entire enterprise Airflow batches."
    p_sum.font.name = FONT; p_sum.font.size = Pt(10.5); p_sum.font.bold = True; p_sum.font.color.rgb = C_DARK
    p_sum2 = tf_sub.add_paragraph(); p_sum2.space_before = Pt(2)
    p_sum2.text = "\u2022 Great Expectations / Monte Carlo: Alert generators that notify you but cannot heal anything."
    p_sum2.font.name = FONT; p_sum2.font.size = Pt(10.5); p_sum2.font.bold = True; p_sum2.font.color.rgb = C_CHARCOAL
    p_sum3 = tf_sub.add_paragraph(); p_sum3.space_before = Pt(2)
    p_sum3.text = "\u2022 Manual Hotfixes: Engineers wake up at 3 AM to update column names and rerun failed DAGs."
    p_sum3.font.name = FONT; p_sum3.font.size = Pt(10.5); p_sum3.font.bold = True; p_sum3.font.color.rgb = C_RED

    add_card(s4, Inches(6.05), Inches(1.25), Inches(6.63), Inches(5.15), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s4, Inches(6.20), Inches(1.35), Inches(1.65), Inches(0.24), "FEATURE MATRIX", C_GREEN)
    _, tf_diff = add_tb(s4, Inches(6.15), Inches(1.65), Inches(6.43), Inches(0.35))
    p = tf_diff.paragraphs[0]; p.text = "BENCHMARK: DATAHEAL VS ALTERNATIVES"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_GREEN

    table_shape = s4.shapes.add_table(6, 5, Inches(6.15), Inches(2.05), Inches(6.43), Inches(3.20))
    table = table_shape.table
    table.columns[0].width = Inches(1.85); table.columns[1].width = Inches(1.10)
    table.columns[2].width = Inches(1.10); table.columns[3].width = Inches(1.10); table.columns[4].width = Inches(1.28)

    headers = ["Capabilities", "Airflow / dbt", "Gt Expectations", "Monte Carlo", "DataHeal"]
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid(); cell.fill.fore_color.rgb = C_DARK if c_idx < 4 else C_GREEN
        p = cell.text_frame.paragraphs[0]; p.text = h_text; p.font.name = FONT; p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    m_data = [
        ("Adaptive Header Re-Mapping", "Crashes DAG", "Alert Only", "Alert Only", "Semantic Embed"),
        ("Mixed Date Dialect Healing", "Throws Error", "Throws Error", "None", "Auto-Harmonized"),
        ("Non-Blocking Row Quarantine", "None", "None", "None", "Dead-Letter Parquet"),
        ("Automated Type Coercion", "Fails Cast", "None", "None", "Regex Sanitizer"),
        ("Self-Documenting Audit Diffs", "Log Traceback", "JSON Test Card", "Slack Webhook", "Full JSON Diff")
    ]
    for r_idx, row_vals in enumerate(m_data):
        for c_idx, val in enumerate(row_vals):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if c_idx == 4:
                cell.fill.fore_color.rgb = C_GREEN_LIGHT
            elif r_idx % 2 == 0:
                cell.fill.fore_color.rgb = C_WHITE
            else:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)

            p = cell.text_frame.paragraphs[0]; p.text = val; p.font.name = FONT; p.font.size = Pt(9.5)
            if c_idx == 4:
                p.font.bold = True; p.font.color.rgb = C_GREEN
            elif "Crash" in val or "Error" in val or "None" in val:
                p.font.color.rgb = C_RED
            else:
                p.font.color.rgb = C_CHARCOAL
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    _, tf_adv = add_tb(s4, Inches(6.15), Inches(5.35), Inches(6.43), Inches(0.95), ml=0.02, mr=0.02)
    p = tf_adv.paragraphs[0]; p.text = "CORE ARCHITECTURAL ADVANTAGE"; p.font.name = FONT; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_DARK
    p_b1 = tf_adv.add_paragraph(); p_b1.space_before = Pt(1)
    r1 = p_b1.add_run(); r1.text = "\u2022 Fail-Forward Architecture: "; r1.font.bold = True; r1.font.color.rgb = C_GREEN
    r2 = p_b1.add_run(); r2.text = "Transitions data systems from catastrophic halt to resilient, autonomous recovery."; r2.font.color.rgb = C_CHARCOAL
    p_b2 = tf_adv.add_paragraph(); p_b2.space_before = Pt(1)
    r1 = p_b2.add_run(); r1.text = "\u2022 Zero Operational Burden: "; r1.font.bold = True; r1.font.color.rgb = C_BLUE
    r2 = p_b2.add_run(); r2.text = "Requires zero DSL authoring; acts as an intelligent intermediary in any existing pipeline."; r2.font.color.rgb = C_CHARCOAL

    # Slide 5: Technical Architecture & System Flow
    s5 = prs.slides[4]
    setup_slide_header(s5, "Technical Architecture & System Flow",
                       "5-Stage Autonomous Self-Healing Pipeline with DuckDB & Embeddings.",
                       "High-throughput modular stream: Data Drop -> Format Sniffer -> Semantic Matcher -> Type Sanitizer -> Clean Sink.")

    add_card(s5, Inches(0.65), Inches(1.25), Inches(5.65), Inches(5.15), C_WHITE, C_CARD_BORDER, 1.2)
    s5.shapes.add_picture('dataheal_architecture.jpg', Inches(0.68), Inches(1.28), Inches(5.59), Inches(5.09))

    layers = [
        ("STAGE 1: INGESTION & FORMAT SNIFFER", "Drop-Zone Watcher & Header Offset",
         "Auto-detects delimiters (comma, tab, semicolon), character encoding (UTF-8, Latin-1), and skips messy preamble rows.",
         C_RED),
        ("STAGE 2: SEMANTIC SCHEMA MATCHER", "Cosine Similarity & Levenshtein",
         "Maps incoming column names to expected schema using Sentence-Transformers embeddings with threshold-based confidence scores.",
         C_ORANGE_DARK),
        ("STAGE 3: TYPE COERCION & CLEANING", "Regex Sanitizer & Date Harmonizer",
         "Strips non-numeric noise from monetary fields, parses ambiguous dates using dateutil, and fills nulls with domain defaults.",
         C_CYAN),
        ("STAGE 4: SURGICAL QUARANTINE", "Dead-Letter Parquet Queue",
         "Surgically isolates records violating logical bounds to quarantine.parquet and captures detailed error stack telemetry.",
         C_BLUE),
        ("STAGE 5: PRODUCTION DISPATCHER", "Clean Warehouse & Audit Logger",
         "Dispatches 100% clean, standardized data frames to PostgreSQL / Snowflake and produces structured JSON transformation logs.",
         C_GREEN)
    ]
    card_lh = Inches(0.96); gap_lh = Inches(0.08)
    for l_idx, (l_pill, l_title, l_desc, l_col) in enumerate(layers):
        top_l = Inches(1.25) + l_idx * (card_lh + gap_lh)
        add_card(s5, Inches(6.50), top_l, Inches(6.18), card_lh, C_WHITE, C_CARD_BORDER, 1.0)
        add_pill_badge(s5, Inches(6.60), top_l + Inches(0.08), Inches(1.85), Inches(0.20), l_pill, l_col)
        _, tf_l = add_tb(s5, Inches(6.60), top_l + Inches(0.26), Inches(5.98), card_lh - Inches(0.30), mt=0.01, mb=0.01)
        p = tf_l.paragraphs[0]; p.text = l_title; p.font.name = FONT; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_DARK
        p2 = tf_l.add_paragraph(); p2.space_before = Pt(1); p2.text = l_desc; p2.font.name = FONT; p2.font.size = Pt(9.5); p2.font.color.rgb = C_CHARCOAL

    # Slide 6: Feasibility, 24-Hour Roadmap & Societal Impact
    s6 = prs.slides[5]
    setup_slide_header(s6, "Feasibility, 24-Hour Roadmap & Societal Impact",
                       "24-Hour Sprint Plan, Live Chaos-Test Demos & Enterprise ROI.",
                       "Built for dramatic live judging: drag-and-drop a deliberately mangled spreadsheet and watch it heal instantly.")

    card_w = Inches(3.88); card_gap = Inches(0.20)
    add_card(s6, Inches(0.65), Inches(1.25), card_w, Inches(2.35), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80), Inches(1.35), Inches(1.40), Inches(0.22), "LIVE PROTOTYPE", C_RED)
    _, tf = add_tb(s6, Inches(0.75), Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "LIVE HACKATHON DEMO PLAN"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_RED
    demo_steps = [
        ("Chaos Injection 1: ", "Drop CSV with renamed columns (Bill_Date -> Invc_Dt) -> DataHeal maps them with 98% confidence."),
        ("Chaos Injection 2: ", "Feed mixed dates (2024/05/12, 12-May-2024) -> Normalized to ISO 8601 instantly."),
        ("Chaos Injection 3: ", "Insert $ and commas into numeric sales columns -> Stripped and cast to float in 2ms."),
        ("Chaos Injection 4: ", "Inject completely corrupted garbage row -> Safely diverted to quarantine.parquet without crashing.")
    ]
    for st, sd in demo_steps:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + st; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    add_card(s6, Inches(0.65) + card_w + card_gap, Inches(1.25), card_w, Inches(2.35), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80) + card_w + card_gap, Inches(1.35), Inches(1.50), Inches(0.22), "TARGET BENCHMARKS", C_ORANGE)
    _, tf = add_tb(s6, Inches(0.75) + card_w + card_gap, Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "EVALUATION TARGETS"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    metrics = [
        ("100% Pipeline Uptime: ", "Zero downstream DAG crashes across 50 simulated broken schemas."),
        ("< 450ms Overhead: ", "Processing latency per 10,000-row batch during autonomous repair."),
        ("96.8% Auto-Recovery: ", "Successful column alignment and datatype resolution rate."),
        ("Zero Data Loss: ", "Every single byte is either safely healed or logged in quarantine.")
    ]
    for mt, md in metrics:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + mt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_GREEN
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    add_card(s6, Inches(0.65) + (card_w + card_gap) * 2, Inches(1.25), card_w, Inches(2.35), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80) + (card_w + card_gap) * 2, Inches(1.35), Inches(1.40), Inches(0.22), "STAKEHOLDERS", C_BLUE)
    _, tf = add_tb(s6, Inches(0.75) + (card_w + card_gap) * 2, Inches(1.60), card_w - Inches(0.20), Inches(1.95), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "WHO BENEFITS?"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_BLUE
    stakeholders = [
        ("Data Engineers: ", "Eliminates on-call alert fatigue and manual 3 AM schema patching."),
        ("Analytics & BI Teams: ", "Clean, unbroken reporting feeds delivered punctually every single morning."),
        ("Business Stakeholders: ", "Zero decision-making paralysis caused by delayed financial dashboards."),
        ("Enterprise IT Operations: ", "Massive reduction in operational maintenance and pipeline incident tickets.")
    ]
    for st, sd in stakeholders:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "\u2022 " + st; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(10); r2.font.color.rgb = C_CHARCOAL

    add_card(s6, Inches(0.65), Inches(3.75), Inches(12.03), Inches(2.65), C_WHITE, C_CARD_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80), Inches(3.85), Inches(1.80), Inches(0.24), "24-HOUR SPRINT TIMELINE", C_ORANGE)
    _, tf = add_tb(s6, Inches(0.75), Inches(4.15), Inches(11.83), Inches(0.35))
    p = tf.paragraphs[0]; p.text = "RIGOROUS 24-HOUR HACKATHON EXECUTION ROADMAP"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_DARK

    phases = [
        ("PHASE 1: 00:00 \u2014 06:00", "CHAOS GENERATOR & INGESTION",
         "\u2022 Build synthetic broken spreadsheet generator (swapped headers, dirty currency, bad dates).\n\u2022 DuckDB high-speed local stream ingestion harness.\n\u2022 Format sniffer for encoding & delimiter autodetection."),
        ("PHASE 2: 06:00 \u2014 12:00", "SEMANTIC MATCHING & HEALING",
         "\u2022 MiniLM sentence embedding column mapper.\n\u2022 Regex-based currency and punctuation sanitizer.\n\u2022 Dateutil multi-dialect timestamp parser."),
        ("PHASE 3: 12:00 \u2014 18:00", "QUARANTINE QUEUE & AUDIT DIFF",
         "\u2022 Surgical dead-letter Parquet isolation queue.\n\u2022 Automated JSON audit ledger and transformation diff generator.\n\u2022 SQLite / DuckDB clean sink export."),
        ("PHASE 4: 18:00 \u2014 24:00", "STREAMLIT UI & LIVE CHAOS DEMO",
         "\u2022 3-pane real-time visual pipeline dashboard.\n\u2022 Stress testing against 50 chaotic edge-case files.\n\u2022 Live pitch rehearsal with instant drag-and-drop healing demo.")
    ]
    p_w = Inches(2.88); p_gap = Inches(0.12)
    for p_idx, (p_title, p_sub, p_desc) in enumerate(phases):
        p_left = Inches(0.80) + (p_w + p_gap) * p_idx
        add_card(s6, p_left, Inches(4.55), p_w, Inches(1.70), C_CYAN_LIGHT if p_idx % 2 == 0 else C_ORANGE_LIGHT, C_CYAN_BORDER if p_idx % 2 == 0 else C_ORANGE_BORDER, 1.0)
        _, tf_p = add_tb(s6, p_left + Inches(0.1), Inches(4.60), p_w - Inches(0.2), Inches(1.60), ml=0.02, mr=0.02)
        p = tf_p.paragraphs[0]; p.text = p_title; p.font.name = FONT; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = C_CYAN if p_idx % 2 == 0 else C_ORANGE_DARK
        p2 = tf_p.add_paragraph(); p2.space_before = Pt(1); p2.text = p_sub; p2.font.name = FONT; p2.font.size = Pt(9.5); p2.font.bold = True; p2.font.color.rgb = C_DARK
        p3 = tf_p.add_paragraph(); p3.space_before = Pt(2); p3.text = p_desc; p3.font.name = FONT; p3.font.size = Pt(8.5); p3.font.color.rgb = C_CHARCOAL

    # Slide 7: Conclusion & References
    s7 = prs.slides[6]
    setup_slide_header(s7, "Conclusion & References",
                       "Autonomous Resilience for Modern Enterprise Data Infrastructure.",
                       "\"Freeing data engineers from mundane firefighting so they can focus on high-impact analytics.\"")

    add_card(s7, Inches(0.65), Inches(1.25), Inches(5.15), Inches(3.05), C_WHITE, C_CYAN_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(1.35), Inches(1.30), Inches(0.24), "CORE SUMMARY", C_CYAN)
    _, tf_k = add_tb(s7, Inches(0.75), Inches(1.65), Inches(4.95), Inches(2.55))
    p = tf_k.paragraphs[0]; p.text = "KEY TAKEAWAYS"; p.font.name = FONT; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_CYAN
    takeaways = [
        ("Eliminates Pipeline Downtime: ", "100% operational continuity even when upstream departments alter formats."),
        ("Semantic Auto-Mapping: ", "Automatically aligns renamed columns without requiring manual schema definitions."),
        ("Zero Data Pollution: ", "Surgical quarantine ensures bad rows never corrupt analytics or crash production workloads."),
        ("Developer Freedom: ", "Reclaims 40% of data engineering sprint capacity from tedious on-call firefighting.")
    ]
    for kt, kd in takeaways:
        pb = tf_k.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "\u2022 " + kt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = kd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    add_card(s7, Inches(5.95), Inches(1.25), Inches(6.73), Inches(3.05), C_SLATE_800, C_CARD_BORDER, 1.2)
    s7.shapes.add_picture('dataheal_badge.jpg', Inches(5.98), Inches(1.28), Inches(6.67), Inches(2.99))

    add_card(s7, Inches(0.65), Inches(4.40), Inches(12.03), Inches(1.95), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(4.50), Inches(1.60), Inches(0.24), "TECHNICAL EVIDENCE", C_BLUE)
    _, tf_rf = add_tb(s7, Inches(0.75), Inches(4.80), Inches(11.83), Inches(1.50))
    p = tf_rf.paragraphs[0]; p.text = "VERIFIABLE REFERENCES & DATA RESILIENCE RESEARCH"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_BLUE

    _, tf_c1 = add_tb(s7, Inches(0.75), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col1 = [
        ("1. Gartner Enterprise Data Quality: ", "Measuring the Business Impact of Data Downtime and Dirty Information (2023)."),
        ("2. Sentence-Transformers (MiniLM): ", "Dense Vector Embeddings for Semantic Text Similarity and Schema Alignment (EMNLP)."),
        ("3. DuckDB In-Memory OLAP Architecture: ", "Fast Analytical Query Processing on Embedded Local Data Streams (VLDB).")
    ]
    for r_num, r_text in ref_col1:
        p = tf_c1.add_paragraph() if tf_c1.paragraphs[0].text else tf_c1.paragraphs[0]
        p.space_before = Pt(1)
        r1 = p.add_run(); r1.text = r_num; r1.font.name = FONT; r1.font.size = Pt(9.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = p.add_run(); r2.text = r_text; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    _, tf_c2 = add_tb(s7, Inches(6.80), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col2 = [
        ("4. Apache Arrow & Parquet Format: ", "Columnar Memory Layout and Efficient Storage for Resilient Data Pipelines."),
        ("5. Dead-Letter Queue Architectures: ", "Fault-Tolerant Streaming and Surgical Anomaly Isolation (ACM Computing Surveys)."),
        ("6. Automated Schema Evolution: ", "Self-Adapting Relational Schemas for Semi-Structured Ingestion (IEEE ICDE).")
    ]
    for r_num, r_text in ref_col2:
        p = tf_c2.add_paragraph() if tf_c2.paragraphs[0].text else tf_c2.paragraphs[0]
        p.space_before = Pt(1)
        r1 = p.add_run(); r1.text = r_num; r1.font.name = FONT; r1.font.size = Pt(9.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = p.add_run(); r2.text = r_text; r2.font.name = FONT; r2.font.size = Pt(9.5); r2.font.color.rgb = C_CHARCOAL

    prs.save('AI_Avengers_Theme04_DataHeal.pptx')
    print("Saved: AI_Avengers_Theme04_DataHeal.pptx")


# ==============================================================================
# PDF EXPORT ROUTINE VIA POWERPOINT COM AUTOMATION
# ==============================================================================
def export_all_to_pdf():
    import win32com.client
    files = [
        ("AI_Avengers_Theme05_VoiceKirana.pptx", "AI_Avengers_Theme05_VoiceKirana.pdf"),
        ("AI_Avengers_Theme02_ScamSentry.pptx", "AI_Avengers_Theme02_ScamSentry.pdf"),
        ("AI_Avengers_Theme04_DataHeal.pptx", "AI_Avengers_Theme04_DataHeal.pdf")
    ]
    
    print("Initializing PowerPoint COM Application for PDF conversion...")
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    
    for pptx_name, pdf_name in files:
        abs_pptx = os.path.abspath(pptx_name)
        abs_pdf = os.path.abspath(pdf_name)
        print(f"Exporting {pptx_name} -> {pdf_name}...")
        prs = ppt.Presentations.Open(abs_pptx, WithWindow=False)
        prs.SaveAs(abs_pdf, 32)  # 32 = ppSaveAsPDF
        prs.Close()
        print(f"Successfully created: {pdf_name} ({os.path.getsize(abs_pdf):,} bytes)")
        
    ppt.Quit()
    print("All PDFs exported successfully.")


if __name__ == '__main__':
    print("=== BUILDING ALL 3 HACKATHON PRESENTATIONS ===")
    build_deck_1_voicekirana()
    build_deck_2_scamsentry()
    build_deck_3_dataheal()
    print("\n=== EXPORTING ALL PRESENTATIONS TO HIGH-RES PDF ===")
    export_all_to_pdf()
    print("\n=== ALL DELIVERABLES GENERATED SUCCESSFULLY! ===")
