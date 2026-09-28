"""
tanmaya_app.py - Standalone test harness for Member 2 (Tanmaya).
Run with: streamlit run tanmaya/tanmaya_app.py
"""

import streamlit as st
import json
import os
import sys

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tanmaya.collision_detector import TanmayaCollisionDetector
from tanmaya.collision_ui import render_collision_cards, render_actionable_guidance
from memory import DealMemoryBank

st.set_page_config(page_title="Tanmaya's Collision Engine | Foresight", page_icon="⚡", layout="wide")

# Initialize persistent session state for memory
if "deal_memory" not in st.session_state:
    st.session_state.deal_memory = DealMemoryBank()

if "memory_updated_event" not in st.session_state:
    st.session_state.memory_updated_event = False

# Load Tanmaya's company rules
kb_path = os.path.join(os.path.dirname(__file__), "company_kb.json")
with open(kb_path, "r", encoding="utf-8") as f:
    company_kb = json.load(f)

detector = TanmayaCollisionDetector(company_kb=company_kb)

st.title("⚡ Foresight: Collision Check & Dynamic Memory Reflection")
st.caption("Developed by **Tanmaya (Member 2)** — Collision Engine & Dynamic Reflection Lead")
st.divider()

# Check current SOC-2 status in memory
soc2_comm = next((c for c in st.session_state.deal_memory.commitments if c["id"] == "COMM-02"), None)
is_soc2_sent = soc2_comm and soc2_comm.get("status") == "Completed"

# Request Input & Trigger controls
col1, col2 = st.columns([3, 1])

with col1:
    default_prompt = "Can you give us 40% off and get us live into production in two weeks?"
    user_request = st.text_area(
        "Incoming Customer Negotiation Request / Email:",
        value=default_prompt,
        height=85
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    check_btn = st.button("🔍 Run Collision Check", type="primary", use_container_width=True)
    
    if not is_soc2_sent:
        mark_btn = st.button("🚀 Mark SOC-2 Sent to Nadia", use_container_width=True, help="Simulate sending the promised compliance report")
        if mark_btn:
            st.session_state.deal_memory.mark_soc2_sent()
            st.session_state.memory_updated_event = True
            st.rerun()
    else:
        st.button("✅ SOC-2 Delivered (Active)", disabled=True, use_container_width=True)
        reset_btn = st.button("🔄 Reset Demo (Revert to Overdue)", use_container_width=True, help="Reset memory to show judges the before state again")
        if reset_btn:
            st.session_state.deal_memory = DealMemoryBank()
            st.session_state.memory_updated_event = False
            st.rerun()

# Highlight live memory reaction banner if just updated
if is_soc2_sent:
    st.success(
        "🎉 **DYNAMIC MEMORY REACTION TRIGGERED!**\n\n"
        "Hindsight memory was updated live: **SOC-2 Report marked as Delivered to Nadia Chen**.\n"
        "The Collision Engine has automatically **re-evaluated all constraints** against the updated deal history:\n"
        "• 🔴 **Security Blocker** → **CLEARED** (Converted to verified step)\n"
        "• 🎯 **Strategic Guidance** → Automatically shifted from **DEFENSIVE STOP** to **OFFENSIVE $49k CLOSING PLAN**"
    )

# Run collision evaluation against current memory
context = st.session_state.deal_memory.get_all_context()
results = detector.check_collisions(customer_request=user_request, deal_context=context)

# Render Tanmaya's UI components
render_collision_cards(results)
st.markdown("---")
render_actionable_guidance(results)
