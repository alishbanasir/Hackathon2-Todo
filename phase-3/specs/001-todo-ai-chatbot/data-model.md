# Data Model: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-01-12
**Purpose**: Define database schema, entity relationships, and data constraints for Phase 3

## Overview

Phase 3 extends the Phase 2 database with two new entities (Conversation, Message) while maintaining compatibility with existing entities (User, Todo). All entities use SQLModel ORM with PostgreSQL as the backing database.

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │ (Phase 2 - Existing)
│─────────────────│
│ id: UUID (PK)   │
│ email: String   │
│ password_hash   │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴────────────────────┬────────────────┐
    │                         │                │
    ▼                         ▼                ▼
┌──────────────┐      ┌──────────────┐  ┌──────────────┐
│     Todo     │      │ Conversation │  │  (Phase 2)   │
│──────────────│      │──────────────│  │              │
│ id: Int (PK) │      │ id: UUID(PK) │  │              │
│ user_id: FK  │      │ user_id: FK  │  │              │
│ title        │      │ thread_id    │  │              │
│ description  │      │ created_at   │  │              │
│ completed    │      │ last_msg_at  │  │              │
│ created_at   │      └──────┬───────┘  │              │
└──────────────┘             │          │              │
  (Phase 2 -                 │ 1:N      │              │
   Existing)                 │          │              │
                             ▼          │              │
                     ┌──────────────┐   │              │
                     │   Message    │   │              │
                     │──────────────│   │              │
                     │ id: UUID(PK) │   │              │
                     │ conv_id: FK  │   │              │
                     │ role: Enum   │   │              │
                     │ content: Text│   │              │
                     │ created_at   │   │              │
                     └──────────────┘   │              │
                       (Phase 3 -       │              │
                        New)            │              │
                                        │              │
                                        └──────────────┘
```

## Entities

### 1. User (Existing - Phase 2)

**Source**: `phase-2/backend/src/models/user.py`

**Purpose**: Represents an authenticated application user. Owns todos and conversations.

**Schema**:
```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    email: str = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False)
    )

    password_hash: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
```

**Constraints**:
- `email` UNIQUE (enforces one account per email)
- `email` INDEXED (fast lookup during authentication)
- `id` PRIMARY KEY, INDEXED

**Relationships**:
- Has many `Todo` (Phase 2)
- Has many `Conversation` (Phase 3)

**Phase 3 Impact**: No modifications required. Phase 3 entities reference this table via foreign keys.

---

### 2. Todo (Existing - Phase 2)

**Source**: `phase-2/backend/src/models/todo.py`

**Purpose**: Represents a task item owned by a user. Operated on by MCP tools in Phase 3.

**Schema**:
```python
class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True
    )

    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )

    title: str = Field(
        sa_column=Column(String(200), nullable=False)
    )

    description: str = Field(
        default="",
        sa_column=Column(String(2000), nullable=False, server_default="")
    )

    completed: bool = Field(
        default=False,
        nullable=False
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
```

**Constraints**:
- `user_id` FOREIGN KEY to `users.id` with CASCADE DELETE
- `user_id` INDEXED (fast filtering by user)
- `title` length: 1-200 characters (validated at API layer)
- `description` length: 0-2000 characters (validated at API layer)

**Relationships**:
- Belongs to one `User`

**Phase 3 Impact**: No modifications required. MCP tools operate on this table with user_id filtering.

---

### 3. Conversation (New - Phase 3)

**Purpose**: Represents a chat session between a user and the AI assistant. Tracks OpenAI Thread ID for context continuity.

**Schema**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )

    openai_thread_id: str = Field(
        sa_column=Column(String(255), nullable=False, unique=True)
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    last_message_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**Constraints**:
- `id` PRIMARY KEY (UUID for distributed system compatibility)
- `user_id` FOREIGN KEY to `users.id` with CASCADE DELETE (conversations deleted when user deleted)
- `user_id` INDEXED (fast retrieval of user's conversations)
- `openai_thread_id` UNIQUE (prevents duplicate thread references)
- `openai_thread_id` NOT NULL (every conversation must have an OpenAI Thread)
- `last_message_at` updated on every message insertion (enables "recent conversations" queries)

**Relationships**:
- Belongs to one `User`
- Has many `Message` (cascade delete)

**State Transitions**:
- **Created**: When user starts a new chat (no conversation_id provided)
- **Active**: When messages are being exchanged
- **Idle**: When no messages sent for a period (no explicit state, inferred from `last_message_at`)

**Validation Rules**:
- `openai_thread_id` format: Starts with "thread_" (OpenAI standard)
- `last_message_at` >= `created_at` (enforced by application logic)
- User can only access their own conversations (enforced by API layer)

**Indexes**:
- Primary: `id` (automatic)
- Foreign Key: `user_id` (explicit)
- Unique: `openai_thread_id` (explicit)
- Recommended additional index: `(user_id, last_message_at DESC)` for "recent conversations" query

---

### 4. Message (New - Phase 3)

**Purpose**: Represents a single message in a conversation. Can be from user or AI assistant.

**Schema**:
```python
from enum import Enum as PyEnum

class MessageRole(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    conversation_id: UUID = Field(
        sa_column=Column(
            ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )

    role: MessageRole = Field(
        sa_column=Column(
            Enum(MessageRole, name="message_role", native_enum=False),
            nullable=False
        )
    )

    content: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    # Relationships
    conversation: Optional[Conversation] = Relationship(
        back_populates="messages"
    )
```

**Constraints**:
- `id` PRIMARY KEY (UUID)
- `conversation_id` FOREIGN KEY to `conversations.id` with CASCADE DELETE
- `conversation_id` INDEXED (fast retrieval of conversation messages)
- `role` ENUM ('user', 'assistant') (prevents invalid roles)
- `content` TEXT type (supports up to 2000 characters, validated at API layer)
- `created_at` NOT NULL (every message has a timestamp)

**Relationships**:
- Belongs to one `Conversation`

**Validation Rules**:
- `role` must be either 'user' or 'assistant' (enforced by enum)
- `content` length: 1-2000 characters (enforced at API layer per spec FR-037)
- Messages are immutable once created (no updates, only inserts)
- Messages ordered by `created_at` ASC within a conversation

**Indexes**:
- Primary: `id` (automatic)
- Foreign Key: `conversation_id` (explicit)
- Recommended additional index: `(conversation_id, created_at ASC)` for chronological message retrieval

---

## Database Migrations

### Migration 001: Create Conversations and Messages Tables

**File**: `phase-3/backend/alembic/versions/001_create_chat_tables.py`

**Operations**:
1. Create `conversations` table with all columns and constraints
2. Create `messages` table with all columns and constraints
3. Create indexes:
   - `ix_conversations_user_id` on `conversations.user_id`
   - `ix_conversations_user_id_last_message_at` on `conversations(user_id, last_message_at DESC)`
   - `ix_messages_conversation_id` on `messages.conversation_id`
   - `ix_messages_conversation_id_created_at` on `messages(conversation_id, created_at ASC)`
4. Create `message_role` enum type (PostgreSQL specific)

**Rollback**:
1. Drop indexes
2. Drop `messages` table (cascade handles foreign key constraints)
3. Drop `conversations` table (cascade handles foreign key constraints)
4. Drop `message_role` enum type

**Testing**:
- Verify foreign key constraints (insert message with invalid conversation_id should fail)
- Verify cascade delete (deleting user should delete their conversations and messages)
- Verify unique constraint (inserting duplicate openai_thread_id should fail)
- Verify enum constraint (inserting message with invalid role should fail)

---

## Data Access Patterns

### ConversationRepository

**Interface**:
```python
class ConversationRepository(ABC):
    @abstractmethod
    async def create(self, user_id: UUID, openai_thread_id: str) -> Conversation:
        """Create a new conversation."""
        pass

    @abstractmethod
    async def get_by_id(self, conversation_id: UUID, user_id: UUID) -> Optional[Conversation]:
        """Retrieve conversation by ID with ownership verification."""
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """List user's conversations ordered by last_message_at DESC."""
        pass

    @abstractmethod
    async def update_last_message_at(self, conversation_id: UUID) -> None:
        """Update last_message_at timestamp to current time."""
        pass

    @abstractmethod
    async def delete(self, conversation_id: UUID, user_id: UUID) -> bool:
        """Delete conversation with ownership verification."""
        pass
```

**Query Patterns**:
- Get conversation: `SELECT * FROM conversations WHERE id = ? AND user_id = ?`
- List conversations: `SELECT * FROM conversations WHERE user_id = ? ORDER BY last_message_at DESC LIMIT ? OFFSET ?`
- Update timestamp: `UPDATE conversations SET last_message_at = ? WHERE id = ?`

---

### MessageRepository

**Interface**:
```python
class MessageRepository(ABC):
    @abstractmethod
    async def create(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str
    ) -> Message:
        """Create a new message in a conversation."""
        pass

    @abstractmethod
    async def list_by_conversation(
        self,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """List messages in chronological order."""
        pass

    @abstractmethod
    async def count_by_conversation(self, conversation_id: UUID) -> int:
        """Count total messages in a conversation."""
        pass

    @abstractmethod
    async def get_recent_messages(
        self,
        conversation_id: UUID,
        count: int = 20
    ) -> List[Message]:
        """Get the N most recent messages (for context truncation)."""
        pass
```

**Query Patterns**:
- Create message: `INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)`
- List messages: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT ? OFFSET ?`
- Recent messages: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?` (then reverse)

---

## Data Integrity Rules

### Referential Integrity
- **User deletion**: Cascade deletes conversations → cascade deletes messages (FR-032)
- **Conversation deletion**: Cascade deletes messages
- **Cannot insert message**: Without valid conversation_id
- **Cannot insert conversation**: Without valid user_id

### Consistency Rules
- **Conversation.last_message_at**: Must be updated atomically when message is inserted (use DB trigger or application transaction)
- **Message immutability**: Messages never updated after creation (append-only log)
- **OpenAI thread uniqueness**: One thread per conversation (prevents orphaned threads)

### Application-Level Constraints
- **User isolation**: All queries filtered by `user_id` from JWT (enforced in repository layer)
- **Message content length**: Max 2000 characters (validated in API layer per FR-037)
- **Conversation access**: User can only access conversations they own (403 Forbidden otherwise per FR-039)

---

## Storage Estimates

### Database Size Projections

**Assumptions**:
- 1000 active users
- Average 5 conversations per user per month
- Average 20 messages per conversation
- Average message size: 150 characters (user) + 300 characters (assistant) = 450 chars total per exchange

**Calculations**:
- Conversations per month: 1000 users × 5 conversations = 5000 conversations
- Messages per month: 5000 conversations × 20 messages = 100,000 messages
- Data size per month: 100,000 messages × 450 chars × 2 bytes/char ≈ 90 MB

**Annual Storage**: ~1 GB (excluding indexes)

**Index Overhead**: ~20-30% of data size ≈ 200-300 MB/year

**Total**: ~1.3 GB/year for 1000 active users

**Scaling**: Linear with user count. 10,000 users = ~13 GB/year.

---

## Performance Considerations

### Query Optimization
- **Conversation list**: Index on `(user_id, last_message_at DESC)` enables fast "recent conversations" query
- **Message retrieval**: Index on `(conversation_id, created_at ASC)` enables fast chronological fetch
- **Thread lookup**: Unique index on `openai_thread_id` enables fast OpenAI→DB mapping

### Caching Strategy
- **Conversation metadata**: Cache user's recent conversations (Redis, 5-minute TTL)
- **Message history**: Cache last 20 messages per conversation (invalidate on new message)
- **OpenAI thread mappings**: Cache `conversation_id → openai_thread_id` (permanent until conversation deleted)

### Pagination
- **Conversation list**: Default 20 per page, max 100
- **Message history**: Default 50 per page, max 200
- Use cursor-based pagination for consistency (timestamp-based cursors)

---

## Data Retention Policy

### Production Recommendations
- **Active conversations**: Keep indefinitely (user owns their data)
- **Inactive conversations**: Consider archival after 90 days of no activity (move to cold storage)
- **Message history**: Keep all messages for audit/compliance

### Compliance Considerations
- **GDPR**: User deletion must cascade delete all conversations/messages (already implemented via CASCADE)
- **Data export**: Support conversation export in JSON format (future feature)
- **Audit trail**: All message insertions logged with timestamps

---

## Testing Strategy

### Unit Tests (Repository Layer)
- Test CRUD operations for Conversation and Message entities
- Test cascade delete behavior (user deletion → conversations → messages)
- Test unique constraint violations (duplicate thread_id)
- Test ownership validation (accessing another user's conversation)

### Integration Tests (Database)
- Test foreign key constraints with real database
- Test index performance (query plans)
- Test transaction rollback on error
- Test concurrent message insertion (race conditions)

### Load Tests
- Insert 10,000 messages across 500 conversations
- Query conversation list (1000 users)
- Measure p95 latency for message retrieval
- Verify performance targets: <200ms for conversation history (per spec NFR)

---

## Schema Evolution

### Planned Enhancements (Future Phases)
- **Conversation.title**: Auto-generated summary of conversation topic (Phase 4+)
- **Message.tool_calls**: JSON field storing MCP tool invocations (Phase 3 iteration)
- **Message.metadata**: JSON field for token counts, model version, latency (Phase 3 iteration)
- **Conversation.archived**: Boolean flag for soft-delete/archival (Phase 4+)

### Backward Compatibility
- All schema changes must be backward compatible (add columns with defaults, never drop columns)
- Use database migrations (Alembic) for all schema changes
- Test migrations in staging environment before production deployment

---

## Summary

Phase 3 data model extends Phase 2 with two new entities (Conversation, Message) while maintaining full compatibility with existing User and Todo entities. The schema design prioritizes:

1. **User Isolation**: Foreign keys and indexes enforce ownership at database level
2. **Referential Integrity**: Cascade deletes prevent orphaned records
3. **Performance**: Indexes optimized for common query patterns (recent conversations, chronological messages)
4. **Scalability**: UUID primary keys enable distributed systems, pagination prevents large result sets
5. **Audit Trail**: Immutable message log with timestamps for compliance
6. **OpenAI Integration**: Unique thread_id links conversations to OpenAI's context management

**Next Step**: Generate API contracts in `/contracts/` directory based on these entities.
