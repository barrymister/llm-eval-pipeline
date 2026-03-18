# Exercises — llm-eval-pipeline

Hands-on exercises mapped to AWS ML Engineer (MLA-C01) and Google ML Engineer cert exam domains.

Work through these while the stack is running. Each exercise references actual code in the repo.

---

## Exercise 1 — Write an Experiment YAML

**Cert domain:** AWS Data Preparation (28%) | Google Data Prep

**Task:**

Without looking at `experiments/example.yaml`, write a new YAML file from scratch for this scenario:

> You want to compare `gemma3:12b` and `mistral-small3.2` on a customer support task. The task: given a customer complaint, write a polite, solution-oriented response. Test it with two different complaint types.

Save it as `experiments/support-comparison.yaml` and run it:
```bash
python scripts/run_experiment.py experiments/support-comparison.yaml
```

**Questions to answer:**
1. What is the difference between `prompt_template` and `inputs`? Which one stays the same across all runs, and which one varies?
2. If you add a third model to `models`, how many total MLflow runs will be created?
3. Where in the codebase does `{{topic}}` get replaced with the actual value? (Hint: look at `api/routes/runs.py` → `_fill_template()`)

---

## Exercise 2 — Read MLflow Results

**Cert domain:** AWS Model Development (26%) | Google Model Development

**Prerequisites:** Run `python scripts/run_experiment.py experiments/example.yaml` first.

**Task:** Open the MLflow UI at `http://localhost:5000`. Find the `writing-quality-comparison` experiment.

**Questions to answer:**
1. Which model had the lower average `latency_ms`? By how much?
2. What does `quality_score` measure? Open `api/evaluators/metrics.py` and read the four signals it checks. What are the limits of this metric — when would it give a high score to a bad output?
3. MLflow stores the raw model output as an **artifact**. Click into any run and find it. What format is it in?
4. In the Compare view, which metric would you use to pick the "best" model for a latency-sensitive production system? Which for a quality-sensitive system?

---

## Exercise 3 — Cross-Cloud MLOps Mapping

**Cert domain:** AWS Deployment & Orchestration (22%) | AWS Monitoring (24%) | Google Pipeline Automation

**Task:** Fill in this table from memory, then verify by reading `api/mlflow_client.py` and the README's MLOps mapping table.

| This project | AWS SageMaker equivalent | Google Vertex AI equivalent | Azure ML equivalent |
|---|---|---|---|
| `mlflow.create_experiment()` | | | |
| `mlflow.start_run()` | | | |
| `mlflow.log_param()` | | | |
| `mlflow.log_metric()` | | | |
| `mlflow.log_artifact()` | | | |
| MLflow Model Registry | | | |

**Questions to answer:**
1. In SageMaker, what is the difference between an **Experiment** and a **Trial**? How does that map to MLflow's experiment/run hierarchy?
2. In Vertex AI, what service replaces MLflow's artifact store? Where do artifacts physically live when using Vertex AI Experiments?
3. On the AWS ML cert, a question asks: "You need to compare 5 training configurations and track hyperparameters, metrics, and model artifacts. Which service should you use?" What's the answer and why?

---

## Exercise 4 — Trace the Code

**Cert domain:** AWS Model Development (26%) | Google Model Development

**Task:** Trace what happens when you call `POST /runs/` with this request:

```json
{
  "experiment_name": "test",
  "prompt_template": "Explain {{topic}}.",
  "inputs": [{"topic": "neural networks"}],
  "models": ["gemma3:12b", "claude-haiku-4-5-20251001"]
}
```

Starting from `api/routes/runs.py`, follow the code path for each model:

1. Which function decides whether to use OllamaProvider or ClaudeProvider?
2. What happens if `ANTHROPIC_API_KEY` is not set in `.env` and you request a Claude model?
3. For `gemma3:12b`, what HTTP call does `OllamaProvider.generate()` make? (Look at `api/providers/ollama.py`)
4. Where is the result logged to MLflow? Which function in `api/mlflow_client.py` does the logging?

**Extension:** The current API returns HTTP 502 if a provider call fails. What would you change to make the failure non-fatal — so a failed model doesn't block results from other models in the same run?

---

## Exercise 5 — Extend the System

**Cert domain:** AWS Monitoring & Maintenance (24%) | Google Monitoring

**Task:** The `RunResponse` currently returns `best_quality_model` and `fastest_model` in the summary. Add `worst_quality_model` (the model with the lowest quality_score) to the summary.

Find where to make the change in `api/routes/runs.py`. You don't need to run it — just identify the exact lines and write the change.

**Questions to answer:**
1. In a production SageMaker environment, what service would you use to detect if model quality is degrading over time — not just in a one-off test? What baseline does it compare against?
2. This project uses heuristic quality scores. In a real production system, what are two alternative approaches to automated output quality measurement? What are the trade-offs of each?
3. If you wanted to set an alert when `quality_score` drops below 0.7 on any run, how would you implement that? Where in the codebase would the check go?
