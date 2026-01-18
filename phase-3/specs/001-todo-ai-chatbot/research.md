# Research: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-01-12
**Purpose**: Resolve technical unknowns and document technology decisions for Phase 3 AI Chatbot implementation

## Research Questions

### 1. OpenAI Agents SDK Integration

**Question**: How do we integrate OpenAI Agents SDK with FastAPI for asynchronous chat processing?

**Research Findings**:
- OpenAI Agents SDK (as of January 2025) provides the Assistants API which supports function calling (tool use)
- The SDK supports async operation through `AsyncOpenAI` client
- Agents can be configured with tools (functions) that map to MCP tool definitions
- Thread-based conversation management maintains context across multiple turns

**Decision**: Use OpenAI Assistants API with async client
- Create an Assistant configured with MCP tool definitions
- Use Threads to maintain conversation context
- Store thread IDs in Conversation table for persistence

**Rationale**:
- Async operation integrates seamlessly with FastAPI's async endpoints
- Built-in thread management provides conversation context without manual prompt engineering
- Function calling automatically maps user intent to tool invocations
- Official SDK provides stability and ongoing support

**Alternatives Considered**:
1. **OpenAI Chat Completions API with manual function calling**: More granular control but requires manual thread management and context assembly
2. **LangChain Agent Framework**: Additional abstraction layer, adds complexity and another dependency
3. **Custom NLU with pattern matching**: No LLM costs but significantly lower accuracy and requires extensive training data

**Implementation Notes**:
- Assistant creation should happen at application startup (reuse assistant ID)
- Thread creation happens per conversation (stored in Conversation.openai_thread_id)
- Tool results must be submitted back to the thread for context continuity

---

### 2. MCP SDK Tool Definition

**Question**: How do we define and register MCP tools that integrate with OpenAI function calling?

**Research Findings**:
- MCP SDK provides a standard protocol for tool definition and invocation
- Tools are defined with JSON Schema for parameters
- OpenAI function calling uses a compatible JSON Schema format
- MCP server can expose tools that OpenAI agents can discover and invoke

**Decision**: Define MCP tools as Python functions with Pydantic models for parameters
- Each tool (add_todo, list_todos, etc.) is a Python async function
- Pydantic models define input schemas (auto-convert to JSON Schema)
- MCP SDK server exposes tools via the Model Context Protocol
- OpenAI Assistant is configured with function definitions matching MCP tools

**Rationale**:
- Pydantic models provide type safety and automatic validation
- JSON Schema generation from Pydantic is native to FastAPI ecosystem
- MCP protocol ensures compatibility with future AI frameworks
- Clear separation between tool definition (MCP) and AI orchestration (OpenAI)

**Alternatives Considered**:
1. **Direct OpenAI function definitions**: Bypasses MCP, creates vendor lock-in
2. **GraphQL schema for tools**: Over-engineered for simple CRUD operations
3. **REST API with AI making HTTP calls**: Higher latency, complex error handling

**Implementation Notes**:
- Define base `MCPTool` interface with `name`, `description`, `parameters` schema
- Each tool implementation validates ownership (user_id) before execution
- Tool responses include success/failure status and structured data
- Tools are stateless - receive user_id and parameters, return results

---

### 3. Conversation State Management

**Question**: How do we maintain conversation context across stateless HTTP requests?

**Research Findings**:
- Stateless API design requires persisting conversation state to database
- OpenAI Threads provide built-in message history storage (in OpenAI's infrastructure)
- For audit/compliance, we need to persist messages in our database as well
- Conversation resumption requires passing conversation_id and retrieving associated thread_id

**Decision**: Dual-storage model for conversation state
- **Primary Context**: OpenAI Thread (managed by OpenAI, used for AI inference)
- **Audit Log**: Our database (Conversation + Message tables, used for history/compliance)
- Conversation table stores `openai_thread_id` to link the two

**Rationale**:
- OpenAI Threads handle the complexity of context window management and truncation
- Our database provides ownership control, audit trail, and offline access to history
- Separates concerns: OpenAI for AI context, our DB for user data management
- Enables conversation export and compliance features in future phases

**Alternatives Considered**:
1. **Only OpenAI Threads**: No audit trail, no user data ownership, vendor lock-in
2. **Only our database with manual context assembly**: Complex prompt engineering, token limit management
3. **Redis cache for ephemeral state**: Requires additional infrastructure, cache invalidation complexity

**Implementation Notes**:
- When creating a new conversation: Create Thread in OpenAI, create Conversation in DB, link via thread_id
- When resuming: Retrieve Conversation from DB by conversation_id, extract thread_id, continue Thread in OpenAI
- After each message exchange: Persist both user and assistant messages to our Message table
- Background job (future): Sync message history from OpenAI Threads to our DB for redundancy

---

### 4. User Isolation in AI Context

**Question**: How do we enforce user data isolation when AI agent is making database queries through MCP tools?

**Research Findings**:
- MCP tools are essentially functions that receive parameters from the AI
- AI could theoretically request any user_id in tool parameters if not restricted
- Tool implementations must validate that requested resources belong to authenticated user
- OpenAI Assistants can be customized per-user or shared with user_id in context

**Decision**: Inject authenticated user_id into MCP tool execution context
- JWT authentication extracts user_id before AI processing
- MCP tools receive user_id as an implicit parameter (injected by framework, not AI)
- AI provides resource identifiers (todo_id), tools validate ownership against injected user_id
- Return 403 Forbidden if AI attempts to access resources not owned by authenticated user

**Rationale**:
- Security boundary at tool execution level, not AI decision level
- AI cannot circumvent user isolation by clever prompt engineering
- Defense in depth: even if AI is compromised, tools enforce ownership
- Consistent with Phase 2 security model (user_id from JWT, not request body)

**Alternatives Considered**:
1. **Pass user_id to AI in system prompt**: AI could ignore or be manipulated to use different user_id
2. **Filter tool responses after execution**: Still executes unauthorized queries, performance impact
3. **Per-user Assistant instances**: Scalability concerns, higher OpenAI costs, management overhead

**Implementation Notes**:
- Create dependency injection for authenticated_user in FastAPI
- MCP tool wrapper injects user_id into all tool calls automatically
- Log all tool invocations with user_id and resource_id for audit trail
- Return clear error messages to AI when authorization fails (AI can inform user gracefully)

---

### 5. Error Handling in AI-Driven Workflows

**Question**: How do we handle errors from database operations, OpenAI API failures, and malformed AI requests gracefully?

**Research Findings**:
- AI agents can handle tool execution failures if provided structured error responses
- OpenAI API can fail due to rate limits, network issues, or quota exhaustion
- Database operations can fail due to constraints, connection issues, or deadlocks
- Users expect natural language error messages, not technical stack traces

**Decision**: Layered error handling with user-friendly AI responses
- **Tool Layer**: Catch database errors, return structured error responses to AI (e.g., `{"error": "todo_not_found", "message": "The task you're looking for doesn't exist"}`)
- **AI Layer**: OpenAI SDK errors (rate limits, timeouts) trigger retry logic (3 attempts) before returning fallback message
- **API Layer**: FastAPI exception handlers convert all errors to user-friendly HTTP responses
- **AI Communication**: AI reformulates technical errors into natural language for user

**Rationale**:
- Users should never see raw error codes or stack traces in chat
- AI can provide context-aware error explanations (e.g., "I couldn't find a task called 'groceries'. Did you mean 'buy groceries'?")
- Retries handle transient failures without user intervention
- Structured error responses enable AI to make intelligent recovery suggestions

**Alternatives Considered**:
1. **Fail fast without retries**: Poor user experience for transient failures
2. **Return raw errors to user**: Not user-friendly, exposes internal details
3. **Silent error suppression**: Hides problems, creates confusion when operations don't complete

**Implementation Notes**:
- Define error schema: `{"success": bool, "error_code": str | null, "message": str, "data": Any}`
- All MCP tools return this schema for both success and failure
- OpenAI client wrapped with retry decorator (exponential backoff)
- FastAPI HTTPException handlers provide fallback messages when AI cannot respond
- Log all errors with context for debugging (structlog with user_id, conversation_id, tool_name)

---

### 6. Natural Language to Todo Extraction

**Question**: How accurately can the AI extract todo title and description from natural language, and do we need fallback mechanisms?

**Research Findings**:
- GPT-4 and later models excel at entity extraction from natural language
- Function calling with well-defined schemas improves extraction accuracy
- Ambiguous inputs can be clarified through follow-up questions
- No additional NLP libraries needed - OpenAI models handle this natively

**Decision**: Rely on OpenAI's native NLU with structured tool parameters
- Define `add_todo` tool with required `title` (string) and optional `description` (string) parameters
- AI extracts title/description from messages like "remind me to buy milk tomorrow at the store"
- If AI cannot extract clear title, it asks clarifying question (built into Assistant instructions)
- No custom NLP pipelines or entity recognition libraries

**Rationale**:
- OpenAI models are specifically trained for entity extraction in function calling scenarios
- Reduces complexity by leveraging LLM's core strengths
- Clarifying questions provide better UX than guessing intent
- Accuracy sufficient for P1 success criteria (90% for clear commands)

**Alternatives Considered**:
1. **spaCy NER for entity extraction**: Unnecessary complexity, lower accuracy than LLM
2. **Regex patterns for command parsing**: Brittle, doesn't handle natural language variations
3. **Separate NLU model (BERT, etc.)**: Training data required, maintenance overhead

**Implementation Notes**:
- Assistant system prompt includes examples of good todo extraction
- Tool schema uses descriptive parameter names and descriptions to guide AI
- Validation in tool implementation: if title is empty or too vague, return error asking AI to clarify
- Future enhancement: Add `due_date` extraction when Phase 3 expands to scheduling

---

### 7. Performance and Cost Optimization

**Question**: How do we balance response time requirements (3s P95) with OpenAI API latency and token costs?

**Research Findings**:
- OpenAI API latency typically 1-2 seconds for chat completions
- Assistants API adds overhead for thread management (~500ms)
- Token costs accumulate with conversation history (context window)
- Streaming responses can improve perceived latency

**Decision**: Optimize for performance within cost constraints
- **Model Selection**: Use GPT-4-turbo for accuracy and speed (faster than GPT-4 base)
- **Context Management**: Limit conversation history to last 20 messages (truncate older messages from thread)
- **Streaming**: Implement streaming responses to reduce perceived latency (start displaying as tokens arrive)
- **Caching**: Cache Assistant configuration (reuse same assistant instance)
- **Async Processing**: All OpenAI calls are async to avoid blocking FastAPI event loop

**Rationale**:
- 3-second P95 latency is achievable with GPT-4-turbo (1-2s AI + <500ms DB + <500ms overhead)
- Streaming provides better UX even if total time is similar
- Context truncation prevents runaway token costs while maintaining recent context
- Async design maximizes throughput for concurrent users

**Alternatives Considered**:
1. **GPT-3.5-turbo**: Lower cost but significantly lower accuracy for complex intent extraction
2. **No truncation**: Costs grow linearly with conversation length, hits token limits eventually
3. **Synchronous processing**: Simpler code but poor scalability and performance

**Implementation Notes**:
- Set `max_tokens` limit on completions to prevent runaway generation
- Monitor token usage via OpenAI API response metadata
- Implement cost tracking: log tokens used per conversation for billing analysis
- Future optimization: Summarize old messages instead of truncating (preserves context, reduces tokens)

---

### 8. Database Schema for Conversation Entities

**Question**: What are the specific field types and constraints for Conversation and Message tables?

**Research Findings**:
- Conversations need unique identification, user ownership, timestamps, and OpenAI thread reference
- Messages need ordering, role distinction, content storage, and conversation membership
- SQLModel/SQLAlchemy best practices: use appropriate column types, indexes, and constraints
- Compatibility with Phase 2 User model required

**Decision**: Define SQLModel entities with full schema specification

**Conversation Table**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True, ondelete="CASCADE")
    openai_thread_id: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    last_message_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)
```

**Message Table**:
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True, ondelete="CASCADE")
    role: str = Field(sa_column=Column(Enum('user', 'assistant', name='message_role'), nullable=False))
    content: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

**Rationale**:
- UUID primary keys consistent with Phase 2 User model
- Indexes on user_id and conversation_id for efficient querying
- CASCADE delete ensures orphaned messages are removed when conversations deleted
- Enum for role field prevents invalid values
- Text type for content supports long messages (up to spec's 2000 char limit validated at API layer)
- Timestamps with timezone awareness for consistency with Phase 2

**Implementation Notes**:
- Migration script will create these tables alongside existing users and todos tables
- Foreign key to User table links conversations to authenticated users
- openai_thread_id unique constraint prevents duplicate thread references
- last_message_at updated on every message insertion (enables "recent conversations" queries)

---

## Technology Stack Summary

### Backend Stack (Phase 3 - /phase-3/backend/)
- **Framework**: FastAPI 0.109+ (consistent with Phase 2)
- **ORM**: SQLModel 0.0.14+ (consistent with Phase 2)
- **Database**: Neon PostgreSQL (extends Phase 2 database)
- **AI Integration**:
  - `openai` Python SDK (1.6.0+) - Official OpenAI API client
  - Assistants API for agent orchestration
- **MCP**: MCP SDK for tool definition (Model Context Protocol)
- **Authentication**: Reuse Phase 2 JWT middleware (python-jose)
- **Logging**: structlog (consistent with Phase 2)
- **Testing**: pytest, pytest-asyncio (consistent with Phase 2)
- **Type Checking**: mypy strict mode (consistent with Phase 2)

### Frontend Stack (Phase 3 - /phase-3/frontend/)
- **Framework**: Next.js 15+ (consistent with Phase 2)
- **Language**: TypeScript 5.x strict mode
- **UI Library**: React 18+ with Server Components
- **Styling**: Tailwind CSS (consistent with Phase 2)
- **API Client**: Fetch API with TypeScript types generated from OpenAPI
- **State Management**: React Context for chat state, React Query for server state
- **WebSocket/Streaming**: EventSource or fetch streaming for real-time chat responses

### Infrastructure (Development)
- **Development Database**: Shared Neon PostgreSQL from Phase 2 (extended with new tables)
- **Environment Variables**: `.env` file with OpenAI API key, database connection string
- **Local Development**: Backend on port 8001 (avoid conflict with Phase 2's 8000), Frontend on port 3001

### External Services
- **OpenAI API**: Assistants API (GPT-4-turbo recommended)
- **Database**: Neon Serverless PostgreSQL (shared with Phase 2)

---

## Architecture Patterns

### Clean Architecture Compliance
- **Domain Layer** (`/phase-3/backend/src/models/`): Conversation, Message entities (SQLModel)
- **Application Layer** (`/phase-3/backend/src/services/`): ChatService, ConversationService (business logic)
- **Infrastructure Layer** (`/phase-3/backend/src/`):
  - `repositories/`: ConversationRepository, MessageRepository (data access)
  - `ai/`: OpenAIAgentClient (AI integration)
  - `mcp/`: MCP tool implementations (add_todo, list_todos, etc.)
- **API Layer** (`/phase-3/backend/src/api/`): chat.py (FastAPI routes)

### Repository Pattern
- `ConversationRepository`: CRUD operations for Conversation entity
- `MessageRepository`: CRUD operations for Message entity
- `TodoRepository`: Reused from Phase 2 (no modifications needed)

### Dependency Injection
- FastAPI's `Depends()` for injecting repositories, services, authenticated user
- OpenAI client initialized at startup, injected into ChatService
- Database session management via async context managers

---

## Integration with Phase 2

### Shared Resources
- **Database**: Same Neon PostgreSQL instance (new tables: conversations, messages)
- **User Model**: Phase 3 references existing `users` table via foreign key
- **Todo Model**: Phase 3 MCP tools operate on existing `todos` table
- **Authentication**: Phase 3 reuses Phase 2's JWT middleware (same secret, same validation logic)

### Separation of Concerns
- Phase 2 code remains in `/phase-2/` directory (untouched)
- Phase 3 code in `/phase-3/` directory (new implementation)
- Shared models imported from Phase 2: `from phase_2.backend.src.models import User, Todo`
- Database migrations managed separately (Phase 3 adds tables, doesn't modify Phase 2 tables)

### API Boundaries
- Phase 2 API: `/api/v1/todos`, `/api/v1/auth` (existing endpoints)
- Phase 3 API: `/api/v1/chat` (new endpoint)
- No modifications to Phase 2 API contracts

---

## Risk Mitigation

### Risk 1: OpenAI API Availability
- **Mitigation**: Implement retry logic with exponential backoff (3 attempts)
- **Fallback**: Return user-friendly error message if all retries fail
- **Monitoring**: Log all OpenAI API failures with context for alerting

### Risk 2: Token Cost Overruns
- **Mitigation**: Context truncation (20 messages), max_tokens limit on completions
- **Monitoring**: Track token usage per conversation, alert on anomalies
- **Budget**: Set OpenAI spending limits in dashboard

### Risk 3: AI Misinterpreting User Intent
- **Mitigation**: Clarifying questions in Assistant instructions, structured tool schemas
- **Testing**: Acceptance tests with diverse natural language inputs (see spec SC-001: 90% success rate)
- **User Feedback**: Log messages where AI confidence is low for future training

### Risk 4: Performance SLA Violations (3s P95)
- **Mitigation**: Async processing, streaming responses, model optimization (GPT-4-turbo)
- **Monitoring**: Track endpoint latency, separate AI latency from DB latency
- **Escalation**: If P95 exceeds 3s, consider model downgrade (GPT-3.5) or response caching

### Risk 5: Security Vulnerabilities in AI Responses
- **Mitigation**: Tool-level authorization (user_id injection), output sanitization
- **Testing**: Security tests for cross-user access attempts, prompt injection attacks
- **Audit**: Log all tool invocations with user_id and resource_id

---

## Performance Benchmarks

### Target Metrics (from Spec)
- **P95 Latency**: <3 seconds (end-to-end chat response)
- **Concurrency**: 100 concurrent chat requests without degradation
- **Database Queries**: <200ms for conversation history retrieval
- **MCP Tool Invocation**: <500ms per tool execution

### Breakdown Estimates
- OpenAI API (GPT-4-turbo): ~1-2 seconds
- Database operations (async): ~100-200ms
- Application logic: ~100-200ms
- Network overhead: ~100-200ms
- **Total**: ~1.5-2.6 seconds (within 3s target)

### Load Testing Strategy
- Simulate 100 concurrent users sending chat messages
- Measure P95, P99 latency under load
- Identify bottlenecks (AI API, database, application)
- Optimize slowest component first

---

## Development Phases

### Phase 0: Research ✅ (This Document)
- Technology decisions finalized
- Architecture patterns defined
- Integration approach clarified

### Phase 1: Design (Next)
- `data-model.md`: Complete entity definitions with schemas
- `/contracts/`: OpenAPI spec for chat endpoint
- `quickstart.md`: Developer setup instructions

### Phase 2: Tasks (After Planning)
- `tasks.md`: Granular implementation tasks with acceptance criteria
- Task ordering by dependencies
- Estimation for each task

### Phase 3-5: Implementation (Future)
- Red: Write failing tests for each requirement
- Green: Implement minimal code to pass tests
- Refactor: Clean up, optimize, document

---

## Open Questions Resolved

All research questions have been answered. No remaining unknowns that block Phase 1 design.

**Status**: Research complete. Proceeding to Phase 1 (Design).
