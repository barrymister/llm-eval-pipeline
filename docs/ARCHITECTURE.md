# Architecture Decision Records

## Why MLflow instead of Weights & Biases or Neptune

**Decision:** MLflow (self-hosted) over W&B or Neptune.

**Reasoning:**
- W&B and Neptune are SaaS — data leaves your infrastructure and costs money at scale
- MLflow is open source, runs in Docker, stores everything locally
- The experiment tracking *pattern* is identical across all three — `log_param`, `log_metric`, `log_artifact` exist in all of them
- Self-hosted means zero ongoing cost and no vendor dependency
- Critically: the patterns you learn in MLflow (experiment → run → params → metrics → artifacts) map directly to SageMaker Experiments, Vertex AI Experiments, and Azure ML Experiments — all three cloud cert tracks test this same mental model

**Trade-off accepted:** No built-in collaboration features (W&B excels here). Acceptable for a solo infrastructure project.

---

## Why FastAPI instead of Flask or a plain script

**Decision:** FastAPI REST API wrapping the evaluation logic.

**Reasoning:**
- A REST API makes the tool composable — other systems can call it, not just humans
- FastAPI auto-generates OpenAPI docs at `/docs` with no extra work
- Async support handles slow LLM calls without blocking
- Pydantic models on request/response make the data contracts explicit — this mirrors how SageMaker endpoints define input/output schemas

**Trade-off accepted:** More infrastructure than a plain script. Worth it for the architectural signal and composability.

---

## Why Ollama as the default backend instead of a cloud API

**Decision:** Ollama (local inference on appfactory GPU) as the primary backend.

**Reasoning:**
- Zero marginal cost per inference — no API bills for running experiments
- GPU is already provisioned on appfactory (RTX-class, running gemma3:12b and mistral-small3.2)
- Forces the architecture to be provider-agnostic — the `BaseProvider` pattern means swapping to AWS Bedrock, Azure OpenAI, or Vertex AI requires only a new adapter file
- Claude API is available as an optional comparison baseline — useful for calibrating quality scores

**Trade-off accepted:** Results are not directly comparable to cloud API benchmarks. For the purpose of learning MLOps patterns and demonstrating the pipeline, local inference is sufficient.

---

## Why Docker Compose instead of Kubernetes

**Decision:** Docker Compose for deployment.

**Reasoning:**
- This is a single-node deployment on appfactory — Kubernetes adds operational complexity with no benefit at this scale
- Docker Compose maps cleanly to the local dev experience (same file in dev and prod)
- MLflow + PostgreSQL + FastAPI is a simple 3-service topology — well within Compose's design envelope
- If this project scales to multi-node, migrating to a Kubeflow Pipeline deployment on the same hardware is straightforward

**Trade-off accepted:** No horizontal scaling. Acceptable for a portfolio/learning project.

---

## Quality metric design

**Decision:** Lightweight heuristic quality scores instead of LLM-as-judge or embedding similarity.

**Reasoning:**
- LLM-as-judge (using a model to score another model's output) introduces circularity and additional API cost
- Embedding similarity requires a separate embedding model and adds a dependency
- The four heuristics chosen (length adequacy, completeness, non-repetition, prompt relevance) each map to a real, interpretable quality concern
- Interpretability matters: when a score drops, you can explain *which signal dropped* — this is exactly what SageMaker Model Monitor data quality constraints do

**Trade-off accepted:** Scores don't correlate perfectly with human judgment. The goal is a consistent, automatable signal for comparison — not a ground-truth quality rating.
