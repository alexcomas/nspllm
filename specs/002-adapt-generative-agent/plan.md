
# Implementation Plan: Adapt Generative Agent Codebase for Neuro-Symbolic Planning

**Branch**: `002-adapt-generative-agent` | **Date**: September 18, 2025 | **Spec**: `/specs/002-adapt-generative-agent/spec.md`
**Input**: Feature specification from `/specs/002-adapt-generative-agent/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Refactor the `reverie/backend_server` engine into clear abstraction layers to support neuro-symbolic planning. Maintain compatibility while enabling pluggable planning modules and multiple LLM providers with a consistent interface, following an incremental, test-driven approach using `uv` and `pytest`.

## Technical Context
**Language/Version**: Python 3.12  
**Primary Dependencies**: `uv` (package manager), `pytest` (tests), existing `services/` and `repositories/` abstractions  
**Storage**: SQLite (`environment/frontend_server/db.sqlite3`), file-based storage in `environment/frontend_server/storage/`  
**Testing**: pytest; strict TDD as per constitution  
**Target Platform**: Linux server  
**Project Type**: Web backend/engine  
**Performance Goals**: Preserve current simulation performance; enable switching planning modules and LLM providers without regressions  
**Constraints**: Incremental refactor, backward compatibility, reproducibility, modular architecture, comprehensive type hints/docstrings  
**Scale/Scope**: Engine refactor only; no UI changes; introduce interfaces and shims where needed

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Test-First: Write failing tests before refactor; enforce with CI
- Incremental Changes: Small, independently verifiable PRs only
- Reproducibility: Version configs, log LLM interactions, preserve state
- Backward Compatibility: Keep public APIs stable; add shims where needed
- Modular Architecture: Keep services/repositories/interfaces cleanly separated
- Code Quality: Linting/typing/docstrings required

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
reverie/backend_server/
├── global_methods.py
├── maze.py
├── path_finder.py
├── reverie.py
├── test.py
└── persona/

services/
├── dialogue_service.py
├── environment_service.py
├── perception_service.py
├── planning_service.py
├── reflection_service.py
└── implementations/

repositories/
├── environment_repository.py
├── llm_repository.py
└── implementations/

tests/
├── test_dialogue_service_shim.py
├── test_perception_service_shim.py
├── test_planning_service_shim.py
├── test_reflection_service_shim.py
└── test_openai_repo.py
```

**Structure Decision**: Web backend/engine with modular service/repository/implementation layers

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Boundaries between engine logic and service/repo abstractions
   - How to introduce planning module interface without breaking `reverie.py`
   - Strategy for LLM provider switching with existing tests
   - Logging and state capture for reproducibility in the engine

2. **Generate and dispatch research agents**:
    - Task: "Define engine-service boundaries in reverie/backend_server"
    - Task: "Design PlanningModule interface and adapter for current engine"
    - Task: "Design LLMRepository interface usage within planning_service"
    - Task: "Design reproducible logging/state capture for simulations"

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh copilot` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
