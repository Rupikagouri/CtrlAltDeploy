"""
collision_ui.py - Member 2 (Tanmaya) Frontend Component.

Renders:
1. Collision Cards (🔴 Security Blocker, 🟠 Timeline Conflict, 🟡 Commercial Alignment).
2. Collapsible Evidence Drawers with verbatim call transcripts and policy citations.
3. The Interactive 'Mark SOC-2 Report as Sent' button that triggers live memory re-evaluation.
4. Dynamic Recommendation & Strategy Display that shifts based on memory state.
"""

import streamlit as st
from typing import Dict, Any


def render_collision_cards(results: Dict[str, Any]):
    """
    Renders the visual collision cards with collapsible evidence citations.
    """
    st.markdown("### 🚨 Detected Collisions against Deal Memory")

    # Metrics row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Active Blockers", value=results.get("active_blockers_count", 0))
    with c2:
        st.metric(label="Warnings & Conflicts", value=results.get("warnings_count", 0))
    with c3:
        st.metric(label="Memory Verification", value="Grounded in Hindsight")

    st.markdown("<br>", unsafe_allow_html=True)

    # Render each collision card
    for col in results.get("collisions", []):
        with st.container():
            if col["severity"] == "RED":
                st.error(f"**{col['badge']}**: {col['title']}")
            elif col["severity"] == "ORANGE":
                st.warning(f"**{col['badge']}**: {col['title']}")
            elif col["severity"] == "YELLOW":
                st.warning(f"**{col['badge']}**: {col['title']}")
            elif col["severity"] == "GREEN":
                st.success(f"**{col['badge']}**: {col['title']}")

            st.write(col["description"])

            # Evidence Drawer
            with st.expander(f"🔍 View Evidence from Hindsight Memory ({len(col['evidence'])} verified sources)"):
                for ev in col["evidence"]:
                    st.markdown(f"- 📌 `{ev}`")
                st.caption(f"**Business Impact:** {col['impact']}")

            st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)


def render_actionable_guidance(results: Dict[str, Any]):
    """
    Renders the strategic advice and memory-aligned reply draft.
    """
    st.markdown("### 🎯 Strategic Recommendation & Ready-to-Send Reply")
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**What You Should Do:**\n\n{results.get('recommended_action')}")

    with col2:
        st.text_area(
            "Drafted Customer Reply (Memory-Aligned):",
            value=results.get("recommended_reply_draft", ""),
            height=200
        )
