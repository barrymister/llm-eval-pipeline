# llm-eval-pipeline

Compare LLM outputs across models and prompt variants with automatic MLflow experiment tracking.

Self-hostable via Docker Compose. Works out of the box with local Ollama inference — no cloud API required.

---

## What it does

- **Run experiments**: Submit a prompt template + variable inputs + list of models → get back scored results for each combination
- **Track everything**: Every run logged to MLflow — model, prompt, output, latency, quality score, token count
- **Compare runs**: Open the MLflow dashboard to compare models side by side, identify regressions, and reproduce the best results
- **Provider-agnostic**: Ollama (local GPU inference) out of the box. Claude API available as an optional comparison baseline. Add new providers with a single file.

---

## Why this exists

Running production AI systems means making decisions under uncertainty: *Is gemma3 or mistral giving better outputs on this task? Did my prompt change improve or hurt quality? Which model should I use for this use case?*

Without experiment tracking, the answer is "I think the new version is better" based on anecdotal testing. With MLflow, every comparison is logged, reproducible, and comparable.

This project demonstrates the MLOps patterns used at production scale — the same patterns that SageMaker Experiments, Vertex AI Experiments, and Azure ML track on managed infrastructure.

---

## Quick start

**Prerequisites:** Docker + Docker Compose. Ollama running locally with at least one model pulled.

```bash
git clone https://github.com/barrymister/llm-eval-pipeline.git
cd llm-eval-pipeline

cp .env.example .env
# Edit .env: set OLLAMA_BASE_URL and DEFAULT_MODELS

docker-compose up -d
```

- **MLflow UI**: http://localhost:5000
- **API docs**: http://localhost:8000/docs

### Run your first experiment

```bash
# Using the CLI runner (requires pyyaml: pip install pyyaml)
python scripts/run_experiment.py experiments/example.yaml

# Or call the API directly
curl -X POST http://localhost:8000/runs/ \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_name": "my-first-experiment",
    "prompt_template": "Explain {{topic}} in one sentence for a {{audience}}.",
    "inputs": [{"topic": "containerization", "audience": "non-technical manager"}],
    "models": ["gemma3:12b", "mistral-small3.2"]
  }'
```

Then open http://localhost:5000 to see the logged runs.

---

## Project structure

```
llm-eval-pipeline/
├── docker-compose.yml          # MLflow server + PostgreSQL + FastAPI API
├── Dockerfile                  # API container
├── requirements.txt
├── api/
│   ├── main.py                 # FastAPI entrypoint
│   ├── config.py               # Settings from .env
│   ├── models.py               # Pydantic request/response schemas
│   ├── mlflow_client.py        # MLflow experiment/run logging
│   ├── providers/
│   │   ├── base.py             # Abstract provider interface
│   │   ├── ollama.py           # Local Ollama inference adapter
│   │   └── claude.py           # Claude API adapter (optional)
│   ├── evaluators/
│   │   └── metrics.py          # Latency, quality score, token count
│   └── routes/
│       ├── experiments.py      # GET /experiments
│       └── runs.py             # POST /runs
├── experiments/
│   └── example.yaml            # Example experiment definition
├── scripts/
│   └── run_experiment.py       # CLI runner for experiment YAMLs
└── docs/
    └── ARCHITECTURE.md         # Design decisions and trade-offs
```

---

## Configuration

Copy `.env.example` to `.env`:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `DEFAULT_MODELS` | `gemma3:12b,mistral-small3.2` | Models to use when none specified |
| `ANTHROPIC_API_KEY` | *(empty)* | Optional — enables Claude provider |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow server (set by docker-compose) |

---

## API reference

### `POST /runs/`

Run an experiment across models and inputs. Each combination is logged as a separate MLflow run.

**Request:**
```json
{
  "experiment_name": "summarization-comparison",
  "prompt_template": "Summarize {{topic}} for a {{audience}} in 3 sentences.",
  "inputs": [
    {"topic": "machine learning", "audience": "executive"},
    {"topic": "containerization", "audience": "product manager"}
  ],
  "models": ["gemma3:12b", "mistral-small3.2"],
  "tags": {"task_type": "summarization"}
}
```

**Response:**
```json
{
  "experiment_name": "summarization-comparison",
  "experiment_id": "1",
  "results": [
    {
      "model": "gemma3:12b",
      "prompt": "Summarize machine learning for a executive in 3 sentences.",
      "output": "...",
      "latency_ms": 1842.3,
      "token_count_estimate": 87,
      "quality_score": 0.891,
      "mlflow_run_id": "abc123..."
    }
  ],
  "summary": {
    "total_runs": 4,
    "best_quality_model": "gemma3:12b",
    "best_quality_score": 0.891,
    "fastest_model": "mistral-small3.2",
    "fastest_latency_ms": 1203.1
  }
}
```

### `GET /experiments/`

List all MLflow experiments with run counts.

---

## Adding a new provider

1. Create `api/providers/your_provider.py` implementing `BaseProvider` (`name`, `generate`, `list_models`)
2. Register the model name prefix in `api/routes/runs.py` → `_resolve_provider()`
3. Add to `.env.example` if it needs credentials

Example: adding AWS Bedrock, Azure OpenAI, or Vertex AI each requires only one new file.

---

## MLflow concepts demonstrated

This project is a hands-on implementation of the MLOps patterns that AWS, Google, and Microsoft test in their ML engineering certifications:

| This project | AWS (SageMaker) | Google (Vertex AI) | Azure (ML Studio) |
|---|---|---|---|
| `mlflow.create_experiment()` | SageMaker Experiment | Vertex AI Experiment | Azure ML Experiment |
| `mlflow.start_run()` | Trial Component | Experiment Run | Azure ML Run |
| `mlflow.log_param()` | Hyperparameter config | Run parameter | Run parameter |
| `mlflow.log_metric()` | Metric definition | Run metric | Run metric |
| `mlflow.log_artifact()` | S3 artifact store | GCS artifact | Blob artifact |
| MLflow Model Registry | SageMaker Model Registry | Vertex AI Model Registry | Azure ML Model Registry |

---

## Infrastructure

Deployed on a self-hosted home server (appfactory):
- MLflow UI: https://mlflow.barrymister.dev
- API: https://llm-eval.barrymister.dev/docs
- Local GPU inference via Ollama (gemma3:12b, mistral-small3.2)
- Docker Compose managed by Coolify PaaS

---

## License

MIT — use freely, attribution appreciated.
