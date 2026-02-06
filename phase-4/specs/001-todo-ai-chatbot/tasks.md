# Tasks: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Branch**: `001-todo-ai-chatbot`
**Input**: Design documents from `phase-3/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/ (all present)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Each user story can be developed and validated independently after the foundational phase is complete.

**Tests**: No test tasks included (not explicitly requested in specification - add later if TDD is desired).

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- All descriptions include exact file paths

## Path Conventions

This is a web application with separate backend and frontend:
- **Backend**: `phase-3/backend/src/`
- **Frontend**: `phase-3/frontend/`
- **Tests**: `phase-3/backend/tests/`
- **Migrations**: `phase-3/backend/alembic/versions/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for Phase 3

**Tasks**:

- [ ] T001 Create backend directory structure: phase-3/backend/src/{models,repositories,services,api,mcp,ai,middleware}
- [X] T002 [P] Create backend requirements.txt with dependencies: fastapi==0.109.0, sqlmodel==0.0.14, openai==1.6.1, python-jose, structlog, asyncpg, alembic
- [X] T003 [P] Create backend pyproject.toml with ruff, mypy strict mode, and pytest configuration
- [X] T004 [P] Create backend .env.example with required environment variables: DATABASE_URL, OPENAI_API_KEY, OPENAI_ASSISTANT_ID, BETTER_AUTH_SECRET
- [X] T005 [P] Create backend src/config.py using Pydantic Settings for environment variable management
- [X] T006 [P] Create backend src/database.py with async database connection and session management (reuse Phase 2 connection string)
- [X] T007 [P] Initialize Alembic for database migrations in phase-3/backend/alembic/
- [X] T008 [P] Create frontend Next.js structure: npx create-next-app@latest phase-3/frontend with TypeScript, Tailwind, App Router
- [X] T009 [P] Create frontend .env.example with NEXT_PUBLIC_API_URL and NEXT_PUBLIC_PHASE_2_API_URL

**Checkpoint**: Basic project structure ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema (FR-001 to FR-005)

- [X] T010 Create Conversation model in phase-3/backend/src/models/conversation.py with fields: id (UUID), user_id (FK to users), openai_thread_id (unique), created_at, last_message_at
- [X] T011 [P] Create Message model in phase-3/backend/src/models/message.py with fields: id (UUID), conversation_id (FK), role (enum: user/assistant), content (Text), created_at
- [X] T012 Create MessageRole enum in phase-3/backend/src/models/message.py (USER, ASSISTANT)
- [X] T013 Create Alembic migration 001_create_chat_tables.py to create conversations and messages tables with indexes and foreign keys
- [X] T014 Apply database migration and verify schema in Neon database

### Shared Infrastructure

- [X] T015 [P] Create base repository interface in phase-3/backend/src/repositories/base.py with abstract CRUD methods
- [X] T016 [P] Create ConversationRepository in phase-3/backend/src/repositories/conversation_repository.py implementing create, get_by_id, list_by_user, update_last_message_at, delete
- [X] T017 [P] Create MessageRepository in phase-3/backend/src/repositories/message_repository.py implementing create, list_by_conversation, get_recent_messages
- [X] T018 [P] Create OpenAI client wrapper in phase-3/backend/src/ai/openai_client.py with async methods for thread creation, message sending, run execution
- [X] T019 [P] Create Assistant configuration in phase-3/backend/src/ai/assistant_config.py for loading OpenAI Assistant ID and instructions from environment
- [X] T020 [P] Create FastAPI dependencies in phase-3/backend/src/api/deps.py for JWT verification (reuse Phase 2 auth), database session injection, authenticated user extraction
- [X] T021 [P] Create authentication middleware in phase-3/backend/src/middleware/auth.py for JWT token validation (import from Phase 2 if available)
- [X] T022 [P] Create logging middleware in phase-3/backend/src/middleware/logging.py using structlog for JSON-formatted request/response logs
- [X] T023 [P] Create global error handler in phase-3/backend/src/middleware/error_handler.py for FastAPI exceptions with user-friendly error messages (FR-034 to FR-040)
- [X] T024 Create FastAPI main app in phase-3/backend/src/main.py with CORS configuration, middleware registration, startup/shutdown handlers, health endpoint

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Todo Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create todos through natural language messages like "remind me to buy groceries tomorrow"

**Independent Test**: Send message "add a task to buy groceries" → verify todo is created in database with user_id from JWT

**Success Criteria**: 90% success rate for clear todo creation commands (SC-001)

### MCP Tool Implementation (FR-006)

- [X] T025 [P] [US1] Create MCPTool abstract base class in phase-3/backend/src/mcp/base.py with execute() method signature
- [X] T026 [P] [US1] Implement AddTodoTool in phase-3/backend/src/mcp/add_todo.py accepting title (required, 1-200 chars) and description (optional, 0-2000 chars) parameters
- [X] T027 [US1] Add user_id injection to AddTodoTool from execution context (not AI parameter) for user isolation (FR-011, FR-031)
- [X] T028 [US1] Add validation to AddTodoTool for title length and empty string prevention (FR-037, return validation_error)
- [X] T029 [US1] Add error handling to AddTodoTool for database errors with user-friendly messages (FR-035, return database_error)
- [X] T030 [P] [US1] Create tool registry in phase-3/backend/src/mcp/tool_registry.py to register and map MCP tools to OpenAI function definitions

### Service Layer (FR-016, FR-017)

- [X] T031 [US1] Create ChatService in phase-3/backend/src/services/chat_service.py with process_message() method
- [X] T032 [US1] Implement OpenAI Assistants API integration in ChatService: create thread (new conversation), add message, run assistant, wait for completion
- [X] T033 [US1] Implement tool call handler in ChatService to invoke AddTodoTool when AI requests add_todo function
- [X] T034 [US1] Implement conversation persistence in ChatService: save user message, save assistant response to messages table (FR-018)
- [X] T035 [US1] Implement user_id injection into MCP tool execution context from JWT token in ChatService (FR-015, FR-030, FR-031)
- [X] T036 [US1] Add error handling in ChatService for OpenAI API failures with retry logic (3 attempts) and fallback messages (FR-036)

### API Layer (FR-014, FR-015)

- [X] T037 [P] [US1] Create Pydantic schemas in phase-3/backend/src/schemas/chat.py: ChatRequest (message, optional conversation_id), ChatResponse (conversation_id, message, tool_calls)
- [X] T038 [US1] Create chat endpoint POST /api/v1/chat in phase-3/backend/src/api/chat.py with JWT authentication dependency
- [X] T039 [US1] Implement request validation in chat endpoint: message length 1-2000 chars (FR-037), extract user_id from JWT (FR-015)
- [X] T040 [US1] Implement conversation creation logic: if no conversation_id, create new Conversation with new OpenAI thread (FR-020)
- [X] T041 [US1] Implement conversation continuation logic: if conversation_id provided, verify ownership and load existing thread (FR-019, FR-032)
- [X] T042 [US1] Connect chat endpoint to ChatService and return ChatResponse with conversation_id, assistant message, tool results (FR-021)
- [X] T043 [US1] Add error responses to chat endpoint: 401 for invalid JWT (FR-038), 403 for unauthorized conversation access (FR-039), 400 for invalid request (FR-040)

### Logging and Audit (FR-033)

- [X] T044 [P] [US1] Add structured logging to ChatService with user_id, conversation_id, tool_name, latency for all chat interactions
- [X] T045 [P] [US1] Add structured logging to AddTodoTool with user_id, todo_id, title for audit trail

**Checkpoint**: At this point, User Story 1 is fully functional - users can create todos through natural language and see confirmation responses

**MVP Scope**: User Story 1 alone constitutes a minimal viable product - ship this first for early user feedback

---

## Phase 4: User Story 2 - Conversational Todo Management (Priority: P2)

**Goal**: Enable users to list, complete, and delete todos through natural language commands

**Independent Test**: Send "show me my tasks" → verify todo list returned. Send "mark task 42 as done" → verify completion. Send "delete task 42" → verify deletion.

**Success Criteria**: 85% accuracy for explicit list/complete/delete commands (SC-003), 2-second response for listing (SC-002)

### MCP Tools Implementation (FR-007, FR-008, FR-010)

- [X] T046 [P] [US2] Implement ListTodosTool in phase-3/backend/src/mcp/list_todos.py accepting optional completed filter (boolean or null)
- [X] T047 [P] [US2] Implement CompleteTodoTool in phase-3/backend/src/mcp/complete_todo.py accepting todo_id parameter
- [X] T048 [P] [US2] Implement DeleteTodoTool in phase-3/backend/src/mcp/delete_todo.py accepting todo_id parameter
- [X] T049 [US2] Add user_id injection to ListTodosTool, CompleteTodoTool, DeleteTodoTool from execution context for user isolation (FR-011, FR-012, FR-031)
- [X] T050 [US2] Add ownership validation to CompleteTodoTool and DeleteTodoTool: verify todo belongs to authenticated user before operation (FR-012, return not_found on failure)
- [X] T051 [US2] Add error handling to all US2 tools: not_found for invalid todo_id, authorization_error for ownership violations, database_error for failures (FR-035)
- [X] T052 [US2] Register US2 tools (list_todos, complete_todo, delete_todo) in tool registry with OpenAI function definitions

### Service Layer Enhancement

- [X] T053 [US2] Extend ChatService tool handler to support list_todos, complete_todo, delete_todo invocations from AI (FR-023, FR-024, FR-025)
- [X] T054 [US2] Implement natural language recognition for listing intents: "show my tasks", "what do I need to do", "list todos" (FR-023)
- [X] T055 [US2] Implement natural language recognition for completion intents: "mark as done", "complete", "finish", "I finished" (FR-024)
- [X] T056 [US2] Implement natural language recognition for deletion intents: "delete", "remove", "get rid of" (FR-025)
- [X] T057 [US2] Add context-aware todo identification: when user says "complete the grocery task", map to correct todo_id using recent list results (FR-027)

### Assistant Configuration

- [X] T058 [US2] Update OpenAI Assistant instructions in phase-3/backend/src/ai/assistant_config.py to emphasize list/complete/delete tool usage for respective user intents

**Checkpoint**: At this point, User Stories 1 AND 2 both work - users can create, list, complete, and delete todos conversationally

---

## Phase 5: User Story 3 - Todo Updates and Modifications (Priority: P3)

**Goal**: Enable users to edit existing todo details through conversational instructions like "change the project report task to include design diagrams"

**Independent Test**: Create todo, then send "rename buy groceries to buy groceries and household items" → verify title updated

### MCP Tool Implementation (FR-009)

- [X] T059 [P] [US3] Implement UpdateTodoTool in phase-3/backend/src/mcp/update_todo.py accepting todo_id (required) and optional title, description, completed parameters
- [X] T060 [US3] Add user_id injection and ownership validation to UpdateTodoTool: verify todo belongs to authenticated user (FR-012, FR-031)
- [X] T061 [US3] Add validation to UpdateTodoTool: title 1-200 chars if provided, description 0-2000 chars if provided, at least one field must be updated (FR-009)
- [X] T062 [US3] Add error handling to UpdateTodoTool: not_found for invalid todo_id, validation_error for invalid parameters, authorization_error for ownership violations (FR-035)
- [X] T063 [US3] Register update_todo tool in tool registry with OpenAI function definition

### Service Layer Enhancement

- [X] T064 [US3] Extend ChatService tool handler to support update_todo invocations from AI (FR-026)
- [X] T065 [US3] Implement natural language recognition for update intents: "change", "update", "modify", "rename" (FR-026)
- [X] T066 [US3] Implement natural language extraction for update parameters: distinguish between title changes, description additions, and status toggles (FR-027)

### Assistant Configuration

- [X] T067 [US3] Update OpenAI Assistant instructions to emphasize update_todo tool usage for modification intents

**Checkpoint**: All basic todo management works - users can create, list, complete, update, and delete todos through natural language

---

## Phase 6: User Story 4 - Conversation Context and History (Priority: P4)

**Goal**: Enable multi-turn conversations with context preservation and allow users to view conversation history

**Independent Test**: Send "what tasks do I have?" → list returned. Follow up with "complete the first one" → verify bot understands reference without re-listing

**Success Criteria**: Conversation history persisted correctly (SC-006), users can resume conversations

### Service Layer

- [X] T068 [P] [US4] Create ConversationService in phase-3/backend/src/services/conversation_service.py with list_conversations(), get_conversation_detail(), delete_conversation() methods
- [X] T069 [US4] Implement pagination in ConversationService.list_conversations(): default 20 per page, max 100, ordered by last_message_at DESC
- [X] T070 [US4] Implement conversation ownership validation in ConversationService: user can only access their own conversations (FR-032)
- [X] T071 [US4] Implement context truncation in ChatService: load last 20 messages from conversation for OpenAI context window management (token limit constraint from spec)

### API Layer

- [X] T072 [P] [US4] Create Pydantic schemas in phase-3/backend/src/schemas/conversation.py: ConversationSummary, ConversationDetail, MessageResponse
- [X] T073 [P] [US4] Create conversations endpoint GET /api/v1/conversations in phase-3/backend/src/api/conversations.py with JWT authentication and pagination parameters
- [X] T074 [P] [US4] Create conversation detail endpoint GET /api/v1/conversations/{id} in phase-3/backend/src/api/conversations.py returning conversation with message history
- [X] T075 [P] [US4] Create conversation delete endpoint DELETE /api/v1/conversations/{id} in phase-3/backend/src/api/conversations.py with ownership verification (FR-032)
- [X] T076 [US4] Connect conversations endpoints to ConversationService and enforce user isolation via JWT (FR-029, FR-030)
- [X] T077 [US4] Add error responses: 401 for invalid JWT, 403 for unauthorized access (FR-038, FR-039), 404 for conversation not found

### Context Management

- [X] T078 [US4] Implement last_message_at timestamp update in ChatService whenever a message is added to conversation (database consistency)
- [X] T079 [US4] Implement reference resolution in ChatService: when user says "complete the first one", use conversation context to identify referenced todo from previous list_todos result

**Checkpoint**: All user stories complete - full conversation management with context awareness

---

## Phase 7: Frontend Implementation

**Purpose**: Build Next.js chat interface for Phase 3

**Note**: Frontend tasks can run in parallel with backend US1-US4 after foundational backend is ready

### Core Components

- [X] T080 [P] Create ChatInterface component in phase-3/frontend/components/ChatInterface.tsx with message list and input field
- [X] T081 [P] Create MessageList component in phase-3/frontend/components/MessageList.tsx displaying user and assistant messages with role indicators
- [X] T082 [P] Create MessageInput component in phase-3/frontend/components/MessageInput.tsx with textarea, send button, character counter (max 2000)
- [X] T083 [P] Create ConversationSidebar component in phase-3/frontend/components/ConversationSidebar.tsx listing recent conversations with timestamps
- [X] T084 [P] Create TodoDisplay component in phase-3/frontend/components/TodoDisplay.tsx for inline todo rendering in chat messages

### API Client

- [X] T085 [P] Create API client in phase-3/frontend/lib/api-client.ts with sendMessage(), getConversations(), getConversationDetail(), deleteConversation() methods
- [X] T086 [P] Add JWT token injection to API client from auth context (reuse Phase 2 auth context)
- [X] T087 [P] Add error handling to API client for 401 (redirect to login), 403 (show error), 400 (validation errors)

### Pages and Routing

- [X] T088 [P] Create home page in phase-3/frontend/app/page.tsx rendering ChatInterface with new conversation
- [X] T089 [P] Create conversation detail page in phase-3/frontend/app/chat/[id]/page.tsx loading existing conversation by ID
- [X] T090 [P] Create auth context provider wrapper in phase-3/frontend/lib/auth-context.tsx (reuse from Phase 2 or create Phase 3-specific)

### Styling and UX

- [X] T091 [P] Style ChatInterface with Tailwind CSS: clean message bubbles, differentiate user/assistant messages
- [X] T092 [P] Add loading states: message sending indicator, typing indicator while AI processes
- [X] T093 [P] Add error display: toast notifications for API errors, inline validation errors for message length

**Checkpoint**: Frontend fully functional - users can chat, view history, switch conversations

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements, observability, and production readiness

### Performance Optimization (NFR)

- [ ] T094 [P] Add database connection pooling configuration in phase-3/backend/src/database.py (target: <200ms query latency)
- [ ] T095 [P] Add index verification script to check (user_id, last_message_at) and (conversation_id, created_at) indexes exist
- [ ] T096 [P] Implement async/await throughout ChatService and repositories to avoid blocking (concurrency: 100 concurrent requests)
- [ ] T097 [P] Add request timeout configuration to OpenAI client: 10-second timeout for assistant runs

### Error Handling and Resilience (FR-036)

- [ ] T098 [P] Implement exponential backoff retry logic for OpenAI API rate limits (429 errors) with max 3 retries
- [ ] T099 [P] Add circuit breaker pattern for OpenAI API: if 5 consecutive failures, return cached response or error for 60 seconds
- [ ] T100 [P] Add database transaction rollback handlers in repositories to prevent partial state on errors

### Observability (NFR - Maintainability)

- [ ] T101 [P] Add structured logging to all API endpoints with request_id, user_id, latency, status_code
- [ ] T102 [P] Add tool execution metrics: log tool_name, user_id, execution_time_ms, success/failure for all MCP tool invocations
- [ ] T103 [P] Add conversation metrics: track messages_per_conversation, tools_called_per_message for cost monitoring
- [ ] T104 [P] Create logging configuration in phase-3/backend/src/main.py: JSON format in production, pretty-print in development

### Security Hardening (NFR - Security)

- [ ] T105 [P] Add input sanitization: strip HTML tags from message content before sending to OpenAI
- [ ] T106 [P] Add SQL injection prevention verification: ensure all repository methods use parameterized queries (SQLModel handles this)
- [ ] T107 [P] Add rate limiting middleware in phase-3/backend/src/middleware/rate_limiter.py: 60 requests per minute per user
- [ ] T108 [P] Add CORS configuration review: restrict origins to Phase 3 frontend URL only (no wildcard)

### Documentation

- [ ] T109 [P] Create API documentation: ensure Swagger UI at /docs shows all Phase 3 endpoints with examples
- [ ] T110 [P] Update phase-3/specs/001-todo-ai-chatbot/quickstart.md with final setup instructions and verification steps
- [ ] T111 [P] Create developer guide in phase-3/README.md: architecture overview, local setup, testing instructions

### Deployment Preparation

- [ ] T112 [P] Create Dockerfile for phase-3/backend with Python 3.11, FastAPI, and dependencies
- [ ] T113 [P] Create docker-compose.yml for local Phase 3 development with backend, frontend, and Phase 2 services
- [ ] T114 [P] Create environment variable validation script: check all required vars (DATABASE_URL, OPENAI_API_KEY, etc.) at startup
- [ ] T115 [P] Add health check endpoint verification: /health returns {"status": "healthy", "phase": "3", "openai_connected": true}

**Checkpoint**: Phase 3 is production-ready with observability, error handling, and deployment artifacts

---

## Dependency Graph (User Story Order)

```
Phase 1 (Setup) → Phase 2 (Foundational)
                      ↓
        ┌─────────────┴─────────────┬───────────────┬──────────────┐
        ↓                           ↓               ↓              ↓
    US1 (P1) 🎯 MVP           US2 (P2)         US3 (P3)       US4 (P4)
    (Create todos)        (List/Complete/     (Update        (Context/
                           Delete)             todos)         History)
        ↓                           ↓               ↓              ↓
        └─────────────┬─────────────┴───────────────┴──────────────┘
                      ↓
              Phase 7 (Frontend) - can run in parallel after Phase 2
                      ↓
              Phase 8 (Polish)
```

**Key Dependencies**:
- **US1 is independent** - can be shipped as MVP
- **US2 depends on US1** - reuses ChatService, adds more MCP tools
- **US3 depends on US1** - adds update capability to existing flow
- **US4 is independent of US1-US3** - focuses on conversation management, not todo logic
- **Frontend can start after Phase 2** - parallel with US1-US4 backend work
- **Phase 8 (Polish) requires all user stories** - cross-cutting enhancements

---

## Parallel Execution Examples

### After Phase 2 Complete (T001-T024):

**Parallel Tracks for User Stories**:
- **Track A**: T025-T045 (US1 - Natural Language Todo Creation) - Developer 1
- **Track B**: T046-T058 (US2 - List/Complete/Delete) - Developer 2 (after US1 core service is done, or in parallel with minor coordination)
- **Track C**: T080-T093 (Frontend) - Developer 3 (can start immediately after Phase 2)

**Within User Story 1 (US1 - T025-T045)**:
Can parallelize:
- T025 (MCPTool base) + T037 (Pydantic schemas) + T044-T045 (logging setup)
- T026-T030 (AddTodoTool + registry) can run while T031-T036 (ChatService) is being designed
- T038-T043 (API layer) can start once T037 (schemas) and T031 (ChatService interface) are defined

**Within User Story 2 (US2 - T046-T058)**:
Can parallelize:
- T046, T047, T048 (three MCP tools) - completely independent
- T052 (tool registry update) after T046-T048 complete
- T053-T057 (ChatService enhancements) can run in parallel with T046-T051 if interfaces are clear

**Within Frontend (T080-T093)**:
Can parallelize:
- T080-T084 (all components) - completely independent React components
- T085-T087 (API client) - independent of components
- T088-T090 (pages) depend on components and API client
- T091-T093 (styling/UX) can happen anytime after components exist

### Phase 8 (Polish - T094-T115):
Almost all tasks are independent and can run in parallel:
- Performance (T094-T097) - 4 developers
- Error handling (T098-T100) - 1 developer
- Observability (T101-T104) - 1 developer
- Security (T105-T108) - 1 developer
- Documentation (T109-T111) - 1 developer
- Deployment (T112-T115) - 1 developer

**Estimated Parallel Reduction**: With 3-4 developers, Phase 3 can be completed in ~40-50% of sequential time.

---

## Implementation Strategy

### MVP-First Approach

**Ship US1 First** (T001-T045):
- Value: Users can immediately create todos through chat
- Validation: Test core AI integration and user adoption
- Feedback loop: Understand if natural language is compelling before building more features

**Then Ship US2** (T046-T058):
- Value: Full todo lifecycle management (list, complete, delete)
- Builds on US1 infrastructure with minimal risk

**Then Ship US3 and US4** (T059-T079):
- Enhancement features that improve UX but aren't blocking

### Incremental Delivery

Each user story is a **shippable increment**:
- US1 alone = minimal viable chatbot (can ship)
- US1 + US2 = complete todo management chatbot (production-ready)
- US1 + US2 + US3 = feature parity with Phase 2 UI (full replacement)
- US1 + US2 + US3 + US4 = delightful conversational experience (competitive advantage)

### Quality Gates

Before moving to next phase:
1. **Phase 2 → US1**: All foundational tests pass, database migrations applied, authentication works
2. **US1 → US2**: US1 acceptance scenarios pass (can create todos via chat), P95 latency < 3s
3. **US2 → US3**: US2 acceptance scenarios pass (can list/complete/delete via chat)
4. **US3 → US4**: US3 acceptance scenarios pass (can update todos via chat)
5. **US4 → Phase 8**: All 4 user stories pass independent tests, conversation history persists correctly

---

## Risk Mitigation

### High-Risk Tasks (May Block Progress)

1. **T018 (OpenAI client wrapper)**: External API dependency
   - Mitigation: Create mock OpenAI client for local testing first
   - Fallback: Use synchronous OpenAI SDK if async causes issues

2. **T033 (Tool call handler in ChatService)**: Complex AI integration logic
   - Mitigation: Start with simple tool dispatch, iterate to handle edge cases
   - Fallback: Manual tool invocation mapping if function calling unreliable

3. **T071 (Context truncation)**: Token limit management critical for performance
   - Mitigation: Test with long conversations early, adjust truncation strategy
   - Fallback: Summarization or shorter context window (10 messages instead of 20)

4. **T079 (Reference resolution)**: Ambiguous user references hard to resolve
   - Mitigation: Store last tool results in conversation context for simple lookups
   - Fallback: Ask user to clarify when reference is ambiguous (graceful degradation per FR-028)

### Medium-Risk Tasks

- **T030 (Tool registry)**: Mapping MCP tools to OpenAI function format may require schema adjustments
- **T036 (Error handling with retries)**: Complex error scenarios to test
- **T054-T057 (Natural language recognition)**: AI may misinterpret user intent despite training

---

## Performance Targets (NFR Validation)

After completion, verify:

- **Chat endpoint P95 latency < 3 seconds** (SC-005, T096, T097)
  - Measure: Add prometheus metrics, analyze P95 over 1000 requests
  - Target breakdown: OpenAI 1-2s + Database 100-200ms + App 100-200ms + Network 100-200ms

- **Database queries < 200ms** (T094, T095)
  - Measure: Log all query execution times, analyze P95
  - Verify indexes exist: (user_id, last_message_at), (conversation_id, created_at)

- **MCP tool execution < 500ms per tool** (T101, T102)
  - Measure: Log tool execution times in structured logs
  - Optimize Phase 2 todo queries if needed

- **Concurrent users: 100 without degradation** (T096)
  - Load test: Use locust or k6 to simulate 100 concurrent chat requests
  - Verify: Connection pooling configured (T094), async/await used (T096)

---

## Summary

**Total Tasks**: 115 tasks across 8 phases

**Task Breakdown by Phase**:
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 15 tasks
- Phase 3 (US1 - Todo Creation): 21 tasks (T025-T045)
- Phase 4 (US2 - List/Complete/Delete): 13 tasks (T046-T058)
- Phase 5 (US3 - Updates): 9 tasks (T059-T067)
- Phase 6 (US4 - Context/History): 12 tasks (T068-T079)
- Phase 7 (Frontend): 14 tasks (T080-T093)
- Phase 8 (Polish): 22 tasks (T094-T115)

**Task Breakdown by User Story**:
- US1: 21 tasks (MVP scope)
- US2: 13 tasks
- US3: 9 tasks
- US4: 12 tasks
- Infrastructure: 60 tasks (Setup + Foundational + Frontend + Polish)

**Parallel Opportunities**:
- 62 tasks marked with [P] can run in parallel within their phase
- User stories US1, US2, US3, US4 can partially overlap after foundational phase
- Frontend (Phase 7) can start immediately after Phase 2 completes

**Critical Path**: Phase 1 → Phase 2 → US1 (MVP) → US2 → US3 → US4 → Phase 8

**Recommended MVP**: Phase 1 + Phase 2 + Phase 3 (US1) = 45 tasks for minimal viable chatbot

**Estimated Effort** (assuming 1 task ≈ 2-4 hours):
- Sequential: 230-460 hours (~6-12 weeks for 1 developer)
- Parallel (3-4 developers): 80-150 hours (~2-4 weeks)

**Next Steps**:
1. Review and approve this task breakdown
2. Assign Phase 1 and Phase 2 tasks to developers
3. Begin implementation with TDD approach (write failing tests first if tests are added later)
4. Ship US1 as MVP after Phase 2 + Phase 3 complete
