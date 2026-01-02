# Data Model: Phase I In-Memory Todo CLI

**Feature**: 001-in-memory-todo-cli
**Date**: 2026-01-02
**Purpose**: Define domain entities, value objects, and data relationships

## Domain Entities

### Task

**Purpose**: Represents a single todo item in the user's task list.

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | `int` | Required, Unique, Auto-generated, Positive, Sequential | Unique identifier for the task, assigned automatically starting from 1 |
| `description` | `str` | Required, Non-empty, Max 10000 chars | Human-readable description of what needs to be done |
| `status` | `TaskStatus` | Required, Enum | Current state of the task (pending or completed) |

**Invariants**:
- ID MUST be assigned sequentially starting from 1
- ID MUST NEVER be reused within a session (even after deletion)
- Description MUST NOT be empty string or whitespace-only
- Status MUST be one of the valid TaskStatus enum values

**State Transitions**:
```
[Created] → status: PENDING
    ↓
[Mark Complete] → status: COMPLETED
    ↓
[No reverse transition - tasks cannot be unmarked as complete in Phase I]
```

**Python Implementation**:
```python
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    """Enumeration of possible task states"""
    PENDING = "pending"
    COMPLETED = "completed"

@dataclass
class Task:
    """
    Domain entity representing a todo task.

    Attributes:
        id: Unique sequential identifier
        description: What needs to be done
        status: Current state (pending or completed)
    """
    id: int
    description: str
    status: TaskStatus

    def __post_init__(self) -> None:
        """Validate task attributes after initialization"""
        if not self.description or not self.description.strip():
            raise ValueError("Task description cannot be empty")
        if self.id < 1:
            raise ValueError("Task ID must be positive")
```

**Validation Rules**:
1. **ID validation**:
   - MUST be positive integer (>= 1)
   - MUST be unique within the session
   - MUST be sequential (no gaps except after deletion)

2. **Description validation** (FR-008):
   - MUST NOT be empty string
   - MUST NOT be whitespace-only
   - SHOULD handle Unicode characters
   - SHOULD trim leading/trailing whitespace
   - RECOMMENDED max length: 10,000 characters (edge case handling)

3. **Status validation**:
   - MUST be valid TaskStatus enum value
   - Default on creation: PENDING

## Value Objects

### TaskStatus (Enum)

**Purpose**: Type-safe enumeration of task states.

**Values**:
- `PENDING`: Task is not yet completed
- `COMPLETED`: Task has been finished

**Why Enum?**
- Type safety (prevents invalid status values)
- IDE autocomplete support
- Clear intent (better than string literals)
- Extensible for future states (Phase II might add "IN_PROGRESS")

## Aggregates

**No aggregates in Phase I** - Task is a standalone entity with no child objects.

Future phases might introduce:
- **TaskList aggregate** (collection of tasks with metadata)
- **User aggregate** (Phase II - multi-user support)
- **Project aggregate** (Phase III+ - task categorization)

## Repository Interface

**Purpose**: Abstract storage operations to enable Phase II database migration.

**Interface Definition**:
```python
from abc import ABC, abstractmethod
from typing import List, Optional

class TodoRepositoryInterface(ABC):
    """
    Abstract interface for task persistence.

    This interface decouples business logic from storage implementation,
    enabling seamless migration from in-memory (Phase I) to database (Phase II).
    """

    @abstractmethod
    def add(self, description: str) -> Task:
        """
        Create and store a new task.

        Args:
            description: Non-empty task description

        Returns:
            Created task with auto-generated ID and PENDING status

        Raises:
            ValueError: If description is empty
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Task]:
        """
        Retrieve all tasks.

        Returns:
            List of all tasks (may be empty)
        """
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task if found, None otherwise
        """
        pass

    @abstractmethod
    def update(self, task_id: int, description: str) -> Task:
        """
        Update a task's description.

        Args:
            task_id: ID of the task to update
            description: New non-empty description

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
            ValueError: If description is empty
        """
        pass

    @abstractmethod
    def mark_complete(self, task_id: int) -> Task:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to complete

        Returns:
            Updated task with COMPLETED status

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if deleted, False if not found
        """
        pass
```

## In-Memory Implementation Details

**Storage Structure**:
```python
class InMemoryTodoRepository(TodoRepositoryInterface):
    """Concrete in-memory implementation for Phase I"""

    def __init__(self):
        self._storage: Dict[int, Task] = {}
        self._next_id: int = 1
        self._lock: threading.Lock = threading.Lock()  # Thread safety

    def add(self, description: str) -> Task:
        with self._lock:
            task = Task(
                id=self._next_id,
                description=description.strip(),
                status=TaskStatus.PENDING
            )
            self._storage[self._next_id] = task
            self._next_id += 1
            return task
```

**Key design decisions**:
1. **Dictionary storage**: O(1) lookup by ID
2. **Atomic ID increment**: Thread-safe ID generation
3. **No ID reuse**: Even after deletion, IDs increment
4. **In-memory only**: Data lost when program exits (per FR-012)

## Domain Exceptions

**Custom exception hierarchy**:
```python
class TodoException(Exception):
    """Base exception for todo domain"""
    pass

class TaskNotFoundError(TodoException):
    """Raised when a task ID doesn't exist"""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")

class EmptyDescriptionError(TodoException):
    """Raised when task description is empty"""
    def __init__(self):
        super().__init__("Task description cannot be empty")

class InvalidTaskIdError(TodoException):
    """Raised when task ID is invalid (negative, zero, etc.)"""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Invalid task ID: {task_id}")
```

## Data Relationships

**Phase I**: No relationships (single entity system)

**Future phases**:
- **Phase II**: User ← has many → Tasks (1:N)
- **Phase III**: Project ← has many → Tasks (1:N)
- **Phase III**: Task ← belongs to → User (N:1)

## Validation Summary

| Rule | Location | Enforcement |
|------|----------|-------------|
| Non-empty description | Task.__post_init__(), Repository.add() | ValueError |
| Positive task ID | Task.__post_init__() | ValueError |
| Unique task ID | Repository._storage (dict keys) | Automatic (dict behavior) |
| Valid status enum | TaskStatus type system | Type error at runtime |
| Sequential IDs | Repository._next_id increment | Implementation logic |
| No ID reuse | Repository._next_id never decrements | Implementation logic |

## Migration Path to Phase II

### Database Schema (SQLAlchemy example)

```python
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TaskModel(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(10000), nullable=False)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
```

**Migration strategy**:
1. Domain `Task` dataclass stays identical
2. Create `TaskModel` for ORM
3. Repository maps `TaskModel` ↔ `Task`
4. No service layer changes required

**Zero business logic changes** - this is the power of Clean Architecture + Repository pattern.

## Performance Considerations

**Phase I (In-Memory)**:
- Add task: O(1)
- Get all: O(n) where n = number of tasks
- Get by ID: O(1) (dictionary lookup)
- Update: O(1)
- Mark complete: O(1)
- Delete: O(1)

**Expected scale**: 1,000 tasks (per SC-002)
- Get all with 1,000 tasks: <1ms
- Individual operations: <0.1ms

**No performance concerns for Phase I**.

## Open Questions

**None** - data model is complete for Phase I scope.

## Compliance Check

| Requirement | Compliance | Evidence |
|-------------|------------|----------|
| FR-002: Auto-assigned IDs | ✅ | Repository._next_id |
| FR-003: Store ID, description, status | ✅ | Task dataclass |
| FR-008: Non-empty descriptions | ✅ | Validation in __post_init__ |
| FR-012: In-memory only | ✅ | Dict storage |
| Constitution: Repository pattern | ✅ | TodoRepositoryInterface + impl |
| Constitution: Type hints | ✅ | Full type annotations |
| Constitution: Domain independence | ✅ | No framework imports in domain |
