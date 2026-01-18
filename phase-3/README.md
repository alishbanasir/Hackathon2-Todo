# Phase 3: Todo AI Chatbot

**AI-powered conversational interface for natural language todo management**

---

## 📖 Overview

Phase 3 delivers a complete AI chatbot that allows users to manage their todos through natural language conversations. Built with OpenAI's GPT-4 and the Assistants API, it provides an intuitive interface for creating, listing, updating, completing, and deleting todos.

### Key Features

- 🤖 **Natural Language Processing**: Interact with todos using plain English
- 💬 **Conversational Interface**: Multi-turn conversations with context preservation
- 🔧 **MCP Tools**: 5 integrated tools for todo operations
- 🔐 **Secure**: JWT authentication with user isolation
- 📱 **Full-Stack**: FastAPI backend + Next.js frontend
- 🚀 **Production-Ready**: Rate limiting, health checks, Docker support

---

## 🏗️ Architecture

### Tech Stack

**Backend**:
- Python 3.11
- FastAPI (async web framework)
- SQLModel + AsyncPG (database ORM)
- OpenAI Assistants API (GPT-4)
- Structlog (structured logging)
- Alembic (database migrations)

**Frontend**:
- Next.js 15 (React framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Axios (HTTP client)
- date-fns (date formatting)

**Database**:
- PostgreSQL 15 (shared with Phase 2)

### High-Level Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Next.js   │────────▶│   FastAPI    │────────▶│  PostgreSQL │
│   Frontend  │  HTTP   │   Backend    │  Async  │  Database   │
│  (Port 3001)│◀────────│  (Port 8000) │◀────────│  (Port 5432)│
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               │ MCP Tools
                               ▼
                        ┌──────────────┐
                        │  OpenAI GPT-4│
                        │ Assistants API│
                        └──────────────┘
```

### Component Overview

**Backend** (`backend/`):
- `src/api/` - REST API endpoints (chat, conversations)
- `src/services/` - Business logic (ChatService, ConversationService)
- `src/mcp/` - MCP tools (add, list, update, complete, delete)
- `src/models/` - Database models (Conversation, Message)
- `src/repositories/` - Data access layer
- `src/middleware/` - Rate limiting, logging, error handling
- `src/ai/` - OpenAI client and configuration

**Frontend** (`frontend/`):
- `app/` - Next.js pages (home, chat, login)
- `components/` - React components (ChatInterface, MessageList, etc.)
- `lib/` - API client and authentication context

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- OpenAI API key
- Phase 2 Better Auth setup (for JWT tokens)

### Option 1: Docker Compose (Recommended)

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env and add your OpenAI API key and assistant ID

# 2. Start all services
cd phase-3
docker-compose up -d

# 3. Run database migrations
docker-compose exec backend alembic upgrade head

# 4. Access the application
# Frontend: http://localhost:3001
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend Setup**:

```bash
cd phase-3/backend

# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 4. Run database migrations
alembic upgrade head

# 5. Start the server
uvicorn src.main:app --reload --port 8000
```

**Frontend Setup**:

```bash
cd phase-3/frontend

# 1. Install dependencies
npm install

# 2. Set up environment variables
cp .env.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Start development server
npm run dev
# Opens at http://localhost:3001
```

---

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todo_app

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ASSISTANT_ID=asst_...

# Authentication (from Phase 2)
BETTER_AUTH_SECRET=your-secret-key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
APP_ENV=development
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3001,http://localhost:3000
```

**Frontend** (`.env.local`):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### OpenAI Assistant Setup

1. **Create an Assistant** at https://platform.openai.com/assistants
2. **Configure the Assistant**:
   - Name: "Todo AI Assistant"
   - Model: GPT-4 Turbo
   - Instructions: Use the instructions from `backend/src/ai/assistant_config.py`
3. **Add Function Tools**: Enable the 5 MCP tools (add_todo, list_todos, complete_todo, update_todo, delete_todo)
4. **Copy the Assistant ID** to your `.env` file

---

## 📚 API Documentation

### Endpoints

**Chat**:
- `POST /api/v1/chat` - Send message to AI assistant

**Conversations**:
- `GET /api/v1/conversations` - List user's conversations (paginated)
- `GET /api/v1/conversations/{id}` - Get conversation detail with messages
- `DELETE /api/v1/conversations/{id}` - Delete conversation

**System**:
- `GET /health` - Health check with component status
- `GET /` - API information
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

### Interactive API Documentation

Visit http://localhost:8000/docs for full interactive API documentation with request/response examples and try-it-out functionality.

### Rate Limiting

All API endpoints (except `/health`, `/docs`) are rate-limited to **60 requests per minute per user**.

Rate limit headers returned:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## 🧪 Testing

### Manual Testing

1. **Start the application** (backend + frontend)

2. **Get a JWT token** from Phase 2 authentication:
   ```bash
   # Via Phase 2 auth endpoint
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password"}'
   ```

3. **Login to frontend** at http://localhost:3001/login
   - Paste the JWT token
   - Click "Sign In"

4. **Test todo operations**:
   - "Add buy groceries to my list"
   - "Show me my tasks"
   - "Mark the first task as complete"
   - "Delete task 1"
   - "Change task 2 title to buy groceries and household items"

### API Testing with curl

```bash
# Get JWT token
TOKEN="your-jwt-token"

# Send a chat message
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add buy groceries to my list"}'

# List conversations
curl http://localhost:8000/api/v1/conversations?page=1&page_size=20 \
  -H "Authorization: Bearer $TOKEN"

# Health check
curl http://localhost:8000/health
```

---

## 📦 Deployment

### Backend Deployment (Railway/Render/Fly.io)

1. **Set environment variables** on your platform
2. **Deploy**:
   ```bash
   # The platform will automatically detect Dockerfile
   # and run: docker build -t app .
   ```
3. **Run migrations**:
   ```bash
   # SSH into container or use platform CLI
   alembic upgrade head
   ```

### Frontend Deployment (Vercel/Netlify)

1. **Connect your repository** to Vercel/Netlify
2. **Configure build settings**:
   - Build command: `npm run build`
   - Output directory: `.next`
   - Install command: `npm install`
3. **Set environment variables**:
   - `NEXT_PUBLIC_API_URL`: Your backend URL
4. **Deploy**: Platform will automatically build and deploy

### Database (Neon/Supabase)

1. **Create PostgreSQL database** on Neon or Supabase
2. **Update `DATABASE_URL`** in backend environment
3. **Run migrations** from local machine:
   ```bash
   DATABASE_URL="your-production-url" alembic upgrade head
   ```

---

## 🔍 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "phase": "3",
  "service": "todo-ai-chatbot",
  "openai_connected": true,
  "database_connected": true,
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### Logs

**Structured logging** with JSON format in production:

```bash
# Backend logs
docker-compose logs -f backend

# View specific log levels
docker-compose logs backend | grep ERROR
```

**Key log events**:
- `chat_processing_started` - User sent message
- `tool_call_received` - AI invoked MCP tool
- `tool_executed` - Tool completed execution
- `rate_limit_exceeded` - User hit rate limit
- `conversation_deleted` - Conversation removed

---

## 🛠️ Development

### Project Structure

```
phase-3/
├── backend/
│   ├── src/
│   │   ├── api/           # REST endpoints
│   │   ├── services/      # Business logic
│   │   ├── mcp/           # MCP tools
│   │   ├── models/        # Database models
│   │   ├── repositories/  # Data access
│   │   ├── middleware/    # Rate limiting, logging
│   │   ├── ai/            # OpenAI integration
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database setup
│   │   └── main.py        # Application entry
│   ├── alembic/           # Database migrations
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Production image
│   └── .env.example       # Environment template
├── frontend/
│   ├── app/               # Next.js pages
│   ├── components/        # React components
│   ├── lib/               # API client, auth
│   ├── package.json       # Node dependencies
│   └── .env.example       # Environment template
├── specs/                 # Specifications
├── history/               # Prompt history records
├── docker-compose.yml     # Local dev setup
└── README.md              # This file
```

### Adding a New MCP Tool

1. **Create tool file**: `backend/src/mcp/your_tool.py`
   ```python
   from src.mcp.base import MCPTool

   class YourTool(MCPTool):
       async def execute(self, parameters, user_id):
           # Implementation
           return {"success": True, ...}
   ```

2. **Register in registry**: `backend/src/mcp/tool_registry.py`
   ```python
   your_tool = YourTool(session=self.session)
   self._tools[your_tool.name] = your_tool
   ```

3. **Update assistant config**: `backend/src/ai/assistant_config.py`
   - Add tool to ASSISTANT_INSTRUCTIONS
   - Add tool definition to tools list

4. **Update OpenAI Assistant**: Add the new function tool in OpenAI dashboard

### Running Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## 🐛 Troubleshooting

### Backend won't start

**Issue**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Ensure you're running from the `backend/` directory and virtual environment is activated.

### OpenAI API errors

**Issue**: `401 Unauthorized` or `Invalid API key`

**Solution**:
1. Check `OPENAI_API_KEY` in `.env`
2. Verify API key at https://platform.openai.com/api-keys
3. Ensure you have credits in your OpenAI account

### Database connection errors

**Issue**: `could not connect to server: Connection refused`

**Solution**:
1. Start PostgreSQL: `docker-compose up postgres -d`
2. Check `DATABASE_URL` in `.env`
3. Verify port 5432 is not in use

### Frontend can't connect to backend

**Issue**: `Failed to fetch` or CORS errors

**Solution**:
1. Check backend is running on port 8000
2. Verify `NEXT_PUBLIC_API_URL` in `.env.local`
3. Check CORS configuration in `backend/src/config.py`

### Rate limit exceeded

**Issue**: `429 Too Many Requests`

**Solution**: Wait 60 seconds or adjust rate limit in `backend/src/main.py`:
```python
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)  # Increase to 120
```

---

## 📈 Performance

### Metrics

- **API Response Time**: < 2 seconds for chat messages
- **Database Query Time**: < 200ms
- **OpenAI API Time**: 1-5 seconds (varies by complexity)
- **Rate Limit**: 60 requests/minute/user
- **Concurrent Users**: 100+ (with async)

### Optimization Tips

1. **Database Indexes**: Already optimized with indexes on `user_id`, `last_message_at`, `conversation_id`
2. **Connection Pooling**: SQLAlchemy pool configured (min=5, max=20)
3. **Async Throughout**: All I/O operations use async/await
4. **OpenAI Timeout**: 10-second timeout prevents hanging requests

---

## 🔒 Security

### Implemented

- ✅ JWT authentication on all endpoints
- ✅ User isolation (users can only access their own data)
- ✅ Parameterized SQL queries (SQL injection prevention)
- ✅ Rate limiting (60 req/min/user)
- ✅ CORS restrictions (only allowed origins)
- ✅ Input validation (Pydantic schemas)
- ✅ Health check doesn't expose sensitive info

### Recommendations for Production

- 🔧 Use HTTPS for all traffic
- 🔧 Store JWT tokens in HTTP-only cookies (not localStorage)
- 🔧 Implement refresh token rotation
- 🔧 Add request signing for API calls
- 🔧 Enable database SSL connections
- 🔧 Use secrets manager for sensitive environment variables
- 🔧 Implement audit logging for sensitive operations
- 🔧 Add CSP headers to frontend

---

## 🤝 Contributing

This is a Phase 3 implementation for the Todo application. To contribute:

1. Follow the existing code structure
2. Use async/await for I/O operations
3. Add type hints to all functions
4. Update documentation for new features
5. Test thoroughly before submitting

---

## 📄 License

This project is part of the Q4 Hackathon series.

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4 and Assistants API
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **Better Auth** - Phase 2 authentication system

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation at `/docs`
3. Check Phase 2 documentation for auth issues
4. Review OpenAI Assistants API documentation

---

**Built with ❤️ for the Q4 Hackathon**
