# Data Model: Todo Full-Stack Web Application

**Date**: 2026-01-07
**Feature**: 002-fullstack-web-app
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the domain entities and their relationships for the multi-user todo application. The data model enforces strict user isolation (FR-017 to FR-020) while supporting all CRUD operations (FR-009 to FR-016).

---

## Entity: User

**Purpose**: Represents an authenticated application user with unique identity

### Attributes

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, AUTO-GENERATED | Unique user identifier |
| `email` | String(255) | UNIQUE, NOT NULL, INDEXED | User's email address (login credential) |
| `password_hash` | String(255) | NOT NULL | Argon2id hashed password (never store plaintext) |
| `created_at` | DateTime | NOT NULL, AUTO-GENERATED | Account creation timestamp (UTC) |

### Relationships

- **Todos**: One user has many todos (1:N relationship)
  - Foreign key: `Todo.user_id` references `User.id`
  - Cascade delete: Deleting user deletes all their todos

### Validation Rules

- **Email Format**: Must match RFC 5322 email regex (FR-002)
  - Regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
  - Validation occurs before database insert

- **Password Requirements** (FR-003):
  - Minimum 8 characters
  - Validation occurs before hashing
  - Hash using Argon2id (time_cost=2, memory_cost=65536, parallelism=1)

- **Email Uniqueness**: Database unique constraint prevents duplicate registrations
  - Violation returns 400 Bad Request with message "Email already registered"

### Indexes

- **Primary Index**: `id` (UUID)
- **Unique Index**: `email` (for fast login lookups and uniqueness enforcement)

### State Transitions

Users have minimal state (account exists or doesn't). No activation/deactivation in Phase II.

**Lifecycle**:
1. **Created**: User registers → account created with hashed password
2. **Active**: User can log in and manage todos
3. **Deleted**: User account removed → all todos cascade deleted (future enhancement)

### Security Considerations

- **Password Storage**: NEVER store plaintext passwords (FR-004)
  - Always hash with Argon2id before INSERT/UPDATE
  - Password field should never be returned in API responses

- **Email Privacy**: Email addresses are sensitive PII
  - Only expose to the owning user (not in public APIs)

- **User Isolation**: Every query MUST filter by authenticated user's ID
  - Prevents data leakage between users (FR-020)

### Example Data

```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c7d-9e0f1a2b3c4d",
  "email": "user@example.com",
  "password_hash": "$argon2id$v=19$m=65536,t=2,p=1$...",
  "created_at": "2026-01-07T10:30:00Z"
}
```

---

## Entity: Todo

**Purpose**: Represents a single task item owned by a specific user

### Attributes

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO-INCREMENT | Unique todo identifier (sequential) |
| `user_id` | UUID | FOREIGN KEY, NOT NULL, INDEXED | Owner of this todo (references User.id) |
| `title` | String(200) | NOT NULL | Todo title (required, max 200 chars) |
| `description` | Text | NULLABLE | Optional detailed description (max 2000 chars) |
| `completed` | Boolean | NOT NULL, DEFAULT FALSE | Completion status (true = done) |
| `created_at` | DateTime | NOT NULL, AUTO-GENERATED | Todo creation timestamp (UTC) |

### Relationships

- **User**: Many todos belong to one user (N:1 relationship)
  - Foreign key: `user_id` references `User.id`
  - ON DELETE CASCADE: If user deleted, all their todos are deleted

### Validation Rules

- **Title Length** (FR-009, Edge Case: Long Content):
  - Required: NOT NULL
  - Minimum: 1 character (after trimming whitespace)
  - Maximum: 200 characters
  - Validation error: "Title must be 1-200 characters"

- **Description Length** (Edge Case: Long Content):
  - Optional: Can be NULL or empty string
  - Maximum: 2000 characters
  - Validation error: "Description cannot exceed 2000 characters"

- **User Ownership** (FR-017):
  - `user_id` must reference valid existing user
  - Foreign key constraint enforced at database level
  - API layer ensures user can only create todos for themselves

### Indexes

- **Primary Index**: `id` (auto-increment integer)
- **Foreign Key Index**: `user_id` (for fast user-specific queries)
- **Ordering Index**: `created_at` (for chronological ordering)

### State Transitions

Todos have two primary states: **Incomplete** and **Completed**

```
[New Todo] → Incomplete (completed=false)
    ↓
Incomplete ⟷ Completed (toggle via PATCH /todos/{id}/toggle)
    ↓
[Deleted] (permanent removal)
```

**State Transition Rules**:
- New todos default to `completed=false`
- Users can toggle between incomplete ↔ completed unlimited times
- No undo after deletion (permanent)

### Query Patterns

**List User's Todos** (FR-012):
```sql
SELECT * FROM todos
WHERE user_id = <authenticated_user_id>
ORDER BY created_at DESC
```

**Get Todo by ID** (FR-013):
```sql
SELECT * FROM todos
WHERE id = <todo_id> AND user_id = <authenticated_user_id>
```
- Returns 404 if todo doesn't exist
- Returns 403 if todo exists but belongs to different user

**Update Todo** (FR-014):
```sql
UPDATE todos
SET title = <new_title>, description = <new_description>
WHERE id = <todo_id> AND user_id = <authenticated_user_id>
```

**Toggle Completion** (FR-015):
```sql
UPDATE todos
SET completed = NOT completed
WHERE id = <todo_id> AND user_id = <authenticated_user_id>
```

**Delete Todo** (FR-016):
```sql
DELETE FROM todos
WHERE id = <todo_id> AND user_id = <authenticated_user_id>
```

### Security Considerations

- **User Isolation** (FR-018, FR-019, FR-020):
  - EVERY query MUST include `WHERE user_id = <authenticated_user_id>`
  - Backend middleware extracts user_id from JWT token
  - Database queries NEVER accept user_id from request body (injection risk)

- **Authorization Checks**:
  - Read: Can only read own todos
  - Create: Can only create todos for self (user_id from JWT, not request)
  - Update: Can only update own todos (WHERE clause enforces ownership)
  - Delete: Can only delete own todos (WHERE clause enforces ownership)

### Example Data

```json
{
  "id": 42,
  "user_id": "a1b2c3d4-e5f6-4a5b-8c7d-9e0f1a2b3c4d",
  "title": "Complete Phase II specification",
  "description": "Write comprehensive spec.md with user stories, requirements, and success criteria",
  "completed": true,
  "created_at": "2026-01-07T09:15:00Z"
}
```

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────┐
│ User                                    │
├─────────────────────────────────────────┤
│ PK  id: UUID                            │
│ UNQ email: String(255)                  │
│     password_hash: String(255)          │
│     created_at: DateTime                │
└─────────────────┬───────────────────────┘
                  │
                  │ 1:N
                  │ (ON DELETE CASCADE)
                  │
                  ▼
┌─────────────────────────────────────────┐
│ Todo                                    │
├─────────────────────────────────────────┤
│ PK  id: Integer (auto-increment)        │
│ FK  user_id: UUID → User.id             │
│     title: String(200) NOT NULL         │
│     description: Text                   │
│     completed: Boolean (default=false)  │
│     created_at: DateTime                │
└─────────────────────────────────────────┘
```

**Relationship Cardinality**:
- One User → Many Todos (0 to unlimited)
- One Todo → Exactly One User (required foreign key)

**Cascade Behavior**:
- Delete User → Cascade delete all user's todos
- Delete Todo → No effect on user

---

## Database Migration Strategy

### Initial Schema Creation

**Tool**: Alembic (standard for SQLAlchemy/SQLModel projects)

**Migration Steps**:
1. Create `users` table with UUID primary key
2. Create `todos` table with foreign key to `users.id`
3. Create indexes: `users.email` (unique), `todos.user_id`, `todos.created_at`
4. Seed data: None (users register organically)

### Schema Version Control

- Alembic tracks schema versions in `alembic_version` table
- Each schema change is a new migration file (numbered sequentially)
- Migrations are forward-only (no rollback in production after Phase IV deployment)

### Sample Alembic Migration

```python
"""Create users and todos tables

Revision ID: 001
Revises:
Create Date: 2026-01-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # Create todos table
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_index('idx_todos_user_id', 'todos', ['user_id'])
    op.create_index('idx_todos_created_at', 'todos', ['created_at'])

def downgrade():
    op.drop_table('todos')
    op.drop_table('users')
```

---

## Validation Summary

| Requirement | Validation Rule | Error Message |
|-------------|----------------|---------------|
| FR-002 | Email format (RFC 5322) | "Invalid email address format" |
| FR-003 | Password min 8 chars | "Password must be at least 8 characters" |
| FR-004 | Password hashing | (internal - never exposed) |
| FR-009 | Title required, 1-200 chars | "Title must be 1-200 characters" |
| FR-009 | Description max 2000 chars | "Description cannot exceed 2000 characters" |
| FR-010 | Auto-increment ID | (automatic - no user input) |
| FR-011 | Auto-generated timestamp | (automatic - no user input) |
| FR-017 | User_id foreign key | "Invalid user reference" (500 if misconfigured) |
| FR-018 | Query filtering by user_id | (enforced in service layer, not exposed to user) |
| FR-019 | Authorization check | "Access denied: not authorized to access this resource" (403) |
| FR-020 | User isolation | (enforced by WHERE clauses, logged as security event if violated) |

---

## Future Enhancements (Out of Scope for Phase II)

The data model is designed to support future enhancements without breaking changes:

1. **Due Dates**: Add `due_date: DateTime` column to Todo
2. **Tags**: Create `Tag` entity with many-to-many relationship to Todo
3. **Priority**: Add `priority: Enum(LOW, MEDIUM, HIGH)` column to Todo
4. **Attachments**: Create `Attachment` entity with foreign key to Todo
5. **Sharing**: Add `Permissions` entity for collaborative todos (Phase III+)
6. **Soft Deletes**: Add `deleted_at: DateTime` column (trash/restore functionality)
7. **Audit Trail**: Create `AuditLog` entity tracking all changes (Phase III+)

All enhancements require new Alembic migrations; existing data remains compatible.

---

## Compliance with Constitution

### Principle I: Incremental Evolution
✓ Repository pattern will abstract database access
✓ Models use SQLModel (can swap Postgres for SQLite with minimal changes)
✓ Domain entities (User, Todo) are independent of storage implementation

### Principle II: Production-Ready Standards
✓ All fields have explicit types and constraints
✓ Validation rules defined for all user inputs
✓ Foreign key constraints enforce referential integrity

### Principle V: Clean Architecture
✓ Data model defined in domain layer (models/)
✓ No references to FastAPI or HTTP concerns in entity definitions
✓ Repository interfaces will wrap database access (infrastructure layer)

### Principle VI: Type Safety
✓ All attributes have explicit types (UUID, String, Integer, Boolean, DateTime)
✓ SQLModel provides runtime type validation via Pydantic
✓ Mypy strict mode will validate type annotations

---

## Next Steps

1. Generate API contracts (OpenAPI spec) based on this data model
2. Create quickstart.md with database setup instructions
3. Implement SQLModel classes in `phase-2/backend/src/models/`
