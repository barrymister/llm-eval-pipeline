from fastapi import APIRouter, HTTPException
from api.mlflow_client import list_experiments, get_experiment_run_count
from api.models import ExperimentInfo

router = APIRouter()


@router.get("/", response_model=list[ExperimentInfo])
def get_experiments():
    """List all MLflow experiments."""
    try:
        experiments = list_experiments()
        result = []
        for exp in experiments:
            run_count = get_experiment_run_count(exp["experiment_id"])
            result.append(
                ExperimentInfo(
                    experiment_id=exp["experiment_id"],
                    name=exp["name"],
                    lifecycle_stage=exp["lifecycle_stage"],
                    run_count=run_count,
                )
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
