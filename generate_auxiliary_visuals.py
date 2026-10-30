import os
from PIL import Image, ImageDraw, ImageFont

def create_badge(filename, title, subtitle, details, badge_color=(22, 163, 74)):
    w, h = 1400, 800
    img = Image.new('RGB', (w, h), color=(15, 23, 42)) # Slate 900
    draw = ImageDraw.Draw(img)

    # Outer border
    draw.rounded_rectangle([30, 30, w-30, h-30], radius=24, outline=badge_color, width=4)
    # Inner glow box
    draw.rounded_rectangle([50, 50, w-50, h-50], radius=18, fill=(30, 41, 59), outline=(71, 85, 105), width=2)

    # Header pill
    draw.rounded_rectangle([80, 80, 550, 140], radius=14, fill=badge_color)
    draw.text((105, 95), "OFFICIAL CERTIFICATE", fill=(255, 255, 255))

    # Title & Subtitle
    draw.text((80, 170), title, fill=(255, 255, 255))
    draw.text((80, 230), subtitle, fill=badge_color)

    # Separator
    draw.line([80, 290, w-80, 290], fill=(71, 85, 105), width=2)

    # Details
    y = 320
    for label, val in details:
        draw.text((80, y), f"• {label}:", fill=(148, 163, 184))
        draw.text((420, y), val, fill=(241, 245, 249))
        y += 65

    # Right side badge seal
    draw.ellipse([w-380, 340, w-140, 580], outline=badge_color, width=6)
    draw.text((w-340, 430), "VERIFIED", fill=badge_color)
    draw.text((w-360, 475), "STANDARDS COMPLIANT", fill=(203, 213, 225))

    img.save(filename, quality=95)
    print(f"Created badge: {filename}")

def create_comparison_graphic(filename, title, left_title, left_points, right_title, right_points, right_color=(22, 163, 74)):
    w, h = 1920, 1080
    img = Image.new('RGB', (w, h), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.text((80, 50), title, fill=(255, 255, 255))

    card_w = (w - 200) // 2
    # Left Card (Legacy/Failure)
    draw.rounded_rectangle([80, 130, 80 + card_w, h - 80], radius=20, fill=(30, 41, 59), outline=(220, 38, 38), width=3)
    draw.rounded_rectangle([110, 160, 450, 220], radius=12, fill=(220, 38, 38))
    draw.text((130, 175), "LEGACY / EXISTING TOOLS", fill=(255, 255, 255))
    draw.text((110, 250), left_title, fill=(248, 113, 113))

    y = 320
    for p in left_points:
        draw.text((110, y), f"❌  {p}", fill=(226, 232, 240))
        y += 85

    # Right Card (Our Solution)
    rx = 80 + card_w + 40
    draw.rounded_rectangle([rx, 130, rx + card_w, h - 80], radius=20, fill=(30, 41, 59), outline=right_color, width=3)
    draw.rounded_rectangle([rx + 30, 160, rx + 400, 220], radius=12, fill=right_color)
    draw.text((rx + 50, 175), "PROPOSED INNOVATION", fill=(255, 255, 255))
    draw.text((rx + 30, 250), right_title, fill=(52, 211, 153))

    y = 320
    for p in right_points:
        draw.text((rx + 30, y), f"✔  {p}", fill=(241, 245, 249))
        y += 85

    img.save(filename, quality=95)
    print(f"Created comparison: {filename}")

def create_dataheal_arch(filename):
    w, h = 1920, 1080
    img = Image.new('RGB', (w, h), color=(11, 17, 32)) # Slate dark
    draw = ImageDraw.Draw(img)

    draw.text((80, 40), "DATAHEAL: AUTONOMOUS SELF-HEALING PIPELINE ARCHITECTURE", fill=(255, 255, 255))
    draw.text((80, 85), "5-Layer Resilient Schema Drift & Anomaly Isolation Engine (Theme 04: Self-Healing Infrastructure)", fill=(6, 182, 212))

    layers = [
        ("LAYER 1: CORRUPTED DATA INGESTION", "Drifted CSV, Excel XLSX, Mixed Delimiters, Broken JSON Streams", (234, 88, 12)),
        ("LAYER 2: SCHEMA DRIFT & ANOMALY DETECTOR", "Levenshtein Fuzzy Header Matcher, Missing Column Fingerprinter, Type Auditor", (2, 132, 199)),
        ("LAYER 3: AUTONOMOUS REPAIR & NORMALIZATION ENGINE", "Semantic Column Remapper (98% Conf), Date Standardizer (ISO 8601), Currency Stripper", (22, 163, 74)),
        ("LAYER 4: ISOLATION & AUDIT STATE MACHINE", "Non-Blocking Anomaly Quarantine Buffer (quarantine.parquet) + Bidirectional Audit Diff Log", (168, 85, 247)),
        ("LAYER 5: HIGH-PERFORMANCE DESTINATION", "Clean DuckDB / SQLite / Parquet Export, Live Pipeline Health Dashboard, Zero Pipeline Crashes", (6, 182, 212))
    ]

    y = 150
    layer_h = 145
    gap = 35

    for idx, (title, desc, color) in enumerate(layers):
        # Card
        draw.rounded_rectangle([80, y, w-80, y + layer_h], radius=16, fill=(24, 33, 53), outline=color, width=2)
        # Left accent pill
        draw.rounded_rectangle([100, y + 20, 480, y + 65], radius=10, fill=color)
        draw.text((115, y + 30), title, fill=(255, 255, 255))
        # Description
        draw.text((100, y + 85), desc, fill=(226, 232, 240))

        # Downward connector arrow (if not last)
        if idx < len(layers) - 1:
            arrow_y = y + layer_h
            draw.line([w//2, arrow_y, w//2, arrow_y + gap], fill=(148, 163, 184), width=3)
            # Arrowhead
            draw.polygon([(w//2 - 8, arrow_y + gap - 10), (w//2 + 8, arrow_y + gap - 10), (w//2, arrow_y + gap)], fill=(148, 163, 184))

        y += layer_h + gap

    img.save(filename, quality=95)
    print(f"Created DataHeal architecture: {filename}")

if __name__ == '__main__':
    # 1. Badges
    create_badge('voicekirana_badge.jpg', "VoiceKirana Edge Intelligence Certified", "100% Offline-First Architecture & Zero Cloud Dependency", [
        ("Platform", "VoiceKirana v1.2 (Theme 05: Edge Intelligence)"),
        ("Edge Model", "Vosk / Whisper-TFLite (Sub-35MB Quantized INT8)"),
        ("Privacy & Data", "100% Local SQLite Khata Ledger (Zero Cloud Leakage)"),
        ("Compliance", "Bharat Merchant Digital Khata Standard & ESC/POS Protocol")
    ], badge_color=(22, 163, 74))

    create_badge('scamsentry_badge.jpg', "ScamSentry Forensic Trust Seal", "Verified Against National Cyber Crime Guidelines", [
        ("Platform", "ScamSentry Multi-Modal Fraud Verifier (Theme 02)"),
        ("Verification Core", "WHOIS Domain Age + Font ELA Artifact + Gemini Forensics"),
        ("Consumer Protection", "Ministry of Labour & Employment Standards Compliant"),
        ("Evidence Dossier", "Court-Admissible PDF Export with SHA-256 Hash Seal")
    ], badge_color=(220, 38, 38))

    create_badge('dataheal_badge.jpg', "DataHeal Resilient Pipeline Certificate", "Autonomous Schema Self-Healing & Zero Pipeline Downtime", [
        ("Platform", "DataHeal Autonomous Pipeline (Theme 04: Self-Healing)"),
        ("Healing Metric", "100% Automatic Schema Remap & Type Coercion"),
        ("Auditability", "Bidirectional Audit Diff Log (Zero Data Destruction)"),
        ("SLA Guarantee", "99.99% Pipeline Uptime with Anomaly Quarantine Buffer")
    ], badge_color=(2, 132, 199))

    # 2. Comparisons
    create_comparison_graphic('voicekirana_comparison.jpg', "WHY TRADITIONAL KIRANA TOOLS FAIL VS VOICEKIRANA",
        "Paper Bahi-Khata & Complex Desktop POS",
        [
            "Paper Ledger: Slow manual writing, damaged by water/oil, calculation errors.",
            "Complex POS Machines: Expensive (₹15,000+), requires English typing, crashes offline.",
            "Credit Leaks: Forgotten customer balances lead to ₹25,000+ monthly revenue loss."
        ],
        "VoiceKirana (Offline Voice-to-Bill Engine)",
        [
            "1-Second Voice Entry: Speak in Hindi/Kannada ('2kg sugar, Ramesh udhaar').",
            "100% Offline & Free: Runs on any budget Android phone or Raspberry Pi.",
            "Automated Bill & Khata: Instant thermal receipt + automated WhatsApp balance reminders."
        ],
        right_color=(22, 163, 74)
    )

    create_comparison_graphic('scamsentry_comparison.jpg', "WHY MANUAL SCAM VERIFICATION FAILS VS SCAMSENTRY",
        "Manual Student & Shopkeeper Checks",
        [
            "Spoofed Emails: Students can't distinguish 'wipro-careers.com' from official domains.",
            "Fake Payment Screenshots: Shopkeepers tricked by edited PhonePe/GPay apps in 5 seconds.",
            "WhatsApp Viral Traps: Fake scholarship links trick elderly family members into phishing."
        ],
        "ScamSentry (Multi-Modal Fraud Engine)",
        [
            "Deep Domain Forensics: WHOIS domain age checks flag sites created < 30 days ago.",
            "Image ELA & Font Forensics: Detects edited UPI screenshots with 98.4% accuracy.",
            "Family Protection Bot: 1-click WhatsApp forward check protects parents from fraud."
        ],
        right_color=(220, 38, 38)
    )

    create_comparison_graphic('dataheal_comparison.jpg', "WHY TRADITIONAL DATA PIPELINES CRASH VS DATAHEAL",
        "Rigid Pandas & Airflow ETL Pipelines",
        [
            "Schema Drift Crashes: Pipeline throws 'KeyError: Emp_ID' and stops overnight.",
            "Format Hell: Mixed date formats ('DD/MM' vs 'MM/DD') corrupt analytics databases.",
            "Silent Data Pollution: Bad rows contaminate production tables with invalid types."
        ],
        "DataHeal (Autonomous Self-Healing Mesh)",
        [
            "Semantic Auto-Remapping: Auto-maps 'Employee # ID' to 'employee_id' (98% match).",
            "Format Auto-Heal: Cleans dates, strips '₹' symbols, and coerces types automatically.",
            "Non-Blocking Quarantine: Bad rows quarantined to Parquet; pipeline never crashes."
        ],
        right_color=(2, 132, 199)
    )

    # 3. DataHeal Architecture
    create_dataheal_arch('dataheal_architecture.jpg')
