# Research: Todo Full-Stack Web Application

**Date**: 2026-01-07
**Feature**: 002-fullstack-web-app
**Phase**: 0 (Research & Technology Validation)

## Research Questions Resolved

### 1. Authentication Strategy: Better Auth + JWT

**Decision**: Use Better Auth library on frontend for authentication flow with JWT token issuance; backend validates tokens using shared secret

**Rationale**:
- Better Auth is a modern, type-safe authentication library for Next.js with built-in JWT support
- Stateless JWT approach aligns with Phase IV/V scalability requirements (no session storage needed)
- Shared secret (BETTER_AUTH_SECRET) enables simple backend validation without coupling frontend/backend auth implementations
- Supports future enhancement to OAuth2/OIDC providers (Phase III requirement per constitution)

**Alternatives Considered**:
- NextAuth.js: More established but heavier; Better Auth is lighter and more modern
- Custom JWT implementation: Reinventing the wheel; Better Auth provides secure defaults
- Session-based auth: Requires state management that doesn't scale to Kubernetes (Phase IV)

**Implementation Notes**:
- Frontend: Better Auth handles registration, login, token issuance
- Backend: python-jose library verifies JWT signatures using BETTER_AUTH_SECRET
- Middleware: FastAPI dependency injection for JWT validation on protected routes

**References**:
- Better Auth documentation: https://www.better-auth.com/
- FastAPI JWT guide: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

---

### 2. Database ORM: SQLModel vs SQLAlchemy vs Raw SQL

**Decision**: Use SQLModel for all database interactions

**Rationale**:
- SQLModel combines SQLAlchemy's ORM power with Pydantic's validation (FR-037 requirement)
- Type-safe models work seamlessly with FastAPI's automatic validation
- Same model classes can be used for database and API schemas (DRY principle)
- Built-in support for async operations (important for API performance)
- Maintained by FastAPI creator (Sebastian Ramirez), ensuring compatibility

**Alternatives Considered**:
- Pure SQLAlchemy: More boilerplate; need separate Pydantic models for API validation
- Raw SQL with psycopg2: No type safety; violates Constitution Principle VI (Type Safety)
- Tortoise ORM: Django-like async ORM but less integration with FastAPI ecosystem

**Implementation Notes**:
- Models inherit from SQLModel with `table=True`
- Relationships use SQLModel's relationship() with back_populates
- Database sessions use async context managers
- Migration strategy: Alembic (standard for SQLAlchemy-based projects)

**References**:
- SQLModel docs: https://sqlmodel.tiangolo.com/
- FastAPI + SQLModel tutorial: https://fastapi.tiangolo.com/tutorial/sql-databases/

---

### 3. Password Hashing: bcrypt vs argon2 vs PBKDF2

**Decision**: Use argon2-cffi (Argon2id algorithm)

**Rationale**:
- Argon2 won the Password Hashing Competition (2015) - industry best practice
- Argon2id variant resistant to both side-channel and GPU attacks
- Configurable memory cost, time cost, parallelism (better than bcrypt's single cost factor)
- Recommended by OWASP for password storage (2024 guidelines)

**Alternatives Considered**:
- bcrypt: Widely used, simpler, but less resistant to GPU cracking than Argon2
- PBKDF2-SHA256: Older standard, easier to crack with specialized hardware
- scrypt: Good memory-hard function but Argon2 has better security margins

**Implementation Notes**:
- Use argon2-cffi library (Python binding to official C implementation)
- Configuration: time_cost=2, memory_cost=65536 (64 MB), parallelism=1
- Hash format: `$argon2id$v=19$m=65536,t=2,p=1$<salt>$<hash>`

**References**:
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- argon2-cffi docs: https://argon2-cffi.readthedocs.io/

---

### 4. Frontend State Management: Server State vs Client State

**Decision**: Use React Server Components (RSC) for data fetching; minimal client state with useState/useContext

**Rationale**:
- Next.js 16+ App Router defaults to Server Components (automatic data fetching)
- Todo list is server-driven data; no need for complex client state management
- Server Components reduce JavaScript bundle size (better mobile performance)
- useState sufficient for form state; useContext for auth state (JWT token)

**Alternatives Considered**:
- Redux Toolkit: Overkill for simple CRUD app; adds unnecessary complexity
- Zustand: Lightweight but still client-side; doesn't leverage Next.js SSR benefits
- TanStack Query (React Query): Good for caching but RSC + fetch() provides built-in caching

**Implementation Notes**:
- Server Components: Fetch todos in server components, pass as props
- Client Components: Use "use client" only for interactive forms and buttons
- Auth context: Client-side context for JWT token storage (localStorage)
- Mutations: Server Actions or API route handlers (Next.js 16+ pattern)

**References**:
- React Server Components: https://react.dev/reference/rsc/server-components
- Next.js App Router data fetching: https://nextjs.org/docs/app/building-your-application/data-fetching

---

### 5. API Design: REST vs GraphQL vs tRPC

**Decision**: RESTful API with FastAPI (per specification FR-021 to FR-026)

**Rationale**:
- Specification explicitly defines REST endpoints (GET, POST, PUT, PATCH, DELETE)
- FastAPI auto-generates OpenAPI documentation (self-documenting API)
- RESTful pattern is simpler for CRUD operations (no over-fetching complexity)
- Aligns with Constitution Principle II (Production-Ready Standards) - industry standard

**Alternatives Considered**:
- GraphQL: More flexible but overkill for simple CRUD; adds complexity
- tRPC: Type-safe but couples frontend/backend tightly (violates clean architecture)
- gRPC: High performance but more complex; HTTP/2 required

**API Design Decisions**:
- Endpoint pattern: `/api/v1/{resource}` (versioned API for future compatibility)
- Authentication: Bearer token in Authorization header
- Response format: JSON with consistent error structure
- Status codes: 200 (success), 201 (created), 400 (validation), 401 (unauthorized), 403 (forbidden), 404 (not found), 500 (server error)

**References**:
- REST API best practices: https://restfulapi.net/
- FastAPI docs: https://fastapi.tiangolo.com/

---

### 6. Database Schema: User-Todo Relationship Strategy

**Decision**: One-to-many relationship with foreign key constraint and CASCADE delete

**Rationale**:
- User deletion should automatically delete all user's todos (data cleanup)
- Foreign key constraint ensures referential integrity at database level
- Index on `user_id` column for fast filtering (FR-018 requirement)
- SQLModel handles relationship mapping automatically

**Schema Design**:
```
User:
  - id: UUID (primary key, auto-generated)
  - email: String(255, unique, indexed)
  - password_hash: String(255)
  - created_at: DateTime (auto-generated)

Todo:
  - id: Integer (primary key, auto-increment)
  - user_id: UUID (foreign key -> User.id, ON DELETE CASCADE, indexed)
  - title: String(200, not null)
  - description: Text (nullable)
  - completed: Boolean (default False)
  - created_at: DateTime (auto-generated)
```

**Indexes**:
- User.email (unique index for login lookups)
- Todo.user_id (index for fast user-specific queries)
- Todo.created_at (index for ordering by creation date)

**References**:
- PostgreSQL foreign keys: https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK
- SQLModel relationships: https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/

---

### 7. Frontend Framework: Next.js 16+ App Router Configuration

**Decision**: Next.js 16+ with App Router, TypeScript strict mode, Tailwind CSS

**Rationale**:
- App Router (default in Next.js 14+) provides modern React patterns (Server Components, Server Actions)
- TypeScript strict mode enforces type safety (Constitution Principle VI)
- Tailwind CSS enables rapid responsive design without custom CSS (FR-034 requirement)

**Configuration Decisions**:
- TypeScript: `strict: true`, `noUncheckedIndexedAccess: true`
- Tailwind: Mobile-first responsive design with breakpoints (sm, md, lg, xl)
- Linting: ESLint with Next.js config + Prettier for formatting
- Directory structure: `app/` (routes), `components/` (reusable UI), `lib/` (utilities)

**References**:
- Next.js App Router: https://nextjs.org/docs/app
- Tailwind CSS responsive design: https://tailwindcss.com/docs/responsive-design

---

### 8. Environment Configuration: Secrets Management

**Decision**: `.env.local` for development; environment variables for production

**Rationale**:
- Next.js loads `.env.local` automatically (gitignored)
- Backend uses python-dotenv for .env file loading
- Shared secret (BETTER_AUTH_SECRET) must be identical in both frontend and backend environments
- Neon connection string (DATABASE_URL) only needed in backend

**Environment Variables**:

Frontend (.env.local):
```
BETTER_AUTH_SECRET=<shared-secret-256-bits>
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Backend (.env):
```
BETTER_AUTH_SECRET=<same-shared-secret>
DATABASE_URL=postgresql://user:pass@neon-host/dbname
CORS_ORIGINS=http://localhost:3000
```

**Security Notes**:
- Never commit .env files to git (add to .gitignore)
- Use different secrets for dev/staging/production
- Rotate BETTER_AUTH_SECRET periodically (invalidates all JWTs)

**References**:
- Next.js environment variables: https://nextjs.org/docs/app/building-your-application/configuring/environment-variables
- python-dotenv: https://pypi.org/project/python-dotenv/

---

### 9. Testing Strategy: Unit + Integration Tests

**Decision**: Pytest for backend, Vitest for frontend; integration tests for API contracts

**Rationale**:
- Pytest is Python standard (Constitution requirement)
- Vitest is faster than Jest for Vite/Next.js projects
- Integration tests verify API contract compliance (critical for user isolation FR-017 to FR-020)

**Test Coverage Goals**:
- Backend: >80% coverage for services and models (Constitution requirement)
- Frontend: Component tests for forms and auth flows
- Integration: API endpoint tests with multiple users (verify isolation)

**Test Categories**:
- Unit: Individual functions, models, components
- Integration: API endpoints with database interactions
- Contract: OpenAPI schema validation

**References**:
- Pytest docs: https://docs.pytest.org/
- Vitest docs: https://vitest.dev/

---

### 10. Error Handling: Structured Logging + User-Friendly Messages

**Decision**: Structlog for backend logging; client-side error boundaries for frontend

**Rationale**:
- Structlog provides JSON-formatted logs (machine-readable for Phase IV/V monitoring)
- Error boundaries prevent app crashes from showing raw errors (SC-010 requirement)
- FastAPI exception handlers convert internal errors to user-friendly messages

**Error Handling Strategy**:
- Backend: Log all errors with context (user_id, endpoint, timestamp); return safe error messages
- Frontend: Error boundaries catch React errors; toast notifications for API errors
- Network failures: Retry logic with exponential backoff for transient errors

**References**:
- Structlog docs: https://www.structlog.org/
- React Error Boundaries: https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary

---

## Technology Stack Summary

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.109+
- **ORM**: SQLModel 0.0.14+
- **Database**: Neon Serverless PostgreSQL (via DATABASE_URL)
- **Auth**: python-jose (JWT), argon2-cffi (password hashing)
- **Logging**: structlog
- **Testing**: pytest, pytest-asyncio
- **Linting**: ruff, mypy (strict mode)

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS 3.x
- **Auth**: Better Auth
- **Testing**: Vitest, React Testing Library
- **Linting**: ESLint, Prettier

### Infrastructure
- **Database Host**: Neon Serverless PostgreSQL
- **Development**: Local (frontend: 3000, backend: 8000)
- **Deployment**: Phase IV consideration (Docker + Kubernetes)

---

## Unresolved Questions

None - All technical decisions are finalized based on specification requirements and project constitution constraints.

---

## Next Steps

Proceed to Phase 1:
1. Generate data-model.md (User and Todo entity schemas)
2. Generate API contracts (OpenAPI spec in contracts/ directory)
3. Create quickstart.md (setup instructions for developers)
4. Update agent context files (CLAUDE.md for phase-2/, frontend/, backend/)
