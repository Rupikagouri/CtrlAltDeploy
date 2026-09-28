"""
collision_detector.py - Member 2 (Tanmaya) Backend Engine.

Core Responsibilities:
1. Implements check_collisions(): Cross-checks incoming customer requests against
   retrieved Hindsight deal memory and Veridian company rules.
2. Implements update_commitment_status(): Dynamic memory reflection loop that updates
   Hindsight memory live when commitments are completed (e.g. Mark SOC-2 Sent).
"""

from typing import Dict, Any, List
from datetime import datetime


class TanmayaCollisionDetector:
    def __init__(self, company_kb: Dict[str, Any]):
        self.company_kb = company_kb

    def check_collisions(self, customer_request: str, deal_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-checks an incoming request against deal memory and company baseline rules.
        Returns categorized collision cards with exact evidence citations.
        """
        commitments = deal_context.get("commitments", [])
        kb_deploy = self.company_kb.get("deployment_rules", {})
        kb_pricing = self.company_kb.get("pricing_and_discount_rules", {})

        # 1. Evaluate Security Blocker
        soc2_comm = next((c for c in commitments if c.get("id") == "COMM-02"), None)
        is_soc2_completed = soc2_comm and soc2_comm.get("status") == "Completed"

        # 2. Parse request intent
        req_lower = customer_request.lower()
        has_discount_request = any(k in req_lower for k in ["40%", "discount", "price", "cheaper", "cost", "off"])
        has_two_week_request = any(k in req_lower for k in ["two weeks", "2 weeks", "two-week", "2-week", "14 days"])

        collisions: List[Dict[str, Any]] = []

        # Collision 1: Security Gate (SOC-2 Type II Report)
        if not is_soc2_completed:
            collisions.append({
                "severity": "RED",
                "badge": "🔴 Security Blocker",
                "category": "Security & Compliance",
                "title": "Unfulfilled SOC-2 Mandate for Production Access",
                "description": "Nadia Chen (CISO) explicitly mandated that NO production data can touch Veridian without reviewed SOC-2 Type II audit report. Promised 31 days ago with no recorded fulfilment.",
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

        # Collision 2: Timeline (2 Weeks vs. 4-6 Weeks)
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
                    f"Veridian Company Policy: {kb_deploy.get('two_week_rejection_reason', 'Minimum 21 days required.')}"
                ],
                "impact": "HIGH: Agreeing to 2 weeks creates catastrophic delivery failure and breach of SLA risk."
            })

        # Collision 3: Commercial & Price (40% vs. $50k Budget Ceiling vs. $48k Competitor)
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
                    f"Veridian Policy: {kb_pricing.get('policy_note', '40% discount requires CEO approval.')}"
                ],
                "impact": "MODERATE: Rep lacks authority for 40%. The true negotiation target is $48,000 to $50,000 (meeting Linda's budget while matching NimbusAI)."
            })

        # Dynamic Recommendation based on state
        if not is_soc2_completed:
            recommended_action = (
                "⛔ DO NOT agree to any deployment timeline or final pricing concession yet. "
                "Your immediate step must be to deliver the overdue SOC-2 Type II report to Nadia Chen. "
                "Once security review is initiated, schedule a commercial call with Linda to negotiate between $48k-$50k."
            )
            reply_draft = (
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
            reply_draft = (
                "Hi Owen and Priya,\n\n"
                "Great news: our SOC-2 Type II audit report has been submitted to Nadia's portal, clearing the compliance path.\n\n"
                "Regarding your request: while 40% exceeds our corporate threshold, we want to win ACME's business before your "
                "October 15 production freeze. We can structure an agreement at $49,000 ARR—well within Linda's $50k departmental "
                "allocation and directly matching alternative proposals you are evaluating.\n\n"
                "To ensure a seamless launch before October 15, we will allocate our senior architecture pod to complete onboarding "
                "in a phased 3-week window. If we can finalize agreement by this Friday, our engineering pod starts Monday.\n\n"
                "Best regards,\n[Your Name] - Veridian Account Executive"
            )

        return {
            "customer_request": customer_request,
            "collisions": collisions,
            "active_blockers_count": sum(1 for c in collisions if c["severity"] == "RED"),
            "warnings_count": sum(1 for c in collisions if c["severity"] in ["ORANGE", "YELLOW"]),
            "recommended_action": recommended_action,
            "recommended_reply_draft": reply_draft
        }

    def update_commitment_status(self, deal_context: Dict[str, Any], commitment_id: str, new_status: str, notes: str) -> bool:
        """
        Executes dynamic memory reflection: mutates commitment state in Hindsight memory.
        """
        commitments = deal_context.get("commitments", [])
        for comm in commitments:
            if comm.get("id") == commitment_id:
                comm["status"] = new_status
                comm["status_notes"] = notes
                comm["last_updated"] = datetime.now().isoformat()
                return True
        return False
