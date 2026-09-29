# I built an agent that checks its own past promises before replying

The problem wasn't in the code. It was in the conversation — a SOC-2 report promised 31 days ago, never delivered, and completely absent from the context window of anyone about to send a commercial reply.

That gap between what was said and what was done is exactly the kind of thing that sinks enterprise deals. And it's exactly the kind of thing a generation step, given only the current incoming message, has no way to detect on its own. The information exists. It just isn't there when it's needed.


So I built a system that retrieves it first.

## What the system does

Foresight is a deal intelligence assistant for enterprise B2B sales. The core idea: before generating any response to a customer request, the system retrieves the relevant history of the deal from an indexed memory bank and checks the incoming request against what's already been established. Not a summary. Not a CRM note passed in as a string. An indexed, queryable memory store — backed by [Hindsight](https://github.com/vectorize-io/hindsight) — that holds every interaction, every stakeholder commitment, and every policy constraint recorded across the deal lifecycle.

The scenario we built around is deliberately messy: an eight-week enterprise deal between a vendor (Veridian) and a customer (ACME Corp), five stakeholders with conflicting priorities, nine recorded interactions, and a Friday vendor-decision deadline. When ACME sends the message "Can you give us 40% off and get us live into production in two weeks?", the system doesn't immediately draft a reply. It first runs a Collision Check — a structured cross-reference of the incoming request against retrieved deal memory and company policy.

The result is three graded collision cards:

- 🔴 **Security Blocker**: A SOC-2 Type II report was promised to Nadia Chen (CISO) 31 days ago. No fulfilment is recorded. Nadia explicitly made this a hard prerequisite for any production access.
- 🟠 **Timeline Conflict**: The 2-week deployment request conflicts with a 4–6 week baseline confirmed by Veridian's Solutions Architect in Call #3. Marcus (Principal Architect) also noted a hard October 15 production freeze in that same call.
- 🟡 **Commercial Alignment**: 40% off a $72,000 ARR quote is $43,200. Linda (CFO) set a hard $50,000 ceiling in Call #4. The rep's unilateral discount authority is capped at 15% ($61,200 floor). Competitor NimbusAI is at $48,000. The actual defensible range is $48,000–$50,000 — not a 40% concession.

The system surfaces each collision with verbatim evidence citations from indexed memory: which call it came from, who said it, what the current commitment status is, and what the company policy says. The recommendation the system generates is a direct function of that state — not a free-form LLM opinion.

## The memory layer is the core design decision

The thing that makes this work is treating deal memory as a first-class object, not a string you pass into a prompt.

I used [Hindsight](https://hindsight.vectorize.io/) as the memory backend. Hindsight exposes two primitives: `retain()` to write observations into the memory bank, and `recall()` to retrieve relevant context. The separation matters — as [agent memory architectures](https://vectorize.io/what-is-agent-memory) that cleanly split storage from retrieval tend to give you more control over what ends up in the context window and when.

The ingestion pipeline seeds all nine interactions, five stakeholder profiles, and three tracked commitments into memory at session start:

```python
# memory.py — seed_deal_memory()
for call in self.interactions:
    content_parts = [
        f"[CALL {call.get('call_id')}] {call.get('title')} — {call.get('date')}.",
        f"Attendees: {', '.join(call.get('attendees', []))}.",
        f"Summary: {call.get('summary', '')}",
        "Key takeaways: " + " | ".join(call.get("key_takeaways", [])),
    ]
    self.retain(
        content=" ".join(content_parts),
        category="interaction",
        metadata={"call_id": call.get("call_id"), "date": call.get("date")},
    )
```

Each `retain()` call logs to a local audit trail and, when a Hindsight API key is configured, pushes to the cloud memory bank. The system runs in hybrid mode: cloud-backed retrieval when the key is available, local token-overlap scoring as a fallback. The fallback is functional but limited — it scores by keyword overlap, which can miss paraphrased queries. It's a development convenience, not a production strategy.

For the pre-call brief, the system fires five targeted queries against Hindsight rather than a single catch-all query:

```python
# memory.py — generate_pre_call_brief()
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
```

These queries are manually specified — each one is targeted at a specific dimension of the deal: security, timeline, commercial, competitive, procurement. Deduplication by ID prevents the same call from appearing multiple times when it matches several queries. What comes out of this is the set of memories that actually goes into the LLM prompt — not a raw dump of all nine interactions.

## Commitments as mutable state

The second design decision I'm glad we made explicitly: commitments are tracked as structured mutable objects, not static text.

Each commitment carries an ID, a status, a recipient, a call reference, and a date. When the SOC-2 report is finally delivered, we don't patch a prompt string. We call `update_commitment_status()`, which mutates the commitment in `self.commitments`, records a structured reflection event via `retain()`, and causes every downstream check to re-evaluate against the new state:

```python
# memory.py — update_commitment_status()
def update_commitment_status(self, commitment_id: str, new_status: str, notes: str) -> bool:
    for comm in self.commitments:
        if comm["id"] == commitment_id:
            old_status = comm["status"]
            comm["status"] = new_status
            comm["status_notes"] = notes
            comm["last_updated"] = datetime.now().isoformat()

            reflection_text = (
                f"COMMITMENT STATE CHANGE: '{comm['title']}' for recipient '{comm['recipient']}' "
                f"changed from [{old_status}] to [{new_status}]. Note: {notes}"
            )
            self.retain(
                content=reflection_text,
                category="commitment_update",
                metadata={"commitment_id": commitment_id}
            )
            return True
    return False
```

The important distinction here: `self.commitments` is the live application state. Hindsight is where the audit trail lives. The `retain()` call after the mutation means the change event is also indexed as a retrievable memory — so a future `recall()` query will surface not just the original promise, but the fact that it was fulfilled and when.

This is the behavior we were optimizing for. The mutable commitment state drives the recommendation logic. The LLM doesn't decide what's true — it reasons from what's already established in memory.

## What the collision detector actually checks

The collision engine is deliberately deterministic. It doesn't ask an LLM whether the incoming request conflicts with deal history. It checks specific conditions directly.

```python
# tanmaya/collision_detector.py — check_collisions()
soc2_comm = next((c for c in commitments if c.get("id") == "COMM-02"), None)
is_soc2_completed = soc2_comm and soc2_comm.get("status") == "Completed"

req_lower = customer_request.lower()
has_discount_request = any(k in req_lower for k in ["40%", "discount", "price", "cheaper", "cost", "off"])
has_two_week_request = any(k in req_lower for k in ["two weeks", "2 weeks", "two-week", "2-week", "14 days"])
```

The security check looks up COMM-02 by ID and reads its `status` field directly. The timeline and discount checks are keyword matches against the lowercased request string. Each collision rule is self-contained and adds one entry to the collision list. Policy constraints — discount authority tiers, deployment minimums — come from a structured JSON knowledge base that feeds the detector separately from the memory bank. When policy changes, one file changes and every future check reflects it.

The approach is auditable precisely because it's not opaque inference. You can read the collision list and trace every item back to a commit status, a keyword match, or a policy value. That traceability is the point.

## How it behaves in practice

Before the SOC-2 has been delivered: the customer sends "Can you give us 40% off and get us live into production in two weeks?" The collision check surfaces three conflicts with evidence citations. The recommended action the system generates is explicit: do not agree to any deployment date or pricing concession until the SOC-2 is delivered. The reply draft reflects this — it cites the security prerequisite honestly, references the 4–6 week baseline from Call #3, and proposes aligning within Linda's $50,000 budget ceiling.

After `mark_soc2_sent()` is called:

- COMM-02 status changes to `Completed` in `self.commitments`
- The state change is recorded via `retain()` with category `commitment_update`
- The collision check re-evaluates against the new commitment state
- The 🔴 Security Blocker resolves to ✅ Security Cleared
- The recommended action shifts to: proceed with commercial negotiation, target $49,000 ARR, propose a 3–4 week phased rollout, close before Friday

The generated reply draft changes completely — from one that stops the conversation to one that closes it. The collision logic is deterministic Python; the final reply is generated by the LLM against the updated context. Same prompt template structure, different underlying state, different output.

That's the whole system. Structured memory state drives what the collision layer detects. The collision layer drives what the LLM is asked to communicate.

## What I'd do differently in production

A few things I'd want to harden before running this against live deal data:

**1. The local recall fallback needs an explicit degradation warning.** Token overlap scoring works for keyword-heavy queries but silently misses paraphrased content. In production, the local path should emit a clear warning rather than substituting quietly. The cloud-backed retrieval via Hindsight is the correct default; the fallback is a development aid.

**2. Commitment IDs shouldn't be hardcoded.** The collision detector references `"COMM-02"` directly. In a system managing multiple deals in parallel, you'd query commitments by type and recipient. The data model supports this already — the execution logic just doesn't use it yet.

**3. The LLM output contract needs tighter enforcement.** Groq's JSON schema mode is used for the pre-call brief, which helps significantly. The system prompt instructs the model to say "No record in memory" rather than invent plausible answers — but that instruction needs to be reinforced by the schema shape and by post-generation validation. The current enforcement could be stricter.

**4. Memory retention should be event-driven.** The current implementation seeds all deal history at session start as a bulk import. In production, `retain()` should be called when meaningful events occur: a call ends, a commitment is made, a stakeholder changes position. Hindsight supports incremental retention; it's a wiring decision in this implementation, not a capability gap.

**5. The audit log is your best debugging surface.** Every `retain()` call appends to `memory_audit_log`. During development, this was the most useful tool when the collision detector produced an unexpected result — the log showed exactly what was in memory and when each entry arrived. In production, this should be queryable, filterable, and persistent across sessions.

---

The engineering lesson here isn't specific to sales. It applies anywhere you have long-running state that accumulates over time: incident response, contract review, engineering design discussions, support escalations.

An agent that only has access to its training weights and the current message is unreliable whenever history is relevant. The fix isn't a better model. It's structured memory — the ability to `retain()` what happened, `recall()` what's relevant, and check the incoming request against that history before generating a single word of output.

`retain()` records what happened. `recall()` retrieves what matters. The collision layer checks the new request against it. The LLM communicates from the resulting evidence. That ordering is what separates a grounded response from a confident hallucination.
