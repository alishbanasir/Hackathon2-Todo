# Quickstart Guide: Phase I Todo CLI

**Feature**: 001-in-memory-todo-cli
**Date**: 2026-01-02
**Purpose**: Step-by-step guide to set up, build, and use the todo CLI application

## Prerequisites

Before starting, ensure you have:

- **Python 3.13+** installed
- **UV package manager** installed ([installation guide](https://github.com/astral-sh/uv))
- **Git** (for cloning the repository)
- **Terminal/Command Prompt** access

### Verify Prerequisites

```bash
# Check Python version (must be 3.13+)
python --version

# Check UV installation
uv --version

# Expected: uv 0.1.0 or higher
```

## Setup (First Time)

### 1. Initialize Project with UV

```bash
# Create new project
uv init --app todo-cli

# Navigate to project directory
cd todo-cli

# Pin Python version to 3.13
uv python pin 3.13

# Add Rich dependency for beautiful CLI output
uv add rich
```

### 2. Project Structure

After initialization, your project should look like this:

```
todo-cli/
├── src/
│   └── todo/
│       ├── __init__.py
│       ├── domain/          # Domain layer (entities, interfaces)
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── repository.py  (interface)
│       │   └── exceptions.py
│       ├── application/     # Application layer (business logic)
│       │   ├── __init__.py
│       │   └── service.py
│       ├── infrastructure/  # Infrastructure layer (implementations)
│       │   ├── __init__.py
│       │   └── in_memory_repository.py
│       └── interface/       # Interface layer (CLI)
│           ├── __init__.py
│           └── cli.py
├── tests/                   # Tests (Phase II+)
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
└── README.md
```

### 3. Configure pyproject.toml

Ensure your `pyproject.toml` includes:

```toml
[project]
name = "todo-cli"
version = "0.1.0"
description = "Simple in-memory todo CLI application"
requires-python = ">=3.13"
dependencies = [
    "rich>=13.0.0",
]

[project.scripts]
todo = "todo.interface.cli:main"

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = []
```

## Installation (After Setup)

If cloning an existing repository:

```bash
# Clone repository
git clone <repository-url>
cd todo-cli

# Install dependencies
uv sync

# Verify installation
uv run todo help
```

## Basic Usage

### Add a New Task

```bash
uv run todo add "Buy groceries"
```

**Output**:
```
✓ Task added successfully
ID: 1
Description: Buy groceries
Status: Pending
```

### List All Tasks

```bash
uv run todo list
```

**Output**:
```
┌────┬─────────────────────┬────────────┐
│ ID │ Description         │ Status     │
├────┼─────────────────────┼────────────┤
│ 1  │ Buy groceries       │ ○ Pending  │
│ 2  │ Write report        │ ○ Pending  │
│ 3  │ Call dentist        │ ✓ Completed│
└────┴─────────────────────┴────────────┘
```

### Mark Task as Complete

```bash
uv run todo done 1
```

**Output**:
```
✓ Task marked as complete
ID: 1
Description: Buy groceries
Status: Completed
```

### Update Task Description

```bash
uv run todo update 1 "Buy organic groceries"
```

**Output**:
```
✓ Task updated successfully
ID: 1
Description: Buy organic groceries
Status: Pending
```

### Delete a Task

```bash
uv run todo delete 1
```

**Output**:
```
✓ Task deleted successfully
ID: 1
Description: Buy groceries
```

### Get Help

```bash
uv run todo help
# OR
uv run todo --help
# OR
uv run todo -h
```

**Output**:
```
Todo CLI - Simple task management

Usage:
  uv run todo <command> [arguments]

Commands:
  add <description>      Add a new task
  list                   List all tasks
  done <id>              Mark task as complete
  update <id> <desc>     Update task description
  delete <id>            Delete a task
  help                   Show this help message

Examples:
  uv run todo add "Buy groceries"
  uv run todo list
  uv run todo done 1
  uv run todo update 1 "Buy organic groceries"
  uv run todo delete 1
```

## Common Workflows

### Daily Task Management

```bash
# Morning: Add tasks for the day
uv run todo add "Review pull requests"
uv run todo add "Update documentation"
uv run todo add "Team standup meeting"

# View your task list
uv run todo list

# As you complete tasks
uv run todo done 1
uv run todo done 3

# Check remaining tasks
uv run todo list

# End of day: Clean up completed tasks
uv run todo delete 1
uv run todo delete 3
```

### Correcting Mistakes

```bash
# Added task with typo
uv run todo add "Buy grcoeries"

# List to find ID
uv run todo list
# Shows: ID 1 - "Buy grcoeries"

# Fix the typo
uv run todo update 1 "Buy groceries"

# Or delete and re-add
uv run todo delete 1
uv run todo add "Buy groceries"
```

## Error Handling Examples

### Task Not Found

```bash
uv run todo done 999
```

**Output**:
```
Error: Task with ID 999 not found
```

### Empty Description

```bash
uv run todo add ""
```

**Output**:
```
Error: Task description cannot be empty
```

### Invalid Command

```bash
uv run todo invalid
```

**Output**:
```
Error: Invalid command: invalid. Use 'help' for usage.
```

## Development Commands

### Type Checking

```bash
# Run mypy in strict mode
uv run mypy src/ --strict
```

**Expected**: No errors (all code must be type-safe)

### Code Formatting

```bash
# Check formatting with ruff
uv run ruff check src/

# Auto-fix issues
uv run ruff check src/ --fix

# Format code
uv run ruff format src/
```

### Running Tests (Phase II+)

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/todo --cov-report=html
```

## Troubleshooting

### Issue: "uv: command not found"

**Solution**: Install UV package manager

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Issue: "Python 3.13 not found"

**Solution**: Install Python 3.13 or use UV to install it

```bash
# UV can install Python for you
uv python install 3.13

# Or download from python.org
```

### Issue: Tasks disappear after closing terminal

**Expected behavior**: Phase I is in-memory only. Tasks are NOT persisted between sessions.

**Solution**: Wait for Phase II (database persistence)

### Issue: Rich tables not displaying correctly

**Solution**: Ensure terminal supports UTF-8 and colors

```bash
# Check terminal encoding
echo $LANG

# Should show: en_US.UTF-8 or similar

# For Windows, use Windows Terminal or PowerShell 7+
```

### Issue: Type checking fails

**Solution**: Ensure all type hints are present

```bash
# Run mypy to see errors
uv run mypy src/ --strict

# Common fixes:
# - Add return type hints
# - Add parameter type hints
# - Remove 'any' types
```

## Performance Expectations

Based on success criteria:

| Operation | Expected Time | Max Tasks |
|-----------|---------------|-----------|
| Add task | <10ms | N/A |
| List tasks | <20ms | 100 |
| List tasks | <50ms | 1,000 |
| Update/Delete | <5ms | N/A |
| Mark complete | <5ms | N/A |

**Note**: All operations are in-memory, so performance is excellent even with 1,000+ tasks.

## Limitations (Phase I)

### What Works
- ✅ Add, view, update, delete, complete tasks
- ✅ Beautiful CLI table display
- ✅ Clear error messages
- ✅ Help documentation
- ✅ Unicode and emoji support
- ✅ Fast in-memory operations

### What Doesn't Work (Yet)
- ❌ No task persistence (data lost on exit)
- ❌ No task due dates or priorities
- ❌ No search or filtering
- ❌ No multi-user support
- ❌ No web interface (Phase II)
- ❌ No AI features (Phase III)
- ❌ No batch operations

**Coming in future phases!**

## Next Steps

### Ready to Build?

1. Follow `/sp.tasks` to generate implementation task list
2. Implement tasks in priority order (P1 → P4)
3. Test against user story acceptance criteria
4. Commit to git with conventional commit messages

### Want to Extend?

**Phase II**: Add database persistence, web API
**Phase III**: Integrate AI chatbot features
**Phase IV**: Deploy to Kubernetes
**Phase V**: Convert to microservices architecture

## Additional Resources

- **UV Documentation**: https://github.com/astral-sh/uv
- **Rich Documentation**: https://rich.readthedocs.io/
- **Python 3.13 Docs**: https://docs.python.org/3.13/
- **Clean Architecture**: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

## Support

For issues or questions:
1. Check this quickstart guide
2. Review contracts in `specs/001-in-memory-todo-cli/contracts/`
3. Review data model in `specs/001-in-memory-todo-cli/data-model.md`
4. Create GitHub issue with reproduction steps

## Summary

**Quick Commands**:
```bash
# Setup
uv init --app todo-cli && cd todo-cli
uv python pin 3.13
uv add rich

# Use
uv run todo add "Task description"
uv run todo list
uv run todo done <id>
uv run todo update <id> "New description"
uv run todo delete <id>
uv run todo help

# Develop
uv run mypy src/ --strict
uv run ruff check src/
```

**Remember**: Phase I is in-memory only. Tasks are lost when you exit the application. This is intentional for learning Clean Architecture patterns that will support database persistence in Phase II.
