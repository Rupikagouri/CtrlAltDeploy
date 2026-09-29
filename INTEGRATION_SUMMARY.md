# Integration Summary — CtrlAltDeploy / Foresight

## What Was Done (Sep 29, 2026)

### 1. Committed Local Untracked Files
- `app.py`, `collision_engine.py`, `prompts.py` were sitting locally but never added to git. Committed them.

### 2. Pulled Veera & Rupika's Folders
- Repo was 14 commits behind `origin/main`.
- Pulled and got `Veera/` and `Rupika/` folders into local.

### 3. Resolved Merge Conflict in `prompts.py`
- Our version had all 3 system prompts (`PRE_CALL_BRIEF`, `COLLISION_DETECTION`, `PREDICTIVE_FORESIGHT`).
- Rupika's version had a detailed `build_pre_call_brief_prompt()` function.
- Kept both in the merged file.

### 4. Unified the App into a Single Entry Point
- `Veera/app.py` was the most complete — already had Member 1 (Pre-Call Brief) + Member 2 (Collision Check).
- Copied `commitment_ledger.py` and `predictive_foresight.py` from `Rupika/` to root.
- Added Member 3 (Rupika) sections — Commitment Ledger + Predictive Foresight — into `Veera/app.py`.
- Copied unified `Veera/app.py` → root `app.py` as the single entry point.

## How to Run
```bash
git clone https://github.com/Rupikagouri/CtrlAltDeploy.git
cd CtrlAltDeploy
pip install -r requirements.txt
cp .env.example .env   # fill in GROQ_API_KEY and HINDSIGHT_API_KEY
streamlit run app.py
```

## App Sections (in order)
| Section | Feature | Owner |
|---|---|---|
| 1 | Pre-Call Executive Brief | Veera (Member 1) |
| 2 | Collision Check + Dynamic Memory Reflection | Tanmaya (Member 2) |
| 3 | Living Commitment Ledger | Rupika (Member 3) |
| 4 | Predictive Foresight | Rupika (Member 3) |

## API Keys Needed
- `GROQ_API_KEY` → https://console.groq.com
- `HINDSIGHT_API_KEY` → https://ui.hindsight.vectorize.io (promo: `MEMHACK99`)
