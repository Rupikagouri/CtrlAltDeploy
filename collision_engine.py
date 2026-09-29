"""
collision_engine.py - Collision Detection and Predictive Foresight Engine for Foresight.

Evaluates customer requests against Hindsight deal memory and company baseline constraints.
Detects:
- 🔴 Security Blockers
- 🟠 Timeline Conflicts
- 🟡 Commercial / Price Misalignments
Predicts:
- 🔮 Anticipated Next Questions
- 🎯 High-Leverage Strategic Counter-Questions
"""

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from memory import DealMemoryBank, deal_memory
import prompts

load_dotenv()


class CollisionEngine:
    def __init__(self, memory_bank: DealMemoryBank = deal_memory):
        self.memory = memory_bank
        self.groq_client = None
        self._init_groq()

    def _init_groq(self):
        api_key = os.getenv("GROQ_API_KEY")
        if api_key and api_key != "your_groq_api_key_here":
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=api_key)
            except Exception:
                self.groq_client = None

    def evaluate_request(self, customer_request: str, memory_bank=None) -> Dict[str, Any]:
        """
        Runs the full collision check and predictive foresight evaluation.
        """
        mem = memory_bank or self.memory
        context = mem.get_all_context()
        commitments = context["commitments"]
        kb = context["company_kb"]

        # 1. Check Security Blocker state
        soc2_comm = next((c for c in commitments if c["id"] == "COMM-02"), None)
        soc2_completed = soc2_comm and soc2_comm["status"] == "Completed"

        # 2. Extract price and timeline mentions
        req_lower = customer_request.lower()
        has_discount_request = any(k in req_lower for k in ["40%", "discount", "price", "cheaper", "cost", "off"])
        has_two_week_request = any(k in req_lower for k in ["two weeks", "2 weeks", "two-week", "2-week", "14 days"])

        collisions: List[Dict[str, Any]] = []

        # Collision A: Security
        if not soc2_completed:
            collisions.append({
                "severity": "RED",
                "badge": "🔴 Security Blocker",
                "category": "Security & Compliance",
                "title": "Unfulfilled SOC-2 Mandate for Production Access",
                "description": "Nadia Chen (CISO) explicitly mandated that NO production data can touch Veridian without reviewed SOC-2 Type II audit report. Promised 31 days ago in Call #2 with no recorded fulfilment.",
                "evidence": [
                    "Call #2 (31 days ago): Nadia stated 'No production data can touch your platform without our security team reviewing your audited SOC-2 Type II report.'",
                    "Commitment COMM-02: 'SOC-2 Type II Audit Report Delivery' is currently OVERDUE (31 days elapsed)."
                ],
                "impact": "CRITICAL: Promising deployment or production access before SOC-2 sign-off will immediately cause security to veto the vendor selection."
            })
        else:
            collisions.append({
                "severity": "GREEN",
                "badge": "✅ Security Cleared",
                "category": "Security & Compliance",
                "title": "SOC-2 Type II Report Delivered",
                "description": "SOC-2 audit report was delivered to Nadia Chen. Mutual security gate is unlocked for staging and production onboarding.",
                "evidence": [
                    f"Commitment COMM-02 updated to 'Completed' at {soc2_comm.get('last_updated', 'recently')}.",
                    "Note: Audited report transmitted to Nadia Chen."
                ],
                "impact": "Security hurdle cleared. Technical deployment can be scheduled subject to engineering timelines."
            })

        # Collision B: Timeline
        if has_two_week_request:
            collisions.append({
                "severity": "ORANGE",
                "badge": "🟠 Timeline Conflict",
                "category": "Engineering Delivery",
                "title": "Unrealistic 2-Week Deployment Request vs. 4-6 Week Baseline",
                "description": "Customer requested a 2-week live deployment. Veridian standard deployment is 4 to 6 weeks. No 2-week commitment was ever made.",
                "evidence": [
                    "Call #3 (6 weeks ago): Veridian Solutions Architect explicitly told Marcus Vance standard onboarding is 4 to 6 weeks.",
                    "Call #3 & #9: Marcus confirmed ACME has an annual production freeze starting October 15.",
                    "Veridian Company Policy: 2-week deployment is marked infeasible due to VPC peering, IAM validation, and automated test gates."
                ],
                "impact": "HIGH: Agreeing to 2 weeks creates catastrophic delivery failure and breach of SLA risk."
            })

        # Collision C: Commercial & Price
        if has_discount_request:
            collisions.append({
                "severity": "YELLOW",
                "badge": "🟡 Commercial Alignment",
                "category": "Pricing & Margin",
                "title": "40% Discount Request Exceeds Delegation Limit ($43.2k vs. $50k Budget Ceiling)",
                "description": "Current quote is $72,000. 40% discount brings price to $43,200. Linda (CFO) stated ACME's budget ceiling is $50,000. Competitor NimbusAI is offering $48,000. Veridian rep discount limit is 15% ($61,200).",
                "evidence": [
                    "Call #4 (5 weeks ago): Linda Sterling established a hard budget ceiling of $50,000.",
                    "Call #6 (3 weeks ago): Priya revealed competitor NimbusAI submitted a $48,000 proposal.",
                    "Veridian Policy: 40% discount ($43,200) requires CEO approval and is forbidden without 3-year upfront commitment."
                ],
                "impact": "MODERATE: Rep lacks authority for 40%. The true negotiation target is $48,000 to $50,000 (meeting Linda's budget while matching NimbusAI)."
            })

        # Generate Strategic Recommendations based on current state
        if not soc2_completed:
            recommended_action = (
                "⛔ DO NOT agree to any deployment timeline or final pricing concession yet. "
                "Your immediate step must be to deliver the overdue SOC-2 Type II report to Nadia Chen. "
                "Once security review is initiated, schedule a commercial call with Linda to negotiate between $48k-$50k."
            )
            email_draft = (
                "Hi Owen and Priya,\n\n"
                "Thank you for following up. Regarding the timeline and commercial terms:\n\n"
                "First, our highest priority is protecting ACME's sensitive financial data. As promised to Nadia, "
                "our audited SOC-2 Type II report is being transmitted via our secure portal today for her review. "
                "We cannot ethically schedule live production onboarding until Nadia's team signs off.\n\n"
                "On timeline, as discussed with Marcus in our architecture review, our standard enterprise onboarding "
                "is 4 to 6 weeks to ensure zero disruption before your October 15 freeze. We can offer a dedicated "
                "solutions architect to target a 3-week express onboarding starting immediately upon security sign-off.\n\n"
                "Let's sync with Linda this Thursday on commercials—we are prepared to align within your $50,000 budget envelope.\n\n"
                "Best regards,\n[Your Name] - Veridian Account Executive"
            )
        else:
            recommended_action = (
                "🎯 PROCEED WITH COMMERCIAL NEGOTIATION. "
                "With the SOC-2 blocker resolved, focus on closing Linda and Owen. "
                "Target price: $49,000 (beats Linda's $50k budget and counters NimbusAI's $48k) on a 3-4 week phased rollout."
            )
            email_draft = (
                "Hi Owen and Priya,\n\n"
                "Great news: our SOC-2 Type II audit report has been submitted to Nadia's portal, clearing the compliance path.\n\n"
                "Regarding your request: while 40% exceeds our corporate threshold, we want to win ACME's business before your "
                "October 15 production freeze. We can structure an agreement at $49,000 ARR—well within Linda's $50k departmental "
                "allocation and directly matching alternative proposals you are evaluating.\n\n"
                "To ensure a seamless launch before October 15, we will allocate our senior architecture pod to complete onboarding "
                "in a phased 3-week window. If we can finalize agreement by this Friday, our engineering pod starts Monday.\n\n"
                "Best regards,\n[Your Name] - Veridian Account Executive"
            )

        # Predictive Foresight: Anticipated Questions & Counter-Questions
        predictive_foresight = {
            "anticipated_next_questions": [
                {
                    "stakeholder": "Owen Miller (Procurement)",
                    "question": "Will Veridian accept Net-60 payment terms, and can you cap annual price increases at 3% for renewals?",
                    "why": "Owen's mandate is commercial extraction; procurement teams routinely push for Net-60 once price reaches agreement."
                },
                {
                    "stakeholder": "Linda Sterling (CFO)",
                    "question": "If our transaction volume exceeds estimates in Q4, will we be hit with variable overage charges?",
                    "why": "Linda is terrified of unexpected budget creep beyond her $50k ceiling."
                },
                {
                    "stakeholder": "Marcus Vance (Architect)",
                    "question": "Can we execute a partial sandbox deploy in parallel with legal review to beat the Oct 15 freeze?",
                    "why": "Marcus is under engineering pressure to show progress before ACME's code freeze."
                }
            ],
            "strategic_counter_questions": [
                {
                    "target": "Priya Sharma (Champion)",
                    "counter_question": "Priya, if we meet Linda at $49,000 and provide dedicated engineering to launch before October 15, will you and Linda sign the agreement by this Friday?",
                    "leverage": "Secures firm closing commitment in exchange for the price concession."
                },
                {
                    "target": "Marcus Vance (Architect)",
                    "counter_question": "Marcus, how many engineering hours can your team dedicate during week 1 of onboarding to assist with VPC peering?",
                    "leverage": "Shifts timeline accountability onto ACME's internal readiness."
                }
            ],
            "similar_deal_insights": (
                "In 84% of comparable FinTech deals with high-volume logistics requirements, "
                "buyers citing competitor bids (like NimbusAI) settled within 2% of budget when guaranteed dedicated migration architects."
            )
        }

        # If Groq is connected, polish the output dynamically
        if self.groq_client:
            try:
                # LLM synthesis could enhance the message if desired
                pass
            except Exception:
                pass

        return {
            "customer_request": customer_request,
            "collisions": collisions,
            "active_blockers_count": sum(1 for c in collisions if c["severity"] == "RED"),
            "warnings_count": sum(1 for c in collisions if c["severity"] in ["ORANGE", "YELLOW"]),
            "recommended_action": recommended_action,
            "recommended_reply_draft": email_draft,
            "predictive_foresight": predictive_foresight
        }

    def generate_pre_call_brief(self, memory_bank=None) -> Dict[str, Any]:
        """
        Generates the instant 10-second Pre-Call Briefing for the ACME Corp deal.
        """
        mem = memory_bank or self.memory
        context = mem.get_all_context()
        commitments = context["commitments"]
        stakeholders = context["stakeholders"]

        soc2_comm = next((c for c in commitments if c["id"] == "COMM-02"), None)
        soc2_status = soc2_comm["status"] if soc2_comm else "Overdue"

        return {
            "deal_title": "ACME Corp Enterprise Evaluation",
            "current_stage": "Stage 4: Proposal Review & Executive Alignment",
            "quote_value": "$72,000 ARR",
            "stakeholders": [
                {"name": s["name"], "title": s["title"], "sentiment": s["sentiment"], "key_focus": s["concerns"][0]}
                for s in stakeholders
            ],
            "competitor_watch": {
                "competitor": "NimbusAI",
                "bid": "$48,000 / year",
                "threat_level": "High (Linda is evaluating closely)",
                "counter_strategy": "Highlight Veridian's zero data-egress fees and native AWS us-east-1 VPC peering. NimbusAI runs on GCP with latency penalties."
            },
            "critical_risks": [
                f"SOC-2 Type II Report delivery is {soc2_status.upper()} (promised 31 days ago to Nadia Chen).",
                "ACME annual production freeze commences October 15 (hard timeline cliff).",
                "Linda's budget ceiling is $50,000; formal quote of $72k requires strategic concession."
            ],
            "learned_winning_tactics": [
                "Tactics from FinTech wins: Counter competitor price by offering $49k with quarterly opt-out, preserving margin while removing lock-in fear.",
                "Never negotiate price until Nadia Chen has verified the compliance documentation."
            ]
        }


# Singleton engine instance
collision_engine = CollisionEngine()
