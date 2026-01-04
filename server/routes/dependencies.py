"""
Dependency injection functions for route handlers.
Provides authentication and authorization dependencies.
"""
from typing import Optional
import logging

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models import User
from core.security import verify_token
from core.exceptions import AuthenticationException

logger = logging.getLogger(__name__)

# Security scheme for JWT Bearer authentication
security = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT token",
    auto_error=True
)

# Optional security scheme (doesn't raise error if no token provided)
optional_security = HTTPBearer(
    scheme_name="JWT",
    description="Optional JWT token",
    auto_error=False
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    
    Args:
        credentials: JWT Bearer token from request header
        db: Database session
        
    Returns:
        Authenticated User object
        
    Raises:
        AuthenticationException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify and decode the token
    payload = verify_token(token, token_type="access")
    if payload is None:
        logger.warning("Invalid or expired access token provided")
        raise AuthenticationException(
            message="Invalid or expired token",
            error_code="INVALID_TOKEN"
        )
    
    # Get user from database
    user_id = int(payload.sub)
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        logger.warning(f"Token valid but user not found: {user_id}")
        raise AuthenticationException(
            message="User not found",
            error_code="USER_NOT_FOUND"
        )
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.email}")
        raise AuthenticationException(
            message="User account is inactive",
            error_code="USER_INACTIVE"
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency.
    
    Returns the authenticated user if a valid token is provided,
    or None if no token is provided. Useful for endpoints that
    can work with or without authentication.
    
    Args:
        credentials: Optional JWT Bearer token from request header
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    # Verify and decode the token
    payload = verify_token(token, token_type="access")
    if payload is None:
        return None
    
    # Get user from database
    user_id = int(payload.sub)
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None or not user.is_active:
        return None
    
    return user
