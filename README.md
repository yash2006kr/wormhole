# 🌀 Wormhole (ApplyCopilot)
> **Voice-Steered Autonomous Web Agent with Specialized Execution Protocols**  
> *Developed for AfterHours 1.0 Hackathon | Theme 01: Agentic AI & Multi-Agent Systems*  
> **Team:** AI Avengers — Don Bosco Institute of Technology (DBIT)

---

## 📌 Overview
**Wormhole** is an autonomous, voice-driven web execution agent that bridges natural language voice steering with live browser execution. Instead of acting as a conversational text-only chatbot, Wormhole physically manipulates dynamic web elements, resolves dynamic seat grids, performs in-memory document surgery, strips deceptive dark-pattern checkout fees, and air-gaps financial transactions.

---

## ⚡ 5 Specialized Execution Protocols

| Protocol | Accent | Core Capabilities |
| :--- | :--- | :--- |
| **1. Transit Rush Protocol** | Red / Amber | Sub-250ms seat grid parsing on KSRTC/IRCTC; instant passenger vault auto-fill to beat 90-sec sellout windows; direct-to-payment bypass. |
| **2. Civic Helper Protocol** | Royal Blue | Vernacular voice navigation (Kannada, Hindi, English) for Seva Sindhu & Parivahan; grounded RAG motivation essays for scholarships; senior citizen accessibility. |
| **3. Fraud Sentinel Protocol** | Emerald Green | Live domain age & SSL provenance audit (<30 days flag); air-gapped interrupt loop freezing DOM on payment fields; human-in-the-loop UPI PIN & OTP verification. |
| **4. Document Exorcist** | Violet Purple | Auto-detects DOM upload constraints; in-memory auto-cropping to 3.5×4.5cm and 200 DPI compression (resizes 2.5MB down to 32KB); passes validation without MS Paint/Photoshop. |
| **5. Anti-Dark-Pattern Protocol** | Cyan | DOM selector watchdog detecting and unchecking hidden insurance and donation boxes; strips hidden convenience surcharges; rotates sessions to bypass dynamic price spikes. |

---

## 🚨 Surprise Hurdle Defense: "Crash After Submit"
*(See detailed architecture & test guide in [SURPRISE_HURDLE.md](SURPRISE_HURDLE.md))*

* **Irreversible Action Idempotency Sentinel (Hint 1)**:
  - Write-Ahead Log (WAL) in `transaction_ledger.json` records in-flight payment intents before clicks.
  - Abrupt browser crash post-click triggers autonomous reconciliation without double-paying on restart.
* **Voice Financial Anchor & Sneaky Fee Interceptor (Hint 2)**:
  - Compares final checkout amounts against voice-approved budget.
  - Detects quiet drip-pricing surcharges added at final steps and halts checkout immediately.
* **Voice Ambiguity Clarification Protocol (Hint 3)**:
  - Intercepts underspecified voice commands when multiple options exist, presenting choice chips and speaking clarifications instead of guessing.

---

## 🛠️ Architecture & Tech Stack

```
[Voice Input (Web Speech / Whisper)]
                │
                ▼
  [Intent & Protocol Router (Groq LPU)]
                │
   ┌────────────┴────────────┐
   ▼                         ▼
[Transit / Civic]    [Exorcist / Dark-Pattern]
   │                         │
   └────────────┬────────────┘
                ▼
 [Playwright Stealth Engine] ──(CDP Stream)──► [Live Mirrored HUD]
                │
                ▼
  [Air-Gapped Payment Gateway] ──► [Human UPI / OTP Authorization]
```

* **Inference & Reasoning:** Groq LPU (`llama-3.3-70b-versatile` / `openai/gpt-oss-20b`) & Google Gemini 2.5 Flash
* **Speech Pipeline:** Whisper Large V3 / Web Speech API (sub-250ms voice latency)
* **Browser Automation:** Playwright Stealth with randomized human-like Bezier mouse curves
* **Image Forensics & Surgery:** In-memory Pillow byte manipulation engine
* **Backend Runtime:** Python 3.12, FastAPI, Uvicorn, SQLite
* **User Vault:** Local encrypted JSON store (`vault.json`)

---

## 👥 Team: AI Avengers
* Don Bosco Institute of Technology (DBIT), Bengaluru
* Raj Aanada
* Yashma C P
* Likith M
* Yashwanth K R

---

## 📄 License
MIT License
