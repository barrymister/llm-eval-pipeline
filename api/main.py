from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.experiments import router as experiments_router
from api.routes.runs import router as runs_router

app = FastAPI(
    title="LLM Eval Pipeline",
    description="Compare LLM outputs across models and prompt variants with MLflow experiment tracking.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(experiments_router, prefix="/experiments", tags=["experiments"])
app.include_router(runs_router, prefix="/runs", tags=["runs"])


@app.get("/")
def root():
    return {
        "service": "llm-eval-pipeline",
        "version": "1.0.0",
        "docs": "/docs",
        "mlflow": "http://localhost:5000",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
