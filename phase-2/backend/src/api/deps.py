"""FastAPI dependencies for dependency injection."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from src.models.user import User
from src.repositories.todo_repository import TodoRepository
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.todo_service import TodoService

# HTTP Bearer token security
security = HTTPBearer()


def get_user_repository() -> UserRepository:
    """Dependency to get UserRepository instance.

    Returns:
        UserRepository instance
    """
    return UserRepository()


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Dependency to get AuthService instance.

    Args:
        user_repository: Injected UserRepository

    Returns:
        AuthService instance
    """
    return AuthService(user_repository)


def get_todo_repository() -> TodoRepository:
    """Dependency to get TodoRepository instance.

    Returns:
        TodoRepository instance
    """
    return TodoRepository()


def get_todo_service(
    todo_repository: TodoRepository = Depends(get_todo_repository)
) -> TodoService:
    """Dependency to get TodoService instance.

    Args:
        todo_repository: Injected TodoRepository

    Returns:
        TodoService instance
    """
    return TodoService(todo_repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Dependency to get the currently authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        auth_service: Injected AuthService for token verification
        user_repository: Injected UserRepository for user lookup

    Returns:
        The authenticated User

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials

    try:
        # Verify token and extract user_id
        user_id = auth_service.verify_jwt_token(token)

        # Get user from database
        user = await user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
