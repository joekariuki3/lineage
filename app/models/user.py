from time import time
from typing import Any, Optional

import jwt
from flask_login import UserMixin
from sqlalchemy.orm import Mapped
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model, UserMixin):
    """Class representing a user in the application."""

    # constants
    NAME_MAX_LENGTH: int = 50
    EMAIL_MAX_LENGTH: int = 50
    PASSWORD_MAX_LENGTH: int = 2500
    PASSWORD_HASH_ALGORITHM: str = "HS256"
    TOKEN_EXPIRATION_DEFAULT: int = 600  # 10 minutes in seconds

    # Configuration
    __tablename__: str = "users"

    user_id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(NAME_MAX_LENGTH), nullable=False)
    email: Mapped[str] = db.Column(
        db.String(EMAIL_MAX_LENGTH), unique=True, nullable=False
    )
    password: Mapped[str] = db.Column(db.String(PASSWORD_MAX_LENGTH), nullable=False)
    emailVerify: Mapped[bool] = db.Column(db.Boolean, default=False)

    # Relationship
    families = db.relationship("Family", back_populates="users")

    def __init__(self, name: str, email: str, password: str) -> None:
        """Initialize a User instance.

        Args:
            name: The user's full name
            email: The user's email address
            password: The user's plain text password (will be hashed)
        """
        self.name = name
        self.email = email
        self.set_password(password)

    def set_password(self, password: str) -> None:
        """Hash and set the user's password.

        Args:
            password: Plain text password to be hashed
        """
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify if the provided password matches the stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password, password)

    def get_id(self) -> str:
        """Get the user's ID for Flask-Login.

        Returns:
            str: The user's ID as a string (required by Flask-Login)
        """
        return str(self.user_id)

    def _create_reset_token_payload(self, expires_in: int) -> dict[str, Any]:
        """Create the payload for a password-reset token.

        Args:
            expires_in: Token expiration time in seconds

        Returns:
            Dict[str, Any]: Token payload with user ID and expiration
        """
        return {"reset_password": self.user_id, "exp": time() + expires_in}

    def get_reset_password_token(
        self, secret: str, expires_in: int = TOKEN_EXPIRATION_DEFAULT
    ) -> str:
        """Generate a password-reset token.

        Args:
            secret: Secret key for token encryption
            expires_in: Token expiration time in seconds, defaults to TOKEN_EXPIRATION_DEFAULT

        Returns:
            str: JWT-encoded reset token
        """
        payload = self._create_reset_token_payload(expires_in)
        return jwt.encode(payload, secret, algorithm=self.PASSWORD_HASH_ALGORITHM)

    @staticmethod
    def verify_reset_password_token(secret: str, token: str) -> Optional["User"]:
        """Verify and decode a password reset token.

        Args:
            secret: Secret key for token verification
            token: JWT token to verify

        Returns:
            Optional[User]: User instance if token is valid, None otherwise

        Note:
            This method handles jwt.InvalidTokenError and KeyError exceptions
            and returns None in case of any validation errors.
        """
        try:
            payload = jwt.decode(
                token, secret, algorithms=[User.PASSWORD_HASH_ALGORITHM]
            )
            user_id = payload["reset_password"]
            user = db.session.get(User, user_id)
            return user
        except (jwt.InvalidTokenError, KeyError):
            return None
