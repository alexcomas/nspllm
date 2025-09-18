# GitHub Copilot Instructions for NSPLLM

This project implements **Generative Agents** with neuro-symbolic planning extensions. It combines LLM-driven cognitive modules with symbolic planning for coherent, believable AI agents in simulated environments.

## Architecture Overview

### Core Components
- **Simulation Orchestrator**: `reverie/backend_server/reverie.py` - Main simulation loop managing personas, environment state, and time progression
- **Cognitive Modules**: `reverie/backend_server/persona/cognitive_modules/` - Agent brains (plan, perceive, converse, reflect, execute, retrieve)
- **Service Layer**: `services/` - Clean abstractions for planning, dialogue, perception, environment I/O, and reflection
- **Repository Layer**: `repositories/` - Data access abstractions for LLM backends and environment storage

### Data Flow Pattern
1. Frontend (`environment/frontend_server`) outputs environment JSON files
2. Backend reads environment state, updates persona positions 
3. Each persona processes: **perceive → retrieve → plan → execute** 
4. Backend writes movement JSON for frontend consumption
5. Cycle repeats with time progression (`sec_per_step`)

### Service-Repository Architecture
```
Cognitive Modules → Services → Repositories → External Systems
                              ↓
                    Planning/Dialogue/etc → LLM/Environment → OpenAI/FileSystem
```

## Development Workflows

### Setup & Dependencies
```bash
# Use uv for dependency management (recommended)
uv sync
# Legacy fallback: pip install -r requirements.txt

# Create reverie/backend_server/utils.py with OpenAI credentials
# See README.md Step 1 for template
```

### Running Simulations
```bash
# Terminal 1: Start environment server
cd environment/frontend_server && uv run python manage.py runserver

# Terminal 2: Start simulation
cd reverie/backend_server && uv run python reverie.py
# Follow prompts to load simulation (e.g., "base_the_ville_isabella_maria_klaus")
# Run steps: "run 100"
```

### Testing & Quality
```bash
uv run pytest                    # Run test suite
uv run ruff check .             # Lint with ruff
uv run ruff format .            # Format code
```

## Project-Specific Patterns

### Dependency Injection in Services
- Services receive repositories as constructor parameters (never hard-coded dependencies)
- Use "shim" implementations (`*_service_shim.py`) that delegate to legacy code during refactoring
- Example: `PlanningServiceShim` wraps legacy `plan.py` while maintaining clean interfaces

### LLM Repository Pattern
```python
# Abstract interface
class LLMRepository(ABC):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str: ...

# Concrete implementations
OpenAIRepo(api_key="...")      # Production
MockLLMRepository(responses=...) # Testing
```

### Environment File Coordination
- Backend reads `{sim_code}/environment/{step}.json` from frontend
- Backend writes `{sim_code}/movement/{step}.json` for frontend
- Temp files in `fs_temp_storage/` coordinate simulation state

### Memory Management
- **Associative Memory**: Event streams, thoughts, conversations stored chronologically
- **Spatial Memory**: Hierarchical world → sector → arena → game_object structure
- **Scratch Memory**: Current state, planned paths, immediate context

## Critical Conventions

### Storage Layout Compatibility
- Never break backwards compatibility with existing simulation storage
- Simulation folders: `environment/frontend_server/storage/{sim_code}/`
- Persona data: `{sim_code}/personas/{name}/bootstrap_memory/`

### Logging Over Print
```python
# ✅ Use logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Processing persona", extra={"persona": persona.name})

# ❌ Avoid print statements  
print(f"Processing {persona.name}")
```

### Pure Service Methods
- Services must be side-effect free beyond returned values
- All I/O goes through repositories
- Enable testing with mock repositories

### Prompt Template Versioning
- Prompts in `reverie/backend_server/persona/prompt_template/`
- Version directories: `v1/`, `v2/`, `v3_ChatGPT/`
- Document prompt changes in commit messages

## Integration Points

### Frontend-Backend Communication
- Django frontend serves web interface and handles user interactions
- JSON file exchange for environment state and agent movements
- WebSocket-like coordination via file polling (legacy pattern)

### LLM Integration
- OpenAI GPT models for natural language reasoning
- Structured prompting for cognitive module outputs
- Fallback/retry logic in `OpenAIRepo` for reliability

### Simulation Persistence
- Complete simulation state serializable to disk
- Fork/branch simulations from prior states
- Compression utilities for storage management

## Key Files for Context

- `AGENTS.md` - AI agent interaction guidelines and architecture overview
- `reverie/backend_server/reverie.py` - Main simulation orchestrator and command interface
- `services/planning_service.py` - Abstract planning interface for neuro-symbolic extensions
- `repositories/implementations/openai_repo.py` - LLM backend with retry logic
- `tests/conftest.py` - Test configuration and sys.path setup

## Neuro-Symbolic Extensions (Thesis Focus)

This project extends generative agents with:
- **PDDL Schema Generation**: LLMs create symbolic domain knowledge
- **Constraint Validation**: Symbolic planners ensure logical coherence
- **Believability Metrics**: Human perception evaluation frameworks

When working on planning-related features, consider both neural (LLM-based) and symbolic (logic-based) approaches to maintain coherence and constraint adherence.