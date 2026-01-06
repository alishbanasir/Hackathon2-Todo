# CLI Interface Contract: Todo Application

**Feature**: 001-in-memory-todo-cli
**Date**: 2026-01-02
**Purpose**: Define command-line interface contract for Phase I

## Overview

The todo CLI provides subcommand-based interface for task management. All commands follow standard Unix conventions with exit codes, help text, and error messaging.

## Command Execution Pattern

```bash
uv run <command> [arguments] [options]
```

## Commands

### 1. Add Task

**Command**: `add`

**Syntax**:
```bash
uv run add <description>
```

**Arguments**:
- `description` (required): Task description as string

**Behavior**:
1. Validate description is non-empty
2. Create task with auto-generated ID
3. Set status to PENDING
4. Display success message with task ID

**Success Output**:
```
✓ Task added successfully
ID: 1
Description: Buy groceries
Status: Pending
```

**Error Cases**:

| Error | Exit Code | Message |
|-------|-----------|---------|
| Empty description | 1 | `Error: Task description cannot be empty` |
| Whitespace-only | 1 | `Error: Task description cannot be empty` |

**Examples**:
```bash
# Success
uv run add "Buy groceries"
✓ Task added successfully (ID: 1)

# Error - empty
uv run add ""
Error: Task description cannot be empty

# Unicode support
uv run add "Купить продукты 🛒"
✓ Task added successfully (ID: 2)
```

---

### 2. List All Tasks

**Command**: `list`

**Syntax**:
```bash
uv run list
```

**Arguments**: None

**Behavior**:
1. Retrieve all tasks from repository
2. Display in rich table format
3. Show ID, description, and status for each task
4. If no tasks, show friendly message

**Success Output** (with tasks):
```
┌────┬─────────────────────┬────────────┐
│ ID │ Description         │ Status     │
├────┼─────────────────────┼────────────┤
│ 1  │ Buy groceries       │ ○ Pending  │
│ 2  │ Write report        │ ✓ Completed│
│ 3  │ Call dentist        │ ○ Pending  │
└────┴─────────────────────┴────────────┘
```

**Success Output** (empty):
```
📝 No tasks yet. Use 'add' to create your first task!
```

**Error Cases**: None (always succeeds)

**Exit Code**: Always 0

---

### 3. Mark Task Complete

**Command**: `done`

**Syntax**:
```bash
uv run done <id>
```

**Arguments**:
- `id` (required): Task ID as positive integer

**Behavior**:
1. Validate ID is positive integer
2. Look up task by ID
3. Update status to COMPLETED
4. Display success message

**Success Output**:
```
✓ Task marked as complete
ID: 1
Description: Buy groceries
Status: Completed
```

**Error Cases**:

| Error | Exit Code | Message |
|-------|-----------|---------|
| Task not found | 1 | `Error: Task with ID {id} not found` |
| Invalid ID format | 1 | `Error: Invalid task ID: {input}` |
| Negative/zero ID | 1 | `Error: Task ID must be a positive number` |

**Examples**:
```bash
# Success
uv run done 1
✓ Task marked as complete (ID: 1)

# Error - not found
uv run done 999
Error: Task with ID 999 not found

# Error - invalid
uv run done abc
Error: Invalid task ID: abc
```

---

### 4. Update Task Description

**Command**: `update`

**Syntax**:
```bash
uv run update <id> <description>
```

**Arguments**:
- `id` (required): Task ID as positive integer
- `description` (required): New task description

**Behavior**:
1. Validate ID and description
2. Look up task by ID
3. Update description (preserve ID and status)
4. Display success message

**Success Output**:
```
✓ Task updated successfully
ID: 1
Description: Buy organic groceries
Status: Pending
```

**Error Cases**:

| Error | Exit Code | Message |
|-------|-----------|---------|
| Task not found | 1 | `Error: Task with ID {id} not found` |
| Empty description | 1 | `Error: Task description cannot be empty` |
| Invalid ID format | 1 | `Error: Invalid task ID: {input}` |

**Examples**:
```bash
# Success
uv run update 1 "Buy organic groceries"
✓ Task updated successfully (ID: 1)

# Error - not found
uv run update 999 "Something"
Error: Task with ID 999 not found

# Error - empty description
uv run update 1 ""
Error: Task description cannot be empty
```

---

### 5. Delete Task

**Command**: `delete`

**Syntax**:
```bash
uv run delete <id>
```

**Arguments**:
- `id` (required): Task ID as positive integer

**Behavior**:
1. Validate ID is positive integer
2. Look up task by ID
3. Remove task from storage
4. Display success message

**Success Output**:
```
✓ Task deleted successfully
ID: 1
Description: Buy groceries
```

**Error Cases**:

| Error | Exit Code | Message |
|-------|-----------|---------|
| Task not found | 1 | `Error: Task with ID {id} not found` |
| Invalid ID format | 1 | `Error: Invalid task ID: {input}` |
| Negative/zero ID | 1 | `Error: Task ID must be a positive number` |

**Examples**:
```bash
# Success
uv run delete 1
✓ Task deleted successfully (ID: 1)

# Error - not found
uv run delete 999
Error: Task with ID 999 not found
```

---

### 6. Help

**Command**: `help` or `-h` or `--help`

**Syntax**:
```bash
uv run help
uv run -h
uv run --help
```

**Arguments**: None

**Behavior**:
Display comprehensive help text with all commands and examples

**Output**:
```
Todo CLI - Simple task management

Usage:
  uv run <command> [arguments]

Commands:
  add <description>      Add a new task
  list                   List all tasks
  done <id>              Mark task as complete
  update <id> <desc>     Update task description
  delete <id>            Delete a task
  help                   Show this help message

Examples:
  uv run add "Buy groceries"
  uv run list
  uv run done 1
  uv run update 1 "Buy organic groceries"
  uv run delete 1

For more information, visit: [project URL]
```

**Exit Code**: 0

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User error (invalid input, task not found, validation failure) |
| 2 | System error (unexpected exception, internal error) |

## Error Message Format

All error messages follow this pattern:
```
[red]Error:[/red] {error_message}
```

Examples:
- `Error: Task with ID 5 not found`
- `Error: Task description cannot be empty`
- `Error: Invalid task ID: abc`

## Success Message Format

All success messages follow this pattern:
```
✓ {success_message}
```

Examples:
- `✓ Task added successfully (ID: 1)`
- `✓ Task marked as complete (ID: 1)`
- `✓ Task updated successfully (ID: 1)`

## Rich Table Display (list command)

**Table Structure**:
- Title: "Todo List"
- Columns: ID (cyan), Description (white), Status (green/yellow)
- Status icons:
  - Pending: `○ Pending` (yellow)
  - Completed: `✓ Completed` (green)

**Example**:
```python
from rich.console import Console
from rich.table import Table

table = Table(title="Todo List")
table.add_column("ID", style="cyan", justify="right")
table.add_column("Description", style="white")
table.add_column("Status", style="green")

for task in tasks:
    status_display = (
        "[green]✓ Completed[/green]"
        if task.status == TaskStatus.COMPLETED
        else "[yellow]○ Pending[/yellow]"
    )
    table.add_row(str(task.id), task.description, status_display)

console = Console()
console.print(table)
```

## Command Parsing (argparse)

**Parser structure**:
```python
import argparse

parser = argparse.ArgumentParser(
    prog="todo",
    description="Simple todo list manager",
    epilog="For more help, visit [project URL]"
)

subparsers = parser.add_subparsers(dest="command", help="Available commands")

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

## Input Validation

| Input | Validation | Error Message |
|-------|------------|---------------|
| Task ID | Must be positive integer | "Invalid task ID: {input}" |
| Task ID | Must exist in repository | "Task with ID {id} not found" |
| Description | Must be non-empty | "Task description cannot be empty" |
| Description | Trim whitespace | (automatic, no error) |
| Command | Must be valid subcommand | "Invalid command: {cmd}. Use 'help' for usage." |

## Unicode and Special Characters

**Support**:
- ✅ Unicode descriptions (e.g., "Купить продукты")
- ✅ Emojis (e.g., "Buy groceries 🛒")
- ✅ Special characters (e.g., quotes, apostrophes)

**Handling**:
- UTF-8 encoding throughout
- Rich library handles display automatically
- No escaping required for user input

## Thread Safety

**Phase I**: Not required (single-user, single-process CLI)

**Phase II+**: Repository will add locking for concurrent access

## Performance Requirements

Based on success criteria:

| Operation | Max Time | Typical Time |
|-----------|----------|--------------|
| Add task | 100ms | <10ms |
| List tasks (100 items) | 50ms | <20ms |
| List tasks (1000 items) | 100ms | <50ms |
| Update/Delete/Complete | 50ms | <5ms |
| Help display | N/A | <10ms |

## Contract Compliance Matrix

| Requirement | Contract Element | Evidence |
|-------------|------------------|----------|
| FR-001 | `add` command | Defined with description argument |
| FR-004 | `list` command | Defined with rich table output |
| FR-005 | `done` command | Defined with ID argument |
| FR-006 | `update` command | Defined with ID and description |
| FR-007 | `delete` command | Defined with ID argument |
| FR-009 | Error messages | Defined for all not-found cases |
| FR-011 | `help` command | Defined with full usage |
| FR-013 | Rich table display | Defined with clear visual separation |
| FR-014 | CLI arguments | All commands use argparse |
| FR-015 | Error messages | Defined for all validation failures |

## Migration to Phase II (API Endpoints)

**Mapping CLI → REST API**:

| CLI Command | HTTP Method | Endpoint | Request Body |
|-------------|-------------|----------|--------------|
| `add <desc>` | POST | `/tasks` | `{"description": "..."}` |
| `list` | GET | `/tasks` | N/A |
| `done <id>` | PATCH | `/tasks/{id}/complete` | N/A |
| `update <id> <desc>` | PUT | `/tasks/{id}` | `{"description": "..."}` |
| `delete <id>` | DELETE | `/tasks/{id}` | N/A |

**Service layer stays identical** - only interface changes (CLI → API).
