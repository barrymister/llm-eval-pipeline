"""
MLflow integration wrapper.

This module is the core of what trains you for the AWS ML cert.
It demonstrates the MLOps patterns the exam tests:
  - mlflow.set_experiment() → experiment management
  - mlflow.start_run() → run lifecycle
  - mlflow.log_param() → hyperparameter tracking (model name, prompt version)
  - mlflow.log_metric() → performance metrics (latency, quality)
  - mlflow.log_artifact() → storing prompt templates and full outputs
  - mlflow.register_model() → model registry and promotion workflow

AWS cert mapping:
  - Experiment = SageMaker Experiment
  - Run = SageMaker Trial Component
  - log_param = SageMaker hyperparameter config
  - log_metric = SageMaker metric definition
  - Model Registry = SageMaker Model Registry
"""

import json
import tempfile
import os
import mlflow
from api.config import settings


def get_or_create_experiment(name: str) -> str:
    """Get experiment ID, creating if it doesn't exist."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    experiment = mlflow.get_experiment_by_name(name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(name)
    else:
        experiment_id = experiment.experiment_id
    return experiment_id


def log_run(
    experiment_name: str,
    model: str,
    provider: str,
    prompt: str,
    output: str,
    metrics: dict,
    tags: dict | None = None,
) -> str:
    """
    Log a single evaluation run to MLflow.

    Returns:
        MLflow run ID for reference.
    """
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    experiment_id = get_or_create_experiment(experiment_name)

    run_tags = {"provider": provider, **(tags or {})}

    with mlflow.start_run(experiment_id=experiment_id, tags=run_tags) as run:
        # Log parameters — what we controlled
        mlflow.log_param("model", model)
        mlflow.log_param("provider", provider)
        mlflow.log_param("prompt_length_chars", len(prompt))

        # Log metrics — what we measured
        mlflow.log_metrics(metrics)

        # Log artifacts — the actual content for reference
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = os.path.join(tmpdir, "prompt.txt")
            output_path = os.path.join(tmpdir, "output.txt")
            meta_path = os.path.join(tmpdir, "meta.json")

            with open(prompt_path, "w") as f:
                f.write(prompt)
            with open(output_path, "w") as f:
                f.write(output)
            with open(meta_path, "w") as f:
                json.dump({"model": model, "provider": provider, **metrics}, f, indent=2)

            mlflow.log_artifact(prompt_path, artifact_path="run")
            mlflow.log_artifact(output_path, artifact_path="run")
            mlflow.log_artifact(meta_path, artifact_path="run")

        return run.info.run_id


def list_experiments() -> list[dict]:
    """Return all MLflow experiments as dicts."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    experiments = mlflow.search_experiments()
    return [
        {
            "experiment_id": e.experiment_id,
            "name": e.name,
            "lifecycle_stage": e.lifecycle_stage,
        }
        for e in experiments
    ]


def get_experiment_run_count(experiment_id: str) -> int:
    """Count runs in an experiment."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    runs = mlflow.search_runs(experiment_ids=[experiment_id])
    return len(runs)
