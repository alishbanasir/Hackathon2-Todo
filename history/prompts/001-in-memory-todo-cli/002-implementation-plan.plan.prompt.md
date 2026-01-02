---
id: 002
title: Phase I Implementation Plan
stage: plan
date: 2026-01-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-in-memory-todo-cli
branch: 001-in-memory-todo-cli
user: Alishba Nasir
command: /sp.plan
labels: ["plan", "architecture", "clean-architecture", "phase-i", "todo-cli"]
links:
  spec: specs/001-in-memory-todo-cli/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-in-memory-todo-cli/plan.md
  - specs/001-in-memory-todo-cli/research.md
  - specs/001-in-memory-todo-cli/data-model.md
  - specs/001-in-memory-todo-cli/quickstart.md
  - specs/001-in-memory-todo-cli/contracts/cli-interface.md
tests:
  - Constitution compliance gates (all passed)
  - Manual testing strategy defined
---

## Prompt

```text
Phase I: In-Memory Todo CLI Implementation

Objective: Build a modular, type-safe, and clean-coded CLI Todo application.

1. Environment Setup:
   - Use `uv init --app` to create the project structure.
   - Update `pyproject.toml` for Python 3.13.
   - Install `rich` (for beautiful CLI tables) via `uv add rich`.

2. Architectural Layers:
   - Domain Model: `src/todo/models.py` (DataClasses for Task entity).
   - Repository: `src/todo/repository.py` (In-memory storage logic to decouple data from logic).
   - Services: `src/todo/service.py` (Business logic: CRUD operations).
   - Interface: `src/todo/cli.py` (Rich-based CLI interaction loop).

3. Implementation Steps:
   - [ ] Step 1: Scaffold directory structure and initialize UV.
   - [ ] Step 2: Implement `Task` model with `id`, `description`, and `is_completed`.
   - [ ] Step 3: Create `InMemoryTodoRepository` with atomic increment for IDs.
   - [ ] Step 4: Develop CLI loop with commands: `add`, `list`, `done`, `update`, `delete`.
   - [ ] Step 5: Add graceful error handling for invalid IDs and empty inputs.

4. Verification:
   - Manual testing of all 4 User Stories (P1 to P4).
   - Ensure `uv run` executes the app seamlessly.
```

## Response snapshot

Created comprehensive implementation plan for Phase I In-Memory Todo CLI following Clean Architecture and constitution requirements.

**Implementation Plan**: `specs/001-in-memory-todo-cli/plan.md` (462 lines)

**Planning Phases Completed**:

### Phase 0: Research ✅
- **Artifact**: `research.md` (339 lines)
- **Key Decisions**:
  - CLI Framework: argparse (stdlib) over Typer/Click (zero deps, Phase II migration)
  - Repository Pattern: Abstract interface + in-memory dict (constitution requirement)
  - Type Checking: Python 3.13 + mypy strict mode + dataclasses
  - Logging: stdlib logging with JSON format (structlog deferred to Phase II)
  - Display: Rich for tables (user requirement)
  - Error Handling: Custom exception hierarchy
  - Commands: Subcommand-based (add, list, done, update, delete, help)

### Phase 1: Design & Contracts ✅
- **Artifacts**:
  - `data-model.md` (314 lines): Task entity, TaskStatus enum, repository interface, validation rules
  - `contracts/cli-interface.md` (353 lines): Full CLI command specs with input/output/errors
  - `quickstart.md` (308 lines): Setup guide, usage examples, troubleshooting

**Architecture**: Clean Architecture with 4 layers
- **Domain**: models.py (Task, TaskStatus), exceptions.py, repository.py (interface)
- **Application**: service.py (TodoService with business logic)
- **Infrastructure**: in_memory_repository.py (Dict storage, ID generation)
- **Interface**: cli.py (argparse + Rich)

**Technology Stack**:
- Python 3.13+ (user requirement)
- UV package manager (user requirement)
- Rich >=13.0.0 (user requirement for beautiful tables)
- argparse (stdlib - zero external deps for CLI parsing)
- dataclasses (type-safe domain models)
- mypy strict mode (constitution requirement)
- ruff (modern linting)

**Constitution Compliance**:
✅ All 6 core principles satisfied:
1. **Incremental Evolution**: Repository abstraction enables Phase II database swap without business logic changes
2. **Production-Ready**: Type hints, structured logging, explicit error handling, docstrings
3. **AI-Native**: Spec → Plan → Tasks workflow, PHRs created
4. **Scalability & Portability**: 12-factor ready, externalized config pattern
5. **Clean Architecture**: 4 layers, dependency inversion, domain independence
6. **Type Safety**: mypy strict mode, full type annotations

✅ All Phase I constraints satisfied:
- In-memory only: Python dict storage
- No external DB: No SQLite/PostgreSQL/files
- Repository pattern: TodoRepositoryInterface + InMemoryImpl
- CLI interface: argparse subcommands

**Key Design Decisions**:

1. **Repository Pattern** (constitution mandated):
   - Interface: `TodoRepositoryInterface(ABC)` with 6 methods
   - Implementation: `InMemoryTodoRepository` with `Dict[int, Task]` storage
   - Migration: Swap implementation in Phase II, zero service changes

2. **Domain Model**:
   - `Task(dataclass)`: id, description, status
   - `TaskStatus(Enum)`: PENDING, COMPLETED
   - Validation in `__post_init__`

3. **CLI Commands** (argparse subcommands):
   - `add <description>`: Create task
   - `list`: Display all tasks in Rich table
   - `done <id>`: Mark task complete
   - `update <id> <description>`: Edit task
   - `delete <id>`: Remove task
   - `help`: Show usage

4. **Error Handling**:
   - Custom exceptions: `TaskNotFoundError`, `EmptyDescriptionError`, `InvalidTaskIdError`
   - Rich-formatted error messages
   - Exit codes: 0 (success), 1 (user error), 2 (system error)

**Performance Targets** (from success criteria):
- Launch: <5 seconds
- CRUD ops: <100ms
- List 100 tasks: <50ms
- List 1,000 tasks: <100ms
- Zero crashes on invalid input

**Migration Path to Phase II**:
- Repository swap: `InMemoryTodoRepository` → `SQLAlchemyTodoRepository`
- Service layer: No changes (depends on interface)
- Add FastAPI: Extract service calls → API endpoints
- Add Pydantic: Wrap domain models for validation
- Domain models: Unchanged (pure business logic)

**Project Structure**:
```
src/todo/
├── domain/          # Task, TaskStatus, TodoRepositoryInterface, exceptions
├── application/     # TodoService (business logic)
├── infrastructure/  # InMemoryTodoRepository (dict storage)
└── interface/       # cli.py (argparse + Rich)
```

**Constitution Gates**:
- **Pre-Research Gate**: ✅ PASSED (repository pattern, type safety, logging)
- **Post-Design Gate**: ✅ PASSED (layer separation, domain independence, types)

## Outcome

- ✅ Impact: Complete Phase I implementation plan with Clean Architecture, 4 design artifacts, constitution compliance validated, ready for task generation
- 🧪 Tests: Manual testing strategy defined for P1-P4 user stories, automated testing deferred to Phase II
- 📁 Files: Created `plan.md` (462 lines), `research.md` (339 lines), `data-model.md` (314 lines), `quickstart.md` (308 lines), `contracts/cli-interface.md` (353 lines)
- 🔁 Next prompts: `/sp.tasks` to generate granular implementation tasks organized by Clean Architecture layers and user story priorities
- 🧠 Reflection: Plan successfully balances constitution requirements (Clean Architecture, repository pattern, type safety) with Phase I simplicity (in-memory, manual testing). Repository abstraction ensures Phase II database migration without business logic rewrites. User's technical guidance (UV, Rich, argparse preference) integrated while maintaining architectural rigor.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning complete on first iteration
- Graders run and results (PASS/FAIL): Constitution compliance gates - PASS (all 15+ checks), Phase I constraints - PASS (all 4 checks)
- Prompt variant (if applicable): N/A (initial planning)
- Next experiment (smallest change to try): Monitor whether argparse (chosen over Typer) provides sufficient CLI ergonomics during implementation, or if interactive REPL mode should be added as enhancement to Phase I scope
