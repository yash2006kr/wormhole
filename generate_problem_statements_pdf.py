import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Top banner line
        self.setStrokeColor(colors.HexColor('#EA580C'))
        self.setLineWidth(2)
        self.line(40, letter[1] - 30, letter[0] - 40, letter[1] - 30)

        # Header text
        self.setFont('Helvetica-Bold', 8)
        self.setFillColor(colors.HexColor('#0F172A'))
        self.drawString(40, letter[1] - 25, "AFTERHOURS 1.0 · 24-HOUR HACKATHON")
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#64748B'))
        self.drawRightString(letter[0] - 40, letter[1] - 25, "THEME 01: AGENTIC AI & MULTI-AGENT SYSTEMS · TEAM AI AVENGERS (DBIT)")

        # Footer line
        self.setStrokeColor(colors.HexColor('#E2E8F0'))
        self.setLineWidth(1)
        self.line(40, 35, letter[0] - 40, 35)

        # Footer text
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#64748B'))
        self.drawString(40, 24, "Don Bosco Institute of Technology (DBIT) · 30–31 October 2026")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 24, page_text)
        self.restoreState()

def build_pdf():
    pdf_filename = "AfterHours_Theme01_Top10_Problem_Statements.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#EA580C'),
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=3
    )

    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#0284C7'),
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=3
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0F172A')
    )

    tag_style = ParagraphStyle(
        'Tag',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []

    # Title Cover Header
    story.append(Paragraph("AFTERHOURS 1.0 — 24-HOUR HACKATHON", subtitle_style))
    story.append(Paragraph("Top 10 High-Impact Problem Statements", title_style))
    story.append(Paragraph("<b>Track:</b> Theme 01 — Agentic AI & Multi-Agent Systems &nbsp;|&nbsp; <b>Team:</b> AI Avengers (DBIT) &nbsp;|&nbsp; <b>Date:</b> 30–31 Oct 2026", meta_style))
    story.append(Spacer(1, 6))

    intro_p = ("This executive brief outlines <b>10 competition-grade problem statements</b> strictly curated for <b>Theme 01 (Agentic AI & Multi-Agent Systems)</b>. "
               "Every problem is architected around <b>autonomous multi-agent collaboration with human-in-the-loop governance</b>, built exclusively on <b>100% free developer tooling</b> "
               "(Gemini 2.5 Flash, Groq Llama 3.3 70B, Playwright, Python open-source), and designed to deliver an unforgettable <b>live working demo</b> to mentors and judges.")
    story.append(Paragraph(intro_p, body_style))
    story.append(Spacer(1, 10))

    # Problems Data
    problems = [
        {
            "num": "01",
            "name": "ApplyCopilot: Autonomous Human-in-the-Loop Web Application Co-Pilot",
            "domain": "Education Equity, Browser Agents & Human-AI Interaction",
            "problem": "Over $100M in scholarships and grants go unclaimed annually because students abandon convoluted 45-minute multi-page portals requiring repetitive bespoke essays. Traditional autofill extensions collapse on modern SPAs, while headless scrapers get 403-banned with zero CAPTCHA recovery.",
            "swarm": [
                "<b>Vault Agent:</b> Ingests candidate transcripts, resume, and income certificates into a verified, 0%-hallucination JSON schema.",
                "<b>Inspector Agent:</b> Queries live DOM accessibility trees via Playwright to classify fields without hardcoded CSS selectors.",
                "<b>Drafter Agent:</b> Synthesizes bespoke, persuasive personal statements anchored strictly to authentic candidate achievements.",
                "<b>Navigator Agent:</b> Dispatches synthetic human-like keystrokes/clicks with randomized micro-delays.",
                "<b>HITL Gateway:</b> Streams live mirrored browser viewport; auto-pauses on CAPTCHAs/OTPs and prompts user for 1-click clearance."
            ],
            "demo": "Open split-screen dashboard. Select a live scholarship portal; watch agent auto-fill page, generate tailored essay, pause at a live CAPTCHA modal for user click, and resume seamlessly to the final review diff.",
            "stack": "Python, Playwright, Google Gemini 2.5 Flash / Groq (Llama 3.3 70B), Streamlit / HTML5 Canvas."
        },
        {
            "num": "02",
            "name": "VigilantSwarm: Autonomous DevSecOps Vulnerability Hunter & Auto-Patcher",
            "domain": "Cybersecurity, Automated Code Repair & Software Engineering",
            "problem": "Enterprise and open-source repositories are flooded with hundreds of automated vulnerability alerts (CVEs, Dependabot). Triaging exploit blast-radius and crafting regression-free patches takes 4–10 developer days per flaw, leaving systems exposed.",
            "swarm": [
                "<b>AST Ingestion Agent:</b> Analyzes repo Abstract Syntax Tree to verify if the vulnerable function path is actually invoked.",
                "<b>Red-Team Hacker Agent:</b> Crafts a reproducible exploit unit test or HTTP payload simulating a real attack vector.",
                "<b>Blue-Team Patcher Agent:</b> Writes a minimal, elegant code patch or library version upgrade to remediate the vulnerability.",
                "<b>QA Verifier Agent:</b> Runs pytest in an isolated sandbox to prove the exploit is blocked and zero regressions occurred."
            ],
            "demo": "Paste a public GitHub repo with a known vulnerability (e.g. SQLi / Path Traversal). Click 'Remediate'. Watch the Red Agent write a failing exploit test, the Blue Agent generate the fix, tests pass live, and a ready-to-merge GitHub PR is created.",
            "stack": "GitPython, Pytest sandbox, Google Gemini 2.5 Flash, Groq (Llama 3.3 70B), GitHub REST API, Streamlit."
        },
        {
            "num": "03",
            "name": "SurgeSync: Multi-Agent Hospital Capacity, ICU & Ambulance Dispatch Coordinator",
            "domain": "Healthcare Logistics, Emergency Response & Mass Casualty Surge",
            "problem": "During urban disasters, highway crashes, or seasonal epidemics, emergency rooms overflow and patients die in transit because ambulance dispatch, ICU beds, trauma teams, and oxygen supply operate in disconnected silos.",
            "swarm": [
                "<b>Triage Urgency Agent:</b> Evaluates incoming emergency patient streams and computes dynamic severity scores.",
                "<b>Bed & ICU Allocator Agent:</b> Tracks real-time bed status and predicts patient discharge times using length-of-stay models.",
                "<b>Ambulance Router Agent:</b> Interacts with routing APIs to dynamically divert ambulances away from saturated hospitals to nearest capable hubs.",
                "<b>Supply Chain Negotiator:</b> Detects regional blood/oxygen deficits and negotiates automated emergency transfers between facilities."
            ],
            "demo": "Interactive hospital city map dashboard. Trigger a simulated '20-Patient Highway Collision'. Watch agents negotiate bed capacities in real time, rebalance queues, and automatically reroute ambulances across the city map.",
            "stack": "Python SimPy, NetworkX, Streamlit-Folium / Leaflet.js, Groq (Llama 3.3 70B), Gemini 2.5 Flash."
        },
        {
            "num": "04",
            "name": "DisruptGuard: Autonomous Multi-Tier Supply Chain Recovery Swarm",
            "domain": "Global Logistics, Manufacturing & Disruption Containment",
            "problem": "Canal blockages, port strikes, and factory fires strand billions in industrial components. Supply chain teams spend weeks making manual calls to locate backup suppliers, leading to assembly line shutdowns.",
            "swarm": [
                "<b>Disruption Monitor Agent:</b> Ingests live news, weather feeds, and maritime AIS vessel telemetry to spot bottleneck events.",
                "<b>BOM Impact Agent:</b> Traverses multi-tier Bill-of-Materials dependency graphs to calculate factory stockout countdowns.",
                "<b>Vendor Sourcing Agent:</b> Automatically searches supplier registries and drafts quote requests (RFPs) to alternate regional vendors.",
                "<b>Logistics Optimizer Agent:</b> Simulates multi-modal routing trade-offs (air freight vs. alternate maritime lanes) for cost vs. speed.",
                "<b>Human Approval Gate:</b> Synthesizes findings into two prioritized recovery plans for 1-click supply chain lead authorization."
            ],
            "demo": "Simulate 'Port of Singapore Strike'. The swarm immediately isolates 3,000 stranded battery units, queries alternate suppliers in Vietnam, computes freight trade-offs, and outputs a complete recovery plan in 30 seconds.",
            "stack": "Python, Pandas, NetworkX, Groq Llama 3.3 70B, FastHTML / Streamlit."
        },
        {
            "num": "05",
            "name": "ContractCouncil: Multi-Agent Autonomous Contract Risk Redlining & Counter-Negotiator",
            "domain": "Legal Tech, SMB Protection & Freelancer Advocacy",
            "problem": "Startups and independent contractors routinely sign predatory non-competes, one-sided indemnity clauses, and unlimited liability terms because professional legal review costs $500+/hour.",
            "swarm": [
                "<b>Clause Auditor Agent:</b> Detects aggressive indemnities, IP forfeiture, unilateral termination, and jurisdiction traps.",
                "<b>Skeptical Advocate Agent:</b> Roleplays as client counsel, evaluating worst-case dispute scenarios under hostile litigation.",
                "<b>Counter-Drafter Agent:</b> Rewrites one-sided clauses into standard, balanced language conforming to commercial precedents.",
                "<b>Negotiation Strategist Agent:</b> Generates a professional, firm counter-offer email itemizing commercial rationale for changes."
            ],
            "demo": "Upload a predatory 15-page client contract PDF. Watch the council debate the abusive clauses, output a side-by-side redlined DOCX/PDF with track changes, and generate a ready-to-send executive negotiation email.",
            "stack": "pdfplumber, python-docx, Google Gemini 2.5 Flash, Groq, Streamlit / React."
        },
        {
            "num": "06",
            "name": "Jan-Sahayak: Multi-Agent Vernacular Welfare Scheme Discovery & Entitlement Claimer",
            "domain": "Civic Tech, Public Welfare & Financial Inclusion",
            "problem": "Over ₹50,000 Crore in government welfare subsidies, student stipends, and farmer relief funds go unclaimed annually because rural citizens cannot decipher dense bureaucratic language or navigate English web portals.",
            "swarm": [
                "<b>Vernacular Voice Agent:</b> Conducts audio conversations with citizens in native regional languages (Kannada, Hindi, Telugu, etc.).",
                "<b>Scheme Matcher Engine:</b> Vector searches 500+ Central and State welfare schemes (PM-Kisan, Ayushman Bharat, Post-Matric grants).",
                "<b>Document Verifier Agent:</b> Analyzes smartphone photos of Aadhaar/Ration/Land records to verify eligibility match.",
                "<b>Application Facilitator Agent:</b> Pre-populates official application forms and generates an offline action checklist with required office contacts."
            ],
            "demo": "Speak in Kannada/Hindi: 'I am a 2-acre farmer in Mandya with a daughter studying engineering.' Swarm identifies ₹65,000 in eligible grants, audits documents, and pre-fills the official benefit forms.",
            "stack": "Whisper / gTTS, ChromaDB, Google Gemini 2.5 Flash, Streamlit."
        },
        {
            "num": "07",
            "name": "FraudSwarm: Multi-Agent Anti-Money Laundering (AML) & Financial Crime Forensics",
            "domain": "FinTech, Banking Compliance & Forensic Graph Intelligence",
            "problem": "Compliance teams at financial institutions are overwhelmed by 50,000+ transaction alerts monthly. Over 90% are false alarms, but compiling regulatory Suspicious Activity Reports (SAR) takes 4 hours per file, delaying real fraud detection.",
            "swarm": [
                "<b>Transaction Graph Agent:</b> Analyzes multi-hop directed graphs to spot structuring, circular layering, and rapid fund pass-through.",
                "<b>Entity & Sanctions Agent:</b> Cross-checks corporate registries, offshore leaks (ICIJ), and PEP (Politically Exposed Persons) databases.",
                "<b>Adversarial Skeptic Agent:</b> Challenges fraud theories: 'Does this match standard seasonal agricultural procurement cycles?'",
                "<b>SAR Dossier Generator:</b> Compiles an audited, regulatory-compliant Suspicious Activity Report with visual fund-trail diagrams."
            ],
            "demo": "Upload a synthetic CSV of 10,000 transactions. Swarm flags a complex 5-account circular laundering ring, renders the money trail on an interactive graph, and generates an official SAR filing document.",
            "stack": "Pandas, NetworkX, PyVis / D3.js, Groq (Llama 3.3 70B), Streamlit."
        },
        {
            "num": "08",
            "name": "ResearchCouncil: Multi-Agent Adversarial Fact-Checking & Intelligence Dossier",
            "domain": "Information Integrity, Deep Due-Diligence & Enterprise Research",
            "problem": "Generative AI summaries frequently hallucinate facts and invent citations. Enterprise analysts spend hours manually cross-checking claims across conflicting industry, financial, and academic publications.",
            "swarm": [
                "<b>Lead Researcher Agent:</b> Scrapes academic papers, SEC filings, and news sources to assemble an initial research dossier.",
                "<b>Adversarial Fact-Checker:</b> Systematically attempts to falsify every single sentence, demanding secondary corroboration.",
                "<b>Primary Citation Auditor:</b> Inspects linked references to confirm whether the primary document actually asserts the claim.",
                "<b>Dossier Synthesizer Agent:</b> Assembles an executive report with green/yellow/red color-coded citation confidence heatmaps."
            ],
            "demo": "Input a controversial economic or technical claim. Watch the two agents engage in live adversarial debate, highlight uncorroborated points in red, and produce an ironclad, citation-verified intelligence briefing.",
            "stack": "Crawl4AI / BeautifulSoup, Tavily API, Google Gemini 2.5 Flash, Groq, FastHTML."
        },
        {
            "num": "09",
            "name": "CodeRefactorSwarm: Multi-Agent Legacy Monolith Migration & Behavior Verifier",
            "domain": "Enterprise Software Engineering & Technical Debt Elimination",
            "problem": "Migrating legacy enterprise systems (Python 2 to 3, Flask to async FastAPI, or monoliths to microservices) costs millions and introduces severe regression bugs because legacy code lacks test suites.",
            "swarm": [
                "<b>AST Dependency Agent:</b> Extracts code call graphs, circular imports, and database coupling from legacy repositories.",
                "<b>Modernizer Agent:</b> Rewrites legacy code into modern, idiomatic async code with Pydantic validation and type annotations.",
                "<b>Synthetic Test Harness Agent:</b> Generates property-based test suites using Hypothesis to capture legacy input/output edge cases.",
                "<b>Equivalence Verifier Agent:</b> Runs legacy and modern code in parallel against 500 synthetic inputs to mathematically prove zero behavioral deviation."
            ],
            "demo": "Paste a legacy Python synchronous block. Watch the agents extract dependencies, refactor to async FastAPI, generate test suites, and execute a side-by-side behavioral equivalence test with 100% match.",
            "stack": "libcst, ast, Pytest, Hypothesis, Google Gemini 2.5 Flash, Groq, Streamlit."
        },
        {
            "num": "10",
            "name": "AeroTriage: Autonomous Multi-Agent Cloud Incident War-Room & Root-Cause Patcher",
            "domain": "DevOps, Cloud SRE & Autonomous Infrastructure Self-Healing",
            "problem": "During 3:00 AM production outages, engineers waste precious hours combing through fragmented logs, Kubernetes events, and Datadog graphs while systems bleed thousands of dollars every minute.",
            "swarm": [
                "<b>Log Clustering Agent:</b> Ingests gigabytes of distributed microservice logs and isolates sudden error-pattern bursts.",
                "<b>Metrics Correlation Agent:</b> Cross-references CPU/memory spikes with distributed latency traces to locate failing services.",
                "<b>Root-Cause Investigator:</b> Inspects recent CI/CD deployments and Git commits to identify the change that triggered the failure.",
                "<b>Remediation Runbook Agent:</b> Formulates safe containment steps (traffic rerouting, pod restart, rollback) and presents a 1-click human execution gate."
            ],
            "demo": "Simulate a live Kubernetes cascading microservice failure. Watch the 4 agents collaborate on a war-room UI, identify a faulty database migration commit in under 15 seconds, and offer a 1-click automated rollback.",
            "stack": "Python, Logstash simulator, NetworkX, Groq Llama 3.3 70B, Streamlit."
        }
    ]

    for p_idx, p in enumerate(problems):
        card_content = []

        # Header bar
        header_text = f"<b>#{p['num']} &nbsp;|&nbsp; {p['name']}</b>"
        card_content.append(Paragraph(header_text, h1_style))
        card_content.append(Paragraph(f"<b>Domain:</b> {p['domain']}", meta_style))
        card_content.append(Spacer(1, 2))

        # Problem
        card_content.append(Paragraph(f"<b>The Friction / Problem Statement:</b> {p['problem']}", body_style))
        card_content.append(Spacer(1, 3))

        # Swarm
        card_content.append(Paragraph("<b>The Multi-Agent Swarm Architecture:</b>", bold_body))
        for ag in p['swarm']:
            card_content.append(Paragraph(f"• {ag}", body_style))
        card_content.append(Spacer(1, 3))

        # Demo & Stack
        card_content.append(Paragraph(f"<b>Live 2-Minute Demo Moment:</b> {p['demo']}", body_style))
        card_content.append(Paragraph(f"<b>24-Hour Free Tech Stack:</b> <font color='#16A34A'>{p['stack']}</font>", body_style))

        # Wrap in a styled table card
        card_table = Table([[card_content]], colWidths=[doc.width])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor('#CBD5E1')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))

        story.append(card_table)
        story.append(Spacer(1, 8))

        # Page break after every 2 problems (clean 5-page dossier)
        if (p_idx + 1) % 2 == 0 and (p_idx + 1) < len(problems):
            story.append(PageBreak())

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {pdf_filename}")

if __name__ == '__main__':
    build_pdf()
