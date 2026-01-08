# Phase 5: Testing and Validation Guide

## Overview
This document outlines the comprehensive testing procedures for Phase 2 Todo Full-Stack Web Application (Tasks T157-T163).

## Prerequisites
- Backend server running on http://localhost:8000
- Frontend server running on http://localhost:3000
- At least one test user account registered

---

## Test Suite

### T157: Todo Creation Testing

**Objective**: Verify todos can be created with proper validation

**Test Cases**:

1. **Valid Todo Creation**
   - Navigate to `/dashboard`
   - Enter title: "Complete project documentation"
   - Enter description: "Write comprehensive API docs"
   - Click "Create Todo"
   - **Expected**: Todo appears in list, form clears, success feedback

2. **Title Validation - Empty**
   - Leave title field empty
   - Click "Create Todo"
   - **Expected**: Error message "Title is required"

3. **Title Validation - Max Length**
   - Enter 201 characters in title field
   - **Expected**: Input limited to 200 characters, character counter shown

4. **Description Validation - Max Length**
   - Enter 2001 characters in description field
   - **Expected**: Input limited to 2000 characters, character counter updates

5. **Whitespace Handling**
   - Enter title: "   Test Todo   " (with leading/trailing spaces)
   - **Expected**: Todo created with trimmed title "Test Todo"

---

### T158: Todo Listing and Filtering

**Objective**: Verify todos display correctly with filters

**Test Cases**:

1. **Empty State**
   - New user with no todos
   - **Expected**: "No todos yet" message with helpful text

2. **Display All Todos**
   - Create 3 todos (2 active, 1 completed)
   - Click "All" tab
   - **Expected**: All 3 todos visible, badge shows "3"

3. **Filter Active Todos**
   - Click "Active" tab
   - **Expected**: Only 2 active todos visible, badge shows "2"

4. **Filter Completed Todos**
   - Click "Completed" tab
   - **Expected**: Only 1 completed todo visible, badge shows "1"

5. **Todo Display Format**
   - **Expected**: Each todo shows:
     - Checkbox (checked if completed)
     - Title (bold, strikethrough if completed)
     - Description (gray text)
     - Creation date (formatted)
     - Edit and Delete buttons

---

### T159: Todo Update/Edit Testing

**Objective**: Verify todos can be updated with validation

**Test Cases**:

1. **Edit Todo Title**
   - Click "Edit" on a todo
   - Change title to "Updated Title"
   - Click "Save"
   - **Expected**: Todo updates, exits edit mode, shows new title

2. **Edit Todo Description**
   - Click "Edit" on a todo
   - Change description to "Updated description"
   - Click "Save"
   - **Expected**: Todo updates with new description

3. **Edit Validation - Empty Title**
   - Click "Edit" on a todo
   - Clear title field
   - Click "Save"
   - **Expected**: Error message "Title is required", remains in edit mode

4. **Cancel Edit**
   - Click "Edit" on a todo
   - Change title
   - Click "Cancel"
   - **Expected**: Changes discarded, exits edit mode, original data shown

5. **Edit Multiple Fields**
   - Click "Edit" on a todo
   - Update both title and description
   - Click "Save"
   - **Expected**: Both fields updated successfully

---

### T160: Todo Completion Toggle Testing

**Objective**: Verify completion status can be toggled

**Test Cases**:

1. **Mark Todo as Complete**
   - Click checkbox on active todo
   - **Expected**:
     - Checkbox becomes checked
     - Title gets strikethrough styling
     - Text color changes to gray
     - Moves to "Completed" filter

2. **Mark Todo as Incomplete**
   - Click checkbox on completed todo
   - **Expected**:
     - Checkbox becomes unchecked
     - Strikethrough removed
     - Text color returns to normal
     - Moves to "Active" filter

3. **Toggle During Loading**
   - Click checkbox rapidly multiple times
   - **Expected**: Loading state prevents multiple requests

---

### T161: Todo Deletion Testing

**Objective**: Verify todos can be deleted with confirmation

**Test Cases**:

1. **Delete Todo - Confirm**
   - Click "Delete" button on a todo
   - Confirm dialog appears
   - Click "OK" / "Confirm"
   - **Expected**: Todo removed from list, count updates

2. **Delete Todo - Cancel**
   - Click "Delete" button on a todo
   - Confirm dialog appears
   - Click "Cancel"
   - **Expected**: Todo remains in list, no changes

3. **Delete Last Todo**
   - Delete all todos until none remain
   - **Expected**: "No todos yet" empty state appears

---

### T162: User Isolation Testing

**Objective**: Verify users can only access their own todos

**Test Cases**:

1. **Create Second User**
   - Logout from current account
   - Navigate to `/register`
   - Register new user: `user2@test.com`
   - **Expected**: Successfully registered and logged in

2. **Verify Empty Dashboard**
   - Check dashboard after login as user2
   - **Expected**: No todos from user1 visible, empty state shown

3. **Create Todos as User2**
   - Create 2 todos as user2
   - **Expected**: Only these 2 todos visible

4. **Switch Back to User1**
   - Logout from user2
   - Login as user1
   - **Expected**: Only user1's todos visible (user2's todos hidden)

5. **API Direct Access Test** (Manual with curl)
   - Get user1's JWT token
   - Try to access user2's todo via API
   - **Expected**: 404 or 403 error (todo not found or forbidden)

---

### T163: Error Handling and Edge Cases

**Objective**: Verify graceful error handling

**Test Cases**:

1. **Network Error Simulation**
   - Stop backend server
   - Try to create a todo
   - **Expected**: User-friendly error message, "Try again" option

2. **Token Expiration**
   - Wait for JWT to expire (or manually clear token)
   - Try to create a todo
   - **Expected**: Redirect to login page with session expired message

3. **Concurrent Edits**
   - Open same todo in two browser tabs
   - Edit in both tabs
   - Save second tab
   - **Expected**: Latest save wins, data consistent

4. **Special Characters in Title**
   - Enter title with special characters: `<script>alert('test')</script>`
   - **Expected**: Saved as plain text, no XSS vulnerability

5. **Long Description Display**
   - Create todo with 2000 character description
   - **Expected**: Description displays without breaking layout

---

## Validation Checklist

### Functional Requirements
- [ ] FR-001: Users can register with email/password
- [ ] FR-002: Users can login with credentials
- [ ] FR-003: Users can logout
- [ ] FR-004: Users can create todos with title (required) and description (optional)
- [ ] FR-005: Users can view all their todos
- [ ] FR-006: Users can filter todos (All/Active/Completed)
- [ ] FR-007: Users can edit todo title and description
- [ ] FR-008: Users can mark todos as complete/incomplete
- [ ] FR-009: Users can delete todos with confirmation
- [ ] FR-010: Todos are persisted to database
- [ ] FR-011: User isolation enforced (can't see other users' todos)

### Non-Functional Requirements
- [ ] NFR-001: Responsive design works on mobile/tablet/desktop
- [ ] NFR-002: Loading states prevent double-submissions
- [ ] NFR-003: Error messages are user-friendly
- [ ] NFR-004: Form validation provides clear feedback
- [ ] NFR-005: JWT authentication secure
- [ ] NFR-006: Password hashing with Argon2id
- [ ] NFR-007: API returns appropriate status codes

---

## Bug Report Template

If you find issues during testing, document using this format:

```markdown
**Bug ID**: BUG-XXX
**Severity**: Critical / High / Medium / Low
**Component**: Frontend / Backend / API
**Test Case**: [Test case ID]

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Result**:
[What should happen]

**Actual Result**:
[What actually happened]

**Screenshots/Logs**:
[Attach if applicable]

**Browser/Environment**:
- Browser: Chrome 120
- OS: Windows 11
- Node version: 20.x
- Python version: 3.11
```

---

## Performance Testing (Optional)

### Load Testing
- Create 100 todos
- Measure list rendering time
- **Expected**: < 500ms

### API Response Times
- Todo creation: < 200ms
- Todo listing: < 300ms
- Todo update: < 200ms
- Todo deletion: < 200ms

---

## Security Testing

### Authentication
- [ ] JWT tokens expire after configured time
- [ ] Logout clears token from storage
- [ ] Unauthorized API calls return 401

### Authorization
- [ ] Users cannot access other users' todos via API
- [ ] Direct API calls without token return 401
- [ ] Tampered tokens are rejected

### Input Validation
- [ ] SQL injection attempts blocked
- [ ] XSS attempts sanitized
- [ ] CSRF protection enabled (if applicable)

---

## Sign-Off

**Tested By**: _________________
**Date**: _________________
**Build Version**: Phase 2 - v0.1.0
**Status**: ☐ Pass ☐ Pass with Minor Issues ☐ Fail

**Notes**:
[Add any additional observations or recommendations]
