"""
memory.py - Hindsight Deal Memory Layer for Foresight.

Handles:
- Ingestion of 9 ACME interactions via retain()
- Multi-query recall() across stakeholder objections, commitments, and commercial limits
- Real-time memory reflection when commitments are updated (e.g., Mark SOC-2 Sent)
- Hybrid client: connects to Hindsight Cloud when API key is set, with an embedded
  high-fidelity memory store fallback for offline/instant local execution.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Pydantic models for structured pre-call brief output
try:
    from pydantic import BaseModel, Field

    class StakeholderSensitivity(BaseModel):
        name: str
        role: str
        sensitivity: str
        recommended_approach: str

    class CompetitorIntelligence(BaseModel):
        competitor: str
        their_offer: str
        our_differentiators: List[str]
        battle_card_tip: str

    class OpenCommitmentRisk(BaseModel):
        commitment: str
        recipient: str
        status: str
        risk: str

    class PreCallBrief(BaseModel):
        headline: str
        stakeholder_sensitivities: List[StakeholderSensitivity]
        competitor_intelligence: CompetitorIntelligence
        open_commitments_at_risk: List[OpenCommitmentRisk]
        winning_tactics: List[str]
        one_sentence_coaching_tip: str

    PYDANTIC_AVAILABLE = True

except ImportError:
    PYDANTIC_AVAILABLE = False
    PreCallBrief = None

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ACME_DEAL_PATH = os.path.join(DATA_DIR, "acme_deal.json")
COMPANY_KB_PATH = os.path.join(DATA_DIR, "company_kb.json")


class DealMemoryBank:
    """
    Manages Hindsight memory operations for an enterprise sales deal.
    """

    def __init__(self, deal_path: str = ACME_DEAL_PATH, kb_path: str = COMPANY_KB_PATH):
        self.deal_path = deal_path
        self.kb_path = kb_path
        self.deal_data = self._load_json(self.deal_path)
        self.company_kb = self._load_json(self.kb_path)
        
        # In-memory working copy of commitments and deal memory facts
        self.commitments: List[Dict[str, Any]] = self.deal_data.get("commitments", [])
        self.interactions: List[Dict[str, Any]] = self.deal_data.get("interactions", [])
        self.stakeholders: List[Dict[str, Any]] = self.deal_data.get("stakeholders", [])
        self.metadata: Dict[str, Any] = self.deal_data.get("deal_metadata", {})
        
        # Memory audit log of changes made during the session
        self.memory_audit_log: List[Dict[str, Any]] = []
        
        # Try initializing Hindsight Cloud client if available
        self.hindsight_client = None
        self._init_hindsight()

    def _load_json(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _init_hindsight(self):
        api_key = os.getenv("HINDSIGHT_API_KEY")
        base_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
        if api_key and api_key != "your_hindsight_api_key_here":
            try:
                import hindsight_client
                self.hindsight_client = hindsight_client.Client(api_key=api_key, base_url=base_url)
            except Exception as e:
                # Fallback to local memory bank
                self.hindsight_client = None

    def retain(self, content: str, category: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Retains an observation, commitment, or interaction into deal memory.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "content": content,
            "metadata": metadata or {}
        }
        self.memory_audit_log.append(entry)
        
        if self.hindsight_client:
            try:
                self.hindsight_client.retain(
                    bank_id=self.metadata.get("deal_id", "acme-deal"),
                    text=content,
                    context=category
                )
            except Exception:
                pass

    def recall(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recalls the most relevant past interactions, stakeholder statements, and commitments.
        """
        # If Hindsight Cloud client is active, query cloud memory
        cloud_results = []
        if self.hindsight_client:
            try:
                cloud_results = self.hindsight_client.recall(
                    bank_id=self.metadata.get("deal_id", "acme-deal"),
                    query=query,
                    limit=top_k
                )
            except Exception:
                cloud_results = []

        # Local recall matching: score interactions and commitments against query terms
        tokens = set(query.lower().replace("?", "").replace(",", "").split())
        matched_memories = []

        for call in self.interactions:
            text = f"{call.get('title', '')} {' '.join(call.get('attendees', []))} {call.get('summary', '')} {' '.join(call.get('key_takeaways', []))}"
            words = text.lower().split()
            overlap = sum(1 for t in tokens if t in words or any(t in w for w in words))
            if overlap > 0:
                matched_memories.append({
                    "type": "interaction",
                    "call_id": call.get("call_id"),
                    "title": call.get("title"),
                    "date": call.get("date"),
                    "attendees": call.get("attendees"),
                    "summary": call.get("summary"),
                    "key_takeaways": call.get("key_takeaways"),
                    "relevance_score": overlap
                })

        for comm in self.commitments:
            text = f"{comm.get('title', '')} {comm.get('recipient', '')} {comm.get('status', '')} {comm.get('status_notes', '')}"
            words = text.lower().split()
            overlap = sum(1 for t in tokens if t in words or any(t in w for w in words))
            matched_memories.append({
                "type": "commitment",
                "id": comm.get("id"),
                "title": comm.get("title"),
                "recipient": comm.get("recipient"),
                "status": comm.get("status"),
                "status_notes": comm.get("status_notes"),
                "call_ref": comm.get("call_ref"),
                "relevance_score": overlap + 1
            })

        matched_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        return matched_memories[:top_k]

    def update_commitment_status(self, commitment_id: str, new_status: str, notes: str) -> bool:
        """
        Dynamically updates a commitment's status in memory and records the reflection.
        Crucial for demonstrating Hindsight's real-time memory mutation.
        """
        updated = False
        for comm in self.commitments:
            if comm["id"] == commitment_id:
                old_status = comm["status"]
                comm["status"] = new_status
                comm["status_notes"] = notes
                comm["last_updated"] = datetime.now().isoformat()
                updated = True
                
                # Retain this critical state change into Hindsight memory
                reflection_text = (
                    f"COMMITMENT STATE CHANGE: '{comm['title']}' for recipient '{comm['recipient']}' "
                    f"changed from [{old_status}] to [{new_status}]. Note: {notes}"
                )
                self.retain(content=reflection_text, category="commitment_update", metadata={"commitment_id": commitment_id})
                break
        return updated

    def mark_soc2_sent(self) -> Dict[str, Any]:
        """
        Helper method specifically for the hackathon demo climax.
        Marks COMM-02 (SOC-2 Type II Report) as Delivered/Sent.
        """
        success = self.update_commitment_status(
            commitment_id="COMM-02",
            new_status="Completed",
            notes="Audited SOC-2 Type II report delivered to Nadia Chen (Security) via encrypted portal. Security review unlocked."
        )
        return {
            "success": success,
            "commitment_id": "COMM-02",
            "new_status": "Completed",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    def get_all_context(self) -> Dict[str, Any]:
        """Returns the full memory snapshot for LLM prompting."""
        return {
            "metadata": self.metadata,
            "stakeholders": self.stakeholders,
            "commitments": self.commitments,
            "interactions": self.interactions,
            "company_kb": self.company_kb,
            "recent_audit_events": self.memory_audit_log[-5:]
        }

    # ------------------------------------------------------------------
    # Member 1: Deal Memory Ingestion & Pre-Call Intelligence
    # ------------------------------------------------------------------

    def seed_deal_memory(self) -> Dict[str, Any]:
        """
        Member 1 — Ingestion Pipeline.

        Seeds the Hindsight memory bank by calling retain() on every
        interaction, stakeholder sensitivity, and commitment loaded from
        data/acme_deal.json.  Idempotent: re-seeding only appends new
        audit entries; it does not duplicate cloud-side data because
        Hindsight deduplicates on content + context.

        Returns a summary dict with counts for UI feedback.
        """
        seeded_interactions = 0
        seeded_stakeholders = 0
        seeded_commitments = 0

        # --- Seed all interactions ---
        for call in self.interactions:
            content_parts = [
                f"[CALL {call.get('call_id')}] {call.get('title')} — {call.get('date')}.",
                f"Attendees: {', '.join(call.get('attendees', []))}.",
                f"Summary: {call.get('summary', '')}",
                "Key takeaways: " + " | ".join(call.get("key_takeaways", [])),
            ]
            content = " ".join(content_parts)
            self.retain(
                content=content,
                category="interaction",
                metadata={
                    "call_id": call.get("call_id"),
                    "title": call.get("title"),
                    "date": call.get("date"),
                    "attendees": call.get("attendees", []),
                },
            )
            seeded_interactions += 1

        # --- Seed stakeholder sensitivities ---
        for stakeholder in self.stakeholders:
            concerns_str = "; ".join(stakeholder.get("concerns", []))
            content = (
                f"[STAKEHOLDER] {stakeholder['name']} ({stakeholder['title']}, {stakeholder['role']}). "
                f"Sentiment: {stakeholder['sentiment']}. "
                f"Key concerns and sensitivities: {concerns_str}."
            )
            self.retain(
                content=content,
                category="stakeholder_sensitivity",
                metadata={
                    "name": stakeholder["name"],
                    "role": stakeholder["role"],
                    "sentiment": stakeholder["sentiment"],
                },
            )
            seeded_stakeholders += 1

        # --- Seed commitments ---
        for commitment in self.commitments:
            content = (
                f"[COMMITMENT {commitment['id']}] '{commitment['title']}' "
                f"promised by {commitment['promised_by']} to {commitment['recipient']} "
                f"(ref: {commitment.get('call_ref', 'N/A')}, promised: {commitment.get('date_promised', 'N/A')}). "
                f"Current status: {commitment['status']}. "
                f"Notes: {commitment.get('status_notes', '')}."
            )
            self.retain(
                content=content,
                category="commitment",
                metadata={
                    "id": commitment["id"],
                    "status": commitment["status"],
                    "recipient": commitment["recipient"],
                },
            )
            seeded_commitments += 1

        summary = {
            "seeded_interactions": seeded_interactions,
            "seeded_stakeholders": seeded_stakeholders,
            "seeded_commitments": seeded_commitments,
            "total_retained": seeded_interactions + seeded_stakeholders + seeded_commitments,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
        return summary

    def generate_pre_call_brief(self) -> Dict[str, Any]:
        """
        Member 1 — Pre-Call Intelligence Engine.

        1. Calls recall() with high-signal queries to surface the most
           relevant memories about stakeholder objections, pricing
           pressure, security blockers, and competitive threats.
        2. Passes the retrieved memories + full deal context into the
           Groq LLM using the prompt template from prompts.py.
        3. Parses the JSON response into a PreCallBrief Pydantic model
           (or a plain dict as fallback).
        4. Returns the brief as a dict, ready for Streamlit to render.

        Raises RuntimeError if GROQ_API_KEY is not set.
        """
        from prompts import PRE_CALL_BRIEF_SYSTEM_PROMPT, build_pre_call_brief_prompt

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key or groq_api_key == "your_groq_api_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file. "
                "Get a free key at https://console.groq.com"
            )

        # --- Multi-query recall to pull the most relevant memories ---
        recall_queries = [
            "stakeholder objections budget security timeline",
            "SOC-2 compliance security blocker Nadia commitment",
            "NimbusAI competitor price 48000 Linda budget ceiling",
            "deployment timeline 4 6 weeks October freeze Marcus",
            "procurement Owen discount concession Friday deadline",
        ]
        recalled = []
        seen_ids = set()
        for query in recall_queries:
            results = self.recall(query=query, top_k=4)
            for r in results:
                uid = r.get("call_id") or r.get("id")
                if uid not in seen_ids:
                    seen_ids.add(uid)
                    recalled.append(r)

        # --- Build the structured prompt ---
        user_prompt = build_pre_call_brief_prompt(
            recalled_memories=recalled,
            stakeholders=self.stakeholders,
            commitments=self.commitments,
            deal_metadata=self.metadata,
            company_kb=self.company_kb,
        )

        # --- Call Groq LLM ---
        try:
            from groq import Groq
        except ImportError:
            raise RuntimeError("groq package not installed. Run: pip install groq")

        client = Groq(api_key=groq_api_key)
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": PRE_CALL_BRIEF_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=3500,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "pre_call_brief",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "headline": {
                                "type": "string"
                            },
                            "stakeholder_sensitivities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "role": {"type": "string"},
                                        "sensitivity": {"type": "string"},
                                        "recommended_approach": {"type": "string"}
                                    },
                                    "required": ["name", "role", "sensitivity", "recommended_approach"],
                                    "additionalProperties": False
                                }
                            },
                            "competitor_intelligence": {
                                "type": "object",
                                "properties": {
                                    "competitor": {"type": "string"},
                                    "their_offer": {"type": "string"},
                                    "our_differentiators": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "battle_card_tip": {"type": "string"}
                                },
                                "required": ["competitor", "their_offer", "our_differentiators", "battle_card_tip"],
                                "additionalProperties": False
                            },
                            "open_commitments_at_risk": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "commitment": {"type": "string"},
                                        "recipient": {"type": "string"},
                                        "status": {"type": "string"},
                                        "risk": {"type": "string"}
                                    },
                                    "required": ["commitment", "recipient", "status", "risk"],
                                    "additionalProperties": False
                                }
                            },
                            "winning_tactics": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "one_sentence_coaching_tip": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "headline",
                            "stakeholder_sensitivities",
                            "competitor_intelligence",
                            "open_commitments_at_risk",
                            "winning_tactics",
                            "one_sentence_coaching_tip"
                        ],
                        "additionalProperties": False
                    }
                }
            },
        )

        raw_json = response.choices[0].message.content

        # --- Parse into Pydantic model or plain dict ---
        try:
            brief_dict = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"LLM returned non-JSON content: {exc}\nRaw: {raw_json[:300]}")

        if PYDANTIC_AVAILABLE and PreCallBrief is not None:
            try:
                brief = PreCallBrief(**brief_dict)
                return brief.model_dump()
            except Exception:
                # If schema mismatch, return the raw dict with a warning flag
                brief_dict["_schema_warning"] = "Response did not match PreCallBrief schema; returning raw dict."
                return brief_dict

        return brief_dict


# Singleton memory instance for runtime sharing
deal_memory = DealMemoryBank()
