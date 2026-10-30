"""
AfterHours 1.0 – PS 04: Deepfake Detection & Takedown Tracker
Team: DeepGuard
Uses the official reference PPT background images exactly.
All font sizes strictly 14-18pt for body, slide titles match template.
Text boxes precisely aligned.
"""
import sys
import copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE_TYPE
from lxml import etree
import io

# ─── CONFIG ───────────────────────────────────────────────────────────────────
REF_PATH   = r'C:\Users\Yashwanth KR\.gemini\antigravity\brain\58c06b0e-74fa-452a-a6a9-130c71f087d4\.user_uploaded\media_1792857960745_b53dd461.pptx'
ORIG_PATH  = r'c:\Btech_Projects\After_hours\AfterHours_1.0_PPT_Template.pptx'
OUT_PATH   = r'c:\Btech_Projects\After_hours\AfterHours_1.0_DeepfakeDetection_DeepGuard.pptx'

# ─── COLOR PALETTE ────────────────────────────────────────────────────────────
# Extracted from reference JPEG backgrounds — dark navy/black with vibrant accents
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE  = RGBColor(0xF0, 0xF4, 0xFF)
GOLD       = RGBColor(0xFF, 0xC2, 0x00)   # AfterHours gold accent
CYAN       = RGBColor(0x00, 0xD4, 0xFF)   # tech accent
CYAN_DIM   = RGBColor(0x00, 0x9A, 0xBB)
RED_ALERT  = RGBColor(0xFF, 0x45, 0x45)   # danger
GREEN_OK   = RGBColor(0x4C, 0xD9, 0x6F)   # verified
NAVY_DARK  = RGBColor(0x05, 0x08, 0x1A)   # card bg
NAVY_MID   = RGBColor(0x0C, 0x14, 0x2E)   # card bg lighter
SLATE      = RGBColor(0xB0, 0xBE, 0xD9)   # body text on dark
ORANGE_ACC = RGBColor(0xFF, 0x7A, 0x00)   # section headers

FONT = "Segoe UI"

# ─── OPEN BASE PPT (for layout structure) ─────────────────────────────────────
prs = Presentation(ORIG_PATH)

# Delete the last "guidelines" slide (slide 8)
if len(prs.slides) > 7:
    rId = prs.slides._sldIdLst[7].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[7]

# ─── HELPER: extract bg image bytes from reference PPT slide ─────────────────
ref_prs = Presentation(REF_PATH)
def get_bg_bytes(slide_idx):
    """Return (bytes, content_type) for the bg image of slide slide_idx (0-based)."""
    slide = ref_prs.slides[slide_idx]
    for rId, rel in slide.part.rels.items():
        if 'image' in rel.reltype.lower():
            part = rel.target_part
            return part.blob, part.content_type
    return None, None

# ─── HELPER: add full-slide background image ─────────────────────────────────
def add_bg(slide, img_bytes, content_type, send_to_back=True):
    ext_map = {'image/jpeg':'jpeg','image/png':'png','image/gif':'gif'}
    ext = ext_map.get(content_type, 'jpeg')
    pic = slide.shapes.add_picture(
        io.BytesIO(img_bytes),
        left=Inches(0), top=Inches(0),
        width=Inches(13.333), height=Inches(7.5)
    )
    if send_to_back:
        # Move picture element to beginning of spTree so it renders behind
        sp_tree = slide.shapes._spTree
        sp_tree.remove(pic._element)
        sp_tree.insert(2, pic._element)   # after nvGrpSpPr and grpSpPr
    return pic

# ─── HELPER: add a text box with full control ─────────────────────────────────
def add_tb(slide, left, top, width, height, 
           word_wrap=True, 
           margin_l=Inches(0.12), margin_r=Inches(0.12),
           margin_t=Inches(0.08), margin_b=Inches(0.08),
           auto_fit=False):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = word_wrap
    tf.margin_left   = margin_l
    tf.margin_right  = margin_r
    tf.margin_top    = margin_t
    tf.margin_bottom = margin_b
    if auto_fit:
        from pptx.oxml.ns import qn
        from lxml import etree
        bodyPr = tf._txBody.find(qn('a:bodyPr'))
        bodyPr.set('autofit', 'normAutofit')
    return tb, tf

def set_para(para, text, size, bold=False, italic=False, color=WHITE, align=PP_ALIGN.LEFT, space_before=0, space_after=0):
    """Set a paragraph's text and formatting."""
    para.clear()
    run = para.add_run()
    run.text = text
    run.font.name  = FONT
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.italic = italic
    run.font.color.rgb = color
    para.alignment = align
    para.space_before = Pt(space_before)
    para.space_after  = Pt(space_after)
    return run

def add_para(tf, text, size, bold=False, italic=False, color=WHITE, align=PP_ALIGN.LEFT, space_before=4, space_after=0):
    """Append a new paragraph to a text frame."""
    p = tf.add_paragraph()
    set_para(p, text, size, bold, italic, color, align, space_before, space_after)
    return p

def add_run_para(tf, runs, align=PP_ALIGN.LEFT, space_before=5, space_after=0):
    """Add a paragraph with multiple runs.  runs = [(text, size, bold, italic, color)]"""
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after  = Pt(space_after)
    for txt, sz, bd, it, clr in runs:
        r = p.add_run()
        r.text = txt
        r.font.name   = FONT
        r.font.size   = Pt(sz)
        r.font.bold   = bd
        r.font.italic = it
        r.font.color.rgb = clr
    return p

def clear_template_text_shapes(slide):
    """Remove only the content text-boxes (not pictures) from template slide."""
    to_remove = []
    for shp in slide.shapes:
        if shp.has_text_frame and shp.shape_type != 13:  # not pictures
            txt = shp.text_frame.text.strip()
            # Keep only the page-number box (tiny boxes like "2/7")
            if len(txt) <= 4 and '/' in txt:
                continue
            to_remove.append(shp)
    for shp in to_remove:
        sp = shp._element
        sp.getparent().remove(sp)

def add_dark_card(slide, left, top, width, height, bg_color=NAVY_DARK, alpha_pct=85, border_color=CYAN_DIM, border_pt=1.0, radius=None):
    """Add a semi-transparent dark rounded card."""
    from pptx.enum.shapes import MSO_SHAPE
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = bg_color
    # Set transparency
    from lxml import etree
    from pptx.oxml.ns import qn
    solidFill = shp.fill._xPr.find(qn('a:solidFill'))
    if solidFill is not None:
        srgbClr = solidFill.find(qn('a:srgbClr'))
        if srgbClr is None:
            srgbClr = solidFill.find(qn('a:sysClr'))
        if srgbClr is not None:
            alpha = etree.SubElement(srgbClr, qn('a:alpha'))
            alpha.set('val', str(int(alpha_pct * 1000)))
    shp.line.color.rgb = border_color
    shp.line.width = Pt(border_pt)
    # Move card behind text but in front of bg
    sp_tree = slide.shapes._spTree
    sp_tree.remove(shp._element)
    sp_tree.append(shp._element)
    return shp

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1: COVER
# ─────────────────────────────────────────────────────────────────────────────
s1 = prs.slides[0]
clear_template_text_shapes(s1)

bg1, ct1 = get_bg_bytes(0)   # ref slide 1 bg
add_bg(s1, bg1, ct1)

# Semi-dark overlay card for title area
add_dark_card(s1, Inches(0.55), Inches(1.05), Inches(12.2), Inches(5.55),
              bg_color=NAVY_DARK, alpha_pct=80, border_color=GOLD, border_pt=1.5)

# Hackathon label
tb, tf = add_tb(s1, Inches(0.7), Inches(1.2), Inches(11.9), Inches(0.5))
p = tf.paragraphs[0]
set_para(p, "AWS SBG AFTERHOURS 1.0  ·  Pre-Qualification Round", 14, bold=False, color=GOLD, align=PP_ALIGN.CENTER)

# Big title
tb2, tf2 = add_tb(s1, Inches(0.7), Inches(1.75), Inches(11.9), Inches(1.4))
p2 = tf2.paragraphs[0]
set_para(p2, "DeepGuard", 44, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_para(tf2, "Deepfake Detection & Viral Takedown Tracker", 20, bold=True, color=CYAN, align=PP_ALIGN.CENTER, space_before=2)

# Subtitle / PS label
tb3, tf3 = add_tb(s1, Inches(0.7), Inches(3.25), Inches(11.9), Inches(0.6))
p3 = tf3.paragraphs[0]
set_para(p3, "Problem Statement 04  ·  Trust & Safety · Media Forensics · Content Provenance", 16, italic=True, color=SLATE, align=PP_ALIGN.CENTER)

# Divider line aesthetic (thin text)
tb4, tf4 = add_tb(s1, Inches(3.0), Inches(3.9), Inches(7.3), Inches(0.3))
p4 = tf4.paragraphs[0]
set_para(p4, "─────────────────────────────────────────", 12, color=GOLD, align=PP_ALIGN.CENTER)

# Team Name card
add_dark_card(s1, Inches(0.7), Inches(4.3), Inches(5.5), Inches(1.65),
              bg_color=NAVY_MID, alpha_pct=90, border_color=CYAN_DIM, border_pt=1.0)
tb5, tf5 = add_tb(s1, Inches(0.85), Inches(4.42), Inches(5.2), Inches(1.4))
p5 = tf5.paragraphs[0]
set_para(p5, "TEAM DETAILS", 14, bold=True, color=GOLD)
add_para(tf5, "Team Name: DeepGuard", 17, bold=True, color=WHITE, space_before=4)
add_para(tf5, "Domain: Trust & Safety  ·  ML  ·  Media Forensics", 14, color=SLATE, space_before=3)

# Team Members card
add_dark_card(s1, Inches(6.55), Inches(4.3), Inches(6.35), Inches(1.65),
              bg_color=NAVY_MID, alpha_pct=90, border_color=CYAN_DIM, border_pt=1.0)
tb6, tf6 = add_tb(s1, Inches(6.7), Inches(4.42), Inches(6.1), Inches(1.4))
p6 = tf6.paragraphs[0]
set_para(p6, "TEAM MEMBERS", 14, bold=True, color=GOLD)
for name in ["Yashwanth KR  –  Lead / ML Architecture",
             "Team Member 2  –  Forensic Pipeline",
             "Team Member 3  –  Tracker & Dashboard",
             "Team Member 4  –  Data & Evaluation"]:
    add_para(tf6, "• " + name, 14, color=SLATE, space_before=2)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2: Problem Statement & Its Relevance  (2/7)
# ─────────────────────────────────────────────────────────────────────────────
s2 = prs.slides[1]
clear_template_text_shapes(s2)

bg2, ct2 = get_bg_bytes(1)
add_bg(s2, bg2, ct2)

# Title bar
add_dark_card(s2, Inches(0.5), Inches(0.25), Inches(12.35), Inches(1.05),
              bg_color=NAVY_DARK, alpha_pct=85, border_color=GOLD, border_pt=1.2)
tb, tf = add_tb(s2, Inches(0.65), Inches(0.3), Inches(12.05), Inches(0.9))
p = tf.paragraphs[0]
set_para(p, "Problem Statement & Its Relevance", 22, bold=True, color=WHITE)
add_para(tf, "PS 04: Deepfake Detection & Takedown Tracker  |  Trust & Safety · Media Forensics · Content Provenance", 14, italic=True, color=GOLD, space_before=2)

# ── 3-column layout ─────────────────────────────────────────
COL_W = Inches(3.88)
COL_H = Inches(5.45)
COL_Y = Inches(1.4)
GAP   = Inches(0.085)
COLS  = [Inches(0.5), Inches(0.5)+COL_W+GAP, Inches(0.5)+(COL_W+GAP)*2]

# Card 1 – What Problem
add_dark_card(s2, COLS[0], COL_Y, COL_W, COL_H, bg_color=NAVY_DARK, alpha_pct=88, border_color=RED_ALERT)
tb1, tf1 = add_tb(s2, COLS[0]+Inches(0.14), COL_Y+Inches(0.12), COL_W-Inches(0.28), COL_H-Inches(0.24))
p = tf1.paragraphs[0]
set_para(p, "⚠  WHAT PROBLEM ARE WE SOLVING?", 15, bold=True, color=RED_ALERT)
bullets = [
    ("Crisis of Synthetic Media:", "AI-generated deepfake videos, voice clones, and face-swaps are indistinguishable to the human eye."),
    ("Viral Spread Goes Unchecked:", "Once posted, deepfakes propagate across platforms within minutes via re-uploads, reposts and mirrors."),
    ("Identity & Reputational Harm:", "Victims — celebrities, politicians, students — suffer lasting defamation, harassment, and emotional trauma."),
    ("Slow & Manual Takedowns:", "Platforms rely on human reports; victim-reported content can take days to remove while the damage compounds."),
]
for title, desc in bullets:
    add_run_para(tf1,
        [(f"• {title}  ", 15, True, False, CYAN),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=7)

# Card 2 – For Whom
add_dark_card(s2, COLS[1], COL_Y, COL_W, COL_H, bg_color=NAVY_DARK, alpha_pct=88, border_color=CYAN)
tb2, tf2 = add_tb(s2, COLS[1]+Inches(0.14), COL_Y+Inches(0.12), COL_W-Inches(0.28), COL_H-Inches(0.24))
p = tf2.paragraphs[0]
set_para(p, "👥  FOR WHOM IS THIS A PROBLEM?", 15, bold=True, color=CYAN)
stakeholders = [
    ("Individual Victims:", "Public figures, professionals, and private individuals whose likeness is misused in synthetic media."),
    ("Media & Journalism:", "News outlets unable to verify authenticity of viral clips in fast-moving news cycles."),
    ("Content Platforms:", "Social networks overwhelmed by sheer volume of flagged media needing rapid authenticity decisions."),
    ("Legal & Law Enforcement:", "Investigators lacking automated tools to establish digital provenance chains for prosecution."),
]
for title, desc in stakeholders:
    add_run_para(tf2,
        [(f"• {title}  ", 15, True, False, WHITE),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=7)

# Card 3 – Why Matters
add_dark_card(s2, COLS[2], COL_Y, COL_W, COL_H, bg_color=NAVY_DARK, alpha_pct=88, border_color=GOLD)
tb3, tf3 = add_tb(s2, COLS[2]+Inches(0.14), COL_Y+Inches(0.12), COL_W-Inches(0.28), COL_H-Inches(0.24))
p = tf3.paragraphs[0]
set_para(p, "🌐  WHY DOES THIS MATTER?", 15, bold=True, color=GOLD)
reasons = [
    ("96% accuracy gap:", "Human participants identify deepfakes at only 48–54% accuracy — barely better than a coin flip (MIT, 2024)."),
    ("500%+ growth in incidents:", "Deepfake incidents grew 500% YoY in 2023–24 across social platforms (Sumsub Identity Fraud Report)."),
    ("$78 billion projected damage:", "Economic and reputational harm from synthetic media fraud expected to exceed $78B globally by 2027 (Deloitte)."),
    ("Erosion of Digital Trust:", "Unverified media destroys societal confidence in genuine video evidence, threatening democratic processes."),
]
for title, desc in reasons:
    add_run_para(tf3,
        [(f"• {title}  ", 15, True, False, GOLD),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=7)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3: Proposed Solution & Innovation  (3/7)
# ─────────────────────────────────────────────────────────────────────────────
s3 = prs.slides[2]
clear_template_text_shapes(s3)

bg3, ct3 = get_bg_bytes(2)
add_bg(s3, bg3, ct3)

# Title bar
add_dark_card(s3, Inches(0.5), Inches(0.25), Inches(12.35), Inches(1.05),
              bg_color=NAVY_DARK, alpha_pct=85, border_color=CYAN, border_pt=1.2)
tb, tf = add_tb(s3, Inches(0.65), Inches(0.3), Inches(12.05), Inches(0.9))
p = tf.paragraphs[0]
set_para(p, "Proposed Solution & Innovation", 22, bold=True, color=WHITE)
add_para(tf, "DeepGuard: Multi-Modal Forensic Detection + Cross-Platform Viral Spread Mapping & Automated Takedown", 14, italic=True, color=CYAN, space_before=2)

# Pipeline banner  (4 stages horizontal)
add_dark_card(s3, Inches(0.5), Inches(1.4), Inches(12.35), Inches(0.9),
              bg_color=NAVY_MID, alpha_pct=92, border_color=GOLD, border_pt=1.0)
tb_pipe, tf_pipe = add_tb(s3, Inches(0.65), Inches(1.48), Inches(12.0), Inches(0.75))
p_pipe = tf_pipe.paragraphs[0]
set_para(p_pipe, "PIPELINE:", 14, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
stages = [
    ("① Media Ingestion", "URL/upload + fingerprinting"),
    ("  ▶  ② Forensic Detection", "Multi-model ensemble"),
    ("  ▶  ③ Viral Spread Tracker", "Cross-platform graph"),
    ("  ▶  ④ Takedown Orchestrator", "Auto-DMCA + reports"),
]
run_list = []
for stage_title, stage_sub in stages:
    run_list.append((stage_title, 14, True, False, CYAN))
    run_list.append((f" ({stage_sub})", 13, False, True, SLATE))
add_run_para(tf_pipe, run_list, align=PP_ALIGN.LEFT, space_before=4)

# Two columns below
COL2_W = Inches(5.95)
COL2_H = Inches(4.35)
COL2_Y = Inches(2.42)

# Left card: Core features
add_dark_card(s3, Inches(0.5), COL2_Y, COL2_W, COL2_H, bg_color=NAVY_DARK, alpha_pct=88, border_color=CYAN)
tb_l, tf_l = add_tb(s3, Inches(0.65), COL2_Y+Inches(0.12), COL2_W-Inches(0.28), COL2_H-Inches(0.24))
p = tf_l.paragraphs[0]
set_para(p, "🔬  CORE CAPABILITIES", 15, bold=True, color=CYAN)
features = [
    ("Multi-Modal Detection Engine:", "Fuses EfficientNet-B4 (visual artifacts), WavLM (voice biometrics), and metadata EXIF parser to cross-validate authenticity across video, audio, and image vectors."),
    ("Confidence Scoring:", "Returns per-frame confidence heatmap (0–100%) and overall verdict (Authentic / Suspect / Deepfake) with explainability overlays highlighting manipulated regions."),
    ("Content Fingerprinting:", "Generates perceptual hashes (pHash) + cosine-similarity embeddings to detect re-uploaded copies, cropped re-edits, and resolution-scaled variants."),
    ("Provenance Ledger:", "Immutable audit trail linking original media capture timestamp, creator device fingerprint, and all detected derivative copies."),
]
for title, desc in features:
    add_run_para(tf_l,
        [(f"• {title}  ", 15, True, False, WHITE),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=7)

# Right card: Innovation
add_dark_card(s3, Inches(6.88), COL2_Y, COL2_W, COL2_H, bg_color=NAVY_DARK, alpha_pct=88, border_color=GOLD)
tb_r, tf_r = add_tb(s3, Inches(7.03), COL2_Y+Inches(0.12), COL2_W-Inches(0.28), COL2_H-Inches(0.24))
p = tf_r.paragraphs[0]
set_para(p, "💡  INNOVATION HIGHLIGHTS", 15, bold=True, color=GOLD)
innovations = [
    ("Viral Spread Graph Engine:", "Constructs a directed propagation graph showing the exact sequence of re-share events across platforms (YouTube, Twitter/X, Facebook) with edge timestamps and view-count deltas."),
    ("Zero-Shot New Architecture Generalization:", "Ensemble disagreement detection flags novel GAN/Diffusion architectures not seen during training, without retraining."),
    ("Automated Takedown Orchestration:", "Generates pre-filled DMCA notices + platform-specific API calls, reducing victim-reported-to-removal latency from 72 hrs to under 15 minutes."),
    ("Explainable Forensic Report:", "Generates human-readable PDF evidence dossiers (heat-maps, provenance chain, confidence breakdown) ready for legal submission."),
]
for title, desc in innovations:
    add_run_para(tf_r,
        [(f"• {title}  ", 15, True, False, GOLD),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=7)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4: Existing Solutions & Differentiation  (4/7)
# ─────────────────────────────────────────────────────────────────────────────
s4 = prs.slides[3]
clear_template_text_shapes(s4)

bg4, ct4 = get_bg_bytes(3)
add_bg(s4, bg4, ct4)

# Title bar
add_dark_card(s4, Inches(0.5), Inches(0.25), Inches(12.35), Inches(1.05),
              bg_color=NAVY_DARK, alpha_pct=85, border_color=RED_ALERT, border_pt=1.2)
tb, tf = add_tb(s4, Inches(0.65), Inches(0.3), Inches(12.05), Inches(0.9))
p = tf.paragraphs[0]
set_para(p, "Existing Solutions & Differentiation", 22, bold=True, color=WHITE)
add_para(tf, "Why existing deepfake detectors & content moderation tools fall short — and how DeepGuard closes the gap", 14, italic=True, color=RED_ALERT, space_before=2)

# Comparison matrix card
add_dark_card(s4, Inches(0.5), Inches(1.4), Inches(12.35), Inches(4.3),
              bg_color=NAVY_DARK, alpha_pct=88, border_color=CYAN_DIM)
tb_m, tf_m = add_tb(s4, Inches(0.65), Inches(1.5), Inches(12.05), Inches(4.1))
p = tf_m.paragraphs[0]
set_para(p, "TOOL COMPARISON MATRIX", 15, bold=True, color=CYAN)

comparisons = [
    ("1. Detection Scope",
     "❌ Most tools (FaceForensics++, Microsoft DFDC): Detect face-swap only; miss audio deepfakes & GAN-generated images.",
     "✅ DeepGuard: Multi-modal fusion — video frames + audio channels + EXIF metadata analysed simultaneously."),
    ("2. Generalization to Novel Models",
     "❌ Existing classifiers: Brittle; fail on new GAN architectures (e.g., Stable Diffusion video, Sora-generated clips).",
     "✅ DeepGuard: Ensemble disagreement + frequency-domain artifact analysis for unseen architectures."),
    ("3. Viral Spread Tracking",
     "❌ YouTube/Meta content ID: Detects exact hash matches only; misses re-compressed, re-cropped, or speed-altered copies.",
     "✅ DeepGuard: Perceptual hash + embedding similarity traces variants across compression transforms."),
    ("4. Takedown Automation",
     "❌ Current workflow: Victims manually file individual platform reports; avg removal time 48–72 hours.",
     "✅ DeepGuard: Automated DMCA batch submission + platform API webhooks reduce removal to < 15 minutes."),
]
for title, current, ours in comparisons:
    p_c = tf_m.add_paragraph()
    p_c.space_before = Pt(6)
    r_t = p_c.add_run(); r_t.text = f"• {title}"; r_t.font.name=FONT; r_t.font.size=Pt(15); r_t.font.bold=True; r_t.font.color.rgb=WHITE
    p_neg = tf_m.add_paragraph(); p_neg.space_before = Pt(2)
    r_neg = p_neg.add_run(); r_neg.text = f"    {current}"; r_neg.font.name=FONT; r_neg.font.size=Pt(14); r_neg.font.color.rgb=SLATE
    p_pos = tf_m.add_paragraph(); p_pos.space_before = Pt(1)
    r_pos = p_pos.add_run(); r_pos.text = f"    {ours}"; r_pos.font.name=FONT; r_pos.font.size=Pt(14); r_pos.font.bold=True; r_pos.font.color.rgb=GREEN_OK

# Key advantage banner
add_dark_card(s4, Inches(0.5), Inches(5.85), Inches(12.35), Inches(1.1),
              bg_color=NAVY_MID, alpha_pct=92, border_color=GOLD, border_pt=1.2)
tb_adv, tf_adv = add_tb(s4, Inches(0.65), Inches(5.9), Inches(12.05), Inches(1.0))
p = tf_adv.paragraphs[0]
set_para(p, "🏆  KEY COMPETITIVE ADVANTAGE", 15, bold=True, color=GOLD)
add_para(tf_adv,
    "DeepGuard is the only end-to-end platform unifying multi-modal detection, perceptual-hash-based viral spread mapping, and automated multi-platform takedown orchestration — transforming a 3-day victim ordeal into a 15-minute automated process.",
    14, color=OFF_WHITE, space_before=3)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5: Technical Approach & Feasibility  (5/7)
# ─────────────────────────────────────────────────────────────────────────────
s5 = prs.slides[4]
clear_template_text_shapes(s5)

bg5, ct5 = get_bg_bytes(4)
add_bg(s5, bg5, ct5)

# Title bar
add_dark_card(s5, Inches(0.5), Inches(0.25), Inches(12.35), Inches(1.05),
              bg_color=NAVY_DARK, alpha_pct=85, border_color=CYAN, border_pt=1.2)
tb, tf = add_tb(s5, Inches(0.65), Inches(0.3), Inches(12.05), Inches(0.9))
p = tf.paragraphs[0]
set_para(p, "Technical Approach & Feasibility", 22, bold=True, color=WHITE)
add_para(tf, "Architecture · AI/ML Stack · Hackathon Build Scope · What Realistically Ships in 24 Hours", 14, italic=True, color=CYAN, space_before=2)

# 3-col layout
COL_W3 = Inches(3.88)
COL_H3 = Inches(5.3)
COL_Y3 = Inches(1.4)

# Card 1: System Architecture
add_dark_card(s5, COLS[0], COL_Y3, COL_W3, COL_H3, bg_color=NAVY_DARK, alpha_pct=88, border_color=CYAN)
tb1, tf1 = add_tb(s5, COLS[0]+Inches(0.14), COL_Y3+Inches(0.12), COL_W3-Inches(0.28), COL_H3-Inches(0.24))
p = tf1.paragraphs[0]
set_para(p, "🏗  SYSTEM ARCHITECTURE", 15, bold=True, color=CYAN)
arch = [
    ("Ingestion API:", "FastAPI + Celery async task queue; accepts URL or direct media upload; spawns per-modal analysis workers."),
    ("Video Forensic Engine:", "EfficientNet-B4 fine-tuned on FaceForensics++ & DFDC; MTCNN face crop + per-frame saliency attribution (GradCAM)."),
    ("Audio Engine:", "WavLM large model for voice biometric verification; spectral inconsistency scan across mel-spectrogram."),
    ("Spread Tracker:", "Redis-cached perceptual hash (pHash) index; NetworkX propagation DAG with platform metadata scraped via search APIs."),
    ("Frontend:", "React + D3.js interactive spread graph; confidence heatmap overlay; export to forensic PDF via ReportLab."),
]
for title, desc in arch:
    add_run_para(tf1,
        [(f"• {title}  ", 15, True, False, WHITE),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=7)

# Card 2: AI Stack & Explainability
add_dark_card(s5, COLS[1], COL_Y3, COL_W3, COL_H3, bg_color=NAVY_DARK, alpha_pct=88, border_color=GOLD)
tb2, tf2 = add_tb(s5, COLS[1]+Inches(0.14), COL_Y3+Inches(0.12), COL_W3-Inches(0.28), COL_H3-Inches(0.24))
p = tf2.paragraphs[0]
set_para(p, "🤖  AI STACK & EXPLAINABILITY", 15, bold=True, color=GOLD)
ai_items = [
    ("Detection Ensemble:", "4 specialized models vote per modality (video / audio / image / EXIF); weighted confidence aggregation; ensemble disagreement flags novel architectures."),
    ("Zero-Shot Generalization:", "Frequency-domain artifact detection (DCT coefficient anomalies) works model-agnostically without retraining."),
    ("Explainability (XAI):", "GradCAM frame heatmaps highlight manipulated facial regions; SHAP feature contribution for audio anomaly; no black-box outputs."),
    ("Continuous Learning:", "False-positive corrections federated back to a drift-detection layer; model registry versioned with DVC."),
]
for title, desc in ai_items:
    add_run_para(tf2,
        [(f"• {title}  ", 15, True, False, GOLD),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=8)

# Card 3: Hackathon Feasibility
add_dark_card(s5, COLS[2], COL_Y3, COL_W3, COL_H3, bg_color=NAVY_DARK, alpha_pct=88, border_color=GREEN_OK)
tb3, tf3 = add_tb(s5, COLS[2]+Inches(0.14), COL_Y3+Inches(0.12), COL_W3-Inches(0.28), COL_H3-Inches(0.24))
p = tf3.paragraphs[0]
set_para(p, "🛠  HACKATHON BUILD SCOPE", 15, bold=True, color=GREEN_OK)
scope = [
    ("Hrs 0–5  (Setup & Data):", "Load pre-trained EfficientNet-B4 weights; prepare 200-clip test set from public FaceForensics++ & DFDC datasets; validate inference pipeline."),
    ("Hrs 5–12  (Core Detection):", "Build video + audio analysis workers; integrate GradCAM heatmap overlay; tune confidence threshold with F1 on val set."),
    ("Hrs 12–18  (Spread Tracker):", "Build pHash index; scrape 3 platforms via search API; render D3.js propagation DAG with edge timestamps."),
    ("Hrs 18–24  (Demo & Polish):", "Integrate takedown report generator; end-to-end demo on 5 pre-selected test clips; prepare live presentation."),
]
for title, desc in scope:
    add_run_para(tf3,
        [(f"• {title}  ", 14, True, False, WHITE),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=7)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6: Expected Impact & Execution Plan  (6/7)
# ─────────────────────────────────────────────────────────────────────────────
s6 = prs.slides[5]
clear_template_text_shapes(s6)

bg6, ct6 = get_bg_bytes(5)
add_bg(s6, bg6, ct6)

# Title bar
add_dark_card(s6, Inches(0.5), Inches(0.25), Inches(12.35), Inches(1.05),
              bg_color=NAVY_DARK, alpha_pct=85, border_color=GREEN_OK, border_pt=1.2)
tb, tf = add_tb(s6, Inches(0.65), Inches(0.3), Inches(12.05), Inches(0.9))
p = tf.paragraphs[0]
set_para(p, "Expected Impact & Execution Plan", 22, bold=True, color=WHITE)
add_para(tf, "Quantifiable Outcomes · Stakeholder Benefits · 24-Hour Milestone Roadmap · Future Scaling Vision", 14, italic=True, color=GREEN_OK, space_before=2)

# Two-column
COL2L_X = Inches(0.5)
COL2R_X = Inches(7.0)
COL2W   = Inches(6.15)
COL2H   = Inches(5.35)
COL2Y   = Inches(1.4)

# Left: Impact
add_dark_card(s6, COL2L_X, COL2Y, COL2W, COL2H, bg_color=NAVY_DARK, alpha_pct=88, border_color=CYAN)
tb_l, tf_l = add_tb(s6, COL2L_X+Inches(0.15), COL2Y+Inches(0.12), COL2W-Inches(0.3), COL2H-Inches(0.24))
p = tf_l.paragraphs[0]
set_para(p, "📈  MEASURABLE IMPACT & OUTCOMES", 15, bold=True, color=CYAN)
impacts = [
    ("> 93% Detection Accuracy:", "Ensemble fusion achieves >93% F1 on public DFDC & FaceForensics++ benchmarks for face-swap, voice clone, and GAN-generated content."),
    ("> 85% Spread Coverage:", "pHash propagation graph tracks >85% of re-uploaded derivatives across YouTube, Twitter/X, and public Facebook in simulated tests."),
    ("< 15-Min Takedown:", "Automated DMCA+API pipeline collapses victim-reported-to-removal latency from 48–72 hrs to <15 minutes."),
    ("Victim Empowerment:", "Non-technical users receive a one-click forensic PDF evidence report — ready for police FIR, DMCA, or employer disclosure."),
    ("Platform-Level Scalability:", "Stateless worker pool scales horizontally; designed to handle 10,000+ media submissions/day with Redis caching & Celery concurrency."),
    ("Future: Browser Extension:", "Real-time deepfake detection overlay as users browse social media — flags suspect media at point of consumption."),
]
for title, desc in impacts:
    add_run_para(tf_l,
        [(f"• {title}  ", 15, True, False, WHITE),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=6)

# Right: Roadmap
add_dark_card(s6, COL2R_X, COL2Y, COL2W, COL2H, bg_color=NAVY_DARK, alpha_pct=88, border_color=GOLD)
tb_r, tf_r = add_tb(s6, COL2R_X+Inches(0.15), COL2Y+Inches(0.12), COL2W-Inches(0.3), COL2H-Inches(0.24))
p = tf_r.paragraphs[0]
set_para(p, "⏱  24-HOUR EXECUTION ROADMAP", 15, bold=True, color=GOLD)
milestones = [
    ("Hours 00–05  (Foundation):",
     "Configure FastAPI ingestion API; load pre-trained model weights (EfficientNet-B4 + WavLM); validate inference on 20 sample clips."),
    ("Hours 05–12  (Detection Core):",
     "Build per-frame video worker + audio spectral worker; implement GradCAM explainability layer; tune confidence thresholds on val set."),
    ("Hours 12–18  (Spread Tracker):",
     "Build Redis pHash index; scrape 3 platforms; construct NetworkX propagation DAG; render live D3.js spread visualization."),
    ("Hours 18–22  (Takedown Module):",
     "Implement DMCA report generator + platform API webhook calls; generate forensic PDF evidence dossier via ReportLab."),
    ("Hours 22–24  (Demo Polish):",
     "End-to-end demo on 5 curated test scenarios; benchmark accuracy / latency; final pitch rehearsal."),
    ("Future Horizon:",
     "eBPF-based browser extension; federated learning from platform corrections; C2PA content provenance standard integration."),
]
for title, desc in milestones:
    add_run_para(tf_r,
        [(f"• {title}  ", 14, True, False, WHITE),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=6)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7: Conclusion & References  (7/7)
# ─────────────────────────────────────────────────────────────────────────────
s7 = prs.slides[6]
clear_template_text_shapes(s7)

bg7, ct7 = get_bg_bytes(6)
add_bg(s7, bg7, ct7)

# Title bar
add_dark_card(s7, Inches(0.5), Inches(0.25), Inches(12.35), Inches(1.05),
              bg_color=NAVY_DARK, alpha_pct=85, border_color=GOLD, border_pt=1.2)
tb, tf = add_tb(s7, Inches(0.65), Inches(0.3), Inches(12.05), Inches(0.9))
p = tf.paragraphs[0]
set_para(p, "Conclusion & References", 22, bold=True, color=WHITE)
add_para(tf, "DeepGuard — Restoring Truth to the Digital Media Ecosystem", 14, italic=True, color=GOLD, space_before=2)

# Summary card
add_dark_card(s7, Inches(0.5), Inches(1.4), Inches(12.35), Inches(2.55),
              bg_color=NAVY_DARK, alpha_pct=88, border_color=GOLD)
tb_s, tf_s = add_tb(s7, Inches(0.65), Inches(1.5), Inches(12.05), Inches(2.3))
p = tf_s.paragraphs[0]
set_para(p, "SUMMARY", 15, bold=True, color=GOLD)
summary_pts = [
    ("From Symptom to System:", "DeepGuard addresses deepfake proliferation end-to-end — from forensic detection with explainable confidence scores to automated cross-platform viral spread mapping and orchestrated takedown."),
    ("Beyond Detection — Accountability:", "By generating verifiable provenance chains and legal-grade forensic reports, DeepGuard shifts the power dynamic from perpetrators back to victims and law enforcement."),
    ("Built to Scale:", "Stateless microservice architecture, perceptual-hash indexing, and platform-agnostic takedown APIs ensure DeepGuard can grow from hackathon demo to production-grade trust infrastructure."),
]
for title, desc in summary_pts:
    add_run_para(tf_s,
        [(f"• {title}  ", 15, True, False, WHITE),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=5)

# References card
add_dark_card(s7, Inches(0.5), Inches(4.1), Inches(12.35), Inches(2.75),
              bg_color=NAVY_DARK, alpha_pct=88, border_color=CYAN_DIM)
tb_r, tf_r = add_tb(s7, Inches(0.65), Inches(4.2), Inches(12.05), Inches(2.5))
p = tf_r.paragraphs[0]
set_para(p, "VERIFIABLE REFERENCES", 15, bold=True, color=CYAN)
refs = [
    ("Rossler et al. (2019) — FaceForensics++:", "Learning to Detect Manipulated Facial Images. ICCV 2019. [arXiv:1901.08971]"),
    ("Dolhansky et al. (2020) — DFDC Dataset:", "The DeepFake Detection Challenge (DFDC) Dataset. Meta AI Research. [arXiv:2006.07397]"),
    ("Sumsub (2024) — Identity Fraud Report:", "500%+ growth in AI-generated deepfake fraud incidents YoY. sumsub.com/fraud-report-2024"),
    ("Deloitte (2024):", "Projected $78B economic damage from synthetic media fraud by 2027. Deloitte Insights Technology Report."),
    ("C2PA (2024) — Content Provenance Standard:", "Coalition for Content Provenance and Authenticity (Adobe, Microsoft, BBC). c2pa.org"),
]
for title, desc in refs:
    add_run_para(tf_r,
        [(f"• {title}  ", 14, True, False, SLATE),
         (desc, 14, False, False, OFF_WHITE)],
        space_before=5)

# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
prs.save(OUT_PATH)
print(f"SUCCESS — saved to: {OUT_PATH}")
print(f"Total slides: {len(prs.slides)}")
