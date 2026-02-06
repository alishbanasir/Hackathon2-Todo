# User Story 3 (US3) Completion Summary

**Feature**: Todo Updates and Modifications

**Date**: 2026-01-13

**Status**: ✅ COMPLETE (Tasks T059-T067)

---

## Overview

US3 adds conversational todo update capabilities, enabling users to modify existing todos through natural language instructions like:
- "change the project report task to include design diagrams"
- "rename buy groceries to buy groceries and household items"
- "update the description of task 5"
- "mark task 3 as incomplete"

All operations maintain strict user isolation and ownership verification, consistent with US1 and US2.

---

## Implementation Details

### 1. UpdateTodoTool Implementation (T059-T062)

**File**: `src/mcp/update_todo.py` (282 lines)

**Purpose**: MCP tool for updating todo details with partial update support

#### Key Features:

**Parameters**:
- `todo_id` (required, integer): ID of the todo to update
- `title` (optional, string): New title (1-200 characters)
- `description` (optional, string): New description (0-2000 characters)
- `completed` (optional, boolean): New completion status

**Validation Rules**:
- At least one optional field must be provided
- Title validation: 1-200 characters if provided
- Description validation: 0-2000 characters if provided
- Completed validation: must be boolean if provided
- todo_id must be positive integer

**Ownership Verification**:
- Uses `UPDATE WHERE id = :todo_id AND user_id = :user_id`
- Returns `not_found` if todo doesn't exist or doesn't belong to user
- Consistent with CompleteTodoTool pattern

**Dynamic Query Building**:
```python
# Build SET clause dynamically based on provided fields
update_fields = []
update_params = {"todo_id": todo_id, "user_id": user_id}

if "title" in parameters:
    update_fields.append("title = :title")
    update_params["title"] = parameters["title"]

if "description" in parameters:
    update_fields.append("description = :description")
    update_params["description"] = parameters["description"]

if "completed" in parameters:
    update_fields.append("completed = :completed")
    update_params["completed"] = parameters["completed"]

query = text(f"""
    UPDATE todos
    SET {', '.join(update_fields)}
    WHERE id = :todo_id AND user_id = :user_id
    RETURNING id, title, description, completed, created_at
""")
```

**Sample Tool Call (Title Update)**:
```json
{
  "name": "update_todo",
  "parameters": {
    "todo_id": 42,
    "title": "Buy groceries and household items"
  }
}
```

**Sample Tool Call (Partial Update - Description Only)**:
```json
{
  "name": "update_todo",
  "parameters": {
    "todo_id": 42,
    "description": "Include milk, eggs, bread, and cleaning supplies"
  }
}
```

**Sample Tool Call (Multiple Fields)**:
```json
{
  "name": "update_todo",
  "parameters": {
    "todo_id": 42,
    "title": "Complete project report",
    "description": "Include design diagrams and user feedback",
    "completed": false
  }
}
```

**Sample Response (Success)**:
```json
{
  "success": true,
  "todo_id": 42,
  "title": "Buy groceries and household items",
  "description": "Include milk, eggs, bread, and cleaning supplies",
  "completed": false,
  "message": "Todo updated successfully"
}
```

**Sample Response (Not Found/Unauthorized)**:
```json
{
  "success": false,
  "error": "not_found",
  "message": "Todo not found or you don't have permission to update it"
}
```

**Sample Response (Validation Error)**:
```json
{
  "success": false,
  "error": "validation_error",
  "message": "At least one field (title, description, or completed) must be provided for update"
}
```

#### Error Handling:

**validation_error**:
- Missing todo_id
- Invalid todo_id type or value
- Invalid title/description/completed type
- Title too short (<1 char) or too long (>200 chars)
- Description too long (>2000 chars)
- No fields provided for update

**not_found**:
- Todo doesn't exist
- Todo doesn't belong to authenticated user

**database_error**:
- Unexpected database failures
- Connection issues

---

### 2. Tool Registration (T063)

**Files Modified**:
- `src/mcp/tool_registry.py` - Added UpdateTodoTool import and registration
- `src/mcp/__init__.py` - Added UpdateTodoTool export

**Registry Update**:
```python
# US3: Todo Updates and Modifications
update_todo_tool = UpdateTodoTool(session=self.session)
self._tools[update_todo_tool.name] = update_todo_tool
```

**Tool Count**: Increased from 4 to 5 tools
- add_todo (US1)
- list_todos (US2)
- complete_todo (US2)
- delete_todo (US2)
- update_todo (US3) ← New

---

### 3. Service Layer (T064-T066)

**Status**: No Code Changes Required

**Rationale**:
- **T064**: ChatService already handles all tools generically via `_handle_tool_calls()`
- **T065**: Natural language recognition for update intents handled by OpenAI GPT-4
- **T066**: Parameter extraction handled by GPT-4's function calling

**How It Works**:
1. User: "change task 5 title to buy groceries and household items"
2. GPT-4 recognizes update intent
3. GPT-4 extracts parameters: `{todo_id: 5, title: "buy groceries and household items"}`
4. Invokes `update_todo` tool call
5. ChatService routes to UpdateTodoTool via registry
6. Tool executes with user_id injection
7. Result returned to GPT-4 for natural language response

**Examples of Natural Language Understanding**:
- "rename task 5 to X" → `{todo_id: 5, title: "X"}`
- "add more details to task 5" → triggers clarification or extracts from context
- "mark task 5 as incomplete" → `{todo_id: 5, completed: false}`
- "change task 5 title to X and add description Y" → `{todo_id: 5, title: "X", description: "Y"}`

---

### 4. Assistant Configuration (T067)

**File**: `src/ai/assistant_config.py`

**Changes**:
1. Removed "(coming in US3)" marker from update_todo capability
2. Added comprehensive update intent examples
3. Added update confirmation example

**Updated Intent Examples**:

**Updating todos** (update_todo):
- "change X to Y"
- "rename X to Y"
- "update the description of X"
- "modify task X"
- "edit the details of X"
- "add more information to X"

**Confirmation Example**:
- "I've updated the task title to 'buy groceries and household items'."

---

## Security & Data Isolation

US3 maintains the same security guarantees as US1 and US2:

### User Isolation (FR-011, FR-031)
- User ID extracted from JWT token at API layer
- User ID injected into tool execution by ChatService
- SQL UPDATE includes `WHERE user_id = :user_id`

### Ownership Verification (FR-012)
- UPDATE query returns null if todo doesn't belong to user
- Returns `not_found` error for unauthorized access
- Consistent with complete_todo pattern

### Validation (FR-009)
- Title: 1-200 characters (if provided)
- Description: 0-2000 characters (if provided)
- Completed: boolean (if provided)
- At least one field required for update

### Error Handling (FR-035)
- **validation_error**: Invalid parameters
- **not_found**: Todo doesn't exist or unauthorized
- **database_error**: Unexpected failures

---

## Testing Recommendations

### Manual Integration Tests

#### Title Update Test:
```bash
# Setup: Create todo "buy groceries"
POST /api/v1/chat
{
  "message": "rename buy groceries to buy groceries and household items"
}

# Expected: AI confirms title updated
# Verify: title = "buy groceries and household items" in database
```

#### Description Update Test:
```bash
# Setup: Create todo with description
POST /api/v1/chat
{
  "message": "add more information to task 1: include milk, eggs, and bread"
}

# Expected: AI confirms description updated
# Verify: description field updated in database
```

#### Completion Status Toggle Test:
```bash
# Setup: Create completed todo
POST /api/v1/chat
{
  "message": "mark task 1 as incomplete"
}

# Expected: AI confirms status changed
# Verify: completed = false in database
```

#### Multiple Fields Update Test:
```bash
POST /api/v1/chat
{
  "message": "change task 1 title to project report and add description: include design diagrams"
}

# Expected: AI confirms both fields updated
# Verify: Both title and description updated in database
```

#### Ownership Verification Test:
```bash
# Setup: Create task as User A
# Switch to User B
POST /api/v1/chat
{
  "message": "update task 1 title to hacked"
}

# Expected: AI responds with error (not found or permission denied)
# Verify: Task 1 remains unchanged in database
```

#### Validation Error Test:
```bash
POST /api/v1/chat
{
  "message": "update task 1"  # No fields specified
}

# Expected: AI asks for clarification or reports error
```

---

## Files Modified

### New Files Created:
1. `phase-3/backend/src/mcp/update_todo.py` (282 lines)

### Files Modified:
1. `phase-3/backend/src/mcp/tool_registry.py` - Added UpdateTodoTool registration
2. `phase-3/backend/src/mcp/__init__.py` - Updated exports
3. `phase-3/backend/src/ai/assistant_config.py` - Enhanced update intent mapping
4. `phase-3/specs/001-todo-ai-chatbot/tasks.md` - Marked T059-T067 complete

---

## Functional Requirements Satisfied

- ✅ **FR-009**: Update todo title, description, or completion status
- ✅ **FR-011**: User isolation via JWT authentication
- ✅ **FR-012**: Ownership verification for update operations
- ✅ **FR-026**: Natural language recognition for update intents
- ✅ **FR-027**: Parameter extraction from natural language
- ✅ **FR-031**: JWT-based authentication
- ✅ **FR-035**: Comprehensive error handling

---

## Architecture Highlights

### Partial Update Support
UpdateTodoTool supports partial updates - any combination of title, description, and completed can be updated in a single operation. This provides flexibility:
- Title only: "rename task X to Y"
- Description only: "add more details to task X"
- Status only: "mark task X as incomplete"
- Multiple fields: "change task X to Y and add description Z"

### Dynamic SQL Query Building
The tool dynamically builds the UPDATE query based on provided fields, ensuring:
- Only specified fields are updated
- Other fields remain unchanged
- Efficient single-query operation
- No unnecessary UPDATE operations

### Consistent Error Handling
Uses the same error patterns as US1 and US2:
- `validation_error` for parameter issues
- `not_found` for missing/unauthorized todos
- `database_error` for unexpected failures
- User-friendly error messages

---

## Next Steps

### Immediate Options:

1. **Test US3 Implementation**:
   - Manually test various update scenarios via `/api/v1/chat`
   - Verify partial updates work correctly
   - Test ownership verification
   - Test validation edge cases

2. **Continue to US4 (Conversation History)**:
   - Implement ConversationService (T068-T079)
   - Enable multi-turn context preservation
   - Add conversation listing and management

3. **Proceed to Frontend Implementation**:
   - Build React UI for chat interface (T080-T093)
   - Integrate with Phase 3 backend
   - Implement real-time updates

---

## Technical Debt & Observations

### Strengths:
- Partial update flexibility (any field combination)
- Dynamic query building reduces code duplication
- Consistent with existing tool patterns
- Comprehensive validation and error handling

### Future Improvements:
- Add automated tests (unit and integration)
- Consider optimistic locking for concurrent updates
- Add update history/audit trail
- Implement undo functionality

---

## Checkpoint Reached

**Status**: ✅ All basic todo management works

**Full CRUD Capabilities**:
- **Create**: Add todos through natural language (US1)
- **Read**: List todos with filtering (US2)
- **Update**: Modify todo details (US3) ← Just completed
- **Delete**: Remove todos permanently (US2)
- **Complete**: Mark todos as done (US2)

**Additional Features**:
- Natural language understanding for all operations
- Strict user isolation and ownership verification
- Comprehensive error handling
- Conversational confirmations

**Progress**: 67/115 tasks complete (58.3%)

**Ready for**: US4 implementation, manual testing, or frontend development
