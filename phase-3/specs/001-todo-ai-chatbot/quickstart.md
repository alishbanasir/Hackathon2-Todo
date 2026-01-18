# Quickstart Guide: Todo AI Chatbot (Phase 3)

**Feature**: 001-todo-ai-chatbot
**Last Updated**: 2026-01-12

## Overview

This guide will help you set up and run the Phase 3 Todo AI Chatbot locally. Phase 3 adds natural language todo management on top of the existing Phase 2 web application.

**What You'll Build**:
- AI chatbot backend with OpenAI Agents SDK
- MCP tools for todo CRUD operations
- Chat API endpoint (`POST /api/v1/chat`)
- Conversation and message persistence
- Integration with Phase 2 authentication and database

**Prerequisites**:
- Phase 2 is already set up and running (see `phase-2/specs/quickstart.md`)
- PostgreSQL database from Phase 2 is accessible
- OpenAI API account with API key
- Python 3.11+, Node.js 18+, npm/pnpm

---

## Architecture Overview

```
┌─────────────────┐
│   Phase 3 UI    │  (Next.js chat interface)
│  localhost:3001 │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│ Phase 3 Backend │  (FastAPI + OpenAI Agents)
│  localhost:8001 │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
    ▼         ▼              ▼
┌────────┐ ┌──────┐  ┌──────────────┐
│ Phase2 │ │ Neon │  │  OpenAI API  │
│ Models │ │ Postgres │  (Assistants)│
└────────┘ └──────┘  └──────────────┘
  (User,     (Shared      (AI Agent)
   Todo)     Database)
```

---

## Quick Setup (5 Minutes)

### 1. Clone and Navigate

```bash
cd phase-3
```

The `phase-3/` directory should have this structure after setup:
```
phase-3/
├── backend/         # FastAPI backend (to be created)
├── frontend/        # Next.js frontend (to be created)
└── README.md        # This file (to be created)
```

### 2. Backend Setup

#### 2.1 Create Backend Structure

```bash
cd phase-3
mkdir -p backend/src/{models,repositories,services,api,mcp,ai,middleware}
cd backend
```

#### 2.2 Install Python Dependencies

Create `requirements.txt`:
```text
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
openai==1.6.1
pydantic==2.5.0
pydantic-settings==2.1.0
structlog==24.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.26.0
alembic==1.13.1
```

Install:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2.3 Environment Variables

Create `.env` file in `phase-3/backend/`:
```env
# Database (shared with Phase 2)
DATABASE_URL=postgresql+asyncpg://user:password@your-neon-host/dbname

# Authentication (same secret as Phase 2)
BETTER_AUTH_SECRET=your-256-bit-secret-here

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_ASSISTANT_ID=asst_your-assistant-id-here

# Application
APP_ENV=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3001

# Server
API_HOST=0.0.0.0
API_PORT=8001
```

**Important**:
- `DATABASE_URL`: Use the same Neon database from Phase 2
- `BETTER_AUTH_SECRET`: Must match Phase 2's secret for JWT validation
- `OPENAI_API_KEY`: Get from OpenAI dashboard (https://platform.openai.com/api-keys)
- `OPENAI_ASSISTANT_ID`: Create an Assistant first (see Step 2.4)

#### 2.4 Create OpenAI Assistant

Before running the backend, create an Assistant in the OpenAI dashboard:

1. Go to https://platform.openai.com/assistants
2. Click "Create Assistant"
3. Configure:
   - **Name**: "Todo Assistant"
   - **Model**: gpt-4-turbo-preview (or gpt-4-1106-preview)
   - **Instructions**:
     ```
     You are a helpful todo list assistant. Help users manage their tasks through natural language conversation.

     When users express intent to create a task, extract the task title and optional description, then call the add_todo function.
     When users ask about their tasks, call the list_todos function.
     When users indicate a task is complete, identify the task and call the complete_todo function.
     When users want to modify a task, call the update_todo function.
     When users want to delete a task, call the delete_todo function.

     Always be conversational and friendly. If intent is unclear, ask clarifying questions.
     Provide confirmations after successful operations.
     ```
   - **Functions**: You'll define these programmatically (MCP tools will be registered via API)
4. Copy the Assistant ID (starts with `asst_`) and add to `.env`

#### 2.5 Run Database Migration

Create migration for new tables:

```bash
cd phase-3/backend

# Initialize Alembic (if not already done)
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Add conversation and message tables"

# Apply migration
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade -> 001, Add conversation and message tables
```

Verify tables exist:
```bash
psql $DATABASE_URL -c "\dt"
```

Should show: `users`, `todos`, `conversations`, `messages`

#### 2.6 Start Backend Server

```bash
cd phase-3/backend
source venv/bin/activate  # If not already activated
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Test the health endpoint:
```bash
curl http://localhost:8001/health
# Expected: {"status": "healthy", "phase": "3"}
```

---

### 3. Frontend Setup

#### 3.1 Create Frontend Structure

```bash
cd phase-3
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
```

Answer prompts:
- ✅ TypeScript: Yes
- ✅ ESLint: Yes
- ✅ Tailwind CSS: Yes
- ✅ `app/` directory: Yes
- ❌ `src/` directory: No
- ✅ Import alias: Yes (@/*)

#### 3.2 Install Dependencies

```bash
npm install @tanstack/react-query axios date-fns
npm install -D @types/node
```

#### 3.3 Environment Variables

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_PHASE_2_API_URL=http://localhost:8000/api/v1
```

#### 3.4 Start Frontend Server

```bash
npm run dev
```

Expected output:
```
   ▲ Next.js 15.0.0
   - Local:        http://localhost:3001
   - Network:      http://192.168.1.x:3001

 ✓ Ready in 2.3s
```

Open browser: http://localhost:3001

---

## Verify Setup

### Backend Verification

1. **Health Check**:
   ```bash
   curl http://localhost:8001/health
   ```
   Expected: `{"status": "healthy", "phase": "3"}`

2. **API Docs**:
   Open http://localhost:8001/docs
   - Should see interactive Swagger UI
   - Endpoints: `/chat`, `/conversations`, `/conversations/{id}`

3. **Database Connection**:
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        http://localhost:8001/api/v1/conversations
   ```
   Expected: `{"conversations": [], "total": 0}`

### Frontend Verification

1. **Home Page**:
   - Navigate to http://localhost:3001
   - Should see Phase 3 chat interface

2. **Authentication**:
   - Login using Phase 2 credentials (backend on port 8000)
   - JWT token should be stored and used for Phase 3 API calls

### End-to-End Test

1. **Start a Conversation**:
   ```bash
   curl -X POST http://localhost:8001/api/v1/chat \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Add a task to buy groceries"
     }'
   ```

   Expected response:
   ```json
   {
     "conversation_id": "uuid-here",
     "message": "I've added 'Buy groceries' to your todo list.",
     "tool_calls": [
       {
         "tool": "add_todo",
         "result": {
           "success": true,
           "todo_id": 1,
           "title": "Buy groceries"
         }
       }
     ]
   }
   ```

2. **Verify Todo Created**:
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        http://localhost:8000/api/v1/todos
   ```

   Should include the newly created todo.

---

## Development Workflow

### Running Both Phases Simultaneously

**Terminal 1 - Phase 2 Backend**:
```bash
cd phase-2/backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Phase 3 Backend**:
```bash
cd phase-3/backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8001
```

**Terminal 3 - Phase 2 Frontend** (optional):
```bash
cd phase-2/frontend
npm run dev  # Runs on port 3000
```

**Terminal 4 - Phase 3 Frontend**:
```bash
cd phase-3/frontend
npm run dev  # Runs on port 3001
```

### Development Tools

#### API Testing (HTTPie)

```bash
# Install HTTPie
pip install httpie

# Test chat endpoint
http POST localhost:8001/api/v1/chat \
  Authorization:"Bearer $JWT_TOKEN" \
  message="Show me my tasks"
```

#### Database GUI (pgAdmin or DBeaver)

Connect to Neon database:
- **Host**: your-neon-host.neon.tech
- **Port**: 5432
- **Database**: your-database-name
- **User**: your-username
- **Password**: your-password

Useful queries:
```sql
-- View all conversations
SELECT * FROM conversations ORDER BY last_message_at DESC;

-- View messages in a conversation
SELECT * FROM messages WHERE conversation_id = 'uuid-here' ORDER BY created_at ASC;

-- Count todos by user
SELECT user_id, COUNT(*) FROM todos GROUP BY user_id;
```

#### Logs and Debugging

**Backend Logs** (structured JSON):
```bash
tail -f phase-3/backend/logs/app.log
```

**Frontend Logs**:
```bash
# Check browser console (F12)
# Or check Next.js terminal output
```

**OpenAI API Logs**:
- Dashboard: https://platform.openai.com/logs
- Monitor token usage and errors

---

## Common Issues and Solutions

### Issue 1: Backend Won't Start

**Symptom**: `ModuleNotFoundError: No module named 'openai'`

**Solution**:
```bash
cd phase-3/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 2: Database Connection Error

**Symptom**: `asyncpg.exceptions.InvalidPasswordError`

**Solution**:
1. Verify `DATABASE_URL` in `.env` is correct
2. Check Neon dashboard for connection string
3. Ensure Phase 2 database is accessible:
   ```bash
   psql $DATABASE_URL -c "SELECT 1"
   ```

### Issue 3: OpenAI API Rate Limit

**Symptom**: `429 Too Many Requests` from OpenAI API

**Solution**:
1. Check usage: https://platform.openai.com/usage
2. Upgrade OpenAI plan if needed
3. Implement request throttling in code (future enhancement)

### Issue 4: JWT Token Invalid

**Symptom**: `401 Unauthorized` on chat endpoint

**Solution**:
1. Verify `BETTER_AUTH_SECRET` matches Phase 2's secret
2. Generate new token by logging in via Phase 2
3. Check token expiration (re-login if expired)

### Issue 5: Assistant Not Calling Tools

**Symptom**: AI responds but doesn't create todos

**Solution**:
1. Verify MCP tools are registered with Assistant (check logs)
2. Ensure tool definitions match OpenAI function calling format
3. Check Assistant instructions emphasize tool usage
4. Test with explicit commands: "Use the add_todo function to create a task"

---

## Testing

### Running Unit Tests

```bash
cd phase-3/backend
pytest tests/unit/ -v
```

Expected output:
```
tests/unit/test_repositories.py::test_create_conversation PASSED
tests/unit/test_services.py::test_chat_service_create PASSED
tests/unit/test_mcp_tools.py::test_add_todo_tool PASSED
...
```

### Running Integration Tests

```bash
pytest tests/integration/ -v
```

These tests hit the real database (test schema) and OpenAI API (using separate assistant).

### Manual Testing Checklist

- [ ] User can send a message and receive AI response
- [ ] AI creates todos from natural language
- [ ] AI lists todos accurately
- [ ] AI completes todos when requested
- [ ] AI updates todo titles/descriptions
- [ ] AI deletes todos when confirmed
- [ ] Conversation history is persisted
- [ ] User can only access their own conversations
- [ ] Error messages are user-friendly
- [ ] Response time is under 3 seconds (P95)

---

## Next Steps

1. **Implement Frontend Chat UI**:
   - Chat message input and display
   - Conversation history sidebar
   - Authentication integration with Phase 2

2. **Add Streaming Responses**:
   - Implement Server-Sent Events for real-time AI responses
   - Improve perceived latency

3. **Enhance MCP Tools**:
   - Add more sophisticated intent recognition
   - Support for bulk operations (e.g., "complete all tasks")

4. **Monitoring and Observability**:
   - Add Prometheus metrics for API latency
   - Track OpenAI token usage
   - Set up alerting for error rates

5. **Run Tasks Command**:
   ```bash
   /sp.tasks  # Generate granular implementation tasks
   ```

---

## Useful Commands

### Backend

```bash
# Start dev server
uvicorn src.main:app --reload --port 8001

# Run type checking
mypy src --strict

# Run linting
ruff check src

# Format code
ruff format src

# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Run type checking
npm run type-check

# Run linting
npm run lint

# Run tests
npm test
```

### Database

```bash
# Connect to database
psql $DATABASE_URL

# View table schema
psql $DATABASE_URL -c "\d conversations"

# Reset database (⚠️ CAUTION: Deletes all data)
alembic downgrade base
alembic upgrade head
```

---

## Resources

- **Specification**: [spec.md](./spec.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contracts**: [contracts/](./contracts/)
- **Phase 2 Quickstart**: [phase-2/specs/quickstart.md](../../../phase-2/specs/quickstart.md)
- **OpenAI Assistants Docs**: https://platform.openai.com/docs/assistants
- **MCP SDK Docs**: https://modelcontextprotocol.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/

---

## Support

For issues or questions:
1. Check specification documents in this directory (spec.md, plan.md, data-model.md)
2. Review Phase 2 setup if integration issues arise
3. Consult OpenAI documentation for AI-specific problems
4. Check Neon dashboard for database issues

**Estimated Setup Time**: 15-30 minutes (excluding OpenAI Assistant creation)
