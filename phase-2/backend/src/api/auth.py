"""Authentication API endpoints."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_auth_service
from src.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
)
from src.services.auth_service import AuthService

logger = structlog.get_logger()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Returns user data and JWT token.",
)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Register a new user.

    Args:
        request: Registration request with email and password
        auth_service: Injected AuthService

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException: 400 if email already registered or validation fails
    """
    try:
        # Register user and get JWT token
        user, token = await auth_service.register_user(
            email=request.email,
            password=request.password
        )

        logger.info(
            "user_registered",
            user_id=str(user.id),
            email=user.email
        )

        return AuthResponse(
            token=token,
            user=UserResponse.model_validate(user)
        )

    except ValueError as e:
        logger.warning(
            "registration_failed",
            email=request.email,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "registration_error",
            email=request.email,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with email and password",
    description="Authenticate user with email and password. Returns user data and JWT token.",
)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Login with email and password.

    Args:
        request: Login request with email and password
        auth_service: Injected AuthService

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Authenticate user
    result = await auth_service.authenticate_user(
        email=request.email,
        password=request.password
    )

    if result is None:
        logger.warning(
            "login_failed",
            email=request.email,
            reason="invalid_credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, token = result

    logger.info(
        "user_logged_in",
        user_id=str(user.id),
        email=user.email
    )

    return AuthResponse(
        token=token,
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/logout",
    summary="Logout (client-side)",
    description="Logout endpoint for client-side token removal. Server-side JWT tokens are stateless.",
)
async def logout() -> dict[str, str]:
    """Logout endpoint.

    Since JWT tokens are stateless, logout is handled client-side by
    removing the token from storage. This endpoint exists for API
    completeness and potential future server-side session management.

    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Check if email exists for password reset",
    description="Verify if a user account exists with the provided email. In production, this would send a password reset email.",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    """Check if user exists for password reset.

    Args:
        request: Email address to check
        auth_service: Injected AuthService

    Returns:
        Success message (always returns success for security reasons)

    Note:
        For security, always returns success even if email doesn't exist.
        This prevents email enumeration attacks.
    """
    user_exists = await auth_service.check_user_exists(request.email)

    logger.info(
        "password_reset_requested",
        email=request.email,
        user_exists=user_exists,
    )

    # Always return success to prevent email enumeration
    return {
        "message": "If an account exists with this email, you can proceed to reset your password."
    }


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset user password",
    description="Reset password for a user account. In production, this would require a reset token from email.",
)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    """Reset user password.

    Args:
        request: Email and new password
        auth_service: Injected AuthService

    Returns:
        Success message

    Raises:
        HTTPException: 404 if user not found, 400 if validation fails

    Note:
        In production, this endpoint would require a secure reset token
        sent via email. This simplified version allows direct password reset
        for demonstration purposes.
    """
    try:
        success = await auth_service.reset_password(
            request.email, request.new_password
        )

        if not success:
            logger.warning(
                "password_reset_failed_user_not_found",
                email=request.email,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found",
            )

        logger.info(
            "password_reset_successful",
            email=request.email,
        )

        return {"message": "Password reset successfully. You can now login with your new password."}

    except ValueError as e:
        logger.warning(
            "password_reset_validation_failed",
            email=request.email,
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
            "password_reset_error",
            email=request.email,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password. Please try again.",
        )
