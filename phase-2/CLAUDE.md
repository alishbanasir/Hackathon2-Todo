# Claude Code Context: Phase II - Todo Full-Stack Web Application

This file provides context-specific guidance for AI agents working in the `phase-2/` directory.

## Phase Overview

**Goal**: Transform Phase I in-memory CLI into a modern multi-user web application with persistent storage

**Architecture**: Full-stack web application with separate frontend and backend
- Frontend: Next.js 16+ (App Router) + TypeScript + Tailwind CSS
- Backend: FastAPI + Python 3.11+ + SQLModel ORM
- Database: Neon Serverless PostgreSQL

**Key Transformation**:
- Single-user CLI → Multi-user web app
- In-memory storage → Persistent database
- Command-line interface → Responsive web UI
- No authentication → JWT-based auth with Better Auth

## Directory Structure

```
phase-2/
├── backend/           # Python FastAPI backend
├── frontend/          # Next.js TypeScript frontend
├── specs/             # Copied from root specs/002-fullstack-web-app/
└── CLAUDE.md         # This file
```

**Important**: All Phase II work MUST stay inside the `phase-2/` directory.

## Specification Documents

**Location**: `phase-2/specs/` (symlinked from root `specs/002-fullstack-web-app/`)

Key documents:
- **spec.md**: Complete requirements specification (42 functional requirements, 5 user stories)
- **plan.md**: Implementation plan and architecture decisions
- **data-model.md**: Database schema and entity relationships
- **quickstart.md**: Developer setup guide
- **contracts/openapi.yaml**: REST API specification

**Always reference these documents** before making architectural decisions or implementing features.

## Technology Stack

### Backend (Python)
- **Framework**: FastAPI 0.109+
- **ORM**: SQLModel 0.0.14+ (combines SQLAlchemy + Pydantic)
- **Database**: PostgreSQL via Neon Serverless
- **Auth**: python-jose (JWT verification), argon2-cffi (password hashing)
- **Logging**: structlog (JSON-formatted)
- **Testing**: pytest, pytest-asyncio
- **Type Checking**: mypy (strict mode)
- **Linting**: ruff

### Frontend (TypeScript)
- **Framework**: Next.js 16+ (App Router, React Server Components)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS 3.x
- **Auth**: Better Auth (JWT token management)
- **Testing**: Vitest, React Testing Library
- **Linting**: ESLint, Prettier

### Infrastructure
- **Database**: Neon Serverless PostgreSQL (connection via DATABASE_URL env var)
- **Development**: Local (frontend: 3000, backend: 8000)

## Core Requirements

### User Isolation (CRITICAL)
Every API endpoint MUST enforce user isolation:
- Extract `user_id` from JWT token (NEVER from request body)
- Filter all queries by `WHERE user_id = <authenticated_user_id>`
- Return 403 Forbidden if user attempts to access another user's data
- Log security events when authorization fails

**This is the most critical security requirement** (FR-017 to FR-020).

### Authentication Flow
1. Frontend: Better Auth handles registration/login, issues JWT token
2. Frontend: Store JWT in secure HTTP-only cookie or localStorage
3. Frontend: Include JWT in Authorization header: `Bearer <token>`
4. Backend: Middleware verifies JWT using BETTER_AUTH_SECRET
5. Backend: Extract user_id from validated JWT claims
6. Backend: Use user_id for all database queries

### API Endpoints
All endpoints under `/api/v1/` prefix:

**Auth**:
- `POST /auth/register` - Create account + return JWT
- `POST /auth/login` - Authenticate + return JWT
- `POST /auth/logout` - Client-side session cleanup

**Todos** (all require authentication):
- `GET /todos` - List user's todos (filtered by user_id)
- `POST /todos` - Create todo (user_id from JWT)
- `GET /todos/{id}` - Get todo details (verify ownership)
- `PUT /todos/{id}` - Update todo (verify ownership)
- `PATCH /todos/{id}/toggle` - Toggle completion (verify ownership)
- `DELETE /todos/{id}` - Delete todo (verify ownership)

### Data Model

**User**:
- `id`: UUID (primary key)
- `email`: String(255), unique, indexed
- `password_hash`: String(255) - Argon2id hashed
- `created_at`: DateTime

**Todo**:
- `id`: Integer (auto-increment primary key)
- `user_id`: UUID (foreign key → User.id, ON DELETE CASCADE)
- `title`: String(200), required
- `description`: Text, optional
- `completed`: Boolean (default false)
- `created_at`: DateTime

**Relationships**: User 1:N Todo (one user has many todos)

### Validation Rules
- Email: RFC 5322 format
- Password: Minimum 8 characters
- Todo title: 1-200 characters (required)
- Todo description: 0-2000 characters (optional)

## Constitution Compliance

This phase MUST adhere to project constitution (`.specify/memory/constitution.md`):

### Critical Principles

**Principle I: Incremental Evolution**
- Use repository pattern to abstract database access
- Domain models MUST NOT reference SQLModel or FastAPI directly
- Business logic decoupled from storage (enables future migrations)

**Principle II: Production-Ready Standards**
- All Python code: PEP 8 compliant, type hints, docstrings
- All TypeScript code: strict mode, no `any` types
- Structured logging (no print statements except CLI output)
- Explicit error handling (no bare except clauses)

**Principle V: Clean Architecture**
- Domain layer: models/ (entities only, no framework imports)
- Application layer: services/ (business logic)
- Infrastructure layer: api/ (FastAPI routes), database (SQLModel sessions)
- Dependency injection for all external dependencies

**Principle VI: Type Safety**
- Python: mypy strict mode MUST pass
- TypeScript: strict mode enabled in tsconfig.json
- No type: ignore comments without justification

### Phase II Specific Constraints
- Database: ONLY Neon PostgreSQL (no SQLite, no in-memory)
- API: ONLY FastAPI (no Flask, no Django)
- Frontend: ONLY Next.js 16+ (no Remix, no plain React)
- Repository pattern: REQUIRED (even though database is fixed for now)

## Development Guidelines

### When Working on Backend (`phase-2/backend/`)

1. **Always use async/await** for database operations
   ```python
   async def get_user_todos(user_id: UUID) -> List[Todo]:
       async with Session(engine) as session:
           result = await session.exec(select(Todo).where(Todo.user_id == user_id))
           return result.all()
   ```

2. **Validate inputs with Pydantic models** (automatic with FastAPI)
   ```python
   class TodoCreate(BaseModel):
       title: str = Field(min_length=1, max_length=200)
       description: str = Field(default="", max_length=2000)
   ```

3. **Use dependency injection for user authentication**
   ```python
   async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
       # Verify JWT and return user
       pass

   @app.get("/todos")
   async def list_todos(user: User = Depends(get_current_user)):
       # user is automatically injected
       pass
   ```

4. **Log all errors with context** using structlog
   ```python
   logger.error("todo_creation_failed", user_id=user.id, error=str(e))
   ```

### When Working on Frontend (`phase-2/frontend/`)

1. **Use Server Components by default** (Next.js 16+ App Router)
   ```tsx
   // app/dashboard/page.tsx (Server Component)
   export default async function DashboardPage() {
     const todos = await fetchTodos(); // Direct server-side fetch
     return <TodoList todos={todos} />;
   }
   ```

2. **Use Client Components only when needed** (interactivity)
   ```tsx
   'use client'; // Explicit directive

   export function TodoForm() {
     const [title, setTitle] = useState('');
     // Interactive form logic
   }
   ```

3. **Handle auth state in client context**
   ```tsx
   // lib/auth-context.tsx
   const AuthContext = createContext<AuthState>(null);

   export function useAuth() {
     const context = useContext(AuthContext);
     if (!context) throw new Error('useAuth must be within AuthProvider');
     return context;
   }
   ```

4. **Use Tailwind's mobile-first responsive design**
   ```tsx
   <div className="w-full md:w-1/2 lg:w-1/3"> {/* Mobile → Tablet → Desktop */}
   ```

### Environment Variables

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://user:pass@neon-host/dbname
BETTER_AUTH_SECRET=<256-bit-secret>
CORS_ORIGINS=http://localhost:3000
APP_ENV=development
LOG_LEVEL=INFO
```

**Frontend** (`.env.local`):
```env
BETTER_AUTH_SECRET=<same-secret-as-backend>
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**CRITICAL**: `BETTER_AUTH_SECRET` MUST be identical in both frontend and backend.

## Common Patterns

### Backend Repository Pattern (Required)

Even though Phase II uses only PostgreSQL, we MUST use repository pattern for future flexibility:

```python
# domain/repositories.py (abstract interface)
class TodoRepository(ABC):
    @abstractmethod
    async def get_by_id(self, todo_id: int, user_id: UUID) -> Optional[Todo]:
        pass

# infrastructure/repositories.py (concrete implementation)
class SQLModelTodoRepository(TodoRepository):
    async def get_by_id(self, todo_id: int, user_id: UUID) -> Optional[Todo]:
        async with Session(engine) as session:
            result = await session.exec(
                select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
            )
            return result.first()

# services/todo_service.py (business logic)
class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository  # Dependency injection
```

### Frontend API Client Pattern

```typescript
// lib/api-client.ts
export class TodoApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL!;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const token = getAuthToken(); // From localStorage or cookie
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new ApiError(response.status, await response.json());
    }

    return response.json();
  }

  async getTodos(): Promise<Todo[]> {
    const data = await this.request<{ todos: Todo[] }>('/todos');
    return data.todos;
  }
}
```

## Testing Requirements

### Backend Tests (pytest)
- **Unit tests**: Test services and models in isolation
- **Integration tests**: Test API endpoints with database
- **Coverage target**: >80% for services and models

```python
# tests/test_todos.py
@pytest.mark.asyncio
async def test_create_todo_success(client, authenticated_user):
    response = await client.post(
        "/api/v1/todos",
        json={"title": "Test todo"},
        headers={"Authorization": f"Bearer {authenticated_user.token}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test todo"
```

### Frontend Tests (Vitest)
- **Component tests**: Test React components
- **Integration tests**: Test auth flows and API interactions

```typescript
// __tests__/TodoForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { TodoForm } from '@/components/TodoForm';

test('validates required title', async () => {
  render(<TodoForm />);
  const submitButton = screen.getByRole('button', { name: /create/i });
  fireEvent.click(submitButton);
  expect(await screen.findByText(/title is required/i)).toBeInTheDocument();
});
```

## Migration from Phase I

**Phase I Architecture** (for reference):
- In-memory Python dictionaries
- CLI with argparse
- Single-user (no authentication)
- Data lost on exit

**Phase II Changes**:
- Persistent PostgreSQL database
- Web UI with responsive design
- Multi-user with JWT authentication
- Data persists across sessions

**NO Data Migration**: Phase I and Phase II are separate applications. Phase I data is NOT migrated.

## Out of Scope for Phase II

These features are explicitly excluded:
- AI integration (Phase III)
- Password reset/recovery
- Email verification
- Todo tags/categories
- Due dates
- Collaborative features (sharing todos)
- Dark mode
- Offline support
- Kubernetes deployment (Phase IV)
- Microservices (Phase V)

## Quick Reference

**Start Development**:
```bash
# Backend
cd phase-2/backend
source venv/bin/activate
uvicorn src.main:app --reload

# Frontend
cd phase-2/frontend
npm run dev
```

**Run Tests**:
```bash
# Backend
cd phase-2/backend && pytest

# Frontend
cd phase-2/frontend && npm test
```

**View API Docs**:
- Swagger UI: http://localhost:8000/docs
- OpenAPI spec: `phase-2/specs/contracts/openapi.yaml`

**Key Files**:
- Backend entry: `backend/src/main.py`
- Frontend layout: `frontend/app/layout.tsx`
- Data models: `backend/src/models/`
- API routes: `backend/src/api/`
- UI components: `frontend/components/`

## Support

For questions or issues:
1. Check phase-2 specifications in `specs/` directory
2. Review this CLAUDE.md and subdirectory CLAUDE.md files
3. Consult project constitution: `.specify/memory/constitution.md`
4. Review quickstart guide: `specs/quickstart.md`
