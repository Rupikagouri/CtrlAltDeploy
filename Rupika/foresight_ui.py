"""Streamlit dashboard for Predictive Foresight and the Commitment Ledger."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from commitment_ledger import build_commitment_ledger
from predictive_foresight import build_predictive_foresight


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "acme_calls_7_9.json"


def _priority_class(priority: str) -> str:
    return {"High": "high", "Medium": "medium", "Low": "low"}.get(
        priority, "neutral"
    )


def _status_class(status: str) -> str:
    return {
        "Completed": "completed",
        "Pending": "pending",
        "Overdue": "overdue",
        "Scheduled": "scheduled",
    }.get(status, "neutral")


def _pill(label: str, css_class: str) -> None:
    st.markdown(
        f'<span class="status-pill {css_class}">{label}</span>',
        unsafe_allow_html=True,
    )


def _evidence(expander_label: str, reason: str | None) -> None:
    if reason:
        with st.expander(expander_label):
            st.write(reason)


def _render_prediction_cards(items: list[dict[str, Any]], title_key: str) -> None:
    if not items:
        st.info("No items recorded.")
        return

    for index, item in enumerate(items, start=1):
        title = item.get(title_key, item.get("description", ""))
        priority = item.get("priority")
        with st.container(border=True):
            title_col, priority_col = st.columns([5, 1])
            with title_col:
                st.markdown(f"**{title}**")
            with priority_col:
                if priority:
                    _pill(priority, _priority_class(priority))
            reason = item.get("reason") or item.get("evidence")
            if reason:
                _evidence(f"View supporting evidence · {index}", reason)


def _render_deadlines(items: list[dict[str, Any]]) -> None:
    if not items:
        st.info("No upcoming deadlines recorded.")
        return

    for index, item in enumerate(items, start=1):
        with st.container(border=True):
            cols = st.columns([1.3, 3.7, 1.2])
            with cols[0]:
                st.markdown(f"**{item.get('deadline', '—')}**")
            with cols[1]:
                st.markdown(f"**{item.get('description', '—')}**")
                if item.get("id"):
                    st.caption(item["id"])
            with cols[2]:
                _pill(item.get("status", ""), _status_class(item.get("status", "")))
            _evidence(f"View deadline evidence · {index}", item.get("evidence_note"))


def _evidence_summary(entry: dict[str, Any]) -> str:
    evidence = entry.get("fulfilment_evidence")
    if not evidence:
        return entry.get("evidence_note") or ""
    if isinstance(evidence, dict):
        return str(evidence.get("summary") or evidence.get("reference") or "Evidence recorded")
    return str(evidence)


def _render_ledger(ledger: dict[str, Any]) -> None:
    entries = ledger.get("commitments", [])
    counts = {
        status: sum(entry.get("ledger_status") == status for entry in entries)
        for status in ("Completed", "Pending", "Overdue")
    }
    st.markdown("### Commitment overview")
    metrics = st.columns(4)
    metrics[0].metric("Total commitments", len(entries))
    for column, status in zip(metrics[1:], ("Completed", "Pending", "Overdue")):
        column.metric(status, counts[status])

    st.markdown("### Recorded commitments")
    for index, entry in enumerate(entries, start=1):
        status = entry.get("ledger_status", "")
        with st.container(border=True):
            headline, status_col = st.columns([5, 1])
            with headline:
                st.markdown(f"**{entry.get('description', '—')}**")
            with status_col:
                # Display the ledger's status verbatim; the UI does not derive it.
                _pill(status, _status_class(status))

            details = st.columns([1.2, 1.3, 1.5])
            details[0].caption("Category")
            details[0].write(entry.get("category", "—").replace("_", " ").title())
            details[1].caption("Due date")
            details[1].write(entry.get("due_date") or "—")
            details[2].caption("Commitment ID")
            details[2].write(entry.get("commitment_id") or "—")
            _evidence(f"View evidence · {index}", _evidence_summary(entry))


def main() -> None:
    st.set_page_config(page_title="Foresight | Hindsight", layout="wide")
    st.markdown(
        """
        <style>
        .block-container { max-width: 1320px; padding-top: 2.2rem; padding-bottom: 3rem; }
        h1 { letter-spacing: -0.035em; color: #172b4d; }
        h2, h3 { color: #203653; letter-spacing: -0.02em; }
        [data-testid="stMetric"] { background: #f7f9fc; border: 1px solid #e4eaf2;
            padding: 14px 16px; border-radius: 10px; }
        [data-testid="stVerticalBlockBorderWrapper"] { border-color: #e4eaf2 !important;
            border-radius: 10px !important; }
        .status-pill { display: inline-block; border-radius: 999px; padding: 4px 10px;
            font-size: 0.76rem; line-height: 1.2; font-weight: 650; white-space: nowrap; }
        .high, .overdue { background: #fff0ed; color: #a53b2c; }
        .medium, .pending { background: #fff6df; color: #8a5b00; }
        .low, .completed { background: #eaf6ef; color: #287148; }
        .scheduled, .neutral { background: #edf2f8; color: #50647e; }
        [data-testid="stExpander"] { border: 1px solid #e8edf3; border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with DATA_PATH.open(encoding="utf-8") as data_file:
        deal_data = json.load(data_file)

    predictions = build_predictive_foresight(deal_data)
    ledger = build_commitment_ledger(deal_data)

    st.title("Foresight")
    st.caption("Evidence-based deal preparation, supported by the Hindsight memory layer")
    st.divider()

    st.header("Predictive Foresight")
    st.write("Anticipate customer questions, surface risks, and prepare for key milestones.")
    forecast_metrics = st.columns(4)
    forecast_metrics[0].metric("Anticipated questions", len(predictions["anticipated_questions"]))
    forecast_metrics[1].metric("Counter-questions", len(predictions["strategic_counter_questions"]))
    forecast_metrics[2].metric("Key risks", len(predictions["key_risks"]))
    forecast_metrics[3].metric("Upcoming deadlines", len(predictions["upcoming_deadlines"]))

    st.subheader("Anticipated Questions")
    _render_prediction_cards(predictions["anticipated_questions"], "question")
    st.subheader("Strategic Counter-Questions")
    _render_prediction_cards(predictions["strategic_counter_questions"], "question")
    st.subheader("Key Risks")
    _render_prediction_cards(predictions["key_risks"], "risk")
    st.subheader("Upcoming Deadlines")
    _render_deadlines(predictions["upcoming_deadlines"])

    st.divider()
    st.header("Commitment Ledger")
    st.write("Commitments and evidence recorded across the deal history.")
    _render_ledger(ledger)


if __name__ == "__main__":
    main()
