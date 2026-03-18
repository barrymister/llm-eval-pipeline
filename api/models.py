from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    experiment_name: str = Field(..., description="MLflow experiment name")
    prompt_template: str = Field(
        ...,
        description="Prompt template with {{variable}} placeholders",
        examples=["Summarize {{topic}} for a {{audience}} audience in 3 sentences."],
    )
    inputs: list[dict] = Field(
        ...,
        description="List of variable dictionaries to fill prompt_template",
        examples=[[{"topic": "machine learning", "audience": "executive"}]],
    )
    models: list[str] = Field(
        default=[],
        description="Model names to evaluate. Defaults to DEFAULT_MODELS env var.",
    )
    tags: dict[str, str] = Field(
        default={},
        description="Optional key-value tags logged to MLflow",
    )


class EvalResult(BaseModel):
    model: str
    prompt: str
    output: str
    latency_ms: float
    token_count_estimate: int
    quality_score: float
    mlflow_run_id: str


class RunResponse(BaseModel):
    experiment_name: str
    experiment_id: str
    results: list[EvalResult]
    summary: dict


class ExperimentInfo(BaseModel):
    experiment_id: str
    name: str
    lifecycle_stage: str
    run_count: int
