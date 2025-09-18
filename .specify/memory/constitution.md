# Neuro-Symbolic Planning Thesis Constitution

## Core Principles

### I. Test-First (NON-NEGOTIABLE)
**TDD Mandatory**: Every feature implementation must follow Test-Driven Development principles. Tests must be written and approved BEFORE implementation begins. The development cycle is strictly: Red (failing tests) → Green (implementation) → Refactor. No code is written without corresponding failing tests first. All tests must pass before committing changes.

### II. Incremental Changes
**Small, Verifiable Increments**: All changes must be made in small, incremental steps that can be easily verified and rolled back if needed. No large monolithic changes. Each increment should:
- Have clear, measurable success criteria
- Be independently testable
- Maintain system stability
- Allow for easy verification of correctness
- Enable quick rollback if issues arise

### III. Research Reproducibility
**Thesis-Grade Rigor**: All experimental changes must maintain reproducibility for academic research. This includes:
- Version-controlled configurations and parameters
- Structured logging of all LLM interactions
- Preservation of simulation state for debugging
- Clear documentation of experimental conditions
- Ability to reproduce results across different runs

### IV. Backward Compatibility
**Preserve Existing Functionality**: Changes must maintain backward compatibility with existing simulation data and APIs. Migration paths must be provided for any breaking changes, with clear deprecation warnings and upgrade guides.

### V. Modular Architecture
**Clean Separation of Concerns**: Code must follow modular architecture principles with clear boundaries between:
- Service layer (business logic)
- Repository layer (data access)
- Implementation layer (concrete classes)

## Development Standards

### Code Quality
- All code must pass linting and formatting checks
- Comprehensive error handling with structured logging
- Clear, descriptive variable and function names
- Comprehensive docstrings for all public APIs
- Type hints for all function parameters and return values


## Governance

**Constitution Authority**: This constitution supersedes all other development practices and guidelines. All changes must comply with these principles.

**Amendment Process**: Constitution amendments require:
1. Clear justification for the change
2. Documentation of impact on existing work
3. Approval from project stakeholders
4. Update to all dependent templates and documentation
5. Migration plan for existing code if needed

**Compliance Verification**: All pull requests must include verification that changes comply with constitution principles. Automated checks should validate test coverage, incremental changes, and other measurable requirements.

**Version**: 1.0.0 | **Ratified**: September 18, 2025 | **Last Amended**: September 18, 2025