# Contributing

## Development workflow

This project uses AI-assisted development. Architecture, design decisions, and operational configuration are human-authored. Implementation is produced with Claude Code and reviewed before merging.

## Running locally

```bash
cp .env.example .env
# Edit .env with your Ollama URL and optional API keys
docker-compose up
```

API docs: http://localhost:8000/docs
MLflow UI: http://localhost:5000

## Submitting changes

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make changes, test locally with `docker-compose up`
4. Open a PR with a description of what you changed and why

## Adding a new provider

1. Create `api/providers/your_provider.py` implementing `BaseProvider`
2. Register the model prefix in `api/routes/runs.py` → `_resolve_provider()`
3. Add example to `experiments/example.yaml`
