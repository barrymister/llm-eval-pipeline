# Operations Guide — llm-eval-pipeline

How to run the stack, interpret results, and extend the project.

---

## Prerequisites

- Docker + Docker Compose installed
- Ollama running locally with at least one model pulled
  ```bash
  ollama pull gemma3:12b         # recommended — best quality/speed balance
  ollama pull mistral-small3.2   # for comparison runs
  ollama pull llama3.2:3b        # lightweight option for quick tests
  ```
- (Optional) Anthropic API key if you want Claude as a comparison baseline

---

## Start the stack

```bash
git clone https://github.com/barrymister/llm-eval-pipeline.git
cd llm-eval-pipeline

cp .env.example .env
# Edit .env — set OLLAMA_BASE_URL and DEFAULT_MODELS (see Configuration below)

docker-compose up -d
```

Check it's running:
```bash
docker-compose ps        # all services should show "Up"
curl http://localhost:8000/health   # API
curl http://localhost:5000          # MLflow UI (opens in browser)
```

---

## Run your first experiment

### Option A — CLI (recommended for cert study)

```bash
pip install pyyaml requests   # one-time
python scripts/run_experiment.py experiments/example.yaml
```

This reads `experiments/example.yaml`, submits all (model × input) combinations to the API, and prints a summary table. Every run is logged to MLflow automatically.

### Option B — Direct API call

```bash
curl -X POST http://localhost:8000/runs/ \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_name": "my-test",
    "prompt_template": "Explain {{topic}} in one sentence.",
    "inputs": [{"topic": "containerization"}],
    "models": ["gemma3:12b"]
  }'
```

---

## Read the MLflow UI

Open `http://localhost:5000` (or `https://mlflow.barrymister.dev` for the live instance).

**Key concepts:**

| UI Element | What it is |
|---|---|
| **Experiment** | A named group of related runs (e.g., `writing-quality-comparison`) |
| **Run** | One (model × input) execution — logged automatically by the API |
| **Parameters** | Inputs to the run: `model`, `prompt_template`, `input_*` variable values |
| **Metrics** | Outputs measured: `latency_ms`, `quality_score`, `token_count_estimate` |
| **Artifacts** | Files stored with the run — here, the raw model output text |

**How to compare runs:**

1. Open an experiment → select 2+ runs → click **Compare**
2. The comparison view shows params and metrics side by side
3. Use the chart tab to plot `latency_ms` or `quality_score` across runs

---

## Understand the example.yaml

```yaml
experiment_name: "writing-quality-comparison"   # groups runs in MLflow

prompt_template: |
  Write a 3-sentence summary of {{topic}} for a {{audience}} audience.
  # {{ }} placeholders are filled in from inputs below

inputs:
  - topic: "machine learning"
    audience: "business executive"
  # each input dict produces one run per model

models:
  - gemma3:12b
  - mistral-small3.2
  # uncomment claude models if ANTHROPIC_API_KEY is set

tags:
  task_type: "summarization"   # free-form labels, stored in MLflow
```

Every (model × input) combination = one MLflow run. With 2 inputs and 2 models, you get 4 runs.

---

## Write a custom experiment YAML

Required fields:
- `experiment_name` — string, used as the MLflow experiment name
- `prompt_template` — string with `{{variable}}` placeholders
- `inputs` — list of dicts; each dict must have a key for every `{{variable}}` in the template
- `models` — list of model names; Ollama models use `name:tag` format

Optional:
- `tags` — dict of arbitrary key/value pairs logged to MLflow

Example — code review task:
```yaml
experiment_name: "code-review-comparison"
prompt_template: |
  Review this {{language}} code for bugs, security issues, and style problems:

  {{code_snippet}}

  List findings as numbered items.
inputs:
  - language: "Python"
    code_snippet: "def divide(a, b): return a / b"
models:
  - gemma3:12b
  - mistral-small3.2
tags:
  task_type: "code_review"
```

---

## Add a new Ollama model

1. Pull it locally:
   ```bash
   ollama pull qwen2.5:7b
   ```
2. Add it to `models` in your experiment YAML:
   ```yaml
   models:
     - gemma3:12b
     - qwen2.5:7b
   ```
3. No code change needed — the Ollama provider handles any model name automatically.

---

## Add a new provider (e.g., AWS Bedrock, Azure OpenAI)

1. Create `api/providers/your_provider.py`:
   ```python
   from api.providers.base import BaseProvider

   class BedrockProvider(BaseProvider):
       @property
       def name(self) -> str:
           return "bedrock"

       async def generate(self, model: str, prompt: str) -> tuple[str, float]:
           # call boto3 bedrock-runtime client here
           ...

       async def list_models(self) -> list[str]:
           return ["anthropic.claude-3-haiku-20240307-v1:0"]
   ```

2. Register the model prefix in `api/routes/runs.py` → `_resolve_provider()`:
   ```python
   if model.startswith("anthropic.") or model.startswith("amazon."):
       return BedrockProvider(), "bedrock"
   ```

3. Add credentials to `.env.example` and `.env`.

---

## Configuration reference

Edit `.env` (copied from `.env.example`):

| Variable | Default | What it does |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint — change if Ollama runs on another host |
| `DEFAULT_MODELS` | `gemma3:12b,mistral-small3.2` | Models used when none are specified in the request |
| `ANTHROPIC_API_KEY` | *(empty)* | Set to enable Claude provider — leave blank to use Ollama only |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | Set by docker-compose; change only if running MLflow externally |

---

## Stop and clean up

```bash
docker-compose down          # stop containers, keep data
docker-compose down -v       # stop + delete MLflow data (wipes all runs)
```
