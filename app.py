"""
app.py - Streamlit Frontend Dashboard for Project Foresight.
Foresight: Powered by Hindsight.
"Hindsight gives you foresight."
"""

import streamlit as st
import json
from datetime import datetime
from memory import DealMemoryBank
from collision_engine import collision_engine

st.set_page_config(
    page_title="Foresight | Deal Intelligence with Hindsight Memory",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize persistent session state for memory
if "deal_memory" not in st.session_state:
    st.session_state.deal_memory = DealMemoryBank()

if "memory_updated_event" not in st.session_state:
    st.session_state.memory_updated_event = False

# Custom Styling for polished enterprise SaaS aesthetic
st.markdown("""
<style>
    .reportview-container {
        background-color: #0e1117;
    }
    .metric-card {
        background: #1e222d;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #2d3342;
        margin-bottom: 12px;
    }
    .badge-red {
        background-color: #ffebe9;
        color: #cf222e;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #ff8182;
    }
    .badge-orange {
        background-color: #fff8c5;
        color: #9a6700;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #d4a72c;
    }
    .badge-yellow {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #facc15;
    }
    .badge-green {
        background-color: #dafbe1;
        color: #1a7f37;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #4ac26b;
    }
    .evidence-box {
        background: #161b22;
        border-left: 3px solid #58a6ff;
        padding: 10px 14px;
        margin-top: 8px;
        border-radius: 0 6px 6px 0;
        font-family: monospace;
        font-size: 0.85rem;
        color: #c9d1d9;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("🔮 Foresight")
    st.caption("Powered by **Hindsight Agent Memory**")
    st.divider()

    st.subheader("🏢 Active Deal")
    st.markdown("**ACME Corp** (FinTech / Logistics)")
    st.markdown("**Stage:** Proposal Review & Negotiation")
    st.markdown("**Quote:** `$72,000 ARR`")
    st.markdown("**History:** `9 Calls | 8 Weeks`")

    st.divider()
    st.subheader("👥 Key Stakeholders")
    for s in st.session_state.deal_memory.stakeholders:
        with st.expander(f"{s['name']} — {s['role']}"):
            st.caption(f"**Title:** {s['title']}")
            st.caption(f"**Sentiment:** {s['sentiment']}")
            st.caption(f"**Top Concern:** {s['concerns'][0]}")

    st.divider()
    st.caption("Repository: `CtrlAltDeploy/Foresight`")
    st.caption("HackwithHyderabad 3.0 Edition")


# ----------------- MAIN HEADER -----------------
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("Foresight: Powered by Hindsight")
    st.markdown("*Checking new customer requests against long-term deal memory to prevent commercial disasters.*")
with col_head2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("🧠 **Memory Bank:** `acme-deal` (Active)")

st.divider()

# ----------------- TABS -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ The Collision Check (Main Demo)",
    "📋 Instant Pre-Call Briefing",
    "📑 Living Commitment Ledger",
    "📜 Deal History Explorer (9 Calls)"
])

# ================= TAB 1: THE COLLISION CHECK =================
with tab1:
    st.subheader("⚡ Automated Deal Collision Detection")
    st.markdown(
        "When an aggressive request or email arrives from a customer, Foresight checks it against "
        "**all 8 weeks of deal memory** and company policies to identify hidden landmines."
    )

    # Check current SOC-2 state
    soc2_comm = next((c for c in st.session_state.deal_memory.commitments if c["id"] == "COMM-02"), None)
    is_soc2_sent = soc2_comm and soc2_comm.get("status") == "Completed"

    # Pre-filled Demo Prompt Box
    col_input1, col_input2 = st.columns([3, 1])
    with col_input1:
        default_req = "Can you give us 40% off and get us live into production in two weeks?"
        customer_request = st.text_area(
            "Incoming Customer Request / Email:",
            value=default_req,
            height=85,
            help="Type any request from the buyer to check against deal memory."
        )

    with col_input2:
        st.markdown("<br>", unsafe_allow_html=True)
        run_check = st.button("🔍 Check Against Deal Memory", type="primary", use_container_width=True)
        
        if not is_soc2_sent:
            mark_soc2 = st.button("🚀 Mark SOC-2 Sent to Nadia", use_container_width=True, help="Simulate sending the promised compliance report")
            if mark_soc2:
                st.session_state.deal_memory.mark_soc2_sent()
                st.session_state.memory_updated_event = True
                st.rerun()
        else:
            st.button("✅ SOC-2 Delivered (Active in Memory)", disabled=True, use_container_width=True)
            reset_btn = st.button("🔄 Reset Demo (Revert to Overdue)", use_container_width=True, help="Reset memory to show judges the before state again")
            if reset_btn:
                st.session_state.deal_memory = DealMemoryBank()
                st.session_state.memory_updated_event = False
                st.rerun()

    # Dynamic Memory Reaction Banner if SOC-2 is sent
    if is_soc2_sent:
        st.success(
            "🎉 **DYNAMIC MEMORY REACTION TRIGGERED!**\n\n"
            "Hindsight memory was updated live: **SOC-2 Report marked as Delivered to Nadia Chen**.\n"
            "The Collision Engine has automatically **re-evaluated all constraints** against the updated deal history:\n"
            "• 🔴 **Security Blocker** → **CLEARED** (Converted to verified step)\n"
            "• 🎯 **Strategic Guidance** → Automatically shifted from **DEFENSIVE STOP** to **OFFENSIVE $49k CLOSING PLAN**"
        )

    # Evaluate Collisions against current memory
    results = collision_engine.evaluate_request(customer_request, memory_bank=st.session_state.deal_memory)

    st.markdown("---")

    # Metrics Summary Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric(label="Critical Blockers", value=results["active_blockers_count"])
    with m_col2:
        st.metric(label="Policy & Budget Warnings", value=results["warnings_count"])
    with m_col3:
        st.metric(label="Historical Calls Scanned", value="9 Interactions")
    with m_col4:
        st.metric(label="Decision Confidence", value="100% Grounded")

    st.markdown("### 🚨 Detected Collisions")

    # Display Collisions
    for col in results["collisions"]:
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
            
            with st.expander(f"🔍 View Evidence from Hindsight Memory ({len(col['evidence'])} verified sources)"):
                for ev in col["evidence"]:
                    st.markdown(f"- 📌 `{ev}`")
                st.caption(f"**Business Impact:** {col['impact']}")
            st.markdown("<br>", unsafe_allow_html=True)

    # Strategic Action & Recommended Reply Draft
    st.markdown("### 🎯 Strategic Guidance & Recommended Reply")
    col_strat1, col_strat2 = st.columns([1, 1])

    with col_strat1:
        st.info(f"**What You Should Do:**\n\n{results['recommended_action']}")

    with col_strat2:
        st.text_area(
            "Drafted Customer Reply (Memory-Aligned):",
            value=results["recommended_reply_draft"],
            height=200
        )

    # Predictive Foresight Panel
    st.markdown("---")
    st.markdown("### 🔮 Predictive Foresight: Anticipate the Next Move")
    st.caption("Foresight analyzes unaddressed stakeholder concerns to predict what the buyer will ask next.")

    pred = results["predictive_foresight"]
    col_pred1, col_pred2 = st.columns(2)

    with col_pred1:
        st.markdown("#### 💬 Anticipated Next Buyer Questions")
        for q in pred["anticipated_next_questions"]:
            st.markdown(f"**{q['stakeholder']}:** *\"{q['question']}\"*")
            st.caption(f"↳ **Why:** {q['why']}")
            st.markdown("<hr style='margin: 4px 0;'>", unsafe_allow_html=True)

    with col_pred2:
        st.markdown("#### 🎯 High-Leverage Counter-Questions to Ask")
        for cq in pred["strategic_counter_questions"]:
            st.markdown(f"**Target:** `{cq['target']}`")
            st.markdown(f"👉 *\"{cq['counter_question']}\"*")
            st.caption(f"↳ **Leverage:** {cq['leverage']}")
            st.markdown("<hr style='margin: 4px 0;'>", unsafe_allow_html=True)

    st.info(f"💡 **Similar Deal Insight:** {pred['similar_deal_insights']}")


# ================= TAB 2: PRE-CALL BRIEFING =================
with tab2:
    st.subheader("📋 10-Second Pre-Call Executive Briefing")
    st.markdown("Never waste hours re-reading CRM notes again. Generate an instant briefing before walking into a meeting.")

    if st.button("⚡ Generate Pre-Call Brief for ACME Corp", type="primary"):
        brief = collision_engine.generate_pre_call_brief(memory_bank=st.session_state.deal_memory)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown("#### 👥 Meeting Dossier: Who is in the Room")
            for sh in brief["stakeholders"]:
                st.markdown(f"- **{sh['name']}** ({sh['title']}): `{sh['sentiment']}`")
                st.caption(f"  Focus: {sh['key_focus']}")

            st.markdown("#### ⚔️ Competitor Threat Analysis")
            comp = brief["competitor_watch"]
            st.warning(f"**Competitor:** {comp['competitor']} | **Bid:** {comp['bid']}")
            st.markdown(f"**Counter-Strategy:** {comp['counter_strategy']}")

        with col_b2:
            st.markdown("#### ⚠️ Critical Commitments & Risks")
            for r in brief["critical_risks"]:
                st.error(r)

            st.markdown("#### 🎯 Learned Winning Tactics from Past Deals")
            for t in brief["learned_winning_tactics"]:
                st.success(t)


# ================= TAB 3: COMMITMENT LEDGER =================
with tab3:
    st.subheader("📑 Living Commitment Ledger")
    st.markdown("An auditable log of promises made across all 8 weeks. Status is verified based on recorded evidence.")

    for comm in st.session_state.deal_memory.commitments:
        col_c1, col_c2, col_c3, col_c4 = st.columns([3, 2, 2, 2])
        with col_c1:
            st.markdown(f"**{comm['title']}** (`{comm['id']}`)")
            st.caption(f"Promised by: {comm['promised_by']} → {comm['recipient']}")
        with col_c2:
            st.markdown(f"**Call Reference:** {comm['call_ref']}")
            st.caption(f"Date: {comm['date_promised']}")
        with col_c3:
            if comm["status"] == "Completed":
                st.markdown("<span class='badge-green'>✅ Completed</span>", unsafe_allow_html=True)
            elif comm["status"] == "Overdue":
                st.markdown("<span class='badge-red'>⚠️ Overdue</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='badge-yellow'>⏳ Pending</span>", unsafe_allow_html=True)
        with col_c4:
            st.caption(f"**Audit Note:** {comm['status_notes']}")
        st.divider()


# ================= TAB 4: DEAL HISTORY EXPLORER =================
with tab4:
    st.subheader("📜 8 Weeks of ACME Corp Deal Memory")
    st.markdown("Foresight retains every conversation, attendee, and objection in Hindsight memory.")

    for call in st.session_state.deal_memory.interactions:
        with st.expander(f"📞 Call #{call['call_id']}: {call['title']} ({call['date']})"):
            st.markdown(f"**Attendees:** {', '.join(call['attendees'])}")
            st.write(call["summary"])
            st.markdown("**Key Memorized Takeaways:**")
            for kw in call["key_takeaways"]:
                st.markdown(f"- 📌 `{kw}`")
