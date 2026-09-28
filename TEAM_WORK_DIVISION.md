# Team Work Division: Full-Stack Feature-Slice Model

> **Project:** Foresight — Powered by Hindsight  
> **Team Size:** 3 Members  
> **Structure:** **Full-Stack Feature Slices** — Every member writes Backend/Memory code, Frontend/UI code, and Data/Prompts for their assigned feature.  
> **Goal:** Ensure every member has git commits across the whole stack and personal Hindsight code snippets for their mandatory hackathon article.

---

## Quick Reference: Full-Stack Ownership per Member

| Member | Feature Slice Owned | Backend & Hindsight Memory Code | Frontend & UI Code (`app.py`) | Data & Prompts Slice | Individual Article Deliverable |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Member 1** | **Deal Memory Ingestion & Pre-Call Intelligence** | `init_hindsight_bank()`, `seed_deal_memory()`, `generate_pre_call_brief()` | Deal Overview Header, Stakeholder Chips, Pre-Call Brief Card | Calls 1–3 in `data/acme_deal.json`, Pre-call prompt in `prompts.py` | *"How We Indexed Multi-Stakeholder Conversations into Hindsight"* |
| **Member 2** | **Collision Check & Reactive Memory Update** | `check_collisions()` logic, `update_commitment_status()` reflection loop | Collision Cards (🔴 🟠 🟡), *"Mark SOC-2 Sent"* Button & Live Re-evaluation | Calls 4–6 in `data/acme_deal.json`, `data/company_kb.json` (Veridian rules) | *"Detecting High-Stakes Collisions with Hindsight Memory Reflection"* |
| **Member 3** | **Predictive Foresight & Commitment Ledger (+ Media Lead)** | Commitment Ledger auditing logic, Question prediction algorithm | Commitment Ledger Table with status pills, Predictive Foresight Drawer | Calls 7–9 in `data/acme_deal.json`, Anticipation prompts, **Demo Video & Thumbnail** | *"Teaching AI to Anticipate Customer Traps Before They Are Asked"* |

---

## Detailed Member Responsibilities

### 👨‍💻 Member 1: Deal Memory Ingestion & Pre-Call Intelligence
* **Backend & Memory Layer (`memory.py`):**
  * Initializes the Hindsight Cloud client (`hindsight-client`) and sets up the `acme-deal` bank.
  * Implements `seed_deal_memory()`: Uses Hindsight `retain()` to index interactions, objections, and stakeholder sensitivities into memory.
  * Implements `generate_pre_call_brief()`: Queries Hindsight via `recall()` and generates a structured executive briefing using Groq LLM.
* **Frontend & UI Layer (`app.py`):**
  * Builds the **Deal Overview Header**: ACME Corp, Stage: Proposal Review, Value: $72k, Stakeholder chips.
  * Builds the **Pre-Call Executive Brief Card**: Generates and displays the 10-second dossier (Stakeholder Sensitivities, Competitor Watch, Learned Winning Tactics).
* **Data & Prompts Layer:**
  * Authors **Calls 1 to 3** in `data/acme_deal.json` (Discovery with Priya, Architecture Review with Marcus, Initial Security Scope with Nadia).
  * Authors the Pre-Call Briefing prompt template in `prompts.py`.
* **Mandatory Content Submission:**
  * **Article (800–1,500 words on Dev.to / Medium):** Deep-dive on indexing complex multi-stakeholder B2B conversations into Hindsight memory. Includes code snippets of `retain()` and `recall()`.
  * **LinkedIn Post:** Andrej Karpathy style breakdown on why memory beats prompt-stuffing.

---

### 🎨 Member 2: The Collision Check Engine & Dynamic Memory Reflection
* **Backend & Memory Layer (`collision_engine.py` & `memory.py`):**
  * Implements `check_collisions()`: Cross-checks new requests against retrieved Hindsight memories and company constraints.
  * Implements `update_commitment_status()`: Executes the dynamic memory reflection loop when commitments are fulfilled (updating Hindsight so future queries reflect the new state).
* **Frontend & UI Layer (`app.py`):**
  * Builds the **Collision Cards Component**:
    * 🔴 **Security Blocker Card** (Nadia's mandate + overdue promise).
    * 🟠 **Timeline Conflict Card** (4–6 week baseline vs 2 weeks).
    * 🟡 **Price / Budget Card** ($72k vs $50k budget vs $48k competitor).
  * Builds the **"Mark SOC-2 Report as Sent" Interactive Button**: Triggers the live memory update, re-runs the collision check, and displays the security blocker resolving in real time.
* **Data & Prompts Layer:**
  * Authors **Calls 4 to 6** in `data/acme_deal.json` (Linda's $50k CFO budget cap, NimbusAI's $48k competitive entry, Nadia's formal SOC-2 requirement).
  * Authors `data/company_kb.json` (Veridian 4–6 week deployment standard, discount approval matrix).
* **Mandatory Content Submission:**
  * **Article (800–1,500 words on Medium / Dev.to):** How to design multi-constraint collision detection and dynamic memory reflection. Includes code snippets of collision evaluation and memory state mutation.
  * **LinkedIn Post:** Showcase screenshots of the before vs. after memory state change.

---

### 📝 Member 3: Predictive Foresight & Commitment Ledger (+ Video Lead)
* **Backend & Memory Layer (`memory.py` & `collision_engine.py`):**
  * Implements the **Commitment Ledger tracking logic**: Audits promises vs. fulfillment, returning *"No fulfilment recorded"* for unverified promises.
  * Implements the **Predictive Foresight algorithm**: Analyzes unaddressed stakeholder concerns in memory to predict what the buyer will ask next and generates strategic counter-questions.
* **Frontend & UI Layer (`app.py`):**
  * Builds the **Commitment Ledger Table**: Displays auditable status pills (Completed, Overdue, Pending).
  * Builds the **Predictive Foresight Accordion**: Displays Anticipated Next Questions and Strategic Counter-Questions.
* **Data, Prompts & Media Layer:**
  * Authors **Calls 7 to 9** in `data/acme_deal.json` (Procurement negotiations with Owen, high-pressure discount demands).
  * Authors anticipation prompts in `prompts.py`.
  * **Video Lead:** Records the 105-second screen demo video via OBS/Loom, generates the 16:9 thumbnail with Google Nano Banana, and uploads to YouTube.
* **Mandatory Content Submission:**
  * **Article (800–1,500 words on Substack / LinkedIn Articles):** Why AI needs predictive foresight in negotiations; anticipating procurement traps before they are sprung. Includes code snippets of question prediction.
  * **LinkedIn Post:** The story of how AI predicted a procurement ambush.

---

## Collaborative Workflow Timeline

```
Phase 1: Seeding Data & Skeletons (Hours 0–1.5)
├── Member 1: Writes Calls 1–3 & memory.py client setup
├── Member 2: Writes Calls 4–6, company_kb.json & collision_engine.py skeleton
└── Member 3: Writes Calls 7–9, prompts.py & app.py UI shell

Phase 2: Full-Stack Integration (Hours 1.5–3.5)
├── Member 1: Completes Pre-Call Briefing backend + UI card
├── Member 2: Completes Collision Check + 'Mark SOC-2 Sent' live trigger
└── Member 3: Completes Commitment Ledger + Predictive Foresight panel

Phase 3: Testing & Demo Recording (Hours 3.5–4.5)
├── All Members: Run end-to-end rehearsal (105-second flow)
└── Member 3: Records the final demo video and creates YouTube thumbnail

Phase 4: Content & Articles (Hours 4.5–6.0)
└── All Members: Write their individual 800–1,500 word articles using their own code snippets
```

---
*Created for CtrlAltDeploy.*
