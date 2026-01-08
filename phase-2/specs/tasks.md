# Implementation Tasks: Todo Full-Stack Web Application

**Feature**: 002-fullstack-web-app
**Branch**: `002-fullstack-web-app`
**Created**: 2026-01-07
**Based on**: [plan.md](./plan.md) | [spec.md](./spec.md)

## Overview

This document breaks down the Phase II implementation into granular, executable tasks organized by user story priority. Each phase corresponds to a user story from spec.md (US1=P1, US2=P2, etc.) and can be independently implemented and tested.

**User Stories**:
- **US1** (P1): User Registration and Authentication - Foundation for multi-user functionality
- **US2** (P2): Create and View Personal Todos - Core business value
- **US3** (P3): Update and Complete Todos - Lifecycle management
- **US4** (P4): Delete Todos - Cleanup capability
- **US5** (P3): Responsive Web Interface - Cross-device UX (built into all frontend tasks)

**Architecture**:
- **Backend**: Python 3.11+ / FastAPI / SQLModel / Neon PostgreSQL
- **Frontend**: TypeScript 5.x / Next.js 16+ / Tailwind CSS
- **All code in**: `phase-2/backend/` and `phase-2/frontend/`

---

## Task Format

Each task follows this strict format:
```
- [ ] [TaskID] [Markers] Description with file path
```

**Markers**:
- `[P]` = Parallelizable (can run concurrently with other [P] tasks in same phase)
- `[US#]` = User Story label (required for story phases only)

**Example**: `- [ ] T025 [P] [US2] Create TodoRepository in phase-2/backend/src/repositories/todo_repository.py`

---

## Phase 1: Project Setup & Infrastructure

**Goal**: Initialize project structure, dependencies, and shared infrastructure

**Deliverables**: Working backend and frontend scaffolds with database connection

### Backend Setup

- [X] T001 Create backend directory structure per plan.md in phase-2/backend/
- [X] T002 [P] Create requirements.txt with FastAPI 0.109+, SQLModel 0.0.14+, python-jose, argon2-cffi, structlog, pytest
- [X] T003 [P] Create pyproject.toml with project metadata and tool configurations
- [X] T004 [P] Create mypy.ini with strict mode configuration
- [X] T005 [P] Create pytest.ini with test discovery settings
- [X] T006 [P] Create .env.example with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS
- [X] T007 Create phase-2/backend/src/__init__.py (empty module marker)
- [X] T008 Create phase-2/backend/src/config.py with Settings class using pydantic-settings
- [X] T009 Create phase-2/backend/src/database.py with async SQLModel engine and session management
- [X] T010 [P] Initialize Alembic with `alembic init alembic` in phase-2/backend/
- [X] T011 Configure Alembic env.py to use SQLModel metadata and async engine

### Frontend Setup

- [X] T012 Create frontend directory structure per plan.md in phase-2/frontend/
- [X] T013 [P] Initialize Next.js 16+ with TypeScript: `npx create-next-app@latest --typescript --tailwind --app`
- [X] T014 [P] Create .env.local.example with BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL
- [X] T015 Update tsconfig.json to enable strict mode and all type safety options
- [X] T016 [P] Update tailwind.config.ts with mobile-first breakpoints (sm, md, lg, xl)
- [X] T017 [P] Create phase-2/frontend/lib/types.ts with User, Todo, API request/response interfaces
- [X] T018 [P] Create phase-2/frontend/lib/utils.ts with classnames utility (cn function)

### Shared Infrastructure

- [X] T019 Create Neon PostgreSQL database project via Neon console
- [X] T020 Copy Neon connection string to phase-2/backend/.env as DATABASE_URL
- [X] T021 Generate BETTER_AUTH_SECRET (256-bit) and add to both .env and .env.local
- [X] T022 Verify backend can connect to Neon database (run test script)
- [X] T023 [P] Create .gitignore entries for .env, .env.local, venv, node_modules, __pycache__

---

## Phase 2: Foundational Layer (Blocking Prerequisites)

**Goal**: Implement shared components required by all user stories

**Deliverables**: Database schema, logging, error handling, base FastAPI app, base Next.js layout

### Database Foundation

- [ ] T024 Create phase-2/backend/src/models/__init__.py
- [ ] T025 [P] Create base SQLModel imports in phase-2/backend/src/models/__init__.py

### Logging & Error Handling

- [ ] T026 Create phase-2/backend/src/middleware/__init__.py
- [ ] T027 Create phase-2/backend/src/middleware/logging.py with structlog configuration
- [ ] T028 [P] Add CORS middleware configuration in phase-2/backend/src/main.py

### Base API Application

- [ ] T029 Create phase-2/backend/src/main.py with FastAPI app initialization
- [ ] T030 Add CORS middleware to allow frontend origin (from CORS_ORIGINS env var)
- [ ] T031 Add structlog middleware for request/response logging
- [ ] T032 Create health check endpoint GET /health in phase-2/backend/src/main.py
- [ ] T033 [P] Test backend starts successfully: `uvicorn src.main:app --reload`

### Frontend Foundation

- [ ] T034 Create phase-2/frontend/app/layout.tsx with root HTML structure and providers
- [ ] T035 Create phase-2/frontend/app/globals.css with Tailwind imports and custom styles
- [ ] T036 Create phase-2/frontend/app/error.tsx with error boundary component
- [ ] T037 [P] Create phase-2/frontend/components/ui/Button.tsx with Tailwind-styled button
- [ ] T038 [P] Create phase-2/frontend/components/ui/Input.tsx with Tailwind-styled input
- [ ] T039 [P] Create phase-2/frontend/components/ui/Card.tsx with Tailwind-styled card container
- [ ] T040 [P] Test frontend starts successfully: `npm run dev`

---

## Phase 3: User Story 1 - User Registration and Authentication (P1)

**Goal**: Enable users to register, login, logout with JWT authentication

**Independent Test**: Create account → Login → Access protected page → Logout → Verify redirect to login

**Story Completion Criteria**:
- ✅ Users can register with email + password
- ✅ Users can login with valid credentials
- ✅ JWT tokens issued and stored
- ✅ Protected routes redirect unauthenticated users to login
- ✅ Users can logout and session is cleared

### Backend: User Model & Database

- [ ] T041 [US1] Create User model in phase-2/backend/src/models/user.py with UUID id, email, password_hash, created_at
- [ ] T042 [US1] Add unique index on User.email in User model
- [ ] T043 [US1] Create Alembic migration for users table: `alembic revision --autogenerate -m "Create users table"`
- [ ] T044 [US1] Apply migration: `alembic upgrade head`
- [ ] T045 [US1] Verify users table created in Neon console

### Backend: Repository Layer

- [ ] T046 [US1] Create phase-2/backend/src/repositories/__init__.py
- [ ] T047 [US1] Create phase-2/backend/src/repositories/base.py with abstract Repository interface
- [ ] T048 [US1] Create UserRepository in phase-2/backend/src/repositories/user_repository.py
- [ ] T049 [P] [US1] Implement `create_user(email, password_hash) -> User` in UserRepository
- [ ] T050 [P] [US1] Implement `get_by_email(email) -> Optional[User]` in UserRepository
- [ ] T051 [P] [US1] Implement `get_by_id(user_id) -> Optional[User]` in UserRepository

### Backend: Authentication Service

- [ ] T052 [US1] Create phase-2/backend/src/services/__init__.py
- [ ] T053 [US1] Create AuthService in phase-2/backend/src/services/auth_service.py
- [ ] T054 [P] [US1] Implement `hash_password(plain_password) -> str` using Argon2id in AuthService
- [ ] T055 [P] [US1] Implement `verify_password(plain, hashed) -> bool` in AuthService
- [ ] T056 [P] [US1] Implement `create_jwt_token(user_id) -> str` using python-jose in AuthService
- [ ] T057 [P] [US1] Implement `verify_jwt_token(token) -> UUID` in AuthService
- [ ] T058 [US1] Implement `register_user(email, password) -> tuple[User, str]` in AuthService (creates user + returns JWT)
- [ ] T059 [US1] Implement `authenticate_user(email, password) -> Optional[tuple[User, str]]` in AuthService

### Backend: Request/Response Schemas

- [ ] T060 [US1] Create phase-2/backend/src/schemas/__init__.py
- [ ] T061 [US1] Create UserResponse schema in phase-2/backend/src/schemas/auth.py (id, email, created_at)
- [ ] T062 [P] [US1] Create RegisterRequest schema in phase-2/backend/src/schemas/auth.py (email, password)
- [ ] T063 [P] [US1] Create LoginRequest schema in phase-2/backend/src/schemas/auth.py (email, password)
- [ ] T064 [P] [US1] Create AuthResponse schema in phase-2/backend/src/schemas/auth.py (token, user)

### Backend: JWT Middleware & Dependencies

- [ ] T065 [US1] Create phase-2/backend/src/middleware/auth.py with JWT verification middleware
- [ ] T066 [US1] Create phase-2/backend/src/api/deps.py with `get_current_user` dependency
- [ ] T067 [US1] Implement `get_current_user` to extract user from JWT in Authorization header

### Backend: Auth API Endpoints

- [ ] T068 [US1] Create phase-2/backend/src/api/__init__.py
- [ ] T069 [US1] Create phase-2/backend/src/api/auth.py with auth router
- [ ] T070 [P] [US1] Implement POST /api/v1/auth/register endpoint in phase-2/backend/src/api/auth.py
- [ ] T071 [P] [US1] Implement POST /api/v1/auth/login endpoint in phase-2/backend/src/api/auth.py
- [ ] T072 [P] [US1] Implement POST /api/v1/auth/logout endpoint (returns success message)
- [ ] T073 [US1] Register auth router in phase-2/backend/src/main.py with /api/v1 prefix
- [ ] T074 [US1] Test auth endpoints with curl or Postman (register, login, verify JWT)

### Frontend: Auth Context & State

- [ ] T075 [US1] Create AuthContext in phase-2/frontend/lib/auth-context.tsx with token/user state
- [ ] T076 [US1] Implement login(email, password) method in AuthContext
- [ ] T077 [P] [US1] Implement register(email, password) method in AuthContext
- [ ] T078 [P] [US1] Implement logout() method in AuthContext
- [ ] T079 [US1] Add AuthProvider to phase-2/frontend/app/layout.tsx
- [ ] T080 [US1] Create useAuth hook in phase-2/frontend/lib/auth-context.tsx

### Frontend: API Client

- [ ] T081 [US1] Create ApiClient class in phase-2/frontend/lib/api-client.ts
- [ ] T082 [P] [US1] Implement `register(email, password)` method in ApiClient
- [ ] T083 [P] [US1] Implement `login(email, password)` method in ApiClient
- [ ] T084 [P] [US1] Add Authorization header injection in ApiClient.request()
- [ ] T085 [US1] Create ApiError class for error handling in phase-2/frontend/lib/api-client.ts

### Frontend: Auth Components

- [ ] T086 [US1] Create phase-2/frontend/components/auth/RegisterForm.tsx
- [ ] T087 [US1] Add email validation (RFC 5322 format) in RegisterForm
- [ ] T088 [US1] Add password validation (min 8 chars) in RegisterForm
- [ ] T089 [US1] Add error display for registration failures in RegisterForm
- [ ] T090 [US1] Create phase-2/frontend/components/auth/LoginForm.tsx
- [ ] T091 [US1] Add email and password inputs in LoginForm
- [ ] T092 [US1] Add error display for login failures in LoginForm
- [ ] T093 [P] [US1] Create phase-2/frontend/components/auth/LogoutButton.tsx

### Frontend: Auth Pages

- [ ] T094 [US1] Create phase-2/frontend/app/(auth)/register/page.tsx
- [ ] T095 [US1] Render RegisterForm in register page
- [ ] T096 [US1] Redirect to dashboard on successful registration
- [ ] T097 [US1] Create phase-2/frontend/app/(auth)/login/page.tsx
- [ ] T098 [US1] Render LoginForm in login page
- [ ] T099 [US1] Redirect to dashboard on successful login

### Frontend: Protected Routes

- [ ] T100 [US1] Create phase-2/frontend/app/(dashboard)/layout.tsx
- [ ] T101 [US1] Add authentication check in dashboard layout (redirect to /login if not authenticated)
- [ ] T102 [US1] Create placeholder dashboard page in phase-2/frontend/app/(dashboard)/page.tsx
- [ ] T103 [US1] Add LogoutButton to dashboard layout

### Integration Testing (US1)

- [ ] T104 [US1] Verify registration flow: Register new user → Auto-login → Dashboard displays
- [ ] T105 [US1] Verify login flow: Login with existing user → Redirected to dashboard
- [ ] T106 [US1] Verify logout flow: Click logout → Redirected to login page
- [ ] T107 [US1] Verify protected route: Access /dashboard without auth → Redirected to /login
- [ ] T108 [US1] Verify invalid login: Wrong password → Error message displayed

---

## Phase 4: User Story 2 - Create and View Personal Todos (P2)

**Goal**: Enable authenticated users to create and view their personal todo list

**Independent Test**: Login → Create todo → View in list → Logout/Login → Todo persists

**Story Completion Criteria**:
- ✅ Users can create todos with title (required) and description (optional)
- ✅ Users can view all their todos in a list
- ✅ Todos persist across sessions
- ✅ User isolation enforced (users only see their own todos)
- ✅ Todos display with ID, title, description, completion status, created_at

### Backend: Todo Model & Database

- [ ] T109 [US2] Create Todo model in phase-2/backend/src/models/todo.py with id, user_id, title, description, completed, created_at
- [ ] T110 [US2] Add foreign key constraint on Todo.user_id → User.id with ON DELETE CASCADE
- [ ] T111 [US2] Add indexes on Todo.user_id and Todo.created_at
- [ ] T112 [US2] Create Alembic migration for todos table: `alembic revision --autogenerate -m "Create todos table"`
- [ ] T113 [US2] Apply migration: `alembic upgrade head`
- [ ] T114 [US2] Verify todos table created in Neon console with foreign key

### Backend: Todo Repository

- [ ] T115 [US2] Create TodoRepository in phase-2/backend/src/repositories/todo_repository.py
- [ ] T116 [P] [US2] Implement `create_todo(title, description, user_id) -> Todo` in TodoRepository
- [ ] T117 [P] [US2] Implement `get_user_todos(user_id) -> List[Todo]` ordered by created_at DESC in TodoRepository
- [ ] T118 [P] [US2] Implement `get_by_id(todo_id, user_id) -> Optional[Todo]` with user_id filter in TodoRepository

### Backend: Todo Service

- [ ] T119 [US2] Create TodoService in phase-2/backend/src/services/todo_service.py
- [ ] T120 [US2] Inject TodoRepository via dependency injection in TodoService.__init__
- [ ] T121 [P] [US2] Implement `create_todo(title, description, user_id)` with validation in TodoService
- [ ] T122 [P] [US2] Implement `get_user_todos(user_id)` in TodoService
- [ ] T123 [P] [US2] Implement `get_todo_by_id(todo_id, user_id)` with ownership check in TodoService

### Backend: Todo Schemas

- [ ] T124 [US2] Create TodoResponse schema in phase-2/backend/src/schemas/todo.py (all fields)
- [ ] T125 [P] [US2] Create TodoCreateRequest schema in phase-2/backend/src/schemas/todo.py (title, description)
- [ ] T126 [P] [US2] Add Field validators for title (1-200 chars) and description (0-2000 chars) in schemas

### Backend: Todo API Endpoints

- [ ] T127 [US2] Create phase-2/backend/src/api/todos.py with todos router
- [ ] T128 [US2] Implement POST /api/v1/todos endpoint (create todo) in phase-2/backend/src/api/todos.py
- [ ] T129 [US2] Implement GET /api/v1/todos endpoint (list user's todos) in phase-2/backend/src/api/todos.py
- [ ] T130 [US2] Implement GET /api/v1/todos/{id} endpoint (get single todo) in phase-2/backend/src/api/todos.py
- [ ] T131 [US2] Add `current_user = Depends(get_current_user)` to all todo endpoints
- [ ] T132 [US2] Ensure all endpoints filter by current_user.id (user isolation)
- [ ] T133 [US2] Register todos router in phase-2/backend/src/main.py
- [ ] T134 [US2] Test todo endpoints with JWT token (create, list, get by ID)

### Frontend: Todo Types & API Client

- [ ] T135 [US2] Add Todo interface to phase-2/frontend/lib/types.ts
- [ ] T136 [P] [US2] Add TodoCreateRequest interface to phase-2/frontend/lib/types.ts
- [ ] T137 [US2] Implement `getTodos() -> Promise<Todo[]>` in ApiClient
- [ ] T138 [P] [US2] Implement `createTodo(request: TodoCreateRequest) -> Promise<Todo>` in ApiClient
- [ ] T139 [P] [US2] Implement `getTodoById(id: number) -> Promise<Todo>` in ApiClient

### Frontend: Todo Components

- [ ] T140 [US2] Create phase-2/frontend/components/todos/TodoList.tsx
- [ ] T141 [US2] Accept todos prop and map to TodoItem components in TodoList
- [ ] T142 [US2] Display empty state when no todos exist in TodoList
- [ ] T143 [US2] Create phase-2/frontend/components/todos/TodoItem.tsx
- [ ] T144 [US2] Display todo title, description, completed status, created_at in TodoItem
- [ ] T145 [US2] Apply responsive Tailwind classes (mobile-first) to TodoItem
- [ ] T146 [US2] Create phase-2/frontend/components/todos/TodoForm.tsx
- [ ] T147 [US2] Add title and description inputs to TodoForm
- [ ] T148 [US2] Add client-side validation (title 1-200 chars, description 0-2000 chars) to TodoForm
- [ ] T149 [US2] Call apiClient.createTodo on form submission in TodoForm
- [ ] T150 [US2] Disable submit button during submission in TodoForm
- [ ] T151 [US2] Clear form after successful todo creation in TodoForm

### Frontend: Dashboard Page

- [ ] T152 [US2] Update phase-2/frontend/app/(dashboard)/page.tsx to fetch and display todos
- [ ] T153 [US2] Use Server Component to fetch todos (direct apiClient call on server)
- [ ] T154 [US2] Render TodoList with fetched todos in dashboard page
- [ ] T155 [US2] Render TodoForm above TodoList in dashboard page
- [ ] T156 [US2] Add page refresh after todo creation (router.refresh())

### Integration Testing (US2)

- [ ] T157 [US2] Verify todo creation: Create todo with title only → Appears in list
- [ ] T158 [US2] Verify todo creation: Create todo with title + description → Both fields saved
- [ ] T159 [US2] Verify todo list: Create 3 todos → All appear in chronological order (newest first)
- [ ] T160 [US2] Verify persistence: Create todo → Logout → Login → Todo still exists
- [ ] T161 [US2] Verify user isolation: User A creates todo → User B logs in → User B sees empty list
- [ ] T162 [US2] Verify validation: Submit todo with empty title → Error message displayed
- [ ] T163 [US2] Verify validation: Submit todo with 201-char title → Error message displayed

---

## Phase 5: User Story 3 - Update and Complete Todos (P3)

**Goal**: Enable users to edit todo details and toggle completion status

**Independent Test**: Create todo → Edit title/description → Toggle complete → Changes persist

**Story Completion Criteria**:
- ✅ Users can edit todo title and description
- ✅ Users can toggle todo completion status
- ✅ Changes persist immediately and across page refreshes
- ✅ Completed todos visually distinguished from incomplete
- ✅ User isolation enforced (cannot edit others' todos)

### Backend: Todo Update Operations

- [ ] T164 [US3] Implement `update_todo(todo_id, title, description, user_id) -> Todo` in TodoRepository
- [ ] T165 [US3] Implement `toggle_completion(todo_id, user_id) -> Todo` in TodoRepository
- [ ] T166 [US3] Implement `update_todo(...)` in TodoService with validation and ownership check
- [ ] T167 [US3] Implement `toggle_completion(...)` in TodoService with ownership check

### Backend: Update Schemas

- [ ] T168 [US3] Create TodoUpdateRequest schema in phase-2/backend/src/schemas/todo.py (optional title, description)
- [ ] T169 [US3] Add validators for optional title (1-200 chars if provided) and description (0-2000 chars if provided)

### Backend: Update API Endpoints

- [ ] T170 [US3] Implement PUT /api/v1/todos/{id} endpoint (update todo) in phase-2/backend/src/api/todos.py
- [ ] T171 [US3] Implement PATCH /api/v1/todos/{id}/toggle endpoint (toggle completion) in phase-2/backend/src/api/todos.py
- [ ] T172 [US3] Return 403 Forbidden if user attempts to update another user's todo
- [ ] T173 [US3] Return 404 Not Found if todo_id doesn't exist
- [ ] T174 [US3] Test update and toggle endpoints with JWT token

### Frontend: Update API Client Methods

- [ ] T175 [US3] Add TodoUpdateRequest interface to phase-2/frontend/lib/types.ts
- [ ] T176 [P] [US3] Implement `updateTodo(id, request) -> Promise<Todo>` in ApiClient
- [ ] T177 [P] [US3] Implement `toggleTodo(id) -> Promise<Todo>` in ApiClient

### Frontend: Edit & Toggle Components

- [ ] T178 [US3] Create phase-2/frontend/components/todos/TodoEditForm.tsx
- [ ] T179 [US3] Pre-populate form with existing todo title and description in TodoEditForm
- [ ] T180 [US3] Call apiClient.updateTodo on form submission in TodoEditForm
- [ ] T181 [US3] Add toggle completion button to TodoItem component
- [ ] T182 [US3] Call apiClient.toggleTodo on toggle button click in TodoItem
- [ ] T183 [US3] Apply visual styling to distinguish completed todos (line-through, opacity, checkmark icon)
- [ ] T184 [US3] Add edit button to TodoItem to open TodoEditForm
- [ ] T185 [US3] Use modal or inline edit for TodoEditForm

### Frontend: Update Dashboard Integration

- [ ] T186 [US3] Add state management for editing mode in dashboard page
- [ ] T187 [US3] Refresh todo list after update or toggle (router.refresh())
- [ ] T188 [US3] Display success message after successful update

### Integration Testing (US3)

- [ ] T189 [US3] Verify update: Create todo → Edit title → Title updated and persisted
- [ ] T190 [US3] Verify update: Edit description → Description updated
- [ ] T191 [US3] Verify toggle: Mark todo complete → Visually distinguished as complete
- [ ] T192 [US3] Verify toggle: Toggle back to incomplete → Returns to normal appearance
- [ ] T193 [US3] Verify persistence: Update todo → Refresh page → Changes still present
- [ ] T194 [US3] Verify authorization: User B attempts to edit User A's todo → 403 error

---

## Phase 6: User Story 4 - Delete Todos (P4)

**Goal**: Enable users to permanently delete todos

**Independent Test**: Create todo → Delete with confirmation → Verify removed from list and database

**Story Completion Criteria**:
- ✅ Users can delete their own todos
- ✅ Confirmation dialog prevents accidental deletions
- ✅ Deleted todos do not reappear after page refresh
- ✅ User isolation enforced (cannot delete others' todos)
- ✅ Deletion is permanent (no undo)

### Backend: Delete Operation

- [ ] T195 [US4] Implement `delete_todo(todo_id, user_id) -> bool` in TodoRepository
- [ ] T196 [US4] Implement `delete_todo(todo_id, user_id)` in TodoService with ownership check
- [ ] T197 [US4] Return True if deleted, raise error if not found or not owned

### Backend: Delete API Endpoint

- [ ] T198 [US4] Implement DELETE /api/v1/todos/{id} endpoint in phase-2/backend/src/api/todos.py
- [ ] T199 [US4] Return 403 Forbidden if user attempts to delete another user's todo
- [ ] T200 [US4] Return 404 Not Found if todo_id doesn't exist
- [ ] T201 [US4] Return 200 OK with success message on successful deletion
- [ ] T202 [US4] Test delete endpoint with JWT token

### Frontend: Delete API Client Method

- [ ] T203 [US4] Implement `deleteTodo(id) -> Promise<void>` in ApiClient

### Frontend: Delete Confirmation Component

- [ ] T204 [US4] Create phase-2/frontend/components/todos/TodoDeleteConfirm.tsx
- [ ] T205 [US4] Create Modal component in phase-2/frontend/components/ui/Modal.tsx
- [ ] T206 [US4] Render Modal with confirmation message in TodoDeleteConfirm
- [ ] T207 [US4] Add "Cancel" and "Delete" buttons in TodoDeleteConfirm
- [ ] T208 [US4] Call apiClient.deleteTodo on "Delete" button click
- [ ] T209 [US4] Close modal and refresh list after successful deletion

### Frontend: Delete Integration

- [ ] T210 [US4] Add delete button to TodoItem component
- [ ] T211 [US4] Open TodoDeleteConfirm modal on delete button click
- [ ] T212 [US4] Refresh todo list after deletion (router.refresh())
- [ ] T213 [US4] Display success message after successful deletion

### Integration Testing (US4)

- [ ] T214 [US4] Verify delete: Create todo → Click delete → Confirm → Todo removed from list
- [ ] T215 [US4] Verify persistence: Delete todo → Refresh page → Todo still deleted
- [ ] T216 [US4] Verify confirmation: Click delete → Click cancel → Todo NOT deleted
- [ ] T217 [US4] Verify authorization: User B attempts to delete User A's todo → 403 error
- [ ] T218 [US4] Verify database: Delete todo → Check Neon console → Todo removed from database

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Final refinements, type safety validation, error handling, performance optimization

**Deliverables**: Production-ready application meeting all success criteria

### Type Safety Validation

- [ ] T219 Run mypy strict mode on backend: `mypy src --strict` → Fix all errors
- [ ] T220 Run TypeScript strict mode on frontend: `npm run type-check` → Fix all errors
- [ ] T221 Verify no `any` types in frontend code (search codebase)
- [ ] T222 Verify all functions have type annotations in backend

### Code Quality & Linting

- [ ] T223 Run ruff on backend: `ruff check src` → Fix all issues
- [ ] T224 Run ESLint on frontend: `npm run lint` → Fix all issues
- [ ] T225 Run Prettier on frontend: `npm run format`
- [ ] T226 Verify PEP 8 compliance in backend code

### Error Handling Improvements

- [ ] T227 Add global error handler to FastAPI app for 500 errors (user-friendly messages)
- [ ] T228 Add network error handling to frontend API client (display retry option)
- [ ] T229 Add loading states to all frontend forms and buttons
- [ ] T230 Add toast notifications for success/error messages in frontend

### Security Hardening

- [ ] T231 Verify all API endpoints have JWT authentication (except /auth/register, /auth/login, /health)
- [ ] T232 Verify all database queries filter by user_id (search codebase for SELECT statements)
- [ ] T233 Add rate limiting to auth endpoints (optional, documented as Phase III enhancement)
- [ ] T234 Verify password hashing uses Argon2id with correct parameters

### Performance Optimization

- [ ] T235 Add database query optimization: verify indexes on user_id and created_at
- [ ] T236 Test API response times with 100 todos (should be <200ms p95)
- [ ] T237 Test frontend render time with 100 todos (should be <1 second)
- [ ] T238 Optimize bundle size: `npm run build` and check output

### Responsive Design Validation

- [ ] T239 Test application on mobile viewport (375px width)
- [ ] T240 Test application on tablet viewport (768px width)
- [ ] T241 Test application on desktop viewport (1920px width)
- [ ] T242 Verify no horizontal scrolling on any viewport size
- [ ] T243 Verify touch targets are appropriately sized on mobile (min 44x44px)

### Documentation & Setup

- [ ] T244 Update quickstart.md with any setup changes discovered during implementation
- [ ] T245 Create example .env files with all required variables documented
- [ ] T246 Verify all file paths in CLAUDE.md files are accurate
- [ ] T247 Add inline code comments for complex business logic

### Final Integration Testing

- [ ] T248 Complete end-to-end user journey: Register → Create 5 todos → Edit 2 → Toggle 3 complete → Delete 1
- [ ] T249 Test concurrent user sessions: Two users in parallel, verify isolation
- [ ] T250 Test session expiration: Wait for JWT expiry → Verify redirect to login
- [ ] T251 Test edge cases from spec.md (empty states, long content, network failures)
- [ ] T252 Verify all 10 success criteria from spec.md (SC-001 to SC-010)

---

## Dependency Graph

Shows prerequisite relationships between user stories:

```
Phase 1 (Setup) ─────────────────────┐
                                     │
Phase 2 (Foundation) ────────────────┤
                                     │
                                     ├──> Phase 3: US1 (Auth) ────────────────┐
                                     │                                        │
                                     │                                        ├──> Phase 4: US2 (Create/View) ─────┐
                                     │                                        │                                    │
                                     │                                        │                                    ├──> Phase 5: US3 (Update/Toggle) ──┐
                                     │                                        │                                    │                                    │
                                     │                                        │                                    │                                    ├──> Phase 6: US4 (Delete) ─> Phase 7 (Polish)
                                     │                                        │                                    │                                    │
                                     │ (US5 - Responsive built into all frontend tasks, no separate dependency)   │                                    │
                                     └────────────────────────────────────────┴────────────────────────────────────┴────────────────────────────────────┘
```

**Critical Path**: Setup → Foundation → US1 → US2 → US3 → US4 → Polish

**Parallel Opportunities**:
- Within each phase, tasks marked `[P]` can run concurrently
- US5 (Responsive) is built into all frontend tasks (Tailwind mobile-first), no separate phase needed
- Backend and frontend tasks within same story can run in parallel (after models/schemas defined)

---

## Parallel Execution Examples

### Phase 3 (US1) Parallel Opportunities

**After T041-T045 (User model + migration)**:
- Group A: T049, T050, T051 (Repository methods)
- Group B: T054, T055, T056, T057 (Auth service crypto functions)
- Group C: T062, T063, T064 (Request/response schemas)

**After T067 (JWT middleware)**:
- Group A: T070, T071, T072 (API endpoints)
- Group B: T082, T083 (Frontend API methods)
- Group C: T087, T088 (Frontend validation)

### Phase 4 (US2) Parallel Opportunities

**After T109-T114 (Todo model + migration)**:
- Group A: T116, T117, T118 (Repository methods)
- Group B: T125, T126 (Schemas)
- Group C: T137, T138, T139 (Frontend API methods)

**Frontend UI (can run concurrently after types defined)**:
- Group A: T140-T145 (TodoList and TodoItem)
- Group B: T146-T151 (TodoForm)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Phase 1 + Phase 2 + Phase 3 (US1 Auth)** = First deployable increment
- Users can register and login
- Protected dashboard exists (even if empty)
- JWT authentication working end-to-end

### Incremental Delivery

1. **Increment 1**: MVP (US1) - Week 1
2. **Increment 2**: US2 (Create/View) - Week 2
3. **Increment 3**: US3 + US4 (Update/Delete) - Week 3
4. **Increment 4**: Polish - Week 4

Each increment is independently testable and deployable.

---

## Task Summary

**Total Tasks**: 252
**By Phase**:
- Phase 1 (Setup): 23 tasks
- Phase 2 (Foundation): 17 tasks
- Phase 3 (US1 - Auth): 68 tasks
- Phase 4 (US2 - Create/View): 55 tasks
- Phase 5 (US3 - Update/Toggle): 31 tasks
- Phase 6 (US4 - Delete): 24 tasks
- Phase 7 (Polish): 34 tasks

**Parallelizable Tasks**: 82 tasks marked [P] (32% can run concurrently)

**Story Breakdown**:
- US1: 68 tasks (Authentication foundation)
- US2: 55 tasks (Core todo functionality)
- US3: 31 tasks (Lifecycle management)
- US4: 24 tasks (Cleanup operations)
- US5: Built into all frontend tasks (responsive design)

---

## Success Criteria Validation

Each phase must satisfy these criteria before moving to next:

**Phase 3 (US1) Complete When**:
- ✅ Users can register with valid email/password
- ✅ Users can login with correct credentials
- ✅ JWT tokens issued and validated
- ✅ Protected routes redirect unauthenticated users
- ✅ Logout clears session

**Phase 4 (US2) Complete When**:
- ✅ Users can create todos (title required, description optional)
- ✅ Todos appear in chronological list (newest first)
- ✅ User isolation: users only see own todos
- ✅ Todos persist across logout/login
- ✅ Empty state displays when no todos

**Phase 5 (US3) Complete When**:
- ✅ Users can edit todo title and description
- ✅ Users can toggle completion status
- ✅ Completed todos visually distinguished
- ✅ Changes persist across page refresh
- ✅ Users cannot edit others' todos (403 error)

**Phase 6 (US4) Complete When**:
- ✅ Users can delete own todos
- ✅ Confirmation prevents accidental deletion
- ✅ Deleted todos don't reappear
- ✅ Users cannot delete others' todos (403 error)

**Phase 7 (Polish) Complete When**:
- ✅ All 10 success criteria from spec.md validated
- ✅ mypy strict + TypeScript strict pass
- ✅ Responsive design works 375px-1920px
- ✅ User-friendly error messages for all failures
- ✅ End-to-end user journey successful

---

**Ready for Implementation** ✅

Next step: Begin with Phase 1 (Setup) tasks T001-T023
