"""
Authentication service module.
Handles user registration, login, and token management.
"""
from typing import Optional
from sqlalchemy.orm import Session
import logging

from models import User
from schemas import UserCreate, Token, TokenResponse
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from core.exceptions import (
    AuthenticationException,
    ConflictException,
    NotFoundException,
)

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for authentication operations.
    
    Handles user registration, authentication, and token management
    following security best practices.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user account.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created User object
            
        Raises:
            ConflictException: If email or username already exists
        """
        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            logger.warning(f"Registration attempt with existing email: {user_data.email}")
            raise ConflictException(
                message="Email already registered",
                error_code="EMAIL_EXISTS",
                details={"field": "email"}
            )
        
        # Check if username already exists
        if self.get_user_by_username(user_data.username):
            logger.warning(f"Registration attempt with existing username: {user_data.username}")
            raise ConflictException(
                message="Username already taken",
                error_code="USERNAME_EXISTS",
                details={"field": "username"}
            )
        
        # Create user with hashed password
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        logger.info(f"New user created: {db_user.email}")
        return db_user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = self.get_user_by_email(email)
        if not user:
            # Use same timing for non-existent users to prevent enumeration
            get_password_hash("dummy_password_for_timing")
            return None
            
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for: {email}")
            return None
            
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {email}")
            return None
            
        return user
    
    def login(self, email: str, password: str) -> TokenResponse:
        """
        Login and return access and refresh tokens.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            TokenResponse with access and refresh tokens
            
        Raises:
            AuthenticationException: If credentials are invalid
        """
        user = self.authenticate_user(email, password)
        if not user:
            raise AuthenticationException(
                message="Incorrect email or password",
                error_code="INVALID_CREDENTIALS"
            )
        
        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        logger.info(f"User logged in: {email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New Token with access token
            
        Raises:
            AuthenticationException: If refresh token is invalid
        """
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise AuthenticationException(
                message="Invalid or expired refresh token",
                error_code="INVALID_REFRESH_TOKEN"
            )
        
        # Verify user still exists and is active
        user = self.get_user_by_id(int(payload.sub))
        if not user or not user.is_active:
            raise AuthenticationException(
                message="User not found or inactive",
                error_code="USER_INVALID"
            )
        
        # Generate new access token
        new_access_token = create_access_token(subject=user.id)
        
        return Token(access_token=new_access_token, token_type="bearer")
    
    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user's password.
        
        Args:
            user: User object
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password changed successfully
            
        Raises:
            AuthenticationException: If current password is incorrect
        """
        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationException(
                message="Current password is incorrect",
                error_code="INVALID_CURRENT_PASSWORD"
            )
        
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        logger.info(f"Password changed for user: {user.email}")
        return True


def get_auth_service(db: Session) -> AuthService:
    """Factory function to get auth service instance."""
    return AuthService(db)
