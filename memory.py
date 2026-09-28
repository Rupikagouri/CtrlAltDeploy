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


# Singleton memory instance for runtime sharing
deal_memory = DealMemoryBank()
