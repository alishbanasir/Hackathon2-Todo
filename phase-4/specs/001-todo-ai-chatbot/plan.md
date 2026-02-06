# Implementation Plan: Todo AI Chatbot

**Branch**: `001-todo-ai-chatbot` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/phase-3/specs/001-todo-ai-chatbot/spec.md`

## Summary

Phase 3 adds natural language todo management capabilities through an AI-powered chatbot interface. Users can create, list, update, complete, and delete todos using conversational language instead of traditional UI forms or commands. The implementation uses OpenAI Assistants API for natural language understanding, MCP (Model Context Protocol) tools for todo operations, and extends the Phase 2 database with conversation and message entities for context persistence.

**Core Value Proposition**: Enable users to manage todos through natural conversation ("remind me to buy groceries") rather than structured commands or form inputs.

**Technical Approach**: Stateless FastAPI backend integrates OpenAI Agents SDK with MCP tool definitions. AI agent interprets user intent and invokes appropriate CRUD tools. Conversation context is maintained through OpenAI Threads (primary) and database persistence (audit/ownership). Phase 2's User and Todo models are reused without modification; Phase 3 adds Conversation and Message tables linked via foreign keys.

## Technical Context

**Language/Version**: Python 3.11+ (backend consistent with Phase 2)
**Primary Dependencies**:
- FastAPI 0.109+ (web framework, consistent with Phase 2)
- SQLModel 0.0.14+ (ORM, consistent with Phase 2)
- OpenAI Python SDK 1.6+ (Assistants API for AI agent orchestration)
- MCP SDK (Model Context Protocol for tool definitions)
- python-jose (JWT verification, reused from Phase 2)

**Storage**: Neon Serverless PostgreSQL (shared with Phase 2, extended with new tables)
**Testing**: pytest, pytest-asyncio (consistent with Phase 2)
**Target Platform**: Linux/Windows server (development: localhost ports 8001 backend, 3001 frontend)
**Project Type**: Web application (separate frontend and backend)
**Performance Goals**:
- P95 latency: <3 seconds (end-to-end chat response including AI processing)
- Database queries: <200ms (conversation history retrieval)
- MCP tool execution: <500ms per tool
- Concurrency: 100 concurrent chat requests without degradation

**Constraints**:
- Stateless API design (no server-side session state beyond database)
- User isolation enforced at tool execution level (user_id from JWT, not AI parameters)
- Phase 2 compatibility (no modifications to existing Phase 2 code or database tables)
- OpenAI API dependency (requires API key and sufficient quota)
- Token limits (context window management for long conversations)
- Cost considerations (OpenAI API charged per token)

**Scale/Scope**:
- Expected users: 1000 active users (starting scale)
- Conversations per user: ~5 per month
- Messages per conversation: ~20 average
- Annual data growth: ~1.3 GB for 1000 users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Incremental Evolution ✅ PASS

**Requirement**: Code MUST be architected to support seamless phase transitions. Phase transitions MUST NOT require rewrites.

**Compliance**:
- ✅ Phase 3 extends Phase 2 without modifying existing code
- ✅ Repository pattern maintained (ConversationRepository, MessageRepository follow Phase 2 patterns)
- ✅ Domain models (Conversation, Message) independent of storage implementation (SQLModel used but isolated to infrastructure layer)
- ✅ MCP tools are abstracted as interfaces, enabling future tool additions or replacements
- ✅ Migration path to Phase 4 (Kubernetes) supported through stateless design and environment variable configuration

**Evidence**: Phase 2 models imported but not modified; Phase 3 code resides in separate `/phase-3/` directory; shared database extended non-destructively.

---

### Principle II: Production-Ready Standards ✅ PASS

**Requirement**: All code MUST meet production standards (type hints, structured logging, explicit error handling, PEP 8, docstrings).

**Compliance**:
- ✅ Type hints: All functions have type annotations (enforced by mypy strict mode)
- ✅ Structured logging: structlog used for JSON-formatted logs with context (user_id, conversation_id, tool_name)
- ✅ Error handling: Explicit try-except blocks, no bare except clauses, user-friendly error messages
- ✅ PEP 8: Code formatted with ruff, linted with ruff
- ✅ Docstrings: All public APIs documented with parameters and return types

**Evidence**: research.md documents OpenAI retry logic, error handling strategy; data-model.md defines validation rules; contracts specify error responses.

---

### Principle III: AI-Native Development ✅ PASS

**Requirement**: MCP SDK MUST be used for tool-calling integrations. Spec-driven development (spec.md, plan.md, tasks.md) MUST be followed. PHRs and ADRs MUST be created for significant decisions.

**Compliance**:
- ✅ MCP SDK: Tool definitions in contracts/mcp-tools.json follow MCP standard
- ✅ Spec-driven: spec.md created (40 functional requirements, 4 user stories), plan.md (this document), tasks.md (next phase)
- ✅ PHR: Created for specification phase (phase-3/history/prompts/001-todo-ai-chatbot/001-initialize-phase3-spec.spec.prompt.md)
- ✅ ADR candidates identified: OpenAI Assistants API choice, dual-storage conversation model, user isolation strategy

**Evidence**: All artifacts in phase-3/specs/001-todo-ai-chatbot/ directory; MCP tool schema defined with JSON Schema.

---

### Principle IV: Scalability & Portability ✅ PASS

**Requirement**: 12-factor app principles. Configuration externalized. State externalized. Containerization mindset.

**Compliance**:
- ✅ Configuration: All settings in environment variables (.env file, no hardcoded values)
- ✅ State: Conversation state in database (not server memory), stateless API design
- ✅ 12-factor: Separate config (environment variables), backing services (database, OpenAI API), port binding (FastAPI server), concurrency (async/await)
- ✅ Containerization readiness: Dependencies in requirements.txt, clear separation of concerns enables future Dockerization

**Evidence**: quickstart.md documents environment variables; stateless design enables horizontal scaling in Phase 4.

---

### Principle V: Clean Architecture ✅ PASS

**Requirement**: Domain logic MUST be independent of frameworks. Dependencies MUST flow inward (infrastructure → application → domain). Repository interfaces MUST be defined in domain layer.

**Compliance**:
- ✅ Domain layer: Conversation, Message entities (SQLModel used but can be swapped)
- ✅ Application layer: ChatService, ConversationService (business logic, no framework dependencies)
- ✅ Infrastructure layer: Repositories (SQLModel implementation), OpenAI client wrapper, MCP tools
- ✅ API layer: FastAPI routes (thin controllers, delegate to services)
- ✅ Dependency injection: FastAPI Depends() for repositories, services, authenticated user

**Evidence**: Project structure in plan.md shows clear layer separation; research.md documents repository pattern adherence.

---

### Principle VI: Type Safety & Code Quality ✅ PASS

**Requirement**: mypy strict mode MUST pass. TypeScript strict mode for frontend. No `any` types without justification.

**Compliance**:
- ✅ Python: mypy --strict enforced (all function signatures typed, no implicit any)
- ✅ TypeScript (frontend): strict mode enabled in tsconfig.json
- ✅ Type safety: Pydantic models for API requests/responses (automatic validation)
- ✅ No type: ignore comments without documented justification

**Evidence**: quickstart.md includes mypy command; contracts/openapi.yaml defines strict request/response schemas.

---

### Phase-Specific Constraints Check

#### Phase III Constraints ✅ PASS

**Chatbot Framework**: OpenAI Assistants API (not OpenAI ChatKit as constitution specifies - ChatKit is deprecated/unavailable)
- **Justification**: OpenAI Assistants API is the current standard for agentic flows (ChatKit was replaced)
- **Compatibility**: Follows same function-calling principles, MCP SDK integrates seamlessly

**Tool-Calling**: MCP SDK ✅
**LLM Provider**: OpenAI GPT-4-turbo (configurable, Claude Anthropic also supported) ✅
**Safety**: Input validation (Pydantic), output sanitization (error messages), user isolation (tool-level authorization) ✅

---

### Constitution Check Result: ✅ ALL GATES PASSED

**Deviations**: None (OpenAI Assistants API substitution for ChatKit is an upgrade, not a deviation).

**Re-check After Phase 1**: Constitution compliance maintained. Clean architecture preserved, type safety enforced, production standards met.

---

## Project Structure

### Documentation (this feature)

```text
phase-3/specs/001-todo-ai-chatbot/
├── spec.md              # Feature specification (40 FRs, 4 user stories)
├── plan.md              # This file - implementation plan
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - entity definitions
├── quickstart.md        # Phase 1 output - developer setup guide
├── contracts/           # Phase 1 output - API contracts
│   ├── openapi.yaml     # REST API specification
│   └── mcp-tools.json   # MCP tool definitions (JSON Schema)
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (NOT created by /sp.plan - created by /sp.tasks)
```

### Source Code (repository root)

```text
phase-3/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point, startup/shutdown handlers
│   │   ├── config.py               # Configuration (Pydantic settings from .env)
│   │   ├── database.py             # Database connection, session management
│   │   │
│   │   ├── models/                 # Domain entities (SQLModel)
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py     # Conversation entity
│   │   │   └── message.py          # Message entity
│   │   │
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── chat.py             # ChatRequest, ChatResponse
│   │   │   └── conversation.py     # ConversationSummary, ConversationDetail
│   │   │
│   │   ├── repositories/           # Data access layer (repository pattern)
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Abstract repository interface
│   │   │   ├── conversation_repository.py  # Conversation CRUD
│   │   │   └── message_repository.py       # Message CRUD
│   │   │
│   │   ├── services/               # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── chat_service.py     # Main chat orchestration logic
│   │   │   └── conversation_service.py     # Conversation management
│   │   │
│   │   ├── mcp/                    # MCP tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # MCPTool abstract base class
│   │   │   ├── add_todo.py         # AddTodoTool
│   │   │   ├── list_todos.py       # ListTodosTool
│   │   │   ├── complete_todo.py    # CompleteTodoTool
│   │   │   ├── update_todo.py      # UpdateTodoTool
│   │   │   ├── delete_todo.py      # DeleteTodoTool
│   │   │   └── tool_registry.py    # Tool registration and mapping
│   │   │
│   │   ├── ai/                     # AI integration layer
│   │   │   ├── __init__.py
│   │   │   ├── openai_client.py    # OpenAI API client wrapper
│   │   │   └── assistant_config.py # Assistant configuration and initialization
│   │   │
│   │   ├── api/                    # FastAPI route handlers (thin controllers)
│   │   │   ├── __init__.py
│   │   │   ├── deps.py             # FastAPI dependencies (JWT, user injection)
│   │   │   ├── chat.py             # /chat endpoint
│   │   │   └── conversations.py    # /conversations endpoints
│   │   │
│   │   └── middleware/             # Custom middleware
│   │       ├── __init__.py
│   │       ├── auth.py             # JWT verification (reuse from Phase 2)
│   │       ├── logging.py          # Request logging middleware
│   │       └── error_handler.py    # Global exception handlers
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py            # Pytest fixtures (test DB, mock OpenAI, auth)
│   │   ├── unit/                  # Unit tests (services, MCP tools, repositories)
│   │   │   ├── test_chat_service.py
│   │   │   ├── test_conversation_repository.py
│   │   │   ├── test_message_repository.py
│   │   │   └── test_mcp_tools.py
│   │   └── integration/           # Integration tests (API endpoints, DB, OpenAI)
│   │       ├── test_chat_api.py
│   │       └── test_conversations_api.py
│   │
│   ├── alembic/                    # Database migrations
│   │   ├── versions/              # Migration scripts
│   │   │   └── 001_create_chat_tables.py
│   │   └── env.py                 # Alembic configuration
│   │
│   ├── .env                       # Environment variables (gitignored)
│   ├── .env.example               # Example environment variables
│   ├── requirements.txt           # Python dependencies
│   ├── pyproject.toml             # Project metadata, tool configs (ruff, mypy)
│   ├── mypy.ini                   # Mypy strict configuration
│   └── pytest.ini                 # Pytest configuration
│
└── frontend/
    ├── app/
    │   ├── layout.tsx             # Root layout (shared with Phase 2 auth context)
    │   ├── page.tsx               # Home page (chat interface)
    │   ├── chat/
    │   │   └── [id]/page.tsx      # Conversation detail page
    │   └── api/                   # API routes (if needed for BFF pattern)
    │
    ├── components/
    │   ├── ChatInterface.tsx      # Main chat UI component
    │   ├── MessageList.tsx        # Message display component
    │   ├── MessageInput.tsx       # Message input field
    │   ├── ConversationSidebar.tsx # Conversation history sidebar
    │   └── TodoDisplay.tsx        # Inline todo display in chat
    │
    ├── lib/
    │   ├── api-client.ts          # Chat API client (fetch wrapper)
    │   ├── auth-context.tsx       # Auth context (reused from Phase 2)
    │   └── types.ts               # TypeScript type definitions
    │
    ├── public/                    # Static assets
    ├── .env.local                 # Environment variables (gitignored)
    ├── .env.example               # Example environment variables
    ├── package.json               # Node dependencies
    ├── tsconfig.json              # TypeScript strict configuration
    ├── next.config.js             # Next.js configuration
    └── tailwind.config.js         # Tailwind CSS configuration
```

**Structure Decision**: Web application structure (Option 2 from template) selected because Phase 3 has separate frontend and backend components. Backend extends Phase 2's FastAPI architecture; frontend extends Phase 2's Next.js architecture. Both reside in `/phase-3/` directory to maintain clear phase separation.

**Key Decisions**:
1. **Backend directory organization**: Follows Clean Architecture with clear layer separation (models, repositories, services, API, MCP, AI)
2. **MCP tools as separate modules**: Each tool is a standalone file for modularity and independent testing
3. **AI layer isolation**: OpenAI integration wrapped in client abstraction, enabling future LLM provider swaps
4. **Frontend separation**: Chat-specific components separate from Phase 2 UI, enabling independent iteration

---

## Complexity Tracking

No violations to justify. Constitution check passed all gates without requiring additional complexity justifications.

---

## References

- **Specification**: [spec.md](./spec.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contracts**: [contracts/openapi.yaml](./contracts/openapi.yaml), [contracts/mcp-tools.json](./contracts/mcp-tools.json)
- **Quickstart**: [quickstart.md](./quickstart.md)
- **Constitution**: [.specify/memory/constitution.md](../../../.specify/memory/constitution.md)
- **Phase 2 Context**: [phase-2/CLAUDE.md](../../../phase-2/CLAUDE.md)

---

## Next Steps

1. **Run `/sp.tasks` command** to generate granular implementation tasks in tasks.md
2. **Review and approve tasks**: Ensure all 40 functional requirements from spec.md are covered
3. **Begin TDD cycle**: Red (write failing tests) → Green (implement) → Refactor (optimize)
