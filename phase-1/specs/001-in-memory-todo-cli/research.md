# Research: Phase I In-Memory Todo CLI

**Feature**: 001-in-memory-todo-cli
**Date**: 2026-01-02
**Purpose**: Technical research for implementation decisions

## Research Questions

### Q1: CLI Framework Selection (Python 3.13)

**Decision**: Use built-in `argparse` for command parsing, not Typer

**Rationale**:
- **Zero external dependencies for core CLI**: argparse is in Python standard library
- **Simpler for Phase I scope**: Only 5 commands (add, list, done, update, delete, help)
- **Constitution compliance**: Avoids framework lock-in (Clean Architecture principle)
- **Rich for display only**: User specified Rich for beautiful tables, not CLI parsing
- **Migration path**: argparse → FastAPI endpoints in Phase II is straightforward

**Alternatives Considered**:
1. **Typer**: Modern, type-hinted CLI framework
   - Rejected: Adds external dependency for minimal Phase I benefit
   - Adds ~10 dependencies transitively
   - Overkill for simple CRUD commands

2. **Click**: Popular CLI framework
   - Rejected: Similar to Typer - unnecessary abstraction for 5 commands
   - Decorators create harder migration path to API endpoints

3. **argparse (CHOSEN)**: Standard library argument parser
   - ✅ Zero dependencies
   - ✅ Simple for Phase I
   - ✅ Well-documented, stable
   - ✅ Easy to extract logic for FastAPI in Phase II

### Q2: Repository Pattern Implementation

**Decision**: Abstract repository interface with in-memory dictionary implementation

**Rationale**:
- **Constitution requirement**: "Repository pattern MUST be used even for in-memory storage"
- **Phase II migration**: Swap `InMemoryTodoRepository` → `SQLAlchemyTodoRepository` without changing business logic
- **Dependency inversion**: Service layer depends on `TodoRepositoryInterface`, not concrete class
- **Testing**: Easy to mock repository for future unit tests

**Implementation Design**:

```python
# Domain layer (src/todo/domain/)
from abc import ABC, abstractmethod
from typing import List, Optional

class TodoRepositoryInterface(ABC):
    @abstractmethod
    def add(self, task: Task) -> Task: ...

    @abstractmethod
    def get_all(self) -> List[Task]: ...

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]: ...

    @abstractmethod
    def update(self, task: Task) -> Task: ...

    @abstractmethod
    def delete(self, task_id: int) -> bool: ...

# Infrastructure layer (src/todo/infrastructure/)
class InMemoryTodoRepository(TodoRepositoryInterface):
    def __init__(self):
        self._storage: Dict[int, Task] = {}
        self._next_id: int = 1
```

**Alternatives Considered**:
1. **Direct dictionary manipulation in service**:
   - Rejected: Violates constitution, blocks Phase II migration

2. **File-based storage**:
   - Rejected: Out of scope for Phase I per spec

3. **Abstract repository (CHOSEN)**:
   - ✅ Constitution compliant
   - ✅ Clean Architecture adherence
   - ✅ Seamless Phase II transition

### Q3: Type Checking and Validation

**Decision**: Use Python 3.13 type hints with mypy strict mode + dataclasses

**Rationale**:
- **Constitution requirement**: "mypy strict mode MUST pass"
- **Python 3.13**: Latest stable, user specified 3.13+
- **No Pydantic in Phase I**: Pydantic is for Phase II FastAPI (per constitution)
- **Dataclasses for Task model**: Built-in, type-safe, immutable option

**Implementation**:
```python
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"

@dataclass
class Task:
    id: int
    description: str
    status: TaskStatus
```

**Alternatives Considered**:
1. **Pydantic models**:
   - Rejected: Pydantic is for Phase II+ (FastAPI integration per constitution)
   - Adds unnecessary dependency in Phase I

2. **TypedDict**:
   - Rejected: Less type-safe than dataclasses, no methods

3. **dataclasses (CHOSEN)**:
   - ✅ Standard library (Python 3.7+)
   - ✅ Type-safe with mypy
   - ✅ Clean, simple for Phase I
   - ✅ Easy to wrap with Pydantic in Phase II

### Q4: Structured Logging

**Decision**: Use Python standard library `logging` with structured format, NOT structlog

**Rationale**:
- **Constitution says**: "structlog (Python)" but Phase I is CLI-only
- **Pragmatic interpretation**: Standard library logging is sufficient for Phase I
- **Migration path**: Add structlog in Phase II when needed for API logging
- **Phase I scope**: Minimal logging needed (errors, debug info)
- **Constitution compliance**: Structured format (JSON) using stdlib logging

**Implementation**:
```python
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

# Use for error logging only in Phase I
```

**Alternatives Considered**:
1. **structlog**:
   - Deferred: Add in Phase II when API logging becomes critical
   - Phase I CLI doesn't need advanced structured logging

2. **print() statements**:
   - Rejected: Constitution forbids "no print statements except CLI output"

3. **stdlib logging with structured format (CHOSEN)**:
   - ✅ Constitution compliant (structured format)
   - ✅ Sufficient for Phase I
   - ✅ Easy migration to structlog in Phase II

### Q5: Display Library for CLI

**Decision**: Use Rich for table display and console output

**Rationale**:
- **User specified**: "Install `rich` (for beautiful CLI tables)"
- **FR-013 requirement**: "Display tasks in human-readable format with clear visual separation"
- **Rich features**: Tables, colors, formatting without complex setup
- **Modern Python**: Well-maintained, popular library

**Implementation**:
```python
from rich.console import Console
from rich.table import Table

def display_tasks(tasks: List[Task]) -> None:
    console = Console()
    table = Table(title="Todo List")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")

    for task in tasks:
        status_display = "✓ Completed" if task.status == TaskStatus.COMPLETED else "○ Pending"
        table.add_row(str(task.id), task.description, status_display)

    console.print(table)
```

**No alternatives considered** - user specified Rich explicitly.

### Q6: UV Package Manager Setup

**Decision**: Use `uv init --app` with Python 3.13 configuration

**Rationale**:
- **User specified**: "Use `uv init --app` to create the project structure"
- **Modern Python packaging**: UV is fast, reliable package manager
- **User requirement**: "Project initialized and managed using 'UV' (Python 3.13+)"

**Project initialization**:
```bash
uv init --app todo-cli
cd todo-cli
uv python pin 3.13
uv add rich
```

**pyproject.toml configuration**:
```toml
[project]
name = "todo-cli"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["rich>=13.0.0"]

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
```

**No alternatives considered** - user requirement.

### Q7: Error Handling Strategy

**Decision**: Custom exception hierarchy with graceful CLI error display

**Rationale**:
- **FR-009**: "Return clear error messages when operations reference non-existent task IDs"
- **FR-010**: "Handle invalid input gracefully without crashing"
- **Constitution**: "Error handling MUST be explicit (no bare except clauses)"

**Implementation**:
```python
# src/todo/domain/exceptions.py
class TodoException(Exception):
    """Base exception for todo application"""
    pass

class TaskNotFoundError(TodoException):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")

class EmptyDescriptionError(TodoException):
    def __init__(self):
        super().__init__("Task description cannot be empty")

class InvalidCommandError(TodoException):
    def __init__(self, command: str):
        super().__init__(f"Invalid command: {command}")
```

**CLI error handling**:
```python
try:
    # Execute command
except TaskNotFoundError as e:
    console.print(f"[red]Error:[/red] {e}", style="bold")
    sys.exit(1)
except EmptyDescriptionError as e:
    console.print(f"[red]Error:[/red] {e}", style="bold")
    sys.exit(1)
```

**Alternatives Considered**:
1. **Generic exceptions**: Rejected - less informative for users
2. **Silent failures**: Rejected - violates FR-010
3. **Custom exceptions (CHOSEN)**: ✅ Clear, testable, user-friendly

### Q8: Command Interface Design

**Decision**: Subcommand-based CLI with argparse

**Rationale**:
- **FR-014**: "Accept commands via command-line arguments or interactive prompts"
- **User guidance**: Commands: `add`, `list`, `done`, `update`, `delete`
- **Standard pattern**: Git-like subcommands (familiar UX)

**Command structure**:
```bash
uv run todo add "Buy groceries"
uv run todo list
uv run todo done 1
uv run todo update 1 "Buy organic groceries"
uv run todo delete 1
uv run todo help
```

**Implementation**:
```python
parser = argparse.ArgumentParser(description="Todo CLI")
subparsers = parser.add_subparsers(dest="command")

# Add command
add_parser = subparsers.add_parser("add", help="Add a new task")
add_parser.add_argument("description", type=str, help="Task description")

# List command
list_parser = subparsers.add_parser("list", help="List all tasks")

# Done command
done_parser = subparsers.add_parser("done", help="Mark task as complete")
done_parser.add_argument("id", type=int, help="Task ID")

# Update command
update_parser = subparsers.add_parser("update", help="Update task description")
update_parser.add_argument("id", type=int, help="Task ID")
update_parser.add_argument("description", type=str, help="New description")

# Delete command
delete_parser = subparsers.add_parser("delete", help="Delete a task")
delete_parser.add_argument("id", type=int, help="Task ID")
```

**Alternative considered**:
- **Interactive REPL**: Deferred to potential Phase I enhancement
- **Subcommand CLI (CHOSEN)**: ✅ Meets FR-014, simple, standard

## Technology Stack Summary

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Language** | Python 3.13 | User requirement, latest stable |
| **Package Manager** | UV | User requirement |
| **CLI Framework** | argparse (stdlib) | Zero dependencies, simple, Phase II migration |
| **Display Library** | Rich | User requirement, beautiful tables |
| **Domain Model** | dataclasses | Type-safe, stdlib, mypy compatible |
| **Repository** | Abstract interface + in-memory dict | Constitution requirement, Clean Architecture |
| **Type Checking** | mypy strict mode | Constitution requirement |
| **Logging** | stdlib logging (structured JSON) | Phase I sufficient, structlog in Phase II |
| **Error Handling** | Custom exception hierarchy | Clear, testable, user-friendly |

## Constitution Compliance Matrix

| Principle | Compliance | Evidence |
|-----------|------------|----------|
| **I. Incremental Evolution** | ✅ PASS | Repository abstraction enables Phase II database swap |
| **II. Production-Ready Standards** | ✅ PASS | Type hints, structured logging, explicit error handling |
| **III. AI-Native Development** | ✅ PASS | Spec → Plan → Tasks workflow, PHR creation |
| **IV. Scalability & Portability** | ✅ PASS | Clean Architecture, externalized config ready |
| **V. Clean Architecture** | ✅ PASS | Domain → Application → Infrastructure layers |
| **VI. Type Safety** | ✅ PASS | mypy strict mode, dataclasses, type hints |

## Phase I Constraints Compliance

| Constraint | Compliance | Evidence |
|------------|------------|----------|
| **In-memory only** | ✅ PASS | Dictionary-based repository, no DB |
| **No external DB** | ✅ PASS | No SQLite, PostgreSQL, files |
| **Repository pattern** | ✅ PASS | Abstract interface + concrete implementation |
| **CLI interface** | ✅ PASS | argparse subcommands |

## Performance Expectations

Based on SC-001 through SC-005:

- **Command execution**: <100ms (in-memory operations, minimal overhead)
- **1000 task capacity**: Dictionary lookup O(1), no performance issues
- **Response time**: <50ms for <100 tasks (easily achievable with in-memory)
- **Launch time**: <5 seconds (Python startup + Rich import)

**No performance concerns** for Phase I in-memory implementation.

## Migration Path to Phase II

### Repository Swap Strategy

1. **Keep interface unchanged**:
   ```python
   # Phase I
   repository = InMemoryTodoRepository()

   # Phase II (zero service layer changes)
   repository = SQLAlchemyTodoRepository(db_url)
   ```

2. **Service layer remains identical**: Business logic doesn't know about storage
3. **CLI → FastAPI**: Extract service calls, wrap in API endpoints
4. **Add Pydantic models**: Wrap domain models for API validation

### No Breaking Changes Required

- Domain models (Task, TaskStatus) stay the same
- Service layer stays the same
- Only swap repository implementation and add API layer

## Open Questions / Decisions Deferred

**None** - all technical decisions resolved for Phase I implementation.

## Next Steps

1. Execute `/sp.tasks` to generate implementation tasks
2. Follow Clean Architecture layers:
   - Domain: models.py, exceptions.py, repository interface
   - Application: service.py (business logic)
   - Infrastructure: in_memory_repository.py
   - Interface: cli.py (argparse + Rich)
3. Implement in priority order (P1 → P4 user stories)
4. Manual testing against acceptance criteria
