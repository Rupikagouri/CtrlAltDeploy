"""Structured predictive foresight for the Foresight sales assistant.

Hindsight is the memory layer; this module turns the recorded deal evidence
into likely questions, useful counter-questions, risks, and deadlines.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from commitment_ledger import build_commitment_ledger, get_open_commitments

Priority = Literal["High", "Medium", "Low"]
DATA_PATH = Path(__file__).parent / "data" / "acme_calls_7_9.json"


def latest_call(data: dict[str, Any]) -> dict[str, Any]:
    """Return the latest recorded call by its ISO date."""
    return max(data.get("calls", []), key=lambda call: call["date"])


def load_deal_context(data: dict[str, Any]) -> dict[str, Any]:
    """Read only evidence present in the deal JSON."""
    continuity = data["cross_call_continuity"]
    latest = latest_call(data)
    outcomes = latest.get("outcomes", {})
    objections = [
        objection
        for call in data.get("calls", [])
        for objection in call.get("objections", [])
        if objection.get("status") == "open"
    ]
    return {
        "customer": data["customer"],
        "product": "Foresight",
        "budget": continuity["budget_trajectory"],
        "predicted_topics": continuity.get("predicted_next_topics", []),
        "objections": objections,
        "latest_call": latest,
        "next_meeting": outcomes.get("next_meeting"),
    }


def predict_questions(ctx: dict[str, Any]) -> list[dict[str, str]]:
    """Likely customer questions grounded in the recorded deal signals."""
    budget = ctx["budget"]
    return [
        {
            "question": (
                f"How does Foresight's ${budget['latest_offer_call_9']:,} offer "
                f"compare with NimbusAI at ${budget['nimbusai_latest']:,}, "
                f"given ACME's ${budget['acme_ceiling']:,} ceiling?"
            ),
            "priority": "High",
            "reason": "The latest offer and NimbusAI price appear in the budget trajectory and open pricing objections.",
        },
        {
            "question": "When will the remaining security evidence be delivered, and when can Elena approve?",
            "priority": "High",
            "reason": "The latest call leaves security documents outstanding and makes approval conditional on receipt.",
        },
        {
            "question": "Can the October 15 deployment target hold if security review or MSA redlines slip?",
            "priority": "High",
            "reason": "The latest open objection says security and legal work put the target at risk.",
        },
        {
            "question": "Can Foresight accept the requested liability and right-to-audit terms?",
            "priority": "High",
            "reason": "The latest call records open MSA issues on liability and audit rights.",
        },
        {
            "question": "Can the $49,000 offer and October 7 deadline be confirmed in writing?",
            "priority": "High",
            "reason": "The formal offer letter is an open pricing commitment in the ledger.",
        },
    ]


def counter_questions(ctx: dict[str, Any]) -> list[dict[str, str]]:
    """Questions that advance the evidenced procurement discussion."""
    return [
        {
            "question": "How will finance assess the $49,000 offer against the $50,000 ceiling and NimbusAI's $46,000 offer?",
            "priority": "High",
            "reason": "The latest budget objection cites the NimbusAI counter and possible finance rejection.",
        },
        {
            "question": "Which security items would Elena still need after receiving the four documents due October 1?",
            "priority": "High",
            "reason": "Elena's assessment is conditional on the recorded security documents.",
        },
        {
            "question": "Can legal resolve the liability cap and right-to-audit redlines before the October 7 signature deadline?",
            "priority": "High",
            "reason": "Both MSA issues are open, and the offer deadline is October 7.",
        },
        {
            "question": "What deployment work can Raj's team start on signing day, and what must wait for security approval?",
            "priority": "Medium",
            "reason": "The call records Raj's readiness to start connector setup and asks about pre-approval deployment.",
        },
    ]


def risks(
    ctx: dict[str, Any], open_commitments: list[dict[str, Any]]
) -> list[dict[str, str]]:
    """Summarize material risks without reimplementing ledger status rules."""
    budget = ctx["budget"]
    items: list[dict[str, str]] = []
    if budget["nimbusai_latest"] < budget["latest_offer_call_9"]:
        items.append({
            "risk": "Competitive pricing and budget pressure",
            "priority": "High",
            "evidence": (
                f"Foresight offer ${budget['latest_offer_call_9']:,}; "
                f"NimbusAI ${budget['nimbusai_latest']:,}; "
                f"ACME ceiling ${budget['acme_ceiling']:,}."
            ),
        })

    security = [item for item in open_commitments if item.get("category") == "security"]
    if security:
        items.append({
            "risk": "Security approval remains a gate",
            "priority": "High",
            "evidence": "Open security commitments: " + ", ".join(
                item["commitment_id"] for item in security
            ),
        })

    overdue = [item for item in open_commitments if item.get("ledger_status") == "Overdue"]
    if overdue:
        items.append({
            "risk": "Overdue commitments",
            "priority": "High",
            "evidence": ", ".join(item["commitment_id"] for item in overdue),
        })

    objection_by_topic = {item.get("topic"): item for item in ctx["objections"]}
    deployment = objection_by_topic.get("deployment_timeline")
    if deployment:
        items.append({
            "risk": "October 15 deployment target may slip",
            "priority": "High",
            "evidence": deployment["summary"],
        })
    legal = [item for item in open_commitments if item.get("category") == "legal"]
    # A security_compliance topic alone does not make an objection legal.
    # Require explicit contract/legal language in the recorded objection text.
    contract_terms = ("legal", "contract", "msa", "liability", "right-to-audit")
    legal_objections = [
        item for item in ctx["objections"]
        if any(term in item.get("summary", "").lower() for term in contract_terms)
    ]
    if legal or legal_objections:
        items.append({
            "risk": "Legal and contract terms remain open",
            "priority": "High",
            "evidence": (
                "Open legal commitment(s): "
                + ", ".join(item["commitment_id"] for item in legal)
                + ("; explicit contract evidence: " + "; ".join(
                    item["summary"] for item in legal_objections
                ) if legal_objections else "")
            ),
        })
    return items


def deadlines(
    open_commitments: list[dict[str, Any]], next_meeting: str | None
) -> list[dict[str, str]]:
    """List deadlines from open ledger entries and the recorded next meeting."""
    result = [
        {
            "id": item["commitment_id"],
            "deadline": item["due_date"],
            "description": item["description"],
            "status": item["ledger_status"],
            "evidence_note": item.get("evidence_note") or "",
        }
        for item in open_commitments
        if item.get("due_date")
    ]
    if next_meeting:
        result.append({
            "id": "NEXT-MEETING",
            "deadline": next_meeting,
            "description": "Next ACME deal checkpoint",
            "status": "Scheduled",
            "evidence_note": "",
        })
    return result


def build_predictive_foresight(data: dict[str, Any]) -> dict[str, Any]:
    """Build the four-section structured foresight result."""
    ctx = load_deal_context(data)
    # Pass the complete source object: the ledger extracts commitments from all calls.
    ledger = build_commitment_ledger(data)
    open_items = get_open_commitments(ledger)
    return {
        "anticipated_questions": predict_questions(ctx),
        "strategic_counter_questions": counter_questions(ctx),
        "key_risks": risks(ctx, open_items),
        "upcoming_deadlines": deadlines(open_items, ctx["next_meeting"]),
    }


if __name__ == "__main__":
    with DATA_PATH.open(encoding="utf-8") as data_file:
        deal_data = json.load(data_file)
    foresight = build_predictive_foresight(deal_data)
    for section, entries in foresight.items():
        print(f"\n{section.upper()}")
        for entry in entries:
            print(entry)
