# Implementation Plan: In-Memory Todo CLI

**Branch**: `001-in-memory-todo-cli` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-in-memory-todo-cli/spec.md`

## Summary

Build a Phase I in-memory Python todo CLI application with Clean Architecture to enable seamless Phase II database migration. Core features include CRUD operations (add, view, update, delete, mark complete) with beautiful Rich-based table display, comprehensive error handling, and production-ready code standards (type hints, structured logging, PEP 8 compliance).

**Technical Approach**: Implement Clean Architecture with distinct domain, application, infrastructure, and interface layers. Use repository pattern to abstract in-memory storage, enabling future database swap without business logic changes. Leverage Python 3.13, UV package manager, argparse for CLI, and Rich for display.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Rich (>=13.0.0) for CLI display
**Storage**: In-memory (Python dict), repository pattern abstraction
**Testing**: Manual testing (Phase I), pytest (Phase II+)
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux)
**Project Type**: Single project (CLI application)
**Performance Goals**: <100ms for CRUD operations, <50ms for lists <100 tasks
**Constraints**: In-memory only (no persistence), <100ms p95 latency, zero manual code edits (agentic workflow)
**Scale/Scope**: 1,000 tasks max, single-user, single-session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate (Phase 0)

| Principle | Requirement | Status | Evidence |
|-----------|-------------|--------|----------|
| **I. Incremental Evolution** | Repository pattern required | ✅ PASS | research.md: Abstract interface + in-memory impl |
| **I. Incremental Evolution** | Migration path documented | ✅ PASS | research.md: Phase II database swap strategy |
| **II. Production-Ready** | Type hints required | ✅ PASS | Python 3.13 with mypy strict mode |
| **II. Production-Ready** | Structured logging | ✅ PASS | stdlib logging with JSON formatter |
| **II. Production-Ready** | Error handling | ✅ PASS | Custom exception hierarchy |
| **II. Production-Ready** | Docstrings | ✅ PASS | Required for all public APIs |
| **III. AI-Native** | Spec/Plan/Tasks workflow | ✅ PASS | Following SDD workflow |
| **III. AI-Native** | PHR creation | ✅ PASS | PHRs created per workflow |
| **V. Clean Architecture** | Domain independence | ✅ PASS | Domain → Application → Infrastructure → Interface |
| **V. Clean Architecture** | Dependency inversion | ✅ PASS | Services depend on repository interface |
| **VI. Type Safety** | mypy strict mode | ✅ PASS | pyproject.toml: mypy strict = true |

**Phase I Constraints**:

| Constraint | Requirement | Status | Evidence |
|------------|-------------|--------|----------|
| **Storage** | In-memory only | ✅ PASS | Dict-based repository, no DB |
| **No External DB** | No SQLite/PostgreSQL/files | ✅ PASS | Pure in-memory (Python dict) |
| **Repository Pattern** | Even for in-memory | ✅ PASS | TodoRepositoryInterface + InMemoryImpl |
| **CLI Interface** | argparse or typer | ✅ PASS | argparse (stdlib, zero deps) |

### Post-Design Gate (Phase 1)

| Principle | Requirement | Status | Evidence |
|-----------|-------------|--------|----------|
| **I. Incremental Evolution** | Interfaces defined | ✅ PASS | TodoRepositoryInterface in domain layer |
| **V. Clean Architecture** | Layers separated | ✅ PASS | domain/, application/, infrastructure/, interface/ |
| **V. Clean Architecture** | Domain no framework imports | ✅ PASS | data-model.md: pure dataclasses |
| **VI. Type Safety** | All types documented | ✅ PASS | data-model.md: full type annotations |

**GATE RESULT**: ✅ ALL GATES PASSED - Proceed to implementation

## Project Structure

### Documentation (this feature)

```text
specs/001-in-memory-todo-cli/
├── spec.md                 # Feature specification
├── plan.md                 # This file (/sp.plan command output)
├── research.md             # Phase 0 output (technology decisions)
├── data-model.md           # Phase 1 output (domain entities)
├── quickstart.md           # Phase 1 output (setup guide)
├── contracts/              # Phase 1 output (CLI interface contract)
│   └── cli-interface.md
├── checklists/
│   └── requirements.md     # Spec quality validation
└── tasks.md                # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
└── todo/
    ├── __init__.py
    ├── domain/                 # Domain layer (entities, interfaces)
    │   ├── __init__.py
    │   ├── models.py          # Task, TaskStatus
    │   ├── repository.py      # TodoRepositoryInterface (ABC)
    │   └── exceptions.py      # TodoException, TaskNotFoundError, etc.
    ├── application/           # Application layer (business logic)
    │   ├── __init__.py
    │   └── service.py         # TodoService (CRUD operations)
    ├── infrastructure/        # Infrastructure layer (implementations)
    │   ├── __init__.py
    │   └── in_memory_repository.py  # InMemoryTodoRepository
    └── interface/             # Interface layer (CLI)
        ├── __init__.py
        └── cli.py             # argparse + Rich CLI

pyproject.toml                 # UV project config
uv.lock                        # Dependency lock file
README.md                      # Project documentation
.gitignore                     # Git ignore rules
```

**Structure Decision**: Single project structure selected (Option 1 from template) because:
- Phase I is CLI-only (no web frontend/backend split)
- Clean Architecture layers fit within single `src/todo/` package
- Phase II will add `backend/` and `frontend/` directories alongside `src/`
- Migration strategy: Extract `src/todo/` business logic → `backend/src/`, add `frontend/`

## Complexity Tracking

**No Constitution violations** - all requirements met without exceptions.

Repository pattern is required by constitution for Phase I, not added complexity.

## Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────┐
│          Interface Layer (CLI)                   │
│  - cli.py: argparse commands + Rich display     │
└──────────────────┬──────────────────────────────┘
                   │ depends on
┌──────────────────▼──────────────────────────────┐
│      Infrastructure Layer                        │
│  - in_memory_repository.py: Dict storage        │
└──────────────────┬──────────────────────────────┘
                   │ implements
┌──────────────────▼──────────────────────────────┐
│      Application Layer (Services)                │
│  - service.py: Business logic (CRUD)            │
└──────────────────┬──────────────────────────────┘
                   │ depends on
┌──────────────────▼──────────────────────────────┐
│      Domain Layer (Entities, Interfaces)         │
│  - models.py: Task, TaskStatus                  │
│  - repository.py: TodoRepositoryInterface (ABC) │
│  - exceptions.py: Domain exceptions             │
└─────────────────────────────────────────────────┘
```

**Dependency Rule**: Outer layers depend on inner layers, never the reverse.

### Key Components

#### Domain Layer (`src/todo/domain/`)

**models.py**:
- `TaskStatus(Enum)`: PENDING, COMPLETED
- `Task(dataclass)`: id, description, status
- Validation in `__post_init__`

**repository.py**:
- `TodoRepositoryInterface(ABC)`: Abstract methods for CRUD
- Methods: add(), get_all(), get_by_id(), update(), mark_complete(), delete()

**exceptions.py**:
- `TodoException`: Base exception
- `TaskNotFoundError`: Task ID doesn't exist
- `EmptyDescriptionError`: Invalid empty description
- `InvalidTaskIdError`: Invalid ID format

#### Application Layer (`src/todo/application/`)

**service.py**:
- `TodoService`: Business logic coordinator
- Constructor injection: `__init__(self, repository: TodoRepositoryInterface)`
- Methods mirror repository but add validation, logging
- Example: `add_task(description: str) -> Task`

#### Infrastructure Layer (`src/todo/infrastructure/`)

**in_memory_repository.py**:
- `InMemoryTodoRepository(TodoRepositoryInterface)`: Concrete implementation
- Storage: `Dict[int, Task]`
- ID generation: `self._next_id` (atomic increment)
- Thread-safe with `threading.Lock` (future-proofing)

#### Interface Layer (`src/todo/interface/`)

**cli.py**:
- `argparse` setup with subcommands: add, list, done, update, delete, help
- `Rich` tables for display
- Error handling: try/except with Rich-formatted error messages
- Entry point: `main()` function for UV script entry

### Data Flow Example: Add Task

```
User: uv run todo add "Buy groceries"
  ↓
cli.py: Parse args → call service.add_task("Buy groceries")
  ↓
service.py: Validate → call repository.add("Buy groceries")
  ↓
in_memory_repository.py: Create Task(id=1, desc="Buy groceries", status=PENDING)
  ↓
in_memory_repository.py: Store in self._storage[1]
  ↓
service.py: Log success → return Task
  ↓
cli.py: Display success with Rich formatting
```

## Implementation Phases

### Phase 0: Research ✅ COMPLETED

**Artifact**: `research.md`

**Key Decisions**:
1. **CLI Framework**: argparse (stdlib) instead of Typer
2. **Repository Pattern**: Abstract interface + in-memory dict
3. **Type Checking**: Python 3.13 + mypy strict mode + dataclasses
4. **Logging**: stdlib logging with structured JSON format
5. **Display**: Rich (user requirement)
6. **Package Manager**: UV (user requirement)
7. **Error Handling**: Custom exception hierarchy
8. **Commands**: Subcommand-based (add, list, done, update, delete, help)

**Rationale**: See research.md for detailed alternatives and justifications.

### Phase 1: Design & Contracts ✅ COMPLETED

**Artifacts**:
- `data-model.md`: Task entity, TaskStatus enum, repository interface
- `contracts/cli-interface.md`: Full CLI command specifications
- `quickstart.md`: Setup and usage guide

**Key Outputs**:
1. **Domain Model**: Task (id, description, status) with validation
2. **Repository Interface**: TodoRepositoryInterface with 6 methods
3. **CLI Contract**: 6 commands with input/output specs
4. **Error Handling**: 3 custom exceptions with clear messages
5. **Display Format**: Rich table with ID, Description, Status columns

### Phase 2: Task Generation (Next Step)

**Command**: `/sp.tasks`

**Expected Output**: `tasks.md` with granular implementation tasks organized by:
- Phase 1: Setup (UV init, dependencies)
- Phase 2: Domain layer (models, exceptions, repository interface)
- Phase 3: Application layer (service)
- Phase 4: Infrastructure layer (in-memory repository)
- Phase 5: Interface layer (CLI with argparse + Rich)
- Phase 6: Integration and testing

**Task Organization**: Follows user story priorities (P1 → P4)

## Technology Stack

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Language** | Python | 3.13+ | User requirement, latest stable |
| **Package Manager** | UV | Latest | User requirement, fast, reliable |
| **CLI Parsing** | argparse | stdlib | Zero deps, simple, Phase II migration |
| **Display Library** | Rich | >=13.0.0 | User requirement, beautiful tables |
| **Domain Models** | dataclasses | stdlib | Type-safe, mypy compatible |
| **Type Checking** | mypy | Latest | Constitution requirement (strict mode) |
| **Linting** | ruff | Latest | Fast, modern Python linter |
| **Logging** | logging | stdlib | Structured JSON, Phase I sufficient |

**No external dependencies** except Rich (explicitly requested by user).

## Development Workflow

### Setup Commands

```bash
# Initialize project
uv init --app todo-cli
cd todo-cli
uv python pin 3.13
uv add rich

# Install dev dependencies (optional)
uv add --dev mypy ruff pytest
```

### Implementation Order

1. **Domain Layer First** (no dependencies):
   - models.py: Task, TaskStatus
   - exceptions.py: Custom exceptions
   - repository.py: TodoRepositoryInterface

2. **Application Layer** (depends on domain):
   - service.py: TodoService

3. **Infrastructure Layer** (implements domain):
   - in_memory_repository.py: InMemoryTodoRepository

4. **Interface Layer Last** (depends on all):
   - cli.py: argparse + Rich CLI

### Quality Gates

Before each layer:
- ✅ Type hints on all functions
- ✅ Docstrings on all public APIs
- ✅ mypy strict mode passes
- ✅ ruff linting passes
- ✅ Manual testing against acceptance criteria

## Testing Strategy

### Phase I: Manual Testing

**Per User Story**:
- P1 (Add/View): Manual test add → list → verify display
- P2 (Complete): Manual test add → done → list → verify status
- P3 (Update): Manual test add → update → list → verify change
- P4 (Delete): Manual test add → delete → list → verify removal

**Edge Cases**:
- Empty description → error message
- Non-existent ID → error message
- Invalid ID format → error message
- Long descriptions (>10,000 chars) → handle gracefully
- Unicode/emoji → display correctly

### Phase II+: Automated Testing

**Unit Tests** (pytest):
- Domain: Task validation, exception raising
- Service: Business logic, repository interaction (mocked)
- Repository: CRUD operations

**Integration Tests**:
- CLI end-to-end: Command → output verification

**Coverage Target**: >80% (Phase II constitution requirement)

## Performance Targets

Based on success criteria (SC-001 through SC-006):

| Metric | Target | Approach |
|--------|--------|----------|
| Launch time | <5s | Minimal imports, fast Python startup |
| CRUD operations | <100ms | In-memory dict O(1) operations |
| List <100 tasks | <50ms | Dict iteration, Rich rendering |
| List 1,000 tasks | <100ms | Same approach, validated in testing |
| Error handling | 0 crashes | Explicit try/except, custom exceptions |

**Validation**: Manual timing during implementation, optimize if needed.

## Migration Path to Phase II

### Phase II Changes Required

**Add (no changes to Phase I code)**:
1. New file: `backend/src/infrastructure/sqlalchemy_repository.py`
2. New file: `backend/src/api/` (FastAPI endpoints)
3. New file: `frontend/` (Next.js app)

**Modify (minimal)**:
1. `backend/src/application/service.py`: No changes (same interface)
2. `backend/src/domain/*`: No changes (pure domain logic)
3. Dependency injection: Swap `InMemoryTodoRepository` → `SQLAlchemyTodoRepository`

**Migration Example**:
```python
# Phase I
repository = InMemoryTodoRepository()
service = TodoService(repository)

# Phase II (zero service changes!)
repository = SQLAlchemyTodoRepository(db_url="postgresql://...")
service = TodoService(repository)  # Identical API
```

**Why This Works**: Clean Architecture + Dependency Inversion Principle

### Database Schema (Phase II Preview)

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    description VARCHAR(10000) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Domain model stays identical** - repository handles mapping.

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Type checking failures | Low | Medium | mypy strict from start, incremental validation |
| Rich display issues (Windows) | Low | Low | Test on Windows Terminal, fallback to plain text |
| ID overflow (>maxint) | Very Low | Low | Use Python arbitrary precision int |
| Performance <1000 tasks | Very Low | Low | Dict operations are O(1), easily meets targets |
| Constitution violations | Low | High | Pre/post design gate checks, automated validation |

**Overall Risk**: LOW - straightforward Phase I implementation with clear requirements.

## Open Questions

**None** - all decisions finalized in research.md.

## Success Criteria Mapping

| Success Criterion | Implementation Evidence |
|-------------------|-------------------------|
| **SC-001**: Operations <5s launch | Python + UV startup time |
| **SC-002**: 1,000 tasks <100ms | Dict storage O(1) |
| **SC-003**: 100% error messages | Custom exceptions + try/except |
| **SC-004**: Help readable <30s | `uv run todo help` command |
| **SC-005**: <50ms for <100 tasks | Rich rendering + dict iteration |
| **SC-006**: Zero manual edits | Agentic workflow (this plan proves it) |

## Next Steps

1. **Run `/sp.tasks`**: Generate granular task breakdown
2. **Implement in order**: Domain → Application → Infrastructure → Interface
3. **Validate per user story**: Test P1, then P2, then P3, then P4
4. **Quality checks**: mypy strict, ruff linting, manual testing
5. **Commit**: Use conventional commits (`feat:`, `fix:`, `docs:`)
6. **Prepare for Phase II**: Document migration insights

## Appendices

### A. File Checklist

- [x] `specs/001-in-memory-todo-cli/spec.md`
- [x] `specs/001-in-memory-todo-cli/plan.md` (this file)
- [x] `specs/001-in-memory-todo-cli/research.md`
- [x] `specs/001-in-memory-todo-cli/data-model.md`
- [x] `specs/001-in-memory-todo-cli/quickstart.md`
- [x] `specs/001-in-memory-todo-cli/contracts/cli-interface.md`
- [ ] `specs/001-in-memory-todo-cli/tasks.md` (generated by `/sp.tasks`)

### B. Constitution Compliance Summary

✅ **All 6 principles satisfied**:
1. Incremental Evolution: Repository abstraction enables Phase II swap
2. Production-Ready: Type hints, logging, error handling, docstrings
3. AI-Native: Spec → Plan → Tasks workflow, PHRs created
4. Scalability: 12-factor ready (externalized config, stateless design)
5. Clean Architecture: 4 layers, dependency inversion, domain independence
6. Type Safety: mypy strict mode, full type annotations

✅ **Phase I constraints satisfied**:
- In-memory only: Dict storage
- No external DB: Pure Python dict
- Repository pattern: Interface + implementation
- CLI interface: argparse subcommands

**APPROVED FOR IMPLEMENTATION** ✅
