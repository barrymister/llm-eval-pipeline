# ADR-002: Model Catalog Over Hardcoded Model Lists

## Status

Accepted

## Context

The initial pipeline used flat model name lists in experiment YAMLs and `.env` configuration. This worked for 2-3 models but broke down when:

- Different models had different capabilities (reasoning vs. creative vs. fast)
- Some models couldn't handle certain tasks (reasoning models producing `<think>` tags in short-form content)
- Users needed to compare models by parameter count, context window, or provider
- The same model metadata was duplicated across multiple systems

## Decision

Replace hardcoded model lists with a structured model catalog containing capability metadata per model.

Each model entry includes:
- **Provider** — which inference backend serves it (Ollama, Claude API, OpenRouter)
- **Parameter count** — for comparing model scale
- **Context window** — maximum tokens accepted
- **Capabilities** — tagged list (e.g., `reasoning`, `creative`, `code`, `fast`)
- **Exclusion rules** — modes where the model should not be offered (e.g., `excludeFromModes: ["social"]` for reasoning models that produce chain-of-thought markup)

## Consequences

**Positive:**
- Model selection UI can filter by capability, provider, and size without hardcoding
- Compatibility guards prevent runtime failures (model excluded before inference, not after)
- New models added by editing catalog metadata, not application code
- Catalog extracted into reusable npm package (ai-model-selector) for use across projects

**Negative:**
- Catalog must be maintained — new Ollama models require a metadata entry
- Risk of catalog drift if model capabilities change upstream (mitigated by version pinning in catalog)

## Alternatives Considered

- **Dynamic model discovery** (query Ollama `/api/tags` at runtime): Returns model names but no capability metadata. Insufficient for filtering.
- **LLM-as-judge for capability detection**: Expensive, slow, and circular — you'd need a model to evaluate whether another model can handle a task.

## Production Validation

This pattern was validated in production systems managing AI content generation across multiple SaaS products. The catalog grew to 76+ models across 3 providers. The exclusion rule system prevented a specific failure mode: reasoning models producing errors when proxy timeouts interrupted extended chain-of-thought generation. The catalog was also wrapped in an MCP server ([ai-model-selector-mcp](https://npmjs.com/package/ai-model-selector-mcp)) giving AI assistants structured tool access to model metadata.
