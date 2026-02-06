# Feature Specification: Todo AI Chatbot

**Feature Branch**: `001-todo-ai-chatbot`
**Created**: 2026-01-12
**Status**: Draft
**Input**: User description: "Initialize Phase 3: Todo AI Chatbot inside the /phase-3 directory based on the following specification. First, read the existing Todo and User models from /phase-2/src/models/ to ensure compatibility. Then, implement the following: 1. Database Schema: Create 'Conversation' and 'Message' tables in /phase-3/backend/models.py. 2. MCP Tools: Implement tools for add, list, complete, delete, and update tasks that interact with the database. 3. Chat Endpoint: Create a stateless POST /api/{user_id}/chat endpoint using OpenAI Agents SDK. 4. Logic: Ensure the AI agent can intelligently map natural language to the correct MCP tools. Specification Detail: - Backend: FastAPI - ORM: SQLModel - Database: Neon PostgreSQL - AI: OpenAI Agents SDK + MCP SDK"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Todo Creation (Priority: P1)

Users can create todos by chatting naturally without needing to remember exact command syntax or navigate through forms.

**Why this priority**: This is the core value proposition of an AI chatbot - enabling users to quickly capture tasks through natural conversation. Without this, the feature provides no advantage over the existing web interface.

**Independent Test**: Can be fully tested by sending a message like "remind me to buy groceries tomorrow" and verifying a todo is created with the appropriate title.

**Acceptance Scenarios**:

1. **Given** a logged-in user, **When** they send a chat message "add a task to finish the project report", **Then** a new todo is created with title "Finish the project report" and the chatbot confirms the creation
2. **Given** a logged-in user, **When** they send "I need to call mom this evening", **Then** a new todo is created with an appropriate title extracted from the message
3. **Given** a logged-in user, **When** they send a message with both title and description context like "remind me to review the PR - it's the authentication one", **Then** a todo is created with the main task as title and additional context as description

---

### User Story 2 - Conversational Todo Management (Priority: P2)

Users can list, complete, and delete todos through natural language queries and commands.

**Why this priority**: After creation, users need to view and update their tasks. This enables full task lifecycle management through conversation.

**Independent Test**: Can be tested by asking "what tasks do I have?" and verifying the list is returned, then saying "mark the first one as done" and verifying the completion.

**Acceptance Scenarios**:

1. **Given** a user with existing todos, **When** they ask "show me my tasks" or "what do I need to do?", **Then** the chatbot returns a formatted list of their todos with completion status
2. **Given** a user viewing their task list, **When** they say "complete the grocery task" or "mark buy groceries as done", **Then** the matching todo is marked complete and confirmed
3. **Given** a user with a completed todo, **When** they say "delete the grocery task" or "remove buy groceries", **Then** the todo is deleted and confirmed
4. **Given** a user with multiple todos, **When** they ask "show me only incomplete tasks", **Then** the chatbot filters and returns only uncompleted todos

---

### User Story 3 - Todo Updates and Modifications (Priority: P3)

Users can edit existing todo details through conversational instructions.

**Why this priority**: While less critical than creation and basic management, editing provides flexibility for users who need to modify task details without recreating them.

**Independent Test**: Can be tested by creating a todo, then saying "change the project report task to include design diagrams" and verifying the update.

**Acceptance Scenarios**:

1. **Given** an existing todo, **When** user says "update my project report task to mention design review", **Then** the todo title or description is updated accordingly
2. **Given** an existing todo, **When** user says "rename buy groceries to buy groceries and household items", **Then** the todo title is updated
3. **Given** a completed todo, **When** user says "mark the grocery task as incomplete" or "reopen buy groceries", **Then** the todo completion status is toggled back to incomplete

---

### User Story 4 - Conversation Context and History (Priority: P4)

Users can have multi-turn conversations where the chatbot remembers context from earlier in the conversation.

**Why this priority**: Improves user experience by enabling more natural conversations, but the basic functionality works without persistent context.

**Independent Test**: Can be tested by asking "what tasks do I have?", then following up with "complete the first one" and verifying the bot understands the reference.

**Acceptance Scenarios**:

1. **Given** a user lists their todos in a message, **When** they follow up with "complete the first one" without specifying which task, **Then** the chatbot uses conversation context to identify and complete the referenced todo
2. **Given** a user asks about a specific task, **When** they say "delete it" in the next message, **Then** the chatbot understands the reference and deletes the previously discussed todo
3. **Given** a multi-turn conversation, **When** the user sends a new request after several exchanges, **Then** the system maintains context for the duration of the conversation session

---

### Edge Cases

- What happens when the AI cannot confidently parse the user's intent (ambiguous commands)?
- How does the system handle requests to modify todos that don't exist or match multiple items?
- What happens when a user tries to create a todo with an empty or invalid title?
- How does the system respond when a user asks a general question unrelated to todos (e.g., "what's the weather?")?
- What happens if the underlying todo database operation fails during an AI-assisted action?
- How does the system handle very long messages or conversations that exceed context limits?
- What happens when a user references "the task" but there's no clear context about which task they mean?

## Requirements *(mandatory)*

### Functional Requirements

**Database Schema & Models:**
- **FR-001**: System MUST create a Conversation entity to track chat sessions, with fields for conversation ID, user ID, created timestamp, and last message timestamp
- **FR-002**: System MUST create a Message entity to track individual messages, with fields for message ID, conversation ID, role (user/assistant), content, and timestamp
- **FR-003**: System MUST maintain referential integrity between Conversation and Message entities (one-to-many relationship)
- **FR-004**: System MUST reuse existing Todo and User models from Phase 2 for compatibility
- **FR-005**: System MUST maintain foreign key relationships: Conversation → User (many-to-one) and Todo → User (many-to-one)

**MCP Tools Implementation:**
- **FR-006**: System MUST implement an "add_todo" MCP tool that accepts title (required) and description (optional) parameters and creates a todo in the database for the authenticated user
- **FR-007**: System MUST implement a "list_todos" MCP tool that retrieves all todos for the authenticated user with optional filtering by completion status
- **FR-008**: System MUST implement a "complete_todo" MCP tool that marks a specified todo as complete by todo ID
- **FR-009**: System MUST implement an "update_todo" MCP tool that modifies a todo's title, description, or completion status by todo ID
- **FR-010**: System MUST implement a "delete_todo" MCP tool that removes a todo by todo ID
- **FR-011**: All MCP tools MUST enforce user isolation - users can only access and modify their own todos
- **FR-012**: All MCP tools MUST validate todo ownership before performing update, complete, or delete operations
- **FR-013**: MCP tools MUST return structured responses indicating success/failure and relevant data

**Chat Endpoint & AI Integration:**
- **FR-014**: System MUST expose a stateless POST endpoint at /api/v1/chat/{user_id} that accepts a message and optional conversation ID
- **FR-015**: System MUST authenticate requests using JWT tokens and extract user_id from the token (not from the URL parameter for authorization)
- **FR-016**: System MUST integrate OpenAI Agents SDK to process natural language messages and determine appropriate MCP tool invocations
- **FR-017**: System MUST configure the AI agent with access to all five MCP tools (add, list, complete, update, delete)
- **FR-018**: System MUST persist conversation messages (both user and assistant) to the database for conversation history
- **FR-019**: System MUST support conversation continuation by accepting an optional conversation_id parameter
- **FR-020**: System MUST create a new conversation if no conversation_id is provided
- **FR-021**: Chat endpoint MUST return the assistant's response message, conversation ID, and any tool execution results

**Natural Language Understanding:**
- **FR-022**: AI agent MUST recognize todo creation intents from messages like "add task", "remind me to", "I need to", "create a todo for"
- **FR-023**: AI agent MUST recognize todo listing intents from messages like "show my tasks", "what do I need to do", "list todos"
- **FR-024**: AI agent MUST recognize completion intents from messages like "mark as done", "complete", "finish", "I finished"
- **FR-025**: AI agent MUST recognize deletion intents from messages like "delete", "remove", "get rid of"
- **FR-026**: AI agent MUST recognize update intents from messages like "change", "update", "modify", "rename"
- **FR-027**: AI agent MUST extract task titles and descriptions from natural language with reasonable accuracy
- **FR-028**: System MUST handle ambiguous requests by asking clarifying questions through the chat interface

**User Isolation & Security:**
- **FR-029**: System MUST verify JWT token on every chat request
- **FR-030**: System MUST ensure user_id from JWT matches the user_id in the URL path for authorization
- **FR-031**: System MUST scope all MCP tool operations to the authenticated user's data only
- **FR-032**: System MUST prevent users from accessing or modifying conversations that don't belong to them
- **FR-033**: System MUST log all chat interactions with user_id for audit purposes

**Error Handling & Responses:**
- **FR-034**: System MUST return user-friendly error messages when the AI cannot parse intent
- **FR-035**: System MUST return clear error messages when MCP tool operations fail (e.g., todo not found, database error)
- **FR-036**: System MUST handle OpenAI API failures gracefully with appropriate fallback messages
- **FR-037**: System MUST validate message content length (maximum 2000 characters per message)
- **FR-038**: Chat endpoint MUST return 401 Unauthorized for invalid or missing JWT tokens
- **FR-039**: Chat endpoint MUST return 403 Forbidden when user attempts to access another user's conversation
- **FR-040**: Chat endpoint MUST return 400 Bad Request for malformed or invalid requests

### Key Entities

- **Conversation**: Represents a chat session between a user and the AI assistant. Contains: unique conversation ID, user ID (foreign key to User), creation timestamp, last updated timestamp. Relationships: belongs to one User, has many Messages.

- **Message**: Represents a single message in a conversation. Contains: unique message ID, conversation ID (foreign key to Conversation), role (enum: 'user' or 'assistant'), message content text, timestamp. Relationships: belongs to one Conversation.

- **Todo** (existing from Phase 2): Represents a task item. Contains: unique todo ID, user ID (foreign key to User), title, description, completion status, creation timestamp. Relationships: belongs to one User. Referenced by MCP tools for task management.

- **User** (existing from Phase 2): Represents an authenticated user. Contains: unique user ID (UUID), email, password hash, creation timestamp. Relationships: has many Todos, has many Conversations.

- **MCP Tool Invocation** (conceptual): Represents the AI's decision to call a specific tool with parameters. Not persisted to database but tracked in conversation context and message metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully create todos through natural language messages with 90% success rate for clear, unambiguous commands (e.g., "add task to buy milk")
- **SC-002**: Users can list their todos and receive properly formatted responses showing all their tasks within 2 seconds
- **SC-003**: Users can complete and delete todos through conversational commands with 85% accuracy for explicitly stated commands
- **SC-004**: System maintains user isolation - zero instances of users accessing or modifying another user's todos through the chat interface
- **SC-005**: Chat endpoint responds within 3 seconds for 95% of requests (including AI processing time)
- **SC-006**: All conversation history is persisted correctly - users can resume conversations and see previous message history
- **SC-007**: System gracefully handles ambiguous commands by asking clarifying questions rather than making incorrect assumptions

## Assumptions

1. Users are already authenticated through Phase 2's JWT authentication system - Phase 3 will reuse the same authentication mechanism
2. OpenAI API key will be provided via environment variables and the account has sufficient API quota
3. The OpenAI Agents SDK supports synchronous or async operation compatible with FastAPI's async architecture
4. MCP SDK provides a standard interface for tool definition and invocation that integrates with OpenAI Agents
5. Natural language processing will be handled primarily by OpenAI's models - no custom NLP training required
6. Conversation context will be maintained through message history rather than session state (stateless API design)
7. The Neon PostgreSQL database from Phase 2 will be extended with new tables for Conversation and Message entities
8. Phase 3 will be implemented as a separate module within the /phase-3 directory but will reference Phase 2 models
9. All Phase 2 API endpoints remain functional - Phase 3 adds new chat functionality without replacing existing REST API
10. Basic todo operations (CRUD) are sufficient - advanced features like tags, due dates, priorities are out of scope
11. The AI will use function calling (tool use) to invoke MCP tools based on user intent
12. Error messages from AI tool invocations should be user-friendly, not technical database or code errors

## Out of Scope

The following features are explicitly excluded from Phase 3:

1. **Voice input/output**: Text-only chat interface
2. **Multi-language support**: English only for natural language processing
3. **Collaborative features**: No shared todos or multi-user conversations
4. **Rich media**: No support for images, attachments, or formatted text in chat
5. **Advanced scheduling**: No due dates, reminders, or calendar integration in chat commands
6. **Todo categorization**: No tags, categories, or projects through chat interface
7. **Analytics**: No usage analytics, sentiment analysis, or conversation metrics
8. **Custom AI training**: Using pre-trained OpenAI models only, no fine-tuning
9. **Mobile-specific features**: No push notifications or mobile app integration
10. **Export functionality**: No ability to export conversation history or chat logs through the interface
11. **Admin features**: No admin dashboard for monitoring conversations or AI performance
12. **Rate limiting per user**: Basic API rate limiting only, no sophisticated per-user throttling
13. **Conversation search**: No ability to search through past conversations or messages
14. **AI personality customization**: No user-configurable AI personality or response style
15. **Integration with external services**: No calendar, email, or third-party app integrations

## Dependencies

- **Phase 2 Models**: Requires existing User and Todo models from phase-2/backend/src/models/
- **Phase 2 Database**: Extends the existing Neon PostgreSQL database with new tables
- **Phase 2 Authentication**: Reuses JWT authentication and user session management
- **OpenAI Agents SDK**: External dependency for AI agent orchestration and natural language understanding
- **MCP SDK**: Model Context Protocol SDK for tool definition and invocation framework
- **FastAPI**: Web framework (already used in Phase 2)
- **SQLModel**: ORM (already used in Phase 2)
- **OpenAI API Access**: Requires valid API key with sufficient quota for chat completions

## Constraints

1. **Stateless Architecture**: Chat endpoint must be stateless; all context derived from conversation history in database
2. **User Isolation**: Strict enforcement required - users must never access other users' data
3. **Phase 2 Compatibility**: Cannot break or modify existing Phase 2 functionality or API contracts
4. **Token Limits**: OpenAI API has context window limits; conversations may need truncation for very long histories
5. **Response Time**: AI processing adds latency; must target under 3 seconds for acceptable user experience
6. **Cost Management**: OpenAI API usage has costs; consider token usage optimization
7. **Directory Structure**: All Phase 3 code must reside in /phase-3 directory, separate from Phase 2
8. **Database Schema**: New tables must not conflict with existing Phase 2 schema
9. **Environment Variables**: Must not conflict with Phase 2 environment variable names

## Non-Functional Requirements

### Performance
- Chat endpoint must respond within 3 seconds for 95% of requests (P95 latency)
- System must handle at least 100 concurrent chat requests without degradation
- Database queries for conversation history must complete within 200ms
- MCP tool invocations must complete within 500ms each

### Reliability
- System must gracefully handle OpenAI API failures with user-friendly error messages
- Database transaction failures must not corrupt conversation state
- System must retry transient OpenAI API errors (rate limits, timeouts) up to 3 times
- All errors must be logged with sufficient context for debugging

### Security
- JWT tokens must be validated on every request
- User data isolation must be enforced at database query level
- API keys and secrets must be stored in environment variables, never hardcoded
- Conversation data must be stored with user_id for authorization checks
- SQL injection must be prevented through ORM parameter binding

### Maintainability
- Code must follow Phase 2 architecture patterns (repository pattern, service layer, clean architecture)
- All functions must have type hints for Python mypy strict mode compliance
- MCP tools must be modular and independently testable
- AI agent configuration must be externalized (not hardcoded)
- Logging must use structured logging format (JSON) for observability

### Scalability
- Stateless design enables horizontal scaling of API servers
- Database connection pooling must be configured appropriately
- OpenAI API calls should use async/await to avoid blocking
- Consider implementing conversation history pagination for users with many messages
