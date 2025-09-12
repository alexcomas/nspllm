# AGENTS.md

This file describes how AI coding agents and contributors should interact with this repository.
Follow these guidelines to keep the project consistent, reliable, and maintainable.

---

## 📖 Overview

This project implements **generative agents**.
Agents simulate personas with cognitive modules that handle **planning, perceiving, conversing, and reflecting**, all running inside a simulated environment.

### Repository Layout

- `persona/cognitive_modules/` → Core agent modules: `plan.py`, `converse.py`, `perceive.py`, `reflect.py`
- `reverie.py` → Main simulation loop / orchestrator
- `services/` → Service layer: `PlanningService`, `DialogueService`, `PerceptionService`, `EnvironmentService`
- `repositories/` → Abstractions for data + LLM backends: `LLMRepository`, `EnvironmentRepository` (+ `OpenAIRepo`, `MockRepo`, `FileEnvRepo`)
- `tests/` → Unit and integration tests
- `prompts/` → Prompt templates used by LLMs

---

## ⚙️ Setup

This repo uses **uv** for dependency management.

### Installation

```bash
uv sync
```

### Running the simulation

```bash
uv run python reverie.py --scenario demo
```

#### Environment variables

- `OPENAI_API_KEY` → required when using the OpenAI backend
- Other config (storage paths, caching, etc.) → must go into `.env` (gitignored)

---

## 🧪 Development

### Running tests

```bash
uv run pytest
```

### Linting & formatting (ruff)

```bash
uv run ruff check .
uv run ruff format .
```

### Type checking (optional, mypy)

```bash
uv run mypy .
```

---

## 📝 Conventions

- Always use `logging` instead of `print`
- No direct file I/O or LLM calls inside cognitive modules — must go through `EnvironmentService` and `LLMRepository`
- Prompts live in `/prompts/` and must be versioned when modified
- Use dependency injection: services must receive repositories as parameters (never hard-code)

---

## 🔧 Refactoring Rules

- Backwards compatibility with storage layout + replays must be maintained
- Every new Service/Repository must have:
  - at least one concrete implementation
  - a Mock implementation for testing
- Keep PRs scoped: refactor one layer at a time

---

## ✅ Testing Standards

### Unit tests

- `tests/test_planning_service.py` → `PlanningService` with `MockRepo`
- `tests/test_dialogue_service.py` → `DialogueService` writing utterances via `EnvRepo`
- `tests/test_perception_service.py` → `PerceptionService` reading utterances via `EnvRepo`

### Integration / smoke tests

- Run pipeline: **perceive → plan → converse**
- Assert output matches baseline behaviour

---

## 🔄 CI / PR Workflow

1. Install dependencies: `uv sync`
2. Run tests + lint: `uv run pytest` and `uv run ruff check .` before pushing
3. Update `pyproject.toml` and `uv.lock` if adding dependencies
4. Document prompt or storage changes in `CHANGELOG.md`

---

## 📂 Repo Map

```
persona/cognitive_modules/   # agent cognitive modules (must call Services)
services/                    # core service layer
repositories/                # abstract + concrete repository implementations
tests/                       # unit + integration tests
prompts/                     # prompt templates
reverie.py                   # simulation orchestrator
```

---

## 🔑 Security Guidelines

- Never commit API keys (store them in `.env`, which is gitignored)
- Assume that external AI tools may read this file — avoid leaking secrets here

---
