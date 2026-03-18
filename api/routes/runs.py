import re
from fastapi import APIRouter, HTTPException
from api.models import RunRequest, RunResponse, EvalResult
from api.providers.ollama import OllamaProvider
from api.providers.claude import ClaudeProvider
from api.evaluators.metrics import compute_metrics
from api.mlflow_client import log_run, get_or_create_experiment
from api.config import settings

router = APIRouter()


def _resolve_provider(model: str):
    """Route a model name to the correct provider."""
    claude_models = {"claude-haiku-4-5-20251001", "claude-sonnet-4-6"}
    if model in claude_models:
        if not settings.anthropic_api_key:
            raise HTTPException(
                status_code=400,
                detail=f"Model '{model}' requires ANTHROPIC_API_KEY to be set in .env",
            )
        return ClaudeProvider(), "claude"
    return OllamaProvider(), "ollama"


def _fill_template(template: str, variables: dict) -> str:
    """Replace {{variable}} placeholders in a prompt template."""
    result = template
    for key, value in variables.items():
        result = re.sub(r"\{\{" + re.escape(key) + r"\}\}", str(value), result)
    return result


@router.post("/", response_model=RunResponse)
async def create_run(request: RunRequest):
    """
    Execute a prompt experiment across one or more models.

    Each (model, input) combination is logged as a separate MLflow run.
    Returns all results with metrics and MLflow run IDs for reference.
    """
    models = request.models if request.models else settings.default_model_list
    if not models:
        raise HTTPException(status_code=400, detail="No models specified and DEFAULT_MODELS is not set.")

    experiment_id = get_or_create_experiment(request.experiment_name)
    results: list[EvalResult] = []

    for variables in request.inputs:
        prompt = _fill_template(request.prompt_template, variables)

        for model in models:
            provider, provider_name = _resolve_provider(model)

            try:
                output, latency_ms = await provider.generate(model, prompt)
            except Exception as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Provider error for model '{model}': {e}",
                )

            metrics = compute_metrics(output, prompt, latency_ms)

            run_id = log_run(
                experiment_name=request.experiment_name,
                model=model,
                provider=provider_name,
                prompt=prompt,
                output=output,
                metrics=metrics,
                tags=request.tags,
            )

            results.append(
                EvalResult(
                    model=model,
                    prompt=prompt,
                    output=output,
                    latency_ms=metrics["latency_ms"],
                    token_count_estimate=metrics["token_count_estimate"],
                    quality_score=metrics["quality_score"],
                    mlflow_run_id=run_id,
                )
            )

    # Summary: best quality score and fastest model
    best_quality = max(results, key=lambda r: r.quality_score)
    fastest = min(results, key=lambda r: r.latency_ms)

    return RunResponse(
        experiment_name=request.experiment_name,
        experiment_id=experiment_id,
        results=results,
        summary={
            "total_runs": len(results),
            "best_quality_model": best_quality.model,
            "best_quality_score": best_quality.quality_score,
            "fastest_model": fastest.model,
            "fastest_latency_ms": fastest.latency_ms,
        },
    )
