"""Authentication service with password hashing and JWT management."""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from src.config import settings
from src.models.user import User
from src.repositories.user_repository import UserRepository


class AuthService:
    """Service for user authentication and password management."""

    def __init__(self, user_repository: UserRepository):
        """Initialize AuthService.

        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
        self.password_hasher = PasswordHasher(
            time_cost=2,  # Number of iterations
            memory_cost=65536,  # 64 MB memory usage
            parallelism=1,  # Number of parallel threads
            hash_len=32,  # Hash output length
            salt_len=16,  # Salt length
        )

    def hash_password(self, plain_password: str) -> str:
        """Hash a password using Argon2id.

        Args:
            plain_password: The plaintext password to hash

        Returns:
            Argon2id password hash
        """
        return self.password_hasher.hash(plain_password)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: The plaintext password to verify
            password_hash: The Argon2id hash to verify against

        Returns:
            True if password matches, False otherwise
        """
        try:
            self.password_hasher.verify(password_hash, plain_password)
            return True
        except VerifyMismatchError:
            return False

    def create_jwt_token(self, user_id: UUID) -> str:
        """Create a JWT access token for a user.

        Args:
            user_id: The user's unique identifier

        Returns:
            Encoded JWT token string
        """
        # Token expires in 7 days
        expire = datetime.utcnow() + timedelta(days=7)

        payload = {
            "sub": str(user_id),  # Subject (user ID)
            "exp": expire,  # Expiration time
            "iat": datetime.utcnow(),  # Issued at
        }

        token = jwt.encode(
            payload,
            settings.better_auth_secret,
            algorithm="HS256"
        )
        return token

    def verify_jwt_token(self, token: str) -> UUID:
        """Verify a JWT token and extract the user ID.

        Args:
            token: The JWT token to verify

        Returns:
            The user ID from the token

        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.better_auth_secret,
                algorithms=["HS256"]
            )
            user_id_str: str = payload.get("sub")
            if user_id_str is None:
                raise JWTError("Invalid token: missing subject")
            return UUID(user_id_str)
        except JWTError as e:
            raise JWTError(f"Token verification failed: {str(e)}")

    async def register_user(
        self, email: str, password: str
    ) -> Tuple[User, str]:
        """Register a new user and return user + JWT token.

        Args:
            email: User's email address
            password: User's plaintext password

        Returns:
            Tuple of (created user, JWT token)

        Raises:
            ValueError: If user already exists or validation fails
        """
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash password
        password_hash = self.hash_password(password)

        # Create user
        user = await self.user_repository.create_user(email, password_hash)

        # Generate JWT token
        token = self.create_jwt_token(user.id)

        return user, token

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[Tuple[User, str]]:
        """Authenticate a user and return user + JWT token.

        Args:
            email: User's email address
            password: User's plaintext password

        Returns:
            Tuple of (user, JWT token) if authentication succeeds,
            None if credentials are invalid
        """
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None

        # Verify password
        if not self.verify_password(password, user.password_hash):
            return None

        # Generate JWT token
        token = self.create_jwt_token(user.id)

        return user, token

    async def check_user_exists(self, email: str) -> bool:
        """Check if a user exists with the given email.

        Args:
            email: User's email address

        Returns:
            True if user exists, False otherwise
        """
        user = await self.user_repository.get_by_email(email)
        return user is not None

    async def reset_password(self, email: str, new_password: str) -> bool:
        """Reset user's password by email.

        Args:
            email: User's email address
            new_password: New plaintext password

        Returns:
            True if password was reset, False if user not found

        Raises:
            ValueError: If password validation fails
        """
        # Validate password
        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Hash new password
        password_hash = self.hash_password(new_password)

        # Update user's password
        user = await self.user_repository.update_password(email, password_hash)

        return user is not None
