"""Commitment Ledger for the Foresight AI sales assistant.

Extracts and tracks salesperson commitments across all ACME sales calls,
recalculating ledger status from fulfilment evidence rather than trusting
source status fields blindly.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal

LedgerStatus = Literal["Completed", "Pending", "Overdue", "Unfulfilled"]

DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "acme_calls_7_9.json"


def _parse_date(value: str) -> date:
    """Parse an ISO date or datetime string into a date."""
    return datetime.fromisoformat(value).date()


def _has_fulfilment_evidence(evidence: Any) -> bool:
    """Return True when evidence is present and non-empty."""
    if evidence is None:
        return False
    if isinstance(evidence, dict):
        return bool(evidence)
    return bool(evidence)


def _recalculate_ledger_status(
    source_status: str,
    due_date: str,
    fulfilment_evidence: Any,
    reference_date: date,
) -> LedgerStatus:
    """Derive ledger status from evidence and due date."""
    if _has_fulfilment_evidence(fulfilment_evidence):
        return "Completed"

    due = _parse_date(due_date)

    if due < reference_date:
        return "Overdue"

    return "Pending"


def load_commitments(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract every commitment from every call in the JSON data.

    Returns raw commitment dicts enriched with call context (call_id, call_date).
    """
    commitments: list[dict[str, Any]] = []

    for call in data.get("calls", []):
        call_id = call.get("call_id", "")
        call_date = call.get("date", "")

        for commitment in call.get("commitments", []):
            entry = dict(commitment)
            entry["call_id"] = call_id
            entry["call_date"] = call_date
            commitments.append(entry)

    return commitments


def build_commitment_ledger(
    data: dict[str, Any],
    reference_date: date | None = None,
) -> dict[str, Any]:
    """Build a full commitment ledger with recalculated statuses.

    Each entry exposes the source fields plus ledger_status and evidence_note.
    """
    if reference_date is None:
        reference_date = date.today()

    raw_commitments = load_commitments(data)
    ledger_entries: list[dict[str, Any]] = []

    for raw in raw_commitments:
        evidence = raw.get("fulfilment_evidence")
        source_status = raw.get("status", "")
        has_evidence = _has_fulfilment_evidence(evidence)

        entry = {
            "commitment_id": raw.get("commitment_id", ""),
            "call_id": raw.get("call_id", ""),
            "call_date": raw.get("call_date", ""),
            "description": raw.get("description", ""),
            "made_by": raw.get("made_by", ""),
            "made_to": raw.get("made_to", ""),
            "due_date": raw.get("due_date", ""),
            "category": raw.get("category", ""),
            "source_status": source_status,
            "status": source_status,
            "fulfilment_evidence": evidence,
            "evidence_note": None if has_evidence else "No fulfilment recorded",
            "ledger_status": _recalculate_ledger_status(
                source_status=source_status,
                due_date=raw.get("due_date", ""),
                fulfilment_evidence=evidence,
                reference_date=reference_date,
            ),
        }
        ledger_entries.append(entry)

    return {
        "reference_date": reference_date.isoformat(),
        "total_commitments": len(ledger_entries),
        "commitments": ledger_entries,
    }


def get_open_commitments(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    """Return commitments that are not yet completed."""
    return [
        entry
        for entry in ledger.get("commitments", [])
        if entry.get("ledger_status") != "Completed"
    ]


def get_overdue_commitments(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    """Return commitments with no evidence whose due date has passed."""
    return [
        entry
        for entry in ledger.get("commitments", [])
        if entry.get("ledger_status") == "Overdue"
    ]


def get_commitments_by_category(
    ledger: dict[str, Any],
    category: str,
) -> list[dict[str, Any]]:
    """Return commitments matching the given category."""
    normalized = category.strip().lower()
    return [
        entry
        for entry in ledger.get("commitments", [])
        if entry.get("category", "").lower() == normalized
    ]


def _format_entry(entry: dict[str, Any]) -> str:
    """Format a single ledger entry for console output."""
    evidence = entry.get("fulfilment_evidence")
    evidence_line = (
        f"    Evidence: {evidence.get('summary', evidence.get('reference', 'present'))}"
        if _has_fulfilment_evidence(evidence)
        else f"    Evidence: {entry.get('evidence_note', 'No fulfilment recorded')}"
    )
    return (
        f"  [{entry['ledger_status']}] {entry['commitment_id']} ({entry['category']})\n"
        f"    Call: {entry['call_id']} | Due: {entry['due_date']}\n"
        f"    {entry['description']}\n"
        f"    By: {entry['made_by']} -> {entry['made_to']}\n"
        f"    Source status: {entry['source_status']}\n"
        f"{evidence_line}"
    )


def _print_summary(ledger: dict[str, Any]) -> None:
    """Print a readable summary of the commitment ledger."""
    commitments = ledger.get("commitments", [])
    by_status: dict[str, list[dict[str, Any]]] = {}
    for entry in commitments:
        by_status.setdefault(entry["ledger_status"], []).append(entry)

    print(f"Commitment Ledger (as of {ledger['reference_date']})")
    print(f"Total commitments: {ledger['total_commitments']}")
    print()

    for status in ("Completed", "Pending", "Overdue", "Unfulfilled"):
        group = by_status.get(status, [])
        if not group:
            continue
        print(f"--- {status} ({len(group)}) ---")
        for entry in group:
            print(_format_entry(entry))
            print()

    open_items = get_open_commitments(ledger)
    overdue_items = get_overdue_commitments(ledger)
    security_items = get_commitments_by_category(ledger, "security")

    print("--- Summary ---")
    print(f"Open (not completed): {len(open_items)}")
    print(f"Overdue: {len(overdue_items)}")
    print(f"Security category: {len(security_items)}")


def _load_json_data(path: Path) -> dict[str, Any]:
    """Load and parse JSON data from a file path."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"JSON file is empty: {path}")
    return json.loads(text)


if __name__ == "__main__":
    data_path = DEFAULT_DATA_PATH
    try:
        data = _load_json_data(data_path)
        ledger = build_commitment_ledger(data)
        _print_summary(ledger)
    except FileNotFoundError:
        print(f"Error: data file not found at {data_path}")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Error loading data: {exc}")
