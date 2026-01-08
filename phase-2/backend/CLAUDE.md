# Claude Code Context: Phase II Backend (FastAPI)

This file provides context for AI agents working in `phase-2/backend/` directory.

## Purpose

Python FastAPI backend providing REST API for multi-user todo management with JWT authentication and PostgreSQL persistence.

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI 0.109+
- **ORM**: SQLModel 0.0.14+ (SQLAlchemy + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Auth**: python-jose (JWT), argon2-cffi (password hashing)
- **Migrations**: Alembic
- **Testing**: pytest, pytest-asyncio
- **Type Checking**: mypy (strict mode)
- **Linting**: ruff
- **Logging**: structlog

## Directory Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration (env vars, settings)
│   ├── database.py             # Database connection and session management
│   │
│   ├── models/                 # Domain entities (SQLModel)
│   │   ├── __init__.py
│   │   ├── user.py            # User entity
│   │   └── todo.py            # Todo entity
│   │
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py            # Registration, login schemas
│   │   └── todo.py            # Todo CRUD schemas
│   │
│   ├── repositories/           # Data access layer (repository pattern)
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract repository interface
│   │   ├── user_repository.py # User data access
│   │   └── todo_repository.py # Todo data access
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Authentication, password hashing
│   │   └── todo_service.py    # Todo CRUD operations
│   │
│   ├── api/                    # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── deps.py            # FastAPI dependencies (JWT verification)
│   │   ├── auth.py            # Auth endpoints
│   │   └── todos.py           # Todo endpoints
│   │
│   └── middleware/             # Custom middleware
│       ├── __init__.py
│       ├── auth.py            # JWT verification middleware
│       └── logging.py         # Request logging middleware
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_auth.py           # Auth endpoint tests
│   ├── test_todos.py          # Todo endpoint tests
│   └── test_repositories.py   # Repository tests
│
├── alembic/                    # Database migrations
│   ├── versions/              # Migration scripts
│   └── env.py                 # Alembic configuration
│
├── .env.example               # Example environment variables
├── .env                       # Actual environment variables (gitignored)
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project metadata, tool configs
├── mypy.ini                   # Mypy configuration
└── pytest.ini                 # Pytest configuration
```

## Critical Requirements

### 1. User Isolation (MOST IMPORTANT)

**EVERY database query MUST filter by authenticated user's ID**:

```python
# ✅ CORRECT - Always filter by user_id
async def get_user_todos(user_id: UUID) -> List[Todo]:
    async with get_session() as session:
        result = await session.exec(
            select(Todo).where(Todo.user_id == user_id)
        )
        return result.all()

# ❌ WRONG - Never query todos without user_id filter
async def get_all_todos() -> List[Todo]:  # SECURITY VIOLATION!
    async with get_session() as session:
        result = await session.exec(select(Todo))
        return result.all()
```

**Authorization Checks**:
- Extract `user_id` from JWT token (NEVER from request body)
- Verify ownership before UPDATE/DELETE operations
- Return 403 Forbidden if user attempts to access another user's resource

### 2. Password Security

**NEVER store plaintext passwords**:

```python
from argon2 import PasswordHasher

hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,  # 64 MB
    parallelism=1,
    hash_len=32,
    salt_len=16
)

# ✅ CORRECT - Hash before storing
password_hash = hasher.hash(plain_password)
user = User(email=email, password_hash=password_hash)

# ✅ CORRECT - Verify during login
try:
    hasher.verify(user.password_hash, provided_password)
    # Login successful
except:
    # Invalid password
```

**NEVER return password_hash in API responses**:

```python
# ✅ CORRECT - Exclude password_hash
class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allow creation from SQLModel

# ❌ WRONG - Including password_hash
class UserResponse(BaseModel):
    id: UUID
    email: str
    password_hash: str  # SECURITY VIOLATION!
```

### 3. Type Safety (Mypy Strict Mode)

**All functions MUST have type annotations**:

```python
# ✅ CORRECT
async def create_todo(
    title: str,
    description: str,
    user_id: UUID,
    repository: TodoRepository
) -> Todo:
    todo = await repository.create(title, description, user_id)
    return todo

# ❌ WRONG - Missing type annotations
async def create_todo(title, description, user_id, repository):  # Mypy error!
    return await repository.create(title, description, user_id)
```

**No `Any` types without justification**:

```python
# ❌ WRONG
from typing import Any
def process_data(data: Any) -> Any:  # Too permissive
    pass

# ✅ CORRECT - Use specific types
def process_data(data: Dict[str, str]) -> List[Todo]:
    pass
```

### 4. Clean Architecture (Repository Pattern)

**Separate concerns into layers**:

```python
# models/todo.py - Domain entity (no business logic)
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: str = Field(default="")
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# repositories/todo_repository.py - Data access layer
class TodoRepository:
    async def create(self, title: str, description: str, user_id: UUID) -> Todo:
        async with get_session() as session:
            todo = Todo(title=title, description=description, user_id=user_id)
            session.add(todo)
            await session.commit()
            await session.refresh(todo)
            return todo

# services/todo_service.py - Business logic layer
class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    async def create_todo(self, title: str, description: str, user_id: UUID) -> Todo:
        # Business logic: validation, authorization, etc.
        if not title.strip():
            raise ValueError("Title cannot be empty")
        return await self.repository.create(title, description, user_id)

# api/todos.py - API layer (FastAPI routes)
@router.post("/todos", response_model=TodoResponse)
async def create_todo(
    request: TodoCreateRequest,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service)
):
    todo = await service.create_todo(
        title=request.title,
        description=request.description,
        user_id=current_user.id
    )
    return todo
```

## FastAPI Patterns

### Dependency Injection

**Use for JWT verification**:

```python
# api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token)
        user_id = UUID(payload["sub"])
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# api/todos.py - Use dependency
@router.get("/todos")
async def list_todos(current_user: User = Depends(get_current_user)):
    # current_user is automatically injected and verified
    todos = await get_user_todos(current_user.id)
    return {"todos": todos}
```

### Request/Response Models

**Use Pydantic models for validation**:

```python
# schemas/todo.py
from pydantic import BaseModel, Field

class TodoCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)

class TodoUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

class TodoResponse(BaseModel):
    id: int
    user_id: UUID
    title: str
    description: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allow creation from SQLModel
```

### Error Handling

**Return user-friendly error messages**:

```python
from fastapi import HTTPException, status

# ✅ CORRECT - User-friendly error
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Title must be 1-200 characters"
)

# ❌ WRONG - Exposing internal details
raise HTTPException(
    status_code=500,
    detail=f"Database error: {str(e)}"  # SECURITY VIOLATION!
)
```

**Log errors with context**:

```python
import structlog

logger = structlog.get_logger()

try:
    todo = await repository.create(title, description, user_id)
except Exception as e:
    logger.error(
        "todo_creation_failed",
        user_id=str(user_id),
        title=title,
        error=str(e),
        exc_info=True
    )
    raise HTTPException(
        status_code=500,
        detail="Failed to create todo. Please try again."
    )
```

## Database Patterns

### Async Sessions

**Always use async/await**:

```python
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_todo_by_id(todo_id: int, user_id: UUID) -> Optional[Todo]:
    async with get_session() as session:
        result = await session.exec(
            select(Todo).where(
                Todo.id == todo_id,
                Todo.user_id == user_id  # ALWAYS filter by user_id
            )
        )
        return result.first()
```

### Relationships

**Define relationships in models**:

```python
# models/user.py
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship (optional, for eager loading)
    todos: List["Todo"] = Relationship(back_populates="user")

# models/todo.py
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, ondelete="CASCADE")
    title: str = Field(max_length=200)
    description: str = Field(default="")
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship (optional)
    user: Optional[User] = Relationship(back_populates="todos")
```

### Migrations (Alembic)

**Create migration after model changes**:

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add indexes to todos table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Environment Variables

**Load from `.env` file**:

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    better_auth_secret: str
    cors_origins: str = "http://localhost:3000"
    app_env: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Required environment variables** (`.env`):
```env
DATABASE_URL=postgresql+asyncpg://user:pass@neon-host/dbname
BETTER_AUTH_SECRET=<256-bit-secret>
CORS_ORIGINS=http://localhost:3000
APP_ENV=development
LOG_LEVEL=INFO
```

## Testing

### Pytest Fixtures

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_session():
    # Create test database session
    async with get_test_session() as session:
        yield session

@pytest.fixture
async def authenticated_user(client):
    # Create and authenticate test user
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    return response.json()
```

### Test Patterns

```python
# tests/test_todos.py
@pytest.mark.asyncio
async def test_create_todo_success(client, authenticated_user):
    token = authenticated_user["token"]
    response = await client.post(
        "/api/v1/todos",
        json={"title": "Test todo", "description": "Test description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test todo"
    assert data["completed"] is False

@pytest.mark.asyncio
async def test_get_todo_unauthorized(client):
    response = await client.get("/api/v1/todos/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_user_isolation(client, authenticated_user):
    # User A creates todo
    token_a = authenticated_user["token"]
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "User A todo"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    todo_id = create_response.json()["id"]

    # User B registers
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "userb@example.com", "password": "password123"}
    )
    token_b = register_response.json()["token"]

    # User B tries to access User A's todo
    get_response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert get_response.status_code == 403  # Forbidden
```

## Common Mistakes to Avoid

### ❌ Don't Accept user_id from Request Body

```python
# ❌ WRONG - Security vulnerability!
@router.post("/todos")
async def create_todo(request: TodoCreateRequest, user_id: UUID):
    # Attacker can set any user_id!
    todo = await create_todo(request.title, request.description, user_id)

# ✅ CORRECT - Extract from JWT
@router.post("/todos")
async def create_todo(
    request: TodoCreateRequest,
    current_user: User = Depends(get_current_user)
):
    # user_id from verified JWT token
    todo = await create_todo(request.title, request.description, current_user.id)
```

### ❌ Don't Use Synchronous Database Calls

```python
# ❌ WRONG - Blocking I/O
def get_todos(user_id: UUID):
    session = Session(engine)
    todos = session.query(Todo).filter(Todo.user_id == user_id).all()
    return todos

# ✅ CORRECT - Async I/O
async def get_todos(user_id: UUID):
    async with get_session() as session:
        result = await session.exec(
            select(Todo).where(Todo.user_id == user_id)
        )
        return result.all()
```

### ❌ Don't Expose Database Errors to Users

```python
# ❌ WRONG - Exposing internal error
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# ✅ CORRECT - User-friendly message + internal logging
except Exception as e:
    logger.error("database_error", error=str(e), exc_info=True)
    raise HTTPException(
        status_code=500,
        detail="An error occurred. Please try again later."
    )
```

## Quick Commands

```bash
# Start development server
uvicorn src.main:app --reload --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Type checking
mypy src --strict

# Linting
ruff check src

# Format code
ruff format src

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## References

- Parent context: `phase-2/CLAUDE.md`
- Specification: `phase-2/specs/spec.md`
- Data model: `phase-2/specs/data-model.md`
- API contract: `phase-2/specs/contracts/openapi.yaml`
- Constitution: `.specify/memory/constitution.md`
