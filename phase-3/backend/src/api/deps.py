"""FastAPI dependencies for Phase 3.

Provides JWT verification, database session injection, and authenticated user extraction.
Reuses Phase 2's JWT secret for authentication compatibility.
"""

from typing import AsyncGenerator
from uuid import UUID

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db_session

logger = structlog.get_logger(__name__)

# HTTP Bearer security scheme for JWT tokens
security = HTTPBearer()


async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """Verify JWT token and extract user ID.

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        User ID (UUID) extracted from valid JWT token

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing
    """
    token = credentials.credentials

    # Debug: Log token info (first 20 chars only for security)
    logger.info(
        "jwt_verification_attempt",
        token_preview=token[:20] + "..." if len(token) > 20 else token,
        token_length=len(token),
        secret_preview=settings.better_auth_secret[:10] + "..." if len(settings.better_auth_secret) > 10 else "***",
    )

    try:
        # Decode JWT using BETTER_AUTH_SECRET (same as Phase 2)
        # Try HS256 first (standard), then try without verification to inspect payload
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )

        logger.info("jwt_decode_success", payload_keys=list(payload.keys()))

        # Extract user ID from "sub" claim
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            logger.warning("jwt_missing_sub_claim", payload=payload)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials: missing 'sub' claim",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = UUID(user_id_str)
        logger.info("jwt_verification_success", user_id=str(user_id))
        return user_id

    except JWTError as e:
        logger.error("jwt_decode_error", error=str(e), error_type=type(e).__name__)

        # Try to decode without verification to see the payload structure
        try:
            unverified = jwt.get_unverified_claims(token)
            logger.info("jwt_unverified_payload", payload_keys=list(unverified.keys()), payload=unverified)
        except Exception as inner_e:
            logger.error("jwt_unverified_decode_failed", error=str(inner_e))

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        # Invalid UUID format
        logger.error("jwt_uuid_parse_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token format: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    user_id: UUID = Depends(verify_jwt_token),
) -> UUID:
    """Get authenticated user ID from JWT token.

    This is a convenience dependency that can be injected directly into endpoints.

    Args:
        user_id: User ID from verified JWT token

    Returns:
        User ID (UUID)

    Example:
        ```python
        @router.post("/chat")
        async def chat(
            request: ChatRequest,
            user_id: UUID = Depends(get_current_user_id),
        ):
            # user_id is automatically extracted and verified
            conversation = await chat_service.process_message(request.message, user_id)
            return conversation
        ```
    """
    return user_id


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection.

    Yields:
        AsyncSession for database operations

    Example:
        ```python
        @router.get("/conversations")
        async def list_conversations(
            user_id: UUID = Depends(get_current_user_id),
            session: AsyncSession = Depends(get_session),
        ):
            repository = ConversationRepository(session)
            conversations = await repository.list_by_user(user_id)
            return conversations
        ```
    """
    async for session in get_db_session():
        yield session
