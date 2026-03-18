#!/usr/bin/env python3
"""
CLI runner for experiment YAML files.

Usage:
    python scripts/run_experiment.py experiments/example.yaml
    python scripts/run_experiment.py experiments/example.yaml --api-url http://localhost:8000

Sends the experiment config to the running API server and prints results.
The API handles MLflow logging — open http://localhost:5000 to see runs.
"""

import sys
import json
import argparse
import urllib.request
import urllib.error

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


def run_experiment(yaml_path: str, api_url: str) -> None:
    with open(yaml_path) as f:
        config = yaml.safe_load(f)

    payload = {
        "experiment_name": config["experiment_name"],
        "prompt_template": config["prompt_template"].strip(),
        "inputs": config.get("inputs", []),
        "models": config.get("models", []),
        "tags": config.get("tags", {}),
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{api_url}/runs/",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    print(f"\nRunning experiment: {payload['experiment_name']}")
    print(f"Models: {payload['models'] or 'DEFAULT_MODELS'}")
    print(f"Inputs: {len(payload['inputs'])} input(s)")
    print("-" * 60)

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"API error {e.code}: {e.read().decode()}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}")
        print(f"Is the API running at {api_url}?")
        sys.exit(1)

    for r in result["results"]:
        print(f"\nModel: {r['model']}")
        print(f"  Latency:       {r['latency_ms']:.0f}ms")
        print(f"  Quality score: {r['quality_score']:.3f}")
        print(f"  Tokens (est):  {r['token_count_estimate']}")
        print(f"  MLflow run:    {r['mlflow_run_id']}")
        print(f"  Output preview: {r['output'][:120].strip()}...")

    summary = result["summary"]
    print("\n" + "=" * 60)
    print(f"SUMMARY — {summary['total_runs']} runs logged to MLflow")
    print(f"  Best quality:  {summary['best_quality_model']} ({summary['best_quality_score']:.3f})")
    print(f"  Fastest:       {summary['fastest_model']} ({summary['fastest_latency_ms']:.0f}ms)")
    print(f"\nView results: http://localhost:5000")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run an LLM evaluation experiment")
    parser.add_argument("yaml_file", help="Path to experiment YAML file")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    run_experiment(args.yaml_file, args.api_url)
