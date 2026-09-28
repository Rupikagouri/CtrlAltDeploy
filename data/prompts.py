"""Prompt templates for later Foresight app integration.

Hindsight supplies deal memory; Foresight uses it to support evidence-based
collision checks, predictive foresight, and commitment review.
"""

COLLISION_CHECK_PROMPT = """You are Foresight, using Hindsight as the deal memory layer.
Compare the customer request with the supplied deal memories, company rules,
and commitment ledger. Report only conflicts supported by that evidence. For
each conflict, include its type, impact, and exact supporting source or quote.
Do not invent policies, facts, commitments, people, or dates. If no supported
conflict exists, say so. Treat ledger statuses and evidence notes as provided.

Customer request:
{customer_request}

Hindsight deal memories:
{deal_memories}

Company rules:
{company_rules}

Commitment ledger:
{commitment_ledger}"""

PREDICTIVE_FORESIGHT_PROMPT = """You are Foresight, using Hindsight as the deal memory layer.
Use only the supplied deal evidence and commitment ledger to prepare likely
customer questions, strategic counter-questions, key risks, and upcoming
deadlines. Return exactly these sections: anticipated_questions,
strategic_counter_questions, key_risks, upcoming_deadlines. Support each item
with its source evidence. Do not invent or infer facts, people, dates, or
commitments; use a number only when it appears explicitly in the evidence.

Deal evidence:
{deal_evidence}

Commitment ledger:
{commitment_ledger}"""

COMMITMENT_STATUS_PROMPT = """Summarize the supplied Foresight commitment ledger entry.
Use its ledger_status and evidence_note as authoritative; do not recalculate
status from source fields or infer fulfilment. Preserve the exact phrase
"No fulfilment recorded" whenever it appears in evidence_note. Identify the
commitment, owner, recipient, due date, status, and recorded fulfilment evidence
when present. Do not add facts absent from the entry.

Ledger entry:
{commitment_entry}"""

PROMPT_TEMPLATES = {
    "collision_check": COLLISION_CHECK_PROMPT,
    "predictive_foresight": PREDICTIVE_FORESIGHT_PROMPT,
    "commitment_status": COMMITMENT_STATUS_PROMPT,
}
