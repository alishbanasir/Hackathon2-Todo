"""Todo API endpoints."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_current_user, get_todo_service
from src.models.user import User
from src.schemas.todo import (
    TodoCreateRequest,
    TodoListResponse,
    TodoResponse,
    TodoUpdateRequest,
)
from src.services.todo_service import TodoService

logger = structlog.get_logger()

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.post(
    "",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
    description="Create a new todo item for the authenticated user.",
)
async def create_todo(
    request: TodoCreateRequest,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Create a new todo.

    Args:
        request: Todo creation request
        current_user: Authenticated user (from JWT)
        todo_service: Injected TodoService

    Returns:
        Created todo

    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        todo = await todo_service.create_todo(
            title=request.title,
            description=request.description,
            user_id=current_user.id,
        )

        logger.info(
            "todo_created",
            todo_id=todo.id,
            user_id=str(current_user.id),
            title=todo.title,
        )

        return TodoResponse.model_validate(todo)

    except ValueError as e:
        logger.warning(
            "todo_creation_failed",
            user_id=str(current_user.id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "todo_creation_error",
            user_id=str(current_user.id),
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create todo. Please try again.",
        )


@router.get(
    "",
    response_model=TodoListResponse,
    summary="List user's todos",
    description="Get all todos for the authenticated user, ordered by creation date (newest first).",
)
async def list_todos(
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoListResponse:
    """List all todos for the authenticated user.

    Args:
        current_user: Authenticated user (from JWT)
        todo_service: Injected TodoService

    Returns:
        List of todos
    """
    todos = await todo_service.get_user_todos(current_user.id)

    logger.info(
        "todos_retrieved",
        user_id=str(current_user.id),
        count=len(todos),
    )

    return TodoListResponse(
        todos=[TodoResponse.model_validate(todo) for todo in todos],
        total=len(todos),
    )


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Get todo by ID",
    description="Get a specific todo by ID. Returns 404 if not found or not owned by user.",
)
async def get_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Get a specific todo by ID.

    Args:
        todo_id: Todo's unique identifier
        current_user: Authenticated user (from JWT)
        todo_service: Injected TodoService

    Returns:
        Todo details

    Raises:
        HTTPException: 404 if todo not found or not owned by user
    """
    todo = await todo_service.get_todo_by_id(todo_id, current_user.id)

    if not todo:
        logger.warning(
            "todo_not_found",
            todo_id=todo_id,
            user_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return TodoResponse.model_validate(todo)


@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Update todo",
    description="Update a todo's title and/or description. Returns 404 if not found or not owned by user.",
)
async def update_todo(
    todo_id: int,
    request: TodoUpdateRequest,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Update a todo.

    Args:
        todo_id: Todo's unique identifier
        request: Update request with new values
        current_user: Authenticated user (from JWT)
        todo_service: Injected TodoService

    Returns:
        Updated todo

    Raises:
        HTTPException: 404 if todo not found, 400 if validation fails
    """
    try:
        todo = await todo_service.update_todo(
            todo_id=todo_id,
            user_id=current_user.id,
            title=request.title,
            description=request.description,
        )

        if not todo:
            logger.warning(
                "todo_update_failed_not_found",
                todo_id=todo_id,
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found",
            )

        logger.info(
            "todo_updated",
            todo_id=todo_id,
            user_id=str(current_user.id),
        )

        return TodoResponse.model_validate(todo)

    except ValueError as e:
        logger.warning(
            "todo_update_failed_validation",
            todo_id=todo_id,
            user_id=str(current_user.id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "todo_update_error",
            todo_id=todo_id,
            user_id=str(current_user.id),
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update todo. Please try again.",
        )


@router.patch(
    "/{todo_id}/toggle",
    response_model=TodoResponse,
    summary="Toggle todo completion",
    description="Toggle a todo's completion status. Returns 404 if not found or not owned by user.",
)
async def toggle_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Toggle a todo's completion status.

    Args:
        todo_id: Todo's unique identifier
        current_user: Authenticated user (from JWT)
        todo_service: Injected TodoService

    Returns:
        Updated todo

    Raises:
        HTTPException: 404 if todo not found or not owned by user
    """
    todo = await todo_service.toggle_completion(todo_id, current_user.id)

    if not todo:
        logger.warning(
            "todo_toggle_failed_not_found",
            todo_id=todo_id,
            user_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    logger.info(
        "todo_toggled",
        todo_id=todo_id,
        user_id=str(current_user.id),
        completed=todo.completed,
    )

    return TodoResponse.model_validate(todo)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete todo",
    description="Permanently delete a todo. Returns 404 if not found or not owned by user.",
)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service),
) -> dict[str, str]:
    """Delete a todo.

    Args:
        todo_id: Todo's unique identifier
        current_user: Authenticated user (from JWT)
        todo_service: Injected TodoService

    Returns:
        Success message

    Raises:
        HTTPException: 404 if todo not found or not owned by user
    """
    deleted = await todo_service.delete_todo(todo_id, current_user.id)

    if not deleted:
        logger.warning(
            "todo_delete_failed_not_found",
            todo_id=todo_id,
            user_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    logger.info(
        "todo_deleted",
        todo_id=todo_id,
        user_id=str(current_user.id),
    )

    return {"message": "Todo deleted successfully"}
