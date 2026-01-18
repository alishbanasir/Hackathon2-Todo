# Phase 3 Database Migrations

This directory contains Alembic migrations for Phase 3: Todo AI Chatbot.

## Prerequisites

1. **Database connection configured**: Ensure `.env` file exists with valid `DATABASE_URL`
2. **Python environment activated**: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
3. **Dependencies installed**: `pip install -r requirements.txt`

## Applying Migrations

### First-time setup

```bash
# From phase-3/backend directory
alembic upgrade head
```

This will apply migration `001_create_chat_tables` which creates:
- `conversations` table (id, user_id, openai_thread_id, created_at, last_message_at)
- `messages` table (id, conversation_id, role, content, created_at)
- `message_role` enum type (user, assistant)
- All necessary indexes and foreign keys

### Verify migration status

```bash
alembic current
# Should show: 001_create_chat_tables (head)

alembic history
# Shows all available migrations
```

### Rollback migration (if needed)

```bash
# Rollback to base (before Phase 3 tables)
alembic downgrade -1

# Or completely remove Phase 3 tables
alembic downgrade base
```

## Creating New Migrations

When adding new models or modifying existing ones:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Or create empty migration for manual changes
alembic revision -m "description of changes"
```

## Database Schema

After applying migration `001_create_chat_tables`, the database will have:

### conversations table
- `id` (UUID, PK) - Unique conversation identifier
- `user_id` (UUID, FK to users.id) - Owner of conversation
- `openai_thread_id` (VARCHAR(255), UNIQUE) - OpenAI thread mapping
- `created_at` (TIMESTAMP WITH TIMEZONE) - Creation time
- `last_message_at` (TIMESTAMP WITH TIMEZONE, INDEXED) - Last activity time

### messages table
- `id` (UUID, PK) - Unique message identifier
- `conversation_id` (UUID, FK to conversations.id) - Parent conversation
- `role` (ENUM: user, assistant) - Message sender
- `content` (TEXT) - Message text
- `created_at` (TIMESTAMP WITH TIMEZONE, INDEXED) - Creation time

### Indexes
- `conversations`: id, user_id, last_message_at (for sorting recent chats)
- `messages`: id, conversation_id, created_at (for chronological ordering)

## Troubleshooting

### Migration fails with "relation already exists"

The tables might already exist. Check current state:
```bash
alembic current
```

If at base but tables exist, stamp the database:
```bash
alembic stamp 001_create_chat_tables
```

### "Can't locate revision identified by 'head'"

Run from the correct directory (phase-3/backend) where alembic.ini exists.
