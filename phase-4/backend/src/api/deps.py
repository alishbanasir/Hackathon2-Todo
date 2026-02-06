"""FastAPI dependencies for Unified Backend (Phase 2 + Phase 3)."""

from typing import AsyncGenerator
from uuid import UUID
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.todo_repository import TodoRepository
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.todo_service import TodoService
from src.config import settings
from src.database import get_db_session

logger = structlog.get_logger(__name__)
security = HTTPBearer()

# --- Repository & Service Getters ---

def get_user_repository() -> UserRepository:
    return UserRepository()

def get_auth_service(user_repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repository)

def get_todo_repository() -> TodoRepository:
    return TodoRepository()

def get_todo_service(todo_repository: TodoRepository = Depends(get_todo_repository)) -> TodoService:
    return TodoService(todo_repository)

# --- Database Session (Required for Phase 3) ---

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides an async database session."""
    async for session in get_db_session():
        yield session

# --- Authentication Logic (Supports both Phase 2 & 3) ---

async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """Extracts User ID from JWT token."""
    token = credentials.credentials
    try:
        # Phase 2 & 3 share BETTER_AUTH_SECRET
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing 'sub' claim in token",
            )
        return UUID(user_id_str)
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(user_id: UUID = Depends(verify_jwt_token)) -> UUID:
    """Helper for Phase 3 AI Chatbot endpoints."""
    return user_id

async def get_current_user(
    user_id: UUID = Depends(verify_jwt_token),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Helper for Phase 2 Todo endpoints."""
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user