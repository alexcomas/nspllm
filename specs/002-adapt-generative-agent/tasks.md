# Tasks: Adapt Generative Agent Codebase for Neuro-Symbolic Planning

**Input**: Design documents from `/specs/002-adapt-generative-agent/`
**Prerequisites**: plan.md (required), research.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks (not present)
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup + integration tasks
   → quickstart.md: Extract scenarios → integration tests
3. Generate tasks by category:
   → Setup: test scaffolding, config toggles, linting verification
   → Tests: contract tests, integration tests
   → Core: interfaces, services, repository implementations
   → Integration: logging, seeding, configuration wiring
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency notes
7. Create parallel execution examples with Task commands
8. Validate task completeness
```

## Phase 3.1: Setup
- [x] T001 [P] Create contract/integration test scaffolding in `/home/ledwo/nspllm/tests/contract/` and `/home/ledwo/nspllm/tests/integration/` (add `__init__.py` if missing)
- [x] T002 Verify pytest/ruff configuration; add `pytest.ini` in `/home/ledwo/nspllm/pytest.ini` for strict failures (xfail-strict=true), testpaths=`tests`
- [x] T003 [P] Add basic testing fixtures for seeding/log dirs in `/home/ledwo/nspllm/tests/conftest.py` (non-breaking, append-only)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
Contract files discovered in `/home/ledwo/nspllm/specs/002-adapt-generative-agent/contracts/`:
- `planning_module.md`
- `llm_provider_contract.md`

- [x] T004 [P] Contract test for PlanningModule interface in `/home/ledwo/nspllm/tests/contract/test_planning_module_contract.py`
  - Assert methods exist: `plan`, `replan`, `next_action`
  - Determinism: same inputs + seed → same outputs
  - Errors: domain-specific exceptions on invalid input
- [x] T005 [P] Contract test for LLM Provider abstraction in `/home/ledwo/nspllm/tests/contract/test_llm_provider_contract.py`
  - Methods: `generate(prompt, **kwargs)`, `structured(prompt, schema, **kwargs)`, `call_function(prompt, functions, **kwargs)`
  - Error types: rate limit/timeout are consistent
  - Metadata: request/response metadata accessible for logging
- [ ] T006 [P] Integration test: Switch LLM provider via `LLM_PROVIDER` config in `/home/ledwo/nspllm/tests/integration/test_switch_llm_provider.py`
  - Given `services/config.py` set to provider `openai`, ensure repository resolves to OpenAI implementation
  - When toggled to a mock provider, ensure resolution switches without code changes in services
- [ ] T007 [P] Integration test: Switch planning module in `/home/ledwo/nspllm/tests/integration/test_switch_planning_module.py`
  - Select module via `services/planning_service.py` wiring or env var
  - Engine caller (`reverie/backend_server/reverie.py`) uses selected module without code changes
- [ ] T008 [P] Integration test: Reproducible logging/state capture in `/home/ledwo/nspllm/tests/integration/test_reproducible_logging.py`
  - Set seed + run one planning step → verify persisted log/checkpoint exists and includes seed, prompts, outputs

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T009 Define `PlanningModule` protocol and exceptions in `/home/ledwo/nspllm/services/planning_service.py` (minimal interface: `plan`, `replan`, `next_action`)
- [ ] T010 Implement shim adapter to current engine in `/home/ledwo/nspllm/services/implementations/planning_service_shim.py` to satisfy `PlanningModule`
- [ ] T011 Wire planning module selection (config/env) in `/home/ledwo/nspllm/services/planning_service.py` without breaking public API
- [ ] T012 Ensure all services depend on `repositories/llm_repository.py` interface (no direct provider use); touch `/home/ledwo/nspllm/services/dialogue_service.py`, `/home/ledwo/nspllm/services/reflection_service.py`, `/home/ledwo/nspllm/services/perception_service.py` as needed (separate commits if multiple files)
- [ ] T013 Extend `/home/ledwo/nspllm/repositories/llm_repository.py` with `structured` and `call_function` signatures as per contract (no breaking changes)
- [ ] T014 Implement OpenAI repo conformance in `/home/ledwo/nspllm/repositories/implementations/openai_repo.py` including metadata hooks and consistent error types
- [ ] T015 [P] Add mock provider for tests in `/home/ledwo/nspllm/repositories/implementations/mock_llm_repo.py` with deterministic outputs given seed

## Phase 3.4: Integration
- [ ] T016 Introduce reproducible logging utility in `/home/ledwo/nspllm/services/implementations/dialogue_service_shim.py` or a new module `/home/ledwo/nspllm/services/logging_utils.py` for centralized context logging (seed, persona, prompts, outputs)
- [ ] T017 Persist simulation checkpoints in `/home/ledwo/nspllm/environment/frontend_server/storage/` with filenames including timestamp + seed; expose small helper in `/home/ledwo/nspllm/reverie/backend_server/global_methods.py`
- [ ] T018 Add `LLM_PROVIDER` and `PLAN_MODULE` config toggles in `/home/ledwo/nspllm/services/config.py` (env-var override, safe defaults)
- [ ] T019 [P] Update `quickstart.md` with concrete provider/module switch steps in `/home/ledwo/nspllm/specs/002-adapt-generative-agent/quickstart.md`

## Phase 3.5: Polish
- [ ] T020 [P] Unit tests for logging utils in `/home/ledwo/nspllm/tests/unit/test_logging_utils.py`
- [ ] T021 Performance sanity: single planning step under acceptable time in `/home/ledwo/nspllm/tests/perf/test_planning_step_perf.py`
- [ ] T022 [P] Developer docs: contract-to-implementation mapping in `/home/ledwo/nspllm/README.md`
- [ ] T023 Dead code scan and small refactors (no behavior changes) across touched files

## Dependencies
- Tests (T004–T008) before implementation (T009–T015)
- T009 blocks T010–T011
- T012 depends on T013
- T014 depends on T013
- T016–T018 depend on core (T009–T015)
- Implementation before polish (T020–T023)
- Same-file tasks are sequential (e.g., T009 → T011 in `services/planning_service.py`)

## Parallel Example
```
# Launch T004–T008 together (different files):
Task: "Contract test PlanningModule in /home/ledwo/nspllm/tests/contract/test_planning_module_contract.py"
Task: "Contract test LLM Provider in /home/ledwo/nspllm/tests/contract/test_llm_provider_contract.py"
Task: "Integration test switch provider in /home/ledwo/nspllm/tests/integration/test_switch_llm_provider.py"
Task: "Integration test switch planning module in /home/ledwo/nspllm/tests/integration/test_switch_planning_module.py"
Task: "Integration test reproducible logging in /home/ledwo/nspllm/tests/integration/test_reproducible_logging.py"

# After core passes, launch polish tasks in parallel:
Task: "Unit tests for logging utils in /home/ledwo/nspllm/tests/unit/test_logging_utils.py"
Task: "Performance test in /home/ledwo/nspllm/tests/perf/test_planning_step_perf.py"
Task: "Docs update in /home/ledwo/nspllm/README.md"
```

## Validation Checklist
- [ ] All contracts have corresponding tests (T004, T005)
- [ ] All tests come before implementation (T004–T008 precede T009+)
- [ ] Parallel tasks are independent and touch different files
- [ ] Each task specifies exact absolute file path
- [ ] LLM provider switching and planning module selection are test-validated
- [ ] Reproducible logging and checkpointing verified by tests
