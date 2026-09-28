"""
prompts.py - Prompt Templates for Foresight Deal Intelligence.

Authored by Member 1 — Deal Memory Ingestion & Pre-Call Intelligence.

Contains:
- PRE_CALL_BRIEF_SYSTEM_PROMPT: System persona for the pre-call briefing LLM.
- build_pre_call_brief_prompt(): Assembles a structured user prompt from live deal memory.

Design principle: All outputs must be strictly grounded in retrieved Hindsight memory.
The LLM must NOT invent facts, numbers, or stakeholder statements.
"""

from typing import List, Dict, Any


# ---------------------------------------------------------------------------
# System prompt — sets the LLM persona and grounding constraint
# ---------------------------------------------------------------------------

PRE_CALL_BRIEF_SYSTEM_PROMPT = """You are Foresight, an AI deal intelligence assistant for enterprise B2B sales.
Your role is to generate a concise, evidence-based Pre-Call Executive Brief for a sales representative
who is about to enter a high-stakes negotiation call.

CRITICAL RULES:
1. Every claim you make MUST be traceable to a specific call, stakeholder statement, or commitment
   drawn from the Hindsight deal memory provided to you.
2. Do NOT invent numbers, timelines, names, or facts not present in the memory context.
3. If a piece of information is uncertain or missing, explicitly say "No record in memory" rather
   than fabricating a plausible answer.
4. Be concise and scannable. Use bullet points. Avoid filler sentences.
5. Output ONLY valid JSON matching the schema described. Do not include markdown fences or commentary.
"""


# ---------------------------------------------------------------------------
# User prompt builder — assembles deal context into a structured LLM prompt
# ---------------------------------------------------------------------------

def build_pre_call_brief_prompt(
    recalled_memories: List[Dict[str, Any]],
    stakeholders: List[Dict[str, Any]],
    commitments: List[Dict[str, Any]],
    deal_metadata: Dict[str, Any],
    company_kb: Dict[str, Any],
) -> str:
    """
    Builds the user-turn prompt for the pre-call briefing LLM call.

    All inputs come directly from DealMemoryBank.recall() and DealMemoryBank.get_all_context(),
    ensuring every fact in the brief traces back to indexed Hindsight memory.

    Returns a plain-text prompt string to be sent as the user message to Groq.
    """

    # --- Format stakeholder dossier ---
    stakeholder_lines = []
    for s in stakeholders:
        concerns_str = "; ".join(s.get("concerns", []))
        stakeholder_lines.append(
            f"  - {s['name']} ({s['title']}, {s['role']}): Sentiment = {s['sentiment']}. "
            f"Key concerns: {concerns_str}"
        )
    stakeholder_block = "\n".join(stakeholder_lines) if stakeholder_lines else "  No stakeholder data in memory."

    # --- Format recalled memory snippets (interactions + commitments) ---
    memory_lines = []
    for mem in recalled_memories:
        if mem.get("type") == "interaction":
            takeaways = "; ".join(mem.get("key_takeaways", []))
            memory_lines.append(
                f"  [{mem['call_id']}] {mem['title']} ({mem['date']}): {mem['summary']} "
                f"| Key takeaways: {takeaways}"
            )
        elif mem.get("type") == "commitment":
            memory_lines.append(
                f"  [COMMITMENT {mem['id']}] {mem['title']} → {mem['recipient']} "
                f"| Status: {mem['status']} | Notes: {mem.get('status_notes', '')}"
            )
    memory_block = "\n".join(memory_lines) if memory_lines else "  No recalled memories."

    # --- Format open commitments summary ---
    open_commitments = [c for c in commitments if c.get("status") != "Completed"]
    commitment_lines = []
    for c in open_commitments:
        commitment_lines.append(
            f"  - [{c['status'].upper()}] {c['title']} promised to {c['recipient']} "
            f"(ref: {c.get('call_ref', 'N/A')}, promised: {c.get('date_promised', 'N/A')})"
        )
    commitment_block = (
        "\n".join(commitment_lines) if commitment_lines else "  All commitments fulfilled."
    )

    # --- Company baseline for grounding ---
    deploy_policy = company_kb.get("deployment_policy", {})
    pricing_policy = company_kb.get("pricing_and_discount_policy", {})
    deploy_summary = (
        f"Standard deployment: {deploy_policy.get('standard_timeline_weeks', 'N/A')}. "
        f"2-week deployment feasible: {deploy_policy.get('two_week_deployment_feasible', 'N/A')}."
    )
    pricing_summary = (
        f"Standard quote: ${pricing_policy.get('standard_acme_quote_annual', 'N/A'):,}. "
        f"Rep max discount: {pricing_policy.get('discount_tiers', {}).get('rep_authority_max_percent', 'N/A')}% "
        f"(floor: ${pricing_policy.get('discount_tiers', {}).get('rep_minimum_floor', 'N/A'):,})."
    )

    prompt = f"""You are briefing a sales representative before their next call with ACME Corp.

=== DEAL OVERVIEW ===
Customer: {deal_metadata.get('customer_name', 'ACME Corp')}
Vendor: {deal_metadata.get('vendor_name', 'Veridian')}
Stage: {deal_metadata.get('stage', 'N/A')}
Current Quote (ARR): ${deal_metadata.get('initial_quote_arr', 0):,}
Deal Status: {deal_metadata.get('current_status', 'N/A')}
Total Interactions Indexed: {deal_metadata.get('total_interactions', 0)} over {deal_metadata.get('history_duration_weeks', 0)} weeks

=== STAKEHOLDER DOSSIER (from Hindsight memory) ===
{stakeholder_block}

=== RECALLED HINDSIGHT MEMORIES (most relevant interactions & commitments) ===
{memory_block}

=== OPEN / OVERDUE COMMITMENTS ===
{commitment_block}

=== VERIDIAN COMPANY BASELINE (policy constraints) ===
Deployment: {deploy_summary}
Pricing: {pricing_summary}

=== YOUR TASK ===
Generate a Pre-Call Executive Brief as a single JSON object with exactly this structure:

{{
  "headline": "<one-sentence situation summary citing the deal stage and urgency>",
  "stakeholder_sensitivities": [
    {{
      "name": "<stakeholder name>",
      "role": "<role>",
      "sensitivity": "<their core concern or mandate — cite the call it came from>",
      "recommended_approach": "<one tactical suggestion grounded in memory>"
    }}
  ],
  "competitor_intelligence": {{
    "competitor": "<name or 'None identified'>",
    "their_offer": "<price or terms from memory, or 'No record in memory'>",
    "our_differentiators": ["<differentiator 1>", "<differentiator 2>"],
    "battle_card_tip": "<one specific tactic to counter them, grounded in deal memory>"
  }},
  "open_commitments_at_risk": [
    {{
      "commitment": "<title>",
      "recipient": "<name>",
      "status": "<Overdue / Pending>",
      "risk": "<what happens if unaddressed>"
    }}
  ],
  "winning_tactics": [
    "<tactic 1 — must cite a specific memory or stakeholder statement>",
    "<tactic 2>",
    "<tactic 3>"
  ],
  "one_sentence_coaching_tip": "<the single most important thing the rep must do or avoid on this call>"
}}

Remember: Every fact must come from the memory provided above. Use exact figures, names, and call references. Output ONLY the JSON object."""

    return prompt
