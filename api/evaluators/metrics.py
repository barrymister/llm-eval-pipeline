"""
Evaluation metrics for LLM outputs.

These are lightweight, dependency-free heuristics — no ML models required.
They are intentionally simple so the project runs with zero GPU/CPU cost for evaluation.

For the AWS cert: these metrics map directly to what SageMaker Model Monitor tracks —
latency, throughput, and quality signals that trigger retraining alerts.
"""


def estimate_token_count(text: str) -> int:
    """
    Rough token count estimate: ~4 characters per token (OpenAI rule of thumb).
    Good enough for comparison purposes without a tokenizer dependency.
    """
    return max(1, len(text) // 4)


def compute_quality_score(output: str, prompt: str) -> float:
    """
    Composite quality score from 0.0 to 1.0 based on heuristics.

    Signals measured:
    - Length adequacy: Is the response substantive? (not a one-liner)
    - Completeness: Does it end with a complete sentence?
    - Non-repetition: Does it avoid repeating the same phrases?
    - Prompt relevance: Does it echo back key terms from the prompt?

    These heuristics are intentionally interpretable — each signal maps
    to a real quality concern (verbosity, coherence, relevance).
    """
    if not output or not output.strip():
        return 0.0

    scores: list[float] = []

    # 1. Length adequacy (target: 50–1000 words)
    word_count = len(output.split())
    if word_count < 5:
        scores.append(0.1)
    elif word_count < 20:
        scores.append(0.5)
    elif word_count <= 1000:
        scores.append(1.0)
    else:
        scores.append(0.8)  # Very long responses penalized slightly

    # 2. Completeness — ends with sentence-ending punctuation
    stripped = output.strip()
    completeness = 1.0 if stripped and stripped[-1] in ".!?\"'" else 0.5
    scores.append(completeness)

    # 3. Non-repetition — check for repeated sentences
    sentences = [s.strip() for s in stripped.split(".") if s.strip()]
    unique_ratio = len(set(sentences)) / len(sentences) if sentences else 1.0
    scores.append(unique_ratio)

    # 4. Prompt relevance — key words from prompt appear in output
    prompt_words = {
        w.lower() for w in prompt.split()
        if len(w) > 4 and w.isalpha()
    }
    if prompt_words:
        output_lower = output.lower()
        matches = sum(1 for w in prompt_words if w in output_lower)
        relevance = min(1.0, matches / max(1, len(prompt_words) * 0.3))
    else:
        relevance = 1.0
    scores.append(relevance)

    return round(sum(scores) / len(scores), 3)


def compute_metrics(output: str, prompt: str, latency_ms: float) -> dict:
    """
    Compute all metrics for a single model output.
    Returns a flat dict suitable for mlflow.log_metrics().
    """
    return {
        "latency_ms": round(latency_ms, 2),
        "token_count_estimate": estimate_token_count(output),
        "word_count": len(output.split()),
        "quality_score": compute_quality_score(output, prompt),
        "char_count": len(output),
    }
