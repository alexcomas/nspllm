# Contract: PlanningModule Interface

## Purpose
Provide a stable interface for planning modules used by the engine.

## Methods
- check out current implementation

## Guarantees
- Deterministic given same inputs and LLM seed/config
- No side-effects outside returned objects
- Errors are raised as domain-specific exceptions

## Non-Goals
- Storage/persistence responsibilities
- Direct UI or environment rendering
