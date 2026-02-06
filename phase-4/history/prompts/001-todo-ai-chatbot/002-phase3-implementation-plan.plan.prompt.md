---
id: 002
title: Phase 3 Todo AI Chatbot Implementation Plan
stage: plan
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: Rizwan Nasir
command: /sp.plan
labels: ["phase-3", "ai-chatbot", "implementation-plan", "openai-agents", "mcp-tools", "architecture"]
links:
  spec: phase-3/specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - phase-3/specs/001-todo-ai-chatbot/plan.md
  - phase-3/specs/001-todo-ai-chatbot/research.md
  - phase-3/specs/001-todo-ai-chatbot/data-model.md
  - phase-3/specs/001-todo-ai-chatbot/quickstart.md
  - phase-3/specs/001-todo-ai-chatbot/contracts/openapi.yaml
  - phase-3/specs/001-todo-ai-chatbot/contracts/mcp-tools.json
tests:
  - Constitution compliance check (ALL PASS)
---

## Prompt

Based on the spec, please generate an implementation plan. Make sure all the backend and MCP server files are created inside the /phase-3/backend directory and frontend in /phase-3/frontend.

## Response snapshot

**Implementation Plan Complete**

I've successfully generated a comprehensive implementation plan for Phase 3: Todo AI Chatbot. Here's what was delivered:

### Planning Artifacts Created

1. **plan.md** (869 lines) - Complete implementation plan with:
   - Technical context and constraints
   - Constitution compliance check (ALL GATES PASSED)
   - Complete project structure for /phase-3/backend and /phase-3/frontend
   - 5 key architecture decisions with rationales
   - Risk analysis and mitigation strategies
   - Non-functional requirements implementation
   - Success criteria verification plan

2. **research.md** (8 sections) - Technology decisions:
   - OpenAI Assistants API integration strategy
   - MCP tool definition approach
   - Dual-storage conversation model (OpenAI Threads + Database)
   - User isolation via tool-level authorization
   - Error handling in AI-driven workflows
   - Natural language to todo extraction
   - Performance and cost optimization
   - Database schema for conversation entities

3. **data-model.md** - Complete database design:
   - 4 entities: User (Phase 2), Todo (Phase 2), Conversation (new), Message (new)
   - Detailed schemas with foreign keys, indexes, constraints
   - Repository interfaces and query patterns
   - Storage estimates and performance considerations
   - Migration strategy and testing approach

4. **contracts/openapi.yaml** - REST API specification:
   - POST /api/v1/chat endpoint (main chat interaction)
   - GET /api/v1/conversations (list conversations)
   - GET/DELETE /api/v1/conversations/{id} (conversation management)
   - Complete request/response schemas with examples
   - Error response specifications

5. **contracts/mcp-tools.json** - MCP tool definitions:
   - add_todo: Create new todo from natural language
   - list_todos: Retrieve user's todos with optional filtering
   - complete_todo: Mark todo as complete
   - update_todo: Modify todo title/description/status
   - delete_todo: Remove todo permanently
   - Complete schemas with parameters, returns, error codes, examples

6. **quickstart.md** - Developer setup guide:
   - Backend setup (Python dependencies, database migration, OpenAI Assistant creation)
   - Frontend setup (Next.js, environment variables)
   - Verification steps and end-to-end testing
   - Common issues and solutions
   - Development workflow for running both phases simultaneously

### Key Architecture Decisions

**Decision 1: OpenAI Assistants API for AI Orchestration**
- Selected over Chat Completions API and LangChain
- Built-in thread management, native function calling, async support
- Balances simplicity with functionality

**Decision 2: Dual-Storage Conversation Model**
- OpenAI Threads for AI context (primary)
- Database for audit trail and ownership (secondary)
- Linked via openai_thread_id column
- Provides both AI convenience and data governance

**Decision 3: Tool-Level User Isolation**
- user_id injected into tool execution context (from JWT)
- AI cannot bypass authorization through prompt manipulation
- Defense-in-depth security model

**Decision 4: Synchronous Responses Initially**
- Meets 3-second P95 target with GPT-4-turbo
- Streaming deferred as optimization (not blocking requirement)
- Simple implementation first, measure, then enhance

**Decision 5: Next.js App Router with Server Components**
- Consistent with Phase 2 frontend architecture
- Server Components for static content, Client Components for interactivity
- Reuses Phase 2 authentication context

### Constitution Compliance: ✅ ALL PASS

Validated against all 6 core principles:
- **Incremental Evolution**: Phase 3 extends Phase 2 without modifications
- **Production-Ready Standards**: Type hints, structured logging, explicit error handling
- **AI-Native Development**: MCP SDK, spec-driven workflow, PHRs created
- **Scalability & Portability**: 12-factor app, stateless design, externalized config
- **Clean Architecture**: Clear layer separation (domain, application, infrastructure, API)
- **Type Safety**: mypy strict mode (Python), TypeScript strict mode (frontend)

### Project Structure

**Backend** (/phase-3/backend/):
- src/models/ - Domain entities (Conversation, Message)
- src/repositories/ - Data access (ConversationRepository, MessageRepository)
- src/services/ - Business logic (ChatService, ConversationService)
- src/mcp/ - MCP tool implementations (5 tools)
- src/ai/ - AI integration (OpenAI client wrapper)
- src/api/ - FastAPI endpoints (chat, conversations)
- src/middleware/ - Auth, logging, error handling

**Frontend** (/phase-3/frontend/):
- app/ - Next.js App Router pages
- components/ - Chat UI (MessageList, MessageInput, ConversationSidebar)
- lib/ - API client and auth context (reused from Phase 2)

### Risk Analysis

Identified and mitigated 5 key risks:
1. **OpenAI API Availability**: Retry logic, fallback messages, feature flag kill switch
2. **Token Cost Overruns**: Context truncation (20 messages), max tokens limit, spending alerts
3. **AI Misinterpreting Intent**: Clear instructions, structured schemas, validation, fallback to Phase 2 UI
4. **Performance SLA Violations**: Async processing, connection pooling, model optimization, load testing
5. **Security Vulnerabilities**: Defense in depth, input validation, security tests, audit logging

### Performance Targets

- Chat endpoint P95: <3s (end-to-end including AI)
- Database queries P95: <200ms
- MCP tool execution P95: <500ms per tool
- Concurrent users: 100 without degradation

**Breakdown**: OpenAI ~1-2s + Database ~100-200ms + Application ~100-200ms + Network ~100-200ms = ~1.5-2.6s total (within 3s target)

### ADR Recommendation

📋 **Architectural decision detected**: OpenAI Assistants API selection, dual-storage conversation model, and tool-level user isolation strategy

**Recommendation**: Document reasoning and tradeoffs in ADR.
Run `/sp.adr openai-assistants-and-conversation-architecture`

**Rationale for ADR**:
- Long-term consequences (vendor dependency, data architecture)
- Multiple viable alternatives considered (Chat Completions, LangChain, prompt-based auth)
- Cross-cutting concerns (affects all layers: AI, database, security, scalability)

## Outcome

- ✅ Impact: Complete implementation plan with 6 design artifacts (plan, research, data-model, contracts, quickstart), 5 architecture decisions, risk analysis, and constitution compliance validation
- 🧪 Tests: Constitution check passed all 6 principles; specification quality checklist passed all criteria
- 📁 Files: Created 6 files - plan.md (869 lines), research.md, data-model.md, quickstart.md, openapi.yaml, mcp-tools.json
- 🔁 Next prompts: Ready for `/sp.tasks` to generate granular implementation tasks, or `/sp.adr` to document architecture decisions
- 🧠 Reflection: Planning phase successfully decomposed the AI chatbot feature into a concrete technical design. All unknowns resolved through research. Clean Architecture and Constitution principles maintained throughout. Phase 2 compatibility preserved (no modifications to existing code).

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow completed successfully with comprehensive artifacts
- Graders run and results (PASS/FAIL): Constitution compliance check - PASS (all 6 principles), Specification quality checklist - PASS (all 14 validation criteria)
- Prompt variant (if applicable): Standard /sp.plan workflow with user-specified directory structure guidance (/phase-3/backend and /phase-3/frontend)
- Next experiment (smallest change to try): Proceed to task breakdown with /sp.tasks to generate testable implementation tasks ordered by dependencies
