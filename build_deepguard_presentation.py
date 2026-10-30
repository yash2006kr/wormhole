import sys
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    template_path = 'AfterHours_1.0_PPT_Template.pptx'
    output_pptx = 'AfterHours_1.0_DeepGuard_Deepfake_Tracker.pptx'
    output_pdf = 'AfterHours_1.0_DeepGuard_Deepfake_Tracker.pdf'

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
    C_ORANGE_TINT = RGBColor(254, 215, 170)  # Orange 200 (#FED7AA)
    C_BLUE = RGBColor(2, 132, 199)           # Sky Blue 600 (#0284C7)
    C_BLUE_LIGHT = RGBColor(240, 249, 255)   # Sky Blue 50 (#F0F9FF)
    C_BLUE_BORDER = RGBColor(125, 211, 252)  # Sky Blue 300 (#7DD3FC)
    C_RED = RGBColor(220, 38, 38)            # Red 600 (#DC2626)
    C_RED_LIGHT = RGBColor(254, 242, 242)    # Red 50 (#FEF2F2)
    C_RED_BORDER = RGBColor(252, 165, 165)   # Red 300 (#FCA5A5)
    C_GREEN = RGBColor(22, 163, 74)          # Green 600 (#16A34A)
    C_GREEN_LIGHT = RGBColor(240, 253, 244)  # Green 50 (#F0FDF4)
    C_GREEN_BORDER = RGBColor(134, 239, 172) # Green 300 (#86EFAC)
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

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 1: COVER SLIDE
    # ═════════════════════════════════════════════════════════════════════════
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.name == 'TextBox 14':
            shape.left = Inches(1.5)
            shape.top = Inches(2.15)
            shape.width = Inches(10.33)
            shape.height = Inches(1.95)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True

            p0 = tf.paragraphs[0]
            p0.text = "PROBLEM STATEMENT 04: TRUST & SAFETY · MEDIA FORENSICS"
            p0.font.name = FONT
            p0.font.size = Pt(14)
            p0.font.bold = True
            p0.font.color.rgb = C_ORANGE
            p0.alignment = PP_ALIGN.CENTER

            p1 = tf.add_paragraph()
            p1.space_before = Pt(4)
            p1.text = "DEEPGUARD"
            p1.font.name = FONT
            p1.font.size = Pt(44)
            p1.font.bold = True
            p1.font.color.rgb = C_DARK
            p1.alignment = PP_ALIGN.CENTER

            p2 = tf.add_paragraph()
            p2.space_before = Pt(2)
            p2.text = "Deepfake Detection & Viral Takedown Tracker"
            p2.font.name = FONT
            p2.font.size = Pt(18)
            p2.font.bold = True
            p2.font.color.rgb = C_BLUE
            p2.alignment = PP_ALIGN.CENTER

            p3 = tf.add_paragraph()
            p3.space_before = Pt(3)
            p3.text = "\"Detect manipulated media. Trace viral spread. Automate takedowns before harm multiplies.\""
            p3.font.name = FONT
            p3.font.size = Pt(14)
            p3.font.italic = True
            p3.font.color.rgb = C_MUTED
            p3.alignment = PP_ALIGN.CENTER

        elif shape.name == 'TextBox 15':
            shape.left = Inches(1.5)
            shape.top = Inches(4.35)
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
            p_tn.space_before = Pt(4)
            p_tn.text = "Team Name: AI Avengers"
            p_tn.font.name = FONT
            p_tn.font.size = Pt(18)
            p_tn.font.bold = True
            p_tn.font.color.rgb = C_DARK

            p_dom = tf.add_paragraph()
            p_dom.space_before = Pt(2)
            p_dom.text = "Track: Trust & Safety · Media Forensics"
            p_dom.font.name = FONT
            p_dom.font.size = Pt(13.5)
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
            shape.top = Inches(4.35)
            shape.width = Inches(5.0)
            shape.height = Inches(1.95)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True

            p = tf.paragraphs[0]
            p.text = "TEAM MEMBERS & ROLES"
            p.font.name = FONT
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_ORANGE

            members = [
                ("Raj Aanada", "Full-Stack & UI/UX Architect"),
                ("Yashma C P", "Audio-Visual Biometrics Engine"),
                ("Likith M", "Perceptual Hashing & Spread Graph"),
                ("Yashwanth K R", "ML Forensics & Takedown Orchestration")
            ]
            for m_name, m_role in members:
                pm = tf.add_paragraph()
                pm.space_before = Pt(2)
                r_n = pm.add_run()
                r_n.text = f"• {m_name} "
                r_n.font.name = FONT
                r_n.font.size = Pt(13)
                r_n.font.bold = True
                r_n.font.color.rgb = C_DARK
                r_r = pm.add_run()
                r_r.text = f"— {m_role}"
                r_r.font.name = FONT
                r_r.font.size = Pt(12)
                r_r.font.color.rgb = C_CHARCOAL

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 2: PROBLEM STATEMENT & ITS RELEVANCE
    # ═════════════════════════════════════════════════════════════════════════
    s2 = prs.slides[1]
    setup_slide_header(s2, "Problem Statement & Its Relevance",
                       "Deepfakes Move Faster Than Human Triage.",
                       "A single fake clip reaches millions in minutes, destroying reputations before reports are seen.")

    # Left Column: Exact Problem (Top) & Why Does It Matter (Bottom)
    # Card 1: Exact Problem
    add_card(s2, Inches(0.65), Inches(1.25), Inches(3.65), Inches(2.50), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(1.35), Inches(1.25), Inches(0.24), "THREAT VECTORS", C_RED)
    _, tf = add_tb(s2, Inches(0.75), Inches(1.63), Inches(3.45), Inches(2.05), mt=0.02, mb=0.02)
    p = tf.paragraphs[0]; p.text = "EXACT PROBLEM"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_DARK
    problems = [
        ("Hyper-Realistic AI Fakes: ", "Convincing face-swaps and voice clones created with zero barrier."),
        ("Viral Spread Velocity: ", "Altered copies are cropped, mirrored, and reposted in seconds."),
        ("Asymmetric Triage: ", "Victims face slow 72-hour manual reporting while damage compounds.")
    ]
    for pt, pd in problems:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.5)
        r1 = pb.add_run(); r1.text = "• " + pt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = pd; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Card 2: Why Does This Matter?
    add_card(s2, Inches(0.65), Inches(3.85), Inches(3.65), Inches(2.45), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s2, Inches(0.80), Inches(3.95), Inches(1.25), Inches(0.24), "URGENCY & SCALE", C_ORANGE)
    _, tf = add_tb(s2, Inches(0.75), Inches(4.23), Inches(3.45), Inches(2.00), mt=0.02, mb=0.02)
    p = tf.paragraphs[0]; p.text = "WHY DOES THIS MATTER?"; p.font.name = FONT; p.font.size = Pt(13.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    matters = [
        ("550% Surge in Deepfakes: ", "Over 500,000 synthetic attacks logged in 2024 alone."),
        ("Irreversible Harm: ", "80% retain false narratives even after official retractions."),
        ("Crippling Latency: ", "Standard DMCA takes 3–5 days; viral damage occurs in <2 hours."),
        ("Trust Crisis: ", "Weaponized against elections, leaders, and private citizens.")
    ]
    for mt, md in matters:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.5)
        r1 = pb.add_run(); r1.text = "• " + mt; r1.font.name = FONT; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = C_CHARCOAL

    # Center: Realistic Forensic Split-Screen Inspection Visual
    add_card(s2, Inches(4.45), Inches(1.25), Inches(4.35), Inches(2.45), C_SLATE_800, C_ORANGE_BORDER, 1.2)
    s2.shapes.add_picture('realistic_deepfake_forensics.jpg', Inches(4.48), Inches(1.28), Inches(4.29), Inches(2.39))

    # Center Middle: Illustrative Attack Lifecycle
    add_card(s2, Inches(4.45), Inches(3.85), Inches(4.35), Inches(1.30), C_WHITE, C_BLUE_BORDER, 1.0)
    add_pill_badge(s2, Inches(4.60), Inches(3.95), Inches(1.40), Inches(0.22), "ATTACK LIFECYCLE", C_BLUE)
    _, tf_lc = add_tb(s2, Inches(4.52), Inches(4.22), Inches(4.22), Inches(0.85), ml=0.02, mr=0.02, mt=0.02, mb=0.02)
    p = tf_lc.paragraphs[0]; p.text = "① Creation ➔ ② Seed ➔ ③ Mirror ➔ ④ Harm ➔ ⑤ Triage"
    p.font.name = FONT; p.font.size = Pt(9.0); p.font.bold = True; p.font.color.rgb = C_ORANGE
    p_sub = tf_lc.add_paragraph(); p_sub.space_before = Pt(2)
    p_sub.text = "Without perceptual tracking, altered copies reappear indefinitely across platforms."
    p_sub.font.name = FONT; p_sub.font.size = Pt(10); p_sub.font.color.rgb = C_CHARCOAL

    # Right Card: Who Faces This Problem?
    add_card(s2, Inches(8.95), Inches(1.25), Inches(3.73), Inches(3.90), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s2, Inches(9.10), Inches(1.35), Inches(1.45), Inches(0.24), "AFFECTED PARTIES", C_BLUE)
    _, tf = add_tb(s2, Inches(9.05), Inches(1.65), Inches(3.53), Inches(3.40))
    p = tf.paragraphs[0]; p.text = "WHO FACES THIS PROBLEM?"; p.font.name = FONT; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_BLUE
    who = [
        ("Public Figures & Leaders: ", "Political disinformation, forged statements, and election tampering."),
        ("Private Citizens & Students: ", "Cyberbullying, identity theft, and non-consensual synthetic abuse."),
        ("Newsrooms & Fact-Checkers: ", "Need rapid verification for breaking viral video before broadcast."),
        ("Trust & Safety Teams: ", "Millions of daily uploads swamping manual human review queues.")
    ]
    for wt, wd in who:
        pb = tf.add_paragraph(); pb.space_before = Pt(3)
        r1 = pb.add_run(); r1.text = "• " + wt; r1.font.name = FONT; r1.font.size = Pt(12); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = wd; r2.font.name = FONT; r2.font.size = Pt(12); r2.font.color.rgb = C_CHARCOAL

    # Bottom Full-Width Banner: Core Problem Statement
    add_card(s2, Inches(4.45), Inches(5.25), Inches(8.23), Inches(1.05), C_ORANGE_LIGHT, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s2, Inches(4.60), Inches(5.33), Inches(1.50), Inches(0.22), "CORE CHALLENGE", C_ORANGE)
    _, tf_core = add_tb(s2, Inches(4.55), Inches(5.58), Inches(8.03), Inches(0.65))
    p_quote = tf_core.paragraphs[0]
    p_quote.text = "\"How might we automatically detect manipulated media with explainable confidence, trace its viral spread across altered copies, and empower victims with automated one-click takedowns?\""
    p_quote.font.name = FONT; p_quote.font.size = Pt(12); p_quote.font.bold = True; p_quote.font.color.rgb = C_DARK

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 3: PROPOSED SOLUTION & INNOVATION
    # ═════════════════════════════════════════════════════════════════════════
    s3 = prs.slides[2]
    setup_slide_header(s3, "Proposed Solution & Innovation",
                       "DEEPGUARD – Multi-Modal Forensics & Automated Takedown Platform",
                       "\"Detect artifacts, trace viral spread, and halt harm in minutes.\"")

    # Top Left Card: What Are We Proposing?
    add_card(s3, Inches(0.65), Inches(1.25), Inches(4.75), Inches(2.45), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s3, Inches(0.80), Inches(1.35), Inches(1.40), Inches(0.24), "CORE PLATFORM", C_ORANGE)
    _, tf = add_tb(s3, Inches(0.75), Inches(1.65), Inches(4.55), Inches(1.95))
    p = tf.paragraphs[0]; p.text = "WHAT ARE WE PROPOSING?"; p.font.name = FONT; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    props = [
        ("Unified Forensics: ", "Combines multi-modal detection, viral spread mapping, and legal takedowns."),
        ("Perceptual Invariance: ", "pHash & visual embeddings detect cropped, compressed, and mirrored copies."),
        ("Automated DMCA: ", "Dispatches verified C2PA legal notices to platform APIs in under 15 minutes.")
    ]
    for pt, pd in props:
        pb = tf.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "• " + pt; r1.font.name = FONT; r1.font.size = Pt(12); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = pd; r2.font.name = FONT; r2.font.size = Pt(12); r2.font.color.rgb = C_CHARCOAL

    # Top Right Visual: Realistic DeepGuard Investigator Studio v2.0 UI
    add_card(s3, Inches(5.55), Inches(1.25), Inches(7.13), Inches(2.45), C_SLATE_800, C_CARD_BORDER, 1.2)
    s3.shapes.add_picture('realistic_deepguard_dashboard.jpg', Inches(5.58), Inches(1.28), Inches(7.07), Inches(2.39))

    # Middle Row: 3 Innovation Pillars
    col_w = Inches(3.88)
    col_gap = Inches(0.19)

    # Pillar 1
    add_card(s3, Inches(0.65), Inches(3.85), col_w, Inches(1.65), C_BLUE_LIGHT, C_BLUE_BORDER, 1.2)
    add_pill_badge(s3, Inches(0.80), Inches(3.95), Inches(0.95), Inches(0.22), "PILLAR 01", C_BLUE)
    _, tf1 = add_tb(s3, Inches(0.75), Inches(4.20), col_w - Inches(0.20), Inches(1.20))
    p = tf1.paragraphs[0]; p.text = "1. Multi-Modal Forensic Fusion"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_BLUE
    p_b = tf1.add_paragraph(); p_b.space_before = Pt(2)
    p_b.text = "EfficientNet-B4 spatial anomaly detection, WavLM audio spectral analysis, and DCT frequency heatmaps robust against re-compression."
    p_b.font.name = FONT; p_b.font.size = Pt(11.5); p_b.font.color.rgb = C_CHARCOAL

    # Pillar 2
    add_card(s3, Inches(0.65) + col_w + col_gap, Inches(3.85), col_w, Inches(1.65), C_ORANGE_LIGHT, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s3, Inches(0.80) + col_w + col_gap, Inches(3.95), Inches(0.95), Inches(0.22), "PILLAR 02", C_ORANGE)
    _, tf2 = add_tb(s3, Inches(0.75) + col_w + col_gap, Inches(4.20), col_w - Inches(0.20), Inches(1.20))
    p = tf2.paragraphs[0]; p.text = "2. Perceptual Hash Spread Graph"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    p_b = tf2.add_paragraph(); p_b.space_before = Pt(2)
    p_b.text = "pHash and CLIP visual embeddings construct a directed propagation DAG mapping mirrored copies, formats, and patient-zero source."
    p_b.font.name = FONT; p_b.font.size = Pt(11.5); p_b.font.color.rgb = C_CHARCOAL

    # Pillar 3
    add_card(s3, Inches(0.65) + (col_w + col_gap) * 2, Inches(3.85), col_w, Inches(1.65), C_GREEN_LIGHT, C_GREEN_BORDER, 1.2)
    add_pill_badge(s3, Inches(0.80) + (col_w + col_gap) * 2, Inches(3.95), Inches(0.95), Inches(0.22), "PILLAR 03", C_GREEN)
    _, tf3 = add_tb(s3, Inches(0.75) + (col_w + col_gap) * 2, Inches(4.20), col_w - Inches(0.20), Inches(1.20))
    p = tf3.paragraphs[0]; p.text = "3. Explainable Legal Takedown API"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_GREEN
    p_b = tf3.add_paragraph(); p_b.space_before = Pt(2)
    p_b.text = "Generates C2PA-compliant cryptographic proof dossiers and dispatches automated, platform-specific DMCA notices via webhooks in <15 mins."
    p_b.font.name = FONT; p_b.font.size = Pt(11.5); p_b.font.color.rgb = C_CHARCOAL

    # Bottom Banner: Workflow Pipeline
    add_card(s3, Inches(0.65), Inches(5.65), Inches(12.03), Inches(0.85), C_WHITE, C_CARD_BORDER, 1.0)
    add_pill_badge(s3, Inches(0.80), Inches(5.72), Inches(1.40), Inches(0.22), "END-TO-END FLOW", C_DARK)
    _, tf_pipe = add_tb(s3, Inches(0.75), Inches(5.95), Inches(11.83), Inches(0.50))
    p_pipe = tf_pipe.paragraphs[0]
    p_pipe.text = "⚡ [1] Ingestion ➔ [2] Forensics ➔ [3] Heatmap ➔ [4] pHash Index ➔ [5] Spread DAG ➔ [6] Legal Notice ➔ [7] Platform API"
    p_pipe.font.name = FONT; p_pipe.font.size = Pt(11.5); p_pipe.font.bold = True; p_pipe.font.color.rgb = C_ORANGE
    p_sub = tf_pipe.add_paragraph(); p_sub.space_before = Pt(1)
    p_sub.text = "From video upload to automated DMCA platform filing and verifiable legal evidence in <15 minutes."
    p_sub.font.name = FONT; p_sub.font.size = Pt(10.5); p_sub.font.color.rgb = C_MUTED

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 4: EXISTING SOLUTIONS & DIFFERENTIATION
    # ═════════════════════════════════════════════════════════════════════════
    s4 = prs.slides[3]
    setup_slide_header(s4, "Existing Solutions & Differentiation",
                       "From Isolated Dashboards to an Integrated Takedown Ecosystem.",
                       "Why legacy detectors fail on viral media — and how DeepGuard wins.")

    # Left Card: Existing Solutions & Limitations
    add_card(s4, Inches(0.65), Inches(1.25), Inches(5.15), Inches(4.15), C_WHITE, C_RED_BORDER, 1.2)
    add_pill_badge(s4, Inches(0.80), Inches(1.35), Inches(1.50), Inches(0.24), "LEGACY SHORTCOMINGS", C_RED)
    _, tf_ex = add_tb(s4, Inches(0.75), Inches(1.65), Inches(4.95), Inches(0.35))
    p = tf_ex.paragraphs[0]; p.text = "EXISTING SOLUTIONS & LIMITATIONS"; p.font.name = FONT; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_RED

    # Item 1: Generic Detector
    s4.shapes.add_picture('widget_ai_detector.jpg', Inches(0.80), Inches(2.05), Inches(1.35), Inches(0.75))
    _, tf_item1 = add_tb(s4, Inches(2.25), Inches(2.05), Inches(3.45), Inches(0.75))
    p = tf_item1.paragraphs[0]; p.text = "Generic Online Detectors"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_DARK
    pb = tf_item1.add_paragraph(); pb.space_before = Pt(1)
    pb.text = "• Vague % score with no explainable heatmap; zero viral spread tracking."
    pb.font.name = FONT; pb.font.size = Pt(11); pb.font.color.rgb = C_CHARCOAL

    # Item 2: Content-ID Hash Matcher
    s4.shapes.add_picture('widget_hash_failed.jpg', Inches(0.80), Inches(2.95), Inches(1.35), Inches(0.75))
    _, tf_item2 = add_tb(s4, Inches(2.25), Inches(2.95), Inches(3.45), Inches(0.75))
    p = tf_item2.paragraphs[0]; p.text = "Platform Content-ID"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_DARK
    pb = tf_item2.add_paragraph(); pb.space_before = Pt(1)
    pb.text = "• Exact hash match (MD5) easily bypassed by cropping, mirrors, or filters."
    pb.font.name = FONT; pb.font.size = Pt(11); pb.font.color.rgb = C_CHARCOAL

    # Item 3: Manual DMCA
    s4.shapes.add_picture('widget_dmca_pending.jpg', Inches(0.80), Inches(3.85), Inches(1.35), Inches(0.75))
    _, tf_item3 = add_tb(s4, Inches(2.25), Inches(3.85), Inches(3.45), Inches(0.75))
    p = tf_item3.paragraphs[0]; p.text = "Manual DMCA Filing Forms"; p.font.name = FONT; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_DARK
    pb = tf_item3.add_paragraph(); pb.space_before = Pt(1)
    pb.text = "• Tedious 48–72 hr forms per platform; copies keep spreading unchecked."
    pb.font.name = FONT; pb.font.size = Pt(11); pb.font.color.rgb = C_CHARCOAL

    # VS Badge in center
    vs_card = add_card(s4, Inches(5.95), Inches(2.85), Inches(0.65), Inches(0.65), C_DARK, C_ORANGE, 2.0)
    _, tf_vs = add_tb(s4, Inches(5.95), Inches(2.85), Inches(0.65), Inches(0.65), ml=0, mr=0, mt=0.12)
    p_vs = tf_vs.paragraphs[0]; p_vs.text = "VS"; p_vs.font.name = FONT; p_vs.font.size = Pt(14); p_vs.font.bold = True; p_vs.font.color.rgb = C_ORANGE
    p_vs.alignment = PP_ALIGN.CENTER

    # Right Card: DeepGuard Advantages
    add_card(s4, Inches(6.75), Inches(1.25), Inches(5.93), Inches(4.15), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s4, Inches(6.90), Inches(1.35), Inches(1.70), Inches(0.24), "DEEPGUARD ADVANTAGE", C_GREEN)
    _, tf_adv = add_tb(s4, Inches(6.85), Inches(1.65), Inches(5.73), Inches(3.65))
    p = tf_adv.paragraphs[0]; p.text = "OUR SOLUTION: DEEPGUARD ADVANTAGES"; p.font.name = FONT; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_BLUE
    advantages = [
        ("Multi-Modal Scope: ", "Analyzes video frames, audio tracks, and EXIF metadata simultaneously."),
        ("Bypass-Resistant: ", "Perceptual hashing (pHash) matches cropped, compressed, and filtered copies."),
        ("Viral Spread Mapping: ", "Directed propagation DAG identifies patient-zero and all downstream mirrors."),
        ("Automated Takedown: ", "Pre-filled DMCA notices & API webhooks cut response time from 72h to <15m."),
        ("Full Explainability: ", "Generates Grad-CAM visual heatmaps and C2PA cryptographic audit trails.")
    ]
    for at, ad in advantages:
        pb = tf_adv.add_paragraph(); pb.space_before = Pt(3)
        r1 = pb.add_run(); r1.text = "✔ " + at; r1.font.name = FONT; r1.font.size = Pt(12); r1.font.bold = True; r1.font.color.rgb = C_GREEN
        r2 = pb.add_run(); r2.text = ad; r2.font.name = FONT; r2.font.size = Pt(12); r2.font.color.rgb = C_CHARCOAL

    # Bottom Banner: Competitive Advantage
    add_card(s4, Inches(0.65), Inches(5.55), Inches(12.03), Inches(0.95), C_ORANGE_LIGHT, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s4, Inches(0.80), Inches(5.62), Inches(1.60), Inches(0.22), "COMPETITIVE MOAT", C_ORANGE)
    _, tf_diff = add_tb(s4, Inches(0.75), Inches(5.88), Inches(11.83), Inches(0.55))
    p_comp = tf_diff.paragraphs[0]
    p_comp.text = "🏆 Judges and investigators can inject a manipulated video, inspect real-time Grad-CAM heatmaps, trace all derivative re-uploads on the spread DAG, and dispatch simulated DMCA takedowns in seconds."
    p_comp.font.name = FONT; p_comp.font.size = Pt(12); p_comp.font.bold = True; p_comp.font.color.rgb = C_DARK

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 5: TECHNICAL APPROACH & FEASIBILITY
    # ═════════════════════════════════════════════════════════════════════════
    s5 = prs.slides[4]
    setup_slide_header(s5, "Technical Approach & Feasibility",
                       "A Working Forensic & Takedown Engine, Not Just a Visual Demo.",
                       "Full-stack architecture, deterministic graph traversal, and 24-hour hackathon scope.")

    # Top Half: Realistic System Architecture & Data Pipeline Diagram
    add_card(s5, Inches(0.65), Inches(1.25), Inches(12.03), Inches(2.45), C_SLATE_800, C_ORANGE_BORDER, 1.2)
    s5.shapes.add_picture('realistic_architecture_diagram.jpg', Inches(0.68), Inches(1.28), Inches(11.97), Inches(2.39))

    # Bottom Row: 3 Modular Cards
    col_w5 = Inches(3.88)
    col_gap5 = Inches(0.19)

    # Card 1: Technologies Used
    add_card(s5, Inches(0.65), Inches(3.85), col_w5, Inches(2.55), C_WHITE, C_CARD_BORDER, 1.0)
    add_pill_badge(s5, Inches(0.80), Inches(3.95), Inches(1.20), Inches(0.22), "TECH STACK", C_BLUE)
    _, tf_t = add_tb(s5, Inches(0.75), Inches(4.22), col_w5 - Inches(0.20), Inches(2.10), mt=0.01, mb=0.01)
    p = tf_t.paragraphs[0]; p.text = "🛠 TECHNOLOGIES USED"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_DARK
    techs = [
        ("Frontend: ", "React.js, Tailwind CSS, D3.js, Canvas"),
        ("Backend API: ", "Python 3.12, FastAPI, Celery, Redis"),
        ("Forensic ML: ", "PyTorch, EfficientNet-B4, WavLM, OpenCV"),
        ("Search & Graph: ", "Milvus Vector DB, NetworkX, pHash"),
        ("Cloud & Standards: ", "AWS S3, SQLite, Docker, C2PA Standard")
    ]
    for tt, td in techs:
        pb = tf_t.add_paragraph(); pb.space_before = Pt(1.2)
        r1 = pb.add_run(); r1.text = "• " + tt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_BLUE
        r2 = pb.add_run(); r2.text = td; r2.font.name = FONT; r2.font.size = Pt(10.5); r2.font.color.rgb = C_CHARCOAL

    # Card 2: Where is AI Needed?
    add_card(s5, Inches(0.65) + col_w5 + col_gap5, Inches(3.85), col_w5, Inches(2.55), C_ORANGE_LIGHT, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s5, Inches(0.80) + col_w5 + col_gap5, Inches(3.95), Inches(1.20), Inches(0.22), "AI RATIONALE", C_ORANGE)
    _, tf_ai = add_tb(s5, Inches(0.75) + col_w5 + col_gap5, Inches(4.22), col_w5 - Inches(0.20), Inches(2.10), mt=0.01, mb=0.01)
    p = tf_ai.paragraphs[0]; p.text = "🤖 WHERE IS AI NEEDED?"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    ai_points = [
        ("Subtle Artifacts: ", "Deep neural nets detect sub-pixel boundary warping and synthetic vocal jitter invisible to rule engines."),
        ("Invariant Matching: ", "Embeddings match cropped, compressed, or speed-altered re-uploads across platforms."),
        ("Deterministic Rules: ", "Takedown filing and provenance validation use deterministic logic to prevent false claims.")
    ]
    for at, ad in ai_points:
        pb = tf_ai.add_paragraph(); pb.space_before = Pt(1.2)
        r1 = pb.add_run(); r1.text = "• " + at; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = ad; r2.font.name = FONT; r2.font.size = Pt(10.5); r2.font.color.rgb = C_CHARCOAL

    # Card 3: Hackathon MVP Scope
    add_card(s5, Inches(0.65) + (col_w5 + col_gap5) * 2, Inches(3.85), col_w5, Inches(2.55), C_GREEN_LIGHT, C_GREEN_BORDER, 1.2)
    add_pill_badge(s5, Inches(0.80) + (col_w5 + col_gap5) * 2, Inches(3.95), Inches(1.20), Inches(0.22), "MVP SCOPE", C_GREEN)
    _, tf_mvp = add_tb(s5, Inches(0.75) + (col_w5 + col_gap5) * 2, Inches(4.22), col_w5 - Inches(0.20), Inches(2.10), mt=0.01, mb=0.01)
    p = tf_mvp.paragraphs[0]; p.text = "🎯 HACKATHON MVP SCOPE"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_GREEN
    mvp_items = [
        ("Media Ingestion: ", "Direct video upload & social URL parser."),
        ("Forensic Scoring: ", "Per-frame Grad-CAM heatmaps & verdict."),
        ("Variant Matching: ", "pHash detection of cropped/mirrored copies."),
        ("Spread Graph: ", "D3.js simulated viral propagation DAG."),
        ("Automated DMCA: ", "Pre-filled legal notice & C2PA manifest log.")
    ]
    for mt, md in mvp_items:
        pb = tf_mvp.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "✔ " + mt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_GREEN
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(10.5); r2.font.color.rgb = C_CHARCOAL

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 6: EXPECTED IMPACT & EXECUTION PLAN
    # ═════════════════════════════════════════════════════════════════════════
    s6 = prs.slides[5]
    setup_slide_header(s6, "Expected Impact & Execution Plan",
                       "Measure the Speed. Stop the Virality. Protect Victims at Scale.",
                       "Quantifiable metrics, stakeholder benefits, and 24-hour milestones.")

    # Top Row: Impact (Left), Evaluation Targets (Center), Who Benefits (Right)
    # Left: Expected Impact
    add_card(s6, Inches(0.65), Inches(1.25), Inches(3.65), Inches(2.25), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s6, Inches(0.80), Inches(1.35), Inches(1.30), Inches(0.22), "EXPECTED IMPACT", C_BLUE)
    _, tf = add_tb(s6, Inches(0.75), Inches(1.60), Inches(3.45), Inches(1.85), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "📈 QUANTIFIABLE OUTCOMES"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_BLUE
    impacts = [
        ("95% Faster Takedown: ", "Cuts triage from 72h to <15 mins."),
        ("Viral Containment: ", "Halts derivative mirrors before 100K views."),
        ("Victim Agency: ", "Free 1-click court-ready C2PA legal dossier."),
        ("Scalable Workers: ", "Stateless pipeline handles 10,000+ daily checks.")
    ]
    for it, idesc in impacts:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "• " + it; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = idesc; r2.font.name = FONT; r2.font.size = Pt(10.5); r2.font.color.rgb = C_CHARCOAL

    # Center: 4 Key Simulation Metrics
    add_card(s6, Inches(4.45), Inches(1.25), Inches(4.45), Inches(2.25), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s6, Inches(4.60), Inches(1.35), Inches(1.40), Inches(0.22), "TARGET BENCHMARKS", C_ORANGE)
    _, tf = add_tb(s6, Inches(4.55), Inches(1.60), Inches(4.25), Inches(1.85), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "🎯 EVALUATION TARGETS"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    metrics = [
        (">92% Detection F1: ", "Benchmarked on DFDC & FaceForensics++"),
        ("<15 Min Takedown: ", "Automated DMCA vs. 3-day manual triage"),
        (">88% Variant Match: ", "Identifies cropped & re-encoded social mirrors"),
        ("<3% False Positives: ", "Validated against authentic broadcast news")
    ]
    for mt, md in metrics:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "✔ " + mt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_GREEN
        r2 = pb.add_run(); r2.text = md; r2.font.name = FONT; r2.font.size = Pt(10.5); r2.font.color.rgb = C_CHARCOAL

    # Right Card: Who Benefits?
    add_card(s6, Inches(9.05), Inches(1.25), Inches(3.63), Inches(2.25), C_WHITE, C_GREEN_BORDER, 1.2)
    add_pill_badge(s6, Inches(9.20), Inches(1.35), Inches(1.30), Inches(0.22), "KEY BENEFICIARIES", C_GREEN)
    _, tf = add_tb(s6, Inches(9.15), Inches(1.60), Inches(3.43), Inches(1.85), mt=0.01, mb=0.01)
    p = tf.paragraphs[0]; p.text = "👥 WHO BENEFITS?"; p.font.name = FONT; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = C_GREEN
    benefits = [
        ("Targeted Victims: ", "Instant removal of defamatory synthetic media."),
        ("Platform Moderators: ", "Automated triage eliminating manual review backlogs."),
        ("Fact-Checkers: ", "Rapid verification for breaking user-generated video."),
        ("Legal Teams: ", "Verifiable cryptographic chain of custody for court.")
    ]
    for bt, bd in benefits:
        pb = tf.add_paragraph(); pb.space_before = Pt(1.0)
        r1 = pb.add_run(); r1.text = "• " + bt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = bd; r2.font.name = FONT; r2.font.size = Pt(10.5); r2.font.color.rgb = C_CHARCOAL

    # Bottom Row: Roadmap & Future Scope
    # Left: 24-Hour Hackathon Roadmap
    add_card(s6, Inches(0.65), Inches(3.62), Inches(6.40), Inches(2.70), C_WHITE, C_CARD_BORDER, 1.0)
    add_pill_badge(s6, Inches(0.80), Inches(3.72), Inches(1.60), Inches(0.24), "HACKATHON EXECUTION", C_DARK)
    _, tf_rd = add_tb(s6, Inches(0.75), Inches(4.00), Inches(6.20), Inches(2.25))
    p = tf_rd.paragraphs[0]; p.text = "⏱ 24-HOUR HACKATHON MILESTONE ROADMAP"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_DARK
    sprints = [
        ("Hours 00–04 (Setup): ", "FastAPI ingestion, OpenCV frames, model weights."),
        ("Hours 04–10 (Forensics): ", "EfficientNet artifacts, WavLM biometrics, heatmaps."),
        ("Hours 10–16 (Spread Graph): ", "pHash indexing, Milvus vector search, NetworkX DAG."),
        ("Hours 16–20 (UI & Legal): ", "React dashboard, D3.js spread graph, DMCA notices."),
        ("Hours 20–24 (Benchmarking): ", "Attack simulation, latency tuning, final pitch demo.")
    ]
    for st, sd in sprints:
        pb = tf_rd.add_paragraph(); pb.space_before = Pt(1.5)
        r1 = pb.add_run(); r1.text = "• " + st; r1.font.name = FONT; r1.font.size = Pt(11.5); r1.font.bold = True; r1.font.color.rgb = C_ORANGE
        r2 = pb.add_run(); r2.text = sd; r2.font.name = FONT; r2.font.size = Pt(11.5); r2.font.color.rgb = C_CHARCOAL

    # Right: Future Scope & Scalability
    add_card(s6, Inches(7.20), Inches(3.62), Inches(5.48), Inches(2.70), C_ORANGE_LIGHT, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s6, Inches(7.35), Inches(3.72), Inches(1.40), Inches(0.24), "EXPANSION PLANS", C_ORANGE)
    _, tf_fut = add_tb(s6, Inches(7.30), Inches(4.00), Inches(5.28), Inches(2.25))
    p = tf_fut.paragraphs[0]; p.text = "🚀 FUTURE SCOPE & SCALABILITY"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    future_items = [
        ("Social Extension: ", "Real-time deepfake warning badge overlay on video feeds."),
        ("Decentralized Provenance: ", "C2PA blockchain ledger for immutable origin logs."),
        ("Moderation Webhooks: ", "Direct push connectors to YouTube, X, and TikTok APIs."),
        ("Live Stream Forensics: ", "Sub-second audio-visual inspection for live broadcast feeds.")
    ]
    for ft, fd in future_items:
        pb = tf_fut.add_paragraph(); pb.space_before = Pt(1.5)
        r1 = pb.add_run(); r1.text = "• " + ft; r1.font.name = FONT; r1.font.size = Pt(11.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = fd; r2.font.name = FONT; r2.font.size = Pt(11.5); r2.font.color.rgb = C_CHARCOAL

    # ═════════════════════════════════════════════════════════════════════════
    # SLIDE 7: CONCLUSION & REFERENCES
    # ═════════════════════════════════════════════════════════════════════════
    s7 = prs.slides[6]
    setup_slide_header(s7, "Conclusion & References",
                       "Protecting Truth, Identity, and Trust in the Age of Generative AI.",
                       "\"Shifting the balance of power from deepfake creators back to victims.\"")

    # Top Left: Key Takeaways Card
    add_card(s7, Inches(0.65), Inches(1.25), Inches(5.15), Inches(3.05), C_WHITE, C_ORANGE_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(1.35), Inches(1.30), Inches(0.24), "CORE SUMMARY", C_ORANGE)
    _, tf_k = add_tb(s7, Inches(0.75), Inches(1.65), Inches(4.95), Inches(2.55))
    p = tf_k.paragraphs[0]; p.text = "💡 KEY TAKEAWAYS"; p.font.name = FONT; p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_ORANGE_DARK
    takeaways = [
        ("Proactive Defense: ", "DeepGuard transforms deepfake response from helpless manual reporting into automated viral containment."),
        ("Multi-Modal Truth: ", "Fuses visual artifacts, audio biometrics, and perceptual hashing to resist evasion transforms."),
        ("Cross-Platform Mapping: ", "Traces patient-zero source and every derivative mirror across networks on a directed DAG."),
        ("Victim Empowerment: ", "Equips non-technical users with court-ready C2PA evidence and 1-click legal DMCA filing.")
    ]
    for kt, kd in takeaways:
        pb = tf_k.add_paragraph(); pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "• " + kt; r1.font.name = FONT; r1.font.size = Pt(11.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = kd; r2.font.name = FONT; r2.font.size = Pt(11.5); r2.font.color.rgb = C_CHARCOAL

    # Top Right: Realistic C2PA Cryptographic Provenance Visual
    add_card(s7, Inches(5.95), Inches(1.25), Inches(6.73), Inches(3.05), C_SLATE_800, C_CARD_BORDER, 1.2)
    s7.shapes.add_picture('realistic_c2pa_provenance.jpg', Inches(5.98), Inches(1.28), Inches(6.67), Inches(2.99))

    # Bottom: References & Benchmarks (2 Clean Columns)
    add_card(s7, Inches(0.65), Inches(4.40), Inches(12.03), Inches(1.95), C_WHITE, C_BLUE_BORDER, 1.2)
    add_pill_badge(s7, Inches(0.80), Inches(4.50), Inches(1.60), Inches(0.24), "ACADEMIC EVIDENCE", C_BLUE)
    _, tf_rf = add_tb(s7, Inches(0.75), Inches(4.80), Inches(11.83), Inches(1.50))
    p = tf_rf.paragraphs[0]; p.text = "📚 VERIFIABLE REFERENCES & SCIENTIFIC BENCHMARKS"; p.font.name = FONT; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_BLUE

    # References Col 1
    _, tf_c1 = add_tb(s7, Inches(0.75), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col1 = [
        ("1. FaceForensics++ (ICCV): ", "Learning to Detect Manipulated Facial Images across Deepfake Methods. [arXiv:1901.08971]"),
        ("2. Meta AI / Kaggle DFDC: ", "The DeepFake Detection Challenge Dataset and Benchmark Findings. [arXiv:2006.07397]"),
        ("3. C2PA Standard: ", "Coalition for Content Provenance and Authenticity Technical Specification (c2pa.org).")
    ]
    for idx, (rt, rd) in enumerate(ref_col1):
        pb = tf_c1.paragraphs[0] if idx == 0 else tf_c1.add_paragraph()
        if idx > 0: pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "• " + rt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = rd; r2.font.name = FONT; r2.font.size = Pt(10.5); r2.font.color.rgb = C_CHARCOAL

    # References Col 2
    _, tf_c2 = add_tb(s7, Inches(6.75), Inches(5.08), Inches(5.80), Inches(1.20))
    ref_col2 = [
        ("4. Sumsub Fraud Report: ", "550%+ Surge in GenAI Deepfakes across Social and Identity Platforms (2024)."),
        ("5. IEEE TIFS: ", "Perceptual Hashing & Robust Media Fingerprinting under Non-Linear Compression."),
        ("6. Legal Compliance: ", "US Digital Millennium Copyright Act (17 U.S.C. § 512) & EU AI Act Annex IV.")
    ]
    for idx, (rt, rd) in enumerate(ref_col2):
        pb = tf_c2.paragraphs[0] if idx == 0 else tf_c2.add_paragraph()
        if idx > 0: pb.space_before = Pt(2)
        r1 = pb.add_run(); r1.text = "• " + rt; r1.font.name = FONT; r1.font.size = Pt(10.5); r1.font.bold = True; r1.font.color.rgb = C_DARK
        r2 = pb.add_run(); r2.text = rd; r2.font.name = FONT; r2.font.size = Pt(10.5); r2.font.color.rgb = C_CHARCOAL

    # Save presentations
    prs.save(output_pptx)
    prs.save('AI_Avengers_4.pptx')
    print(f"Saved PPTX successfully to: {output_pptx} and AI_Avengers_4.pptx")
    print(f"Total slides: {len(prs.slides)}")

    # Export to PDF and preview PNGs
    try:
        import win32com.client
        ppt = win32com.client.Dispatch('PowerPoint.Application')
        ppt.Visible = 1
        full_pptx_path = os.path.abspath(output_pptx)
        full_pdf_path = os.path.abspath(output_pdf)
        deck = ppt.Presentations.Open(full_pptx_path)
        deck.SaveAs(full_pdf_path, 32)
        for i in range(1, 8):
            out_img = os.path.abspath(f'slide_{i}_preview.png')
            deck.Slides(i).Export(out_img, 'PNG', 1920, 1080)
        deck.Close()

        # Also export AI_Avengers_4.pdf
        full_ai_pptx = os.path.abspath('AI_Avengers_4.pptx')
        full_ai_pdf = os.path.abspath('AI_Avengers_4.pdf')
        deck_ai = ppt.Presentations.Open(full_ai_pptx)
        deck_ai.SaveAs(full_ai_pdf, 32)
        deck_ai.Close()

        ppt.Quit()
        print(f"Exported PDF and all 7 preview PNGs successfully!")
    except Exception as e:
        print(f"Export note: {e}")

if __name__ == '__main__':
    build_presentation()
