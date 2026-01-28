## Adapting the Design for No Internet Access

In the current POC, the backend is deployed on Railway and uses a hosted LLM (Google Gemini) through a clear abstraction layer. The core data plane (KB markdown files, embeddings, vector store, tickets, metrics) is already local to the backend and does not depend on external HTTP calls beyond the LLM itself. To run in a no‑internet, internal‑only environment, we would:

- Deploy the FastAPI backend, Postgres/pgvector database, and KB/ingestion jobs entirely inside the private network.
- Ensure all KB content and embeddings are stored in internal storage (already true in the current design).
- Remove any outbound network dependencies from the chatbot flow other than the LLM provider; all RAG retrieval, tiering, guardrails, and analytics already execute locally.
- Replace environment configuration that currently points to public Railway/Vercel endpoints with internal URLs or service discovery inside the cluster.

Because the architecture cleanly separates “LLM provider” from the rest of the system and does not allow web-search/tool-using models, the move to a fully air‑gapped deployment is primarily an infrastructure and configuration change rather than a redesign of business logic.

## Adapting the Design for No External LLM (Self-Hosted Only)

The backend encapsulates LLM interaction behind a provider abstraction, and the RAG engine passes only: user message, retrieved KB chunks, and metadata. To support a self‑hosted model (e.g., Llama, Mistral, or other on‑prem models), we would:

- Implement a new LLM provider module that calls a self‑hosted inference endpoint (HTTP or gRPC) instead of a cloud API.
- Keep the same prompt contract and output schema so that downstream components (tiering, guardrails, analytics, and frontend) remain unchanged.
- Tune the prompt and max‑token settings for the on‑prem model so that it stays strictly KB‑grounded; the same guardrail checks and “not in KB” behavior continue to apply.
- Optionally, introduce CPU/GPU‑aware batching at the provider layer to make model usage efficient under higher concurrency without touching the chat API contract.

Because all KB retrieval, tiering decisions, and escalation logic are deterministic and independent from the specific LLM vendor, the swap from an external hosted LLM to a self‑hosted one is localized to a single integration point.

## Adapting the Design for CPU-Only Hardware

Running entirely on CPU requires careful attention to model size, latency, and throughput. The current design already helps by separating retrieval from generation and by using a database‑backed vector store. To adapt for CPU‑only environments, we would:

- Use a smaller, CPU‑friendly embedding model (or reuse precomputed embeddings and avoid online re‑embedding during normal chat flow).
- Choose a compact instruction‑tuned LLM (e.g., a 7B‑class model with quantization) behind the provider abstraction to keep per‑request latency acceptable on CPU.
- Rely even more heavily on RAG: retrieve a small, high‑quality context window so that the LLM has less to process per call.
- Introduce simple caching for frequent queries or common KB question patterns to avoid repeated generation when possible.
- Adjust non‑critical paths (e.g., some analytics aggregation) to run asynchronously or in scheduled jobs so that CPU is prioritized for user‑visible chat traffic.

These adaptations keep the user‑facing behavior and API contract the same while making the computational profile realistic for CPU‑only deployments.

## POC vs. Full Production: Trade-Offs

For this POC, I intentionally made several trade‑offs to balance completeness with delivery speed:

- **Operational Hardening**: The system has structured logging, basic error handling, and metrics, but does not yet include production‑grade alerting, SLO dashboards, or full runbooks for every failure mode.
- **Security & Compliance Depth**: Guardrails enforce the key policies from the KB (no host access, no disabling logging, no destructive commands), but a full production system would add fine‑grained authorization, audit log export to a SIEM, and more formal privacy/compliance controls.
- **Scalability & Multi-Tenancy**: The architecture can scale horizontally (stateless backend + database), but the POC runs with a single logical tenant. A production build would add explicit tenant isolation, rate‑limiting per tenant, and stronger performance testing.
- **KB & Ingestion Automation**: KB ingestion is implemented and sufficient for the provided documents, but a production system would need a more robust ingestion pipeline (version tracking, approvals, rollback, and possibly a UI for KB curation).
- **Frontend Polish**: The UI fully supports the required fields (answer, confidence, KB refs, tier/severity, guardrail state, tickets, metrics), but a production UX would add more accessibility work, role‑specific dashboards, and deeper analytics views.

Overall, the POC focuses on correctness, determinism, and safety for the 12 required workflows and core policies, while leaving room to deepen operational robustness, security hardening, and scalability in a full production build.
