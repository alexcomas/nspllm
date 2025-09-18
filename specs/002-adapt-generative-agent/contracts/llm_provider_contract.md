# Contract: LLM Provider Abstraction

## Purpose
Define how services interact with an LLM provider via the repository layer.

## Methods
- generate(prompt: str, **kwargs) -> str | dict
- structured(prompt: str, schema: dict, **kwargs) -> dict
- call_function(prompt: str, functions: list[dict], **kwargs) -> dict

## Guarantees
- Consistent error types for rate limits/timeouts
- Request/response metadata available for logging
- Supports seeding or reproducibility hooks when available
