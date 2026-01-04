"""
Authentication routes for user registration, login, and profile management.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    TokenResponse,
    TokenRefresh,
    UserUpdate,
    PasswordChange,
)
from services import get_auth_service
from routes.dependencies import get_current_user
from models import User
from core.exceptions import ConflictException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "Email or username already exists"},
        422: {"description": "Validation error"},
    }
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **username**: 3-100 characters, letters, numbers, underscores, hyphens only
    - **password**: Minimum 8 characters with at least one uppercase, lowercase, and digit
    - **full_name**: Optional full name
    """
    auth_service = get_auth_service(db)
    user = auth_service.create_user(user_data)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get access tokens",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    }
)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and return access and refresh tokens.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns both access token (short-lived) and refresh token (long-lived).
    Use the access token in the Authorization header: `Bearer <token>`
    """
    auth_service = get_auth_service(db)
    tokens = auth_service.login(login_data.email, login_data.password)
    return tokens


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid or expired refresh token"},
    }
)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Token:
    """
    Get a new access token using a valid refresh token.
    
    Use this endpoint when your access token expires to get a new one
    without requiring the user to log in again.
    """
    auth_service = get_auth_service(db)
    new_token = auth_service.refresh_access_token(token_data.refresh_token)
    return new_token


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    responses={
        200: {"description": "User profile retrieved"},
        401: {"description": "Not authenticated"},
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get the profile information of the currently authenticated user.
    
    Requires a valid access token in the Authorization header.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    responses={
        200: {"description": "Profile updated successfully"},
        401: {"description": "Not authenticated"},
        409: {"description": "Email or username already taken"},
    }
)
async def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update the profile of the currently authenticated user.
    
    Only provided fields will be updated. All fields are optional.
    """
    auth_service = get_auth_service(db)
    
    # Check if new email is already taken
    if update_data.email and update_data.email != current_user.email:
        existing = auth_service.get_user_by_email(update_data.email)
        if existing:
            raise ConflictException(
                message="Email already registered",
                error_code="EMAIL_EXISTS",
                details={"field": "email"}
            )
    
    # Check if new username is already taken
    if update_data.username and update_data.username != current_user.username:
        existing = auth_service.get_user_by_username(update_data.username)
        if existing:
            raise ConflictException(
                message="Username already taken",
                error_code="USERNAME_EXISTS",
                details={"field": "username"}
            )
    
    # Update user fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change user password",
    responses={
        204: {"description": "Password changed successfully"},
        401: {"description": "Current password is incorrect"},
    }
)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Change the password of the currently authenticated user.
    
    Requires the current password for verification.
    """
    auth_service = get_auth_service(db)
    auth_service.change_password(
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
