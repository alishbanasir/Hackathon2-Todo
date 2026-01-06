---
description: "Task list for Phase I In-Memory Todo CLI implementation"
---

# Tasks: In-Memory Python Todo Console App

**Input**: Design documents from `/specs/001-in-memory-todo-cli/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/

**Tests**: Manual testing only for Phase I (per constitution - automated tests in Phase II+)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/todo/` at repository root
- Layers: `domain/`, `application/`, `infrastructure/`, `interface/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize UV project with `uv init --app todo-cli`
- [ ] T002 Pin Python version to 3.13 with `uv python pin 3.13`
- [ ] T003 [P] Add Rich dependency with `uv add rich`
- [ ] T004 [P] Configure pyproject.toml with project metadata and mypy strict settings
- [ ] T005 [P] Create .gitignore file with Python/UV patterns
- [ ] T006 Create src/todo/ directory structure (domain/, application/, infrastructure/, interface/)
- [ ] T007 [P] Create __init__.py files in src/todo/ and all subdirectories
- [ ] T008 [P] Create README.md with project description and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain layer that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 [P] Create TaskStatus enum in src/todo/domain/models.py with PENDING and COMPLETED values
- [ ] T010 [P] Create Task dataclass in src/todo/domain/models.py with id, description, status fields
- [ ] T011 Add validation in Task.__post_init__() for non-empty description and positive ID
- [ ] T012 [P] Create base TodoException class in src/todo/domain/exceptions.py
- [ ] T013 [P] Create TaskNotFoundError exception in src/todo/domain/exceptions.py
- [ ] T014 [P] Create EmptyDescriptionError exception in src/todo/domain/exceptions.py
- [ ] T015 [P] Create InvalidTaskIdError exception in src/todo/domain/exceptions.py
- [ ] T016 Create TodoRepositoryInterface (ABC) in src/todo/domain/repository.py with abstract methods: add(), get_all(), get_by_id(), update(), mark_complete(), delete()
- [ ] T017 Add type hints and docstrings to all domain layer classes and methods

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks and view them in a beautiful table

**Independent Test**: Can be fully tested by running `uv run todo add "Buy groceries"` and `uv run todo list` to verify task creation and display

### Implementation for User Story 1

- [ ] T018 [P] [US1] Create InMemoryTodoRepository class in src/todo/infrastructure/in_memory_repository.py with __init__ setting up empty dict storage and _next_id counter
- [ ] T019 [US1] Implement add() method in InMemoryTodoRepository with sequential ID generation and Task creation
- [ ] T020 [US1] Implement get_all() method in InMemoryTodoRepository to return list of all tasks
- [ ] T021 [US1] Implement get_by_id() method in InMemoryTodoRepository with Optional[Task] return type
- [ ] T022 [P] [US1] Create TodoService class in src/todo/application/service.py with repository dependency injection
- [ ] T023 [US1] Implement TodoService.add_task(description: str) -> Task method with validation and logging
- [ ] T024 [US1] Implement TodoService.get_all_tasks() -> List[Task] method
- [ ] T025 [P] [US1] Create argparse parser in src/todo/interface/cli.py with subcommands structure
- [ ] T026 [US1] Implement "add" subcommand parser with description argument in cli.py
- [ ] T027 [US1] Implement "list" subcommand parser in cli.py
- [ ] T028 [US1] Create display_tasks() function in cli.py using Rich Table with ID, Description, Status columns
- [ ] T029 [US1] Implement handle_add() function in cli.py calling service.add_task() with Rich success message
- [ ] T030 [US1] Implement handle_list() function in cli.py calling service.get_all_tasks() with Rich table display or empty message
- [ ] T031 [US1] Create main() entry point in cli.py with repository and service initialization
- [ ] T032 [US1] Add error handling in main() for EmptyDescriptionError with Rich error formatting
- [ ] T033 [US1] Configure project.scripts in pyproject.toml to map "todo" command to cli:main
- [ ] T034 [US1] Add structured logging setup in service.py for add and list operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

**Manual Test Plan for US1**:
1. Test add task: `uv run todo add "Buy groceries"` → verify success message with ID 1
2. Test add another: `uv run todo add "Write report"` → verify success with ID 2
3. Test list tasks: `uv run todo list` → verify Rich table shows both tasks with pending status
4. Test empty list: Start fresh session, `uv run todo list` → verify friendly empty message
5. Test empty description: `uv run todo add ""` → verify error message
6. Test Unicode: `uv run todo add "Купить продукты 🛒"` → verify success and correct display

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Enable users to mark tasks as completed and see status changes in list view

**Independent Test**: Can be tested by adding tasks with US1, marking them complete, and viewing updated status in list

### Implementation for User Story 2

- [ ] T035 [US2] Implement mark_complete() method in InMemoryTodoRepository to update task status to COMPLETED
- [ ] T036 [US2] Implement TodoService.mark_task_complete(task_id: int) -> Task method with TaskNotFoundError handling
- [ ] T037 [US2] Implement "done" subcommand parser in cli.py with task_id argument
- [ ] T038 [US2] Implement handle_done() function in cli.py calling service.mark_task_complete() with Rich success message
- [ ] T039 [US2] Add error handling in main() for TaskNotFoundError with Rich error formatting
- [ ] T040 [US2] Update display_tasks() to show "✓ Completed" in green and "○ Pending" in yellow based on status
- [ ] T041 [US2] Add structured logging in service.py for mark_complete operations

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

**Manual Test Plan for US2**:
1. Add 3 tasks using US1
2. Test mark complete: `uv run todo done 1` → verify success message
3. Test list with mixed status: `uv run todo list` → verify task 1 shows "✓ Completed" in green
4. Test invalid ID: `uv run todo done 999` → verify error message "Task with ID 999 not found"
5. Test negative ID: `uv run todo done -1` → verify error message
6. Mark all tasks complete → verify all show completed status

---

## Phase 5: User Story 3 - Update Task Descriptions (Priority: P3)

**Goal**: Enable users to edit task descriptions while preserving ID and status

**Independent Test**: Can be tested by creating tasks with US1, updating descriptions, and verifying changes persist

### Implementation for User Story 3

- [ ] T042 [US3] Implement update() method in InMemoryTodoRepository to update task description
- [ ] T043 [US3] Implement TodoService.update_task(task_id: int, description: str) -> Task method with validation
- [ ] T044 [US3] Implement "update" subcommand parser in cli.py with task_id and description arguments
- [ ] T045 [US3] Implement handle_update() function in cli.py calling service.update_task() with Rich success message
- [ ] T046 [US3] Add validation in handle_update() for empty description with Rich error message
- [ ] T047 [US3] Add structured logging in service.py for update operations

**Checkpoint**: All user stories (1, 2, 3) should now be independently functional

**Manual Test Plan for US3**:
1. Add task: `uv run todo add "Buy milk"`
2. Test update: `uv run todo update 1 "Buy organic milk"` → verify success and new description
3. Test list: `uv run todo list` → verify updated description shown
4. Test preserve status: Mark task 1 complete, update it, verify status stays completed
5. Test invalid ID: `uv run todo update 999 "Something"` → verify error
6. Test empty description: `uv run todo update 1 ""` → verify validation error

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Enable users to remove tasks they no longer need

**Independent Test**: Can be tested by creating tasks with US1, deleting specific ones, and verifying removal from list

### Implementation for User Story 4

- [ ] T048 [US4] Implement delete() method in InMemoryTodoRepository to remove task and return success boolean
- [ ] T049 [US4] Implement TodoService.delete_task(task_id: int) -> bool method with TaskNotFoundError handling
- [ ] T050 [US4] Implement "delete" subcommand parser in cli.py with task_id argument
- [ ] T051 [US4] Implement handle_delete() function in cli.py calling service.delete_task() with Rich success message
- [ ] T052 [US4] Add structured logging in service.py for delete operations

**Checkpoint**: All user stories should now be independently functional

**Manual Test Plan for US4**:
1. Add 5 tasks using US1
2. Test delete: `uv run todo delete 2` → verify success message
3. Test list: `uv run todo list` → verify 4 tasks remain, ID 2 is gone
4. Test invalid ID: `uv run todo delete 999` → verify error message
5. Delete all tasks one by one → verify list eventually shows empty message
6. Verify IDs are not reused: Add new task after deletions → verify ID continues from highest used

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T053 [P] Implement "help" subcommand in cli.py displaying all commands with examples
- [ ] T054 [P] Add --help/-h flag support to argparse parser
- [ ] T055 [P] Configure exit codes in cli.py (0=success, 1=user error, 2=system error)
- [ ] T056 Add comprehensive docstrings to all public methods in service.py
- [ ] T057 Add comprehensive docstrings to all public methods in repository.py
- [ ] T058 [P] Add type hints validation with `uv run mypy src/todo/ --strict`
- [ ] T059 [P] Add code formatting check with `uv run ruff check src/todo/`
- [ ] T060 [P] Create comprehensive README.md with quickstart examples and architecture explanation
- [ ] T061 Test all edge cases: Unicode descriptions, extremely long descriptions, rapid commands
- [ ] T062 Performance validation: Test with 1000 tasks to ensure <100ms operations
- [ ] T063 Run full manual test suite for all 4 user stories (P1-P4) end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses display from US1 but is independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent, no dependencies on US1/US2
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent, no dependencies on US1/US2/US3

### Within Each User Story

- Repository methods before service methods
- Service methods before CLI handlers
- CLI handlers before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models, exceptions, and interfaces within Foundational phase marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# These tasks can run simultaneously (different files):
T018: InMemoryTodoRepository class skeleton
T022: TodoService class skeleton
T025: argparse parser setup in cli.py

# After skeleton tasks complete, these can run in parallel:
T019: add() method in repository
T020: get_all() method in repository
T023: add_task() in service
T024: get_all_tasks() in service
T026: "add" subcommand parser
T027: "list" subcommand parser
T028: display_tasks() function
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add and View)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Manual test: Add tasks and view them
   - Verify Rich table displays correctly
   - Test error cases (empty description)
5. Deploy/demo if ready

**Result**: Minimal viable product with basic task management

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Mark Complete) → Test independently → Deploy/Demo
4. Add User Story 3 (Update) → Test independently → Deploy/Demo
5. Add User Story 4 (Delete) → Test independently → Deploy/Demo
6. Polish → Final release
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Add/View)
   - Developer B: User Story 2 (Mark Complete)
   - Developer C: User Story 3 (Update)
   - Developer D: User Story 4 (Delete)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each completed task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Phase I uses manual testing only (per constitution - automated tests in Phase II+)

---

## Task Count Summary

- **Total Tasks**: 63
- **Setup (Phase 1)**: 8 tasks
- **Foundational (Phase 2)**: 9 tasks (CRITICAL - blocks all user stories)
- **User Story 1 (P1)**: 17 tasks
- **User Story 2 (P2)**: 7 tasks
- **User Story 3 (P3)**: 6 tasks
- **User Story 4 (P4)**: 5 tasks
- **Polish (Phase 7)**: 11 tasks

**Parallel Opportunities**: 31 tasks marked [P] can run simultaneously

**Critical Path**: Setup (8) → Foundational (9) → User Story 1 (17) = 34 tasks minimum for MVP

---

## Validation Checklist

Before marking tasks.md complete:

- [x] All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- [x] Every user story phase has [Story] labels (US1, US2, US3, US4)
- [x] Setup and Foundational phases have NO story labels
- [x] All tasks have unique sequential IDs (T001-T063)
- [x] File paths are included in task descriptions
- [x] Dependencies section shows execution order
- [x] Independent test criteria defined for each user story
- [x] MVP scope identified (User Story 1 only)
- [x] Parallel opportunities marked with [P]
- [x] Implementation strategy includes incremental delivery plan

**VALIDATION RESULT**: ✅ PASS - All tasks properly formatted and organized by user story
