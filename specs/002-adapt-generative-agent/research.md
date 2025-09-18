# Phase 0: Research

## Unknowns
- Engine-service boundaries within `reverie/backend_server`
- Introducing `PlanningModule` interface without breaking `reverie.py`
- Strategy for LLM provider switching aligned with existing tests
- Reproducible logging and state capture in simulation runs

## Findings

### Engine-Service Boundaries
- Decision: Keep environment state and simulation loops in engine; delegate planning, LLM calls, and perception/reflection to services via interfaces.
- Rationale: Minimizes churn in engine; leverages existing service abstractions.
- Alternatives considered: Full rewrite of engine around services (rejected: too risky, violates incremental change).

### PlanningModule Interface
- Decision: Define a minimal interface (plan, replan, next_action) and adapt current logic via a shim.
- Rationale: Allows incremental swap without changing callers.
- Alternatives: Replace engine logic entirely (rejected due to backward compatibility risk).

### LLM Provider Switching
- Decision: Use `repositories/llm_repository.py` interface; ensure all services depend on it rather than concrete providers.
- Rationale: Existing tests already validate repo switching; keep the contract stable.
- Alternatives: Direct provider calls in services (rejected: breaks modularity).

### Reproducibility
- Decision: Centralize logging context (seed, persona, prompts, outputs) and persist simulation checkpoints to the existing storage directory.
- Rationale: Satisfies constitution; keeps debugability high.
- Alternatives: Ad-hoc prints/state (rejected: non-reproducible).

## Next Steps
- Define data entities and contracts (Phase 1)
- Draft failing contract tests for planning module and LLM switching
