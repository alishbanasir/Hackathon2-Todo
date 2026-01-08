# Implementation Plan: Todo Full-Stack Web Application

**Branch**: `002-fullstack-web-app` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-fullstack-web-app/spec.md`

## Summary

Transform Phase I in-memory CLI todo application into a modern multi-user web application with persistent storage. The system will support user registration/authentication, full CRUD operations on todos, and strict user data isolation. Built as a full-stack application with Next.js 16+ (App Router) frontend, FastAPI backend, and Neon Serverless PostgreSQL database. Authentication via Better Auth with JWT tokens verified on all protected API endpoints.

**Key Transformation**:
- Single-user → Multi-user with authentication
- In-memory storage → Persistent PostgreSQL database
- CLI interface → Responsive web UI (mobile to desktop)
- No security → JWT-based auth with user isolation

**Technical Approach** (from research.md):
- **Frontend**: Next.js 16+ App Router with React Server Components, TypeScript strict mode, Tailwind CSS
- **Backend**: FastAPI with SQLModel ORM, Argon2id password hashing, python-jose JWT verification
- **Database**: Neon Serverless PostgreSQL with Alembic migrations
- **Architecture**: Clean architecture with repository pattern, dependency injection for services

## Technical Context

**Language/Version**:
- Backend: Python 3.11+
- Frontend: TypeScript 5.x (strict mode)

**Primary Dependencies**:
- Backend: FastAPI 0.109+, SQLModel 0.0.14+, python-jose, argon2-cffi, structlog
- Frontend: Next.js 16+, Better Auth, Tailwind CSS 3.x

**Storage**: Neon Serverless PostgreSQL (connection via DATABASE_URL environment variable)

**Testing**:
- Backend: pytest, pytest-asyncio, mypy (strict mode), ruff
- Frontend: Vitest, React Testing Library, ESLint

**Target Platform**:
- Backend: Linux/Windows server (local development)
- Frontend: Modern web browsers (Chrome, Firefox, Safari, Edge)
- Mobile-responsive (375px to 1920px viewport width)

**Project Type**: Web application (separate frontend + backend)

**Performance Goals**:
- API response time: <200ms p95 (excluding network latency)
- Todo list render: <1 second for 100 items
- User registration + first todo creation: <3 minutes

**Constraints**:
- All work MUST be in phase-2/ directory
- Backend MUST verify JWT on all protected endpoints
- MUST filter all queries by authenticated user's ID (strict isolation)
- MUST use repository pattern (even though database is fixed)
- TypeScript strict mode + mypy strict mode (no type violations)

**Scale/Scope**:
- Initial target: Local development (single developer)
- Future Phase IV: Cloud deployment with Kubernetes
- Database: Designed for thousands of users, millions of todos
- Code: ~5,000-10,000 lines (backend + frontend combined)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Check (Phase 0)

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Incremental Evolution** | ✅ PASS | Repository pattern enforced; business logic decoupled from SQLModel/FastAPI; enables future storage migrations |
| **II. Production-Ready Standards** | ✅ PASS | Type hints required (mypy strict); structured logging (structlog); PEP 8 compliance; comprehensive error handling |
| **III. AI-Native Development** | ✅ PASS | spec.md, plan.md, tasks.md generated; PHRs created for all development decisions; MCP SDK for future Phase III |
| **IV. Scalability & Portability** | ✅ PASS | Environment variables for config; Neon PostgreSQL supports Phase IV K8s; stateless JWTs enable horizontal scaling |
| **V. Clean Architecture** | ✅ PASS | Domain entities in models/; business logic in services/; infrastructure in api/ and repositories/; DI for services |
| **VI. Type Safety** | ✅ PASS | TypeScript strict mode enabled; mypy strict mode enforced; SQLModel provides runtime validation via Pydantic |

### Phase II Specific Constraints

| Constraint | Status | Notes |
|------------|--------|-------|
| Database: PostgreSQL only | ✅ PASS | Neon Serverless PostgreSQL via DATABASE_URL |
| API Framework: FastAPI | ✅ PASS | FastAPI 0.109+ with Pydantic validation |
| Frontend: Next.js | ✅ PASS | Next.js 16+ App Router with TypeScript |
| Repository Pattern Required | ✅ PASS | Abstract repository interfaces in domain layer, SQLModel implementation in infrastructure |

**Overall Gate Status**: ✅ **PASSED** - All constitution principles and phase constraints satisfied

### Post-Design Check (Phase 1)

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Incremental Evolution** | ✅ PASS | data-model.md shows User/Todo entities independent of SQLModel; repository abstractions defined |
| **II. Production-Ready Standards** | ✅ PASS | All validation rules documented; password hashing (Argon2id) specified; structured logging planned |
| **III. AI-Native Development** | ✅ PASS | research.md, data-model.md, quickstart.md, openapi.yaml generated; agent context files (CLAUDE.md) created |
| **IV. Scalability & Portability** | ✅ PASS | Database schema uses indexes for performance; ON DELETE CASCADE for data cleanup; JWT stateless design |
| **V. Clean Architecture** | ✅ PASS | Three-layer architecture: domain (models), application (services), infrastructure (api/repositories) |
| **VI. Type Safety** | ✅ PASS | All types defined in data-model.md and openapi.yaml; TypeScript types in lib/types.ts; Python type hints enforced |

**Overall Gate Status**: ✅ **PASSED** - Design maintains constitution compliance

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-web-app/
├── plan.md                  # This file (/sp.plan output)
├── spec.md                  # Requirements specification
├── research.md              # Phase 0 output (technology decisions)
├── data-model.md            # Phase 1 output (database schema)
├── quickstart.md            # Phase 1 output (developer setup guide)
├── contracts/               # Phase 1 output (API contracts)
│   └── openapi.yaml        # OpenAPI 3.1 specification
├── checklists/              # Quality validation
│   └── requirements.md     # Spec quality checklist (from /sp.specify)
└── tasks.md                 # Phase 2 output (/sp.tasks - NOT created yet)
```

### Source Code (repository root)

```text
phase-2/                     # ALL Phase II work in this directory
├── CLAUDE.md               # Agent context for phase-2/
│
├── backend/                # Python FastAPI backend
│   ├── CLAUDE.md          # Agent context for backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── config.py      # Environment configuration
│   │   ├── database.py    # Database connection management
│   │   │
│   │   ├── models/        # Domain entities (SQLModel)
│   │   │   ├── __init__.py
│   │   │   ├── user.py   # User entity
│   │   │   └── todo.py   # Todo entity
│   │   │
│   │   ├── schemas/       # Pydantic request/response models
│   │   │   ├── __init__.py
│   │   │   ├── auth.py   # Auth schemas
│   │   │   └── todo.py   # Todo schemas
│   │   │
│   │   ├── repositories/  # Data access layer (repository pattern)
│   │   │   ├── __init__.py
│   │   │   ├── base.py   # Abstract repository interface
│   │   │   ├── user_repository.py
│   │   │   └── todo_repository.py
│   │   │
│   │   ├── services/      # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   └── todo_service.py
│   │   │
│   │   ├── api/           # FastAPI route handlers
│   │   │   ├── __init__.py
│   │   │   ├── deps.py   # Dependency injection (JWT auth)
│   │   │   ├── auth.py   # Auth endpoints
│   │   │   └── todos.py  # Todo endpoints
│   │   │
│   │   └── middleware/    # Custom middleware
│   │       ├── __init__.py
│   │       ├── auth.py   # JWT verification
│   │       └── logging.py # Structured logging
│   │
│   ├── tests/             # Pytest test suite
│   │   ├── __init__.py
│   │   ├── conftest.py   # Pytest fixtures
│   │   ├── test_auth.py
│   │   ├── test_todos.py
│   │   └── test_repositories.py
│   │
│   ├── alembic/           # Database migrations
│   │   ├── versions/     # Migration scripts
│   │   └── env.py
│   │
│   ├── .env.example      # Example environment variables
│   ├── .env              # Actual environment variables (gitignored)
│   ├── requirements.txt  # Python dependencies
│   ├── pyproject.toml    # Project metadata
│   ├── mypy.ini          # Mypy configuration
│   └── pytest.ini        # Pytest configuration
│
├── frontend/              # Next.js TypeScript frontend
│   ├── CLAUDE.md         # Agent context for frontend/
│   ├── app/              # Next.js App Router
│   │   ├── (auth)/      # Public auth routes
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   │
│   │   ├── (dashboard)/ # Protected routes
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── todos/[id]/page.tsx
│   │   │
│   │   ├── layout.tsx   # Root layout
│   │   ├── globals.css  # Tailwind imports
│   │   └── error.tsx    # Error boundary
│   │
│   ├── components/       # Reusable React components
│   │   ├── ui/          # Base UI components
│   │   ├── auth/        # Auth components
│   │   └── todos/       # Todo components
│   │
│   ├── lib/             # Utilities and services
│   │   ├── api-client.ts
│   │   ├── auth-context.tsx
│   │   ├── types.ts
│   │   └── utils.ts
│   │
│   ├── hooks/           # Custom React hooks
│   ├── public/          # Static assets
│   ├── __tests__/       # Vitest tests
│   │
│   ├── .env.local.example
│   ├── .env.local       # Environment variables (gitignored)
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── vitest.config.ts
│
└── specs/               # Symlink or copy of specs/002-fullstack-web-app/
    ├── spec.md
    ├── plan.md
    ├── data-model.md
    └── ...
```

**Structure Decision**: Web application (Option 2) with clean separation of frontend and backend. Backend uses three-layer architecture (domain → application → infrastructure) as per Clean Architecture principle. Frontend uses Next.js 16+ App Router with route groups for auth/dashboard separation. All code resides in `phase-2/` directory to maintain phase isolation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No Violations** - All design decisions comply with project constitution.

The repository pattern is required by Constitution Principle I (Incremental Evolution) and enforced for Phase II even though the database is fixed (PostgreSQL only). This enables future phase migrations without business logic changes.

## Phase Outputs

### Phase 0: Research (Completed)
- ✅ `research.md`: Technology decisions and rationale
  - Authentication strategy (Better Auth + JWT)
  - Database ORM (SQLModel)
  - Password hashing (Argon2id)
  - Frontend state management (React Server Components)
  - API design (RESTful with FastAPI)
  - All 10 research questions resolved

### Phase 1: Design (Completed)
- ✅ `data-model.md`: Database schema and entity relationships
  - User entity (UUID primary key, email, password_hash)
  - Todo entity (integer ID, foreign key to user, title, description, completed)
  - Relationships, indexes, validation rules documented

- ✅ `contracts/openapi.yaml`: OpenAPI 3.1 specification
  - 8 endpoints defined (3 auth + 5 todo operations)
  - Request/response schemas for all operations
  - Error responses (401, 403, 404, 400, 500)
  - Security scheme (Bearer JWT)

- ✅ `quickstart.md`: Developer setup guide
  - Prerequisites and required software
  - Backend setup (Python venv, dependencies, Neon DB)
  - Frontend setup (npm install, environment variables)
  - Testing instructions and troubleshooting

- ✅ Agent context files
  - `phase-2/CLAUDE.md`: Phase II overview and guidelines
  - `phase-2/backend/CLAUDE.md`: Backend-specific patterns
  - `phase-2/frontend/CLAUDE.md`: Frontend-specific patterns

### Phase 2: Tasks (Next Step)
- ⏳ `tasks.md`: Not yet created (requires `/sp.tasks` command)
  - Will break down implementation into granular, testable tasks
  - Will include dependency ordering and acceptance criteria
  - Will reference this plan and specification

## Next Steps

1. **Review Planning Artifacts**
   - Specification: `phase-2/specs/spec.md` (42 functional requirements, 5 user stories)
   - This plan: `phase-2/specs/plan.md` (architecture and design decisions)
   - Data model: `phase-2/specs/data-model.md` (database schema)
   - API contract: `phase-2/specs/contracts/openapi.yaml` (REST API definition)
   - Quickstart: `phase-2/specs/quickstart.md` (setup instructions)

2. **Generate Tasks** (Ready to proceed)
   - Run `/sp.tasks` to generate `phase-2/specs/tasks.md`
   - Tasks will be based on this plan and specification
   - Each task will have clear acceptance criteria

3. **Implementation Workflow** (After tasks.md generated)
   - Backend: Implement in order (database → models → repositories → services → API)
   - Frontend: Implement in order (auth → API client → components → pages)
   - Test as you go (TDD recommended for critical features)

4. **Validation Checkpoints**
   - Constitution compliance: Review against `.specify/memory/constitution.md`
   - Specification coverage: Verify all 42 FRs implemented
   - Type safety: mypy strict + TypeScript strict must pass
   - Security: User isolation tests must pass (100% isolation)

## Implementation Priority

Based on user story priorities from spec.md:

**P1 - User Authentication** (Foundation)
- Backend: User model, auth service, JWT middleware
- Frontend: Login/register pages, auth context
- Database: Create users table
- Tests: Auth flow, JWT verification

**P2 - Create and View Todos** (Core Value)
- Backend: Todo model, repository, service, API endpoints (GET, POST)
- Frontend: Todo list component, create form
- Database: Create todos table with foreign key
- Tests: CRUD operations, user isolation

**P3 - Update and Complete Todos** (Lifecycle)
- Backend: Update/toggle endpoints (PUT, PATCH)
- Frontend: Edit form, toggle button
- Tests: Update persistence, toggle functionality

**P3 - Responsive Interface** (UX)
- Frontend: Tailwind responsive classes (mobile-first)
- Tests: Visual regression testing (optional)

**P4 - Delete Todos** (Cleanup)
- Backend: Delete endpoint (DELETE)
- Frontend: Delete button with confirmation
- Tests: Deletion verification

## Risk Mitigation

| Risk | Impact | Mitigation Strategy |
|------|--------|-------------------|
| Better Auth integration complexity | High | Study Better Auth docs thoroughly; create spike/prototype before full implementation |
| JWT secret mismatch between frontend/backend | High | Document in quickstart.md; add validation script to check secrets match |
| User isolation implementation errors | Critical | Write user isolation tests FIRST (TDD); review every query for user_id filter |
| Database migration conflicts | Medium | Use Alembic properly; test migrations on empty database first |
| TypeScript strict mode violations | Medium | Fix incrementally; use `unknown` with type guards instead of `any` |
| Neon PostgreSQL connection issues | Medium | Provide clear connection string format in quickstart; add connection test script |

## Success Metrics (from spec.md SC-001 to SC-010)

Implementation will be considered complete when:
- ✅ Users can register + create first todo in <3 minutes
- ✅ Todo list renders in <1 second for 100 items
- ✅ API responds in <200ms p95
- ✅ 100% user isolation (zero data leakage in testing)
- ✅ Responsive design works 375px-1920px
- ✅ Data persists across sessions (no data loss)
- ✅ Frontend builds without errors (TypeScript strict)
- ✅ Backend passes type checking (mypy strict)
- ✅ JWT verification on all protected endpoints
- ✅ User-friendly error messages (no raw errors exposed)

## Documentation References

All planning artifacts completed and available:
- **Specification**: `phase-2/specs/spec.md`
- **This Plan**: `phase-2/specs/plan.md`
- **Research**: `phase-2/specs/research.md`
- **Data Model**: `phase-2/specs/data-model.md`
- **API Contract**: `phase-2/specs/contracts/openapi.yaml`
- **Quickstart**: `phase-2/specs/quickstart.md`
- **Spec Checklist**: `phase-2/specs/checklists/requirements.md`
- **Agent Context**: `phase-2/CLAUDE.md`, `phase-2/backend/CLAUDE.md`, `phase-2/frontend/CLAUDE.md`

**Project Constitution**: `.specify/memory/constitution.md`

---

**Planning Phase Complete** ✅

Ready for task generation via `/sp.tasks` command.
