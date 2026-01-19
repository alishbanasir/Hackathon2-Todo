---
title: Todo AI API Backend
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---
# Todo CLI - Phase I: In-Memory Task Management

A clean, CLI-based task management tool built with Clean Architecture principles.

## Features

- ✅ Add tasks with descriptions
- ✅ View all tasks in a beautiful table
- ✅ Mark tasks as complete
- ✅ Update task descriptions
- ✅ Delete tasks
- ✅ In-memory storage (no persistence)

## Requirements

- Python 3.13+
- UV package manager

## Installation

```bash
# Install dependencies
uv sync

# Run the application
uv run todo --help
```

## Usage

```bash
# Add a new task
uv run todo add "Buy groceries"

# List all tasks
uv run todo list

# Mark a task as complete
uv run todo done 1

# Update a task description
uv run todo update 1 "Buy organic groceries"

# Delete a task
uv run todo delete 1

# Show help
uv run todo help
```

## Architecture

This project follows Clean Architecture with four distinct layers:

- **Domain Layer** (`src/todo/domain/`): Entities, value objects, repository interfaces
- **Application Layer** (`src/todo/application/`): Business logic and use cases
- **Infrastructure Layer** (`src/todo/infrastructure/`): Concrete implementations (in-memory repository)
- **Interface Layer** (`src/todo/interface/`): CLI with argparse and Rich

## Development

```bash
# Type checking
uv run mypy src/todo/ --strict

# Code formatting
uv run ruff check src/todo/
uv run ruff format src/todo/
```

## Note

Phase I uses in-memory storage. Tasks are lost when the application exits. Database persistence will be added in Phase II.

## License

MIT
