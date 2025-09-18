# Quickstart

## Prerequisites
- Python 3.12
- uv (https://github.com/astral-sh/uv)

## Setup
```zsh
uv sync
```

## Run Tests
```zsh
uv run pytest -q
```

## Switch LLM Provider (example)
- Configure via `services/config.py` or environment variable `LLM_PROVIDER`
- Ensure `repositories/implementations/*` has the desired provider implementation

## Switch Planning Module (example)
- Use `services/planning_service.py` to select module implementation
- Implementations can live in `services/implementations/planning_service_shim.py` initially

## Validate Refactor Incrementally
- Add failing tests first in `tests/`
- Implement minimal changes to pass
- Run full test suite frequently
