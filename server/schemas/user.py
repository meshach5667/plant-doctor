from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user schema with common fields."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "full_name": "John Doe"
            }
        }
    )
    
    email: EmailStr = Field(
        ...,
        description="Valid email address",
        json_schema_extra={"example": "user@example.com"}
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Username (3-100 chars, letters, numbers, underscores, hyphens)",
        json_schema_extra={"example": "john_doe"}
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Full display name (optional)",
        json_schema_extra={"example": "John Doe"}
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username contains only allowed characters."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        return v.lower()


class UserCreate(UserBase):
    """Schema for user registration."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "SecurePass123",
                "full_name": "John Doe"
            }
        }
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, must include uppercase, lowercase, and digit)",
        json_schema_extra={"example": "SecurePass123"}
    )
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if v is None:
            raise ValueError("Password is required")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: Optional[EmailStr] = Field(
        None, 
        description="New email address"
    )
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=100,
        description="New username"
    )
    full_name: Optional[str] = Field(
        None, 
        max_length=255,
        description="New full name"
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not re.match(r"^[a-zA-Z0-9_-]+$", v):
                raise ValueError(
                    "Username can only contain letters, numbers, underscores, and hyphens"
                )
            return v.lower()
        return v


class UserResponse(UserBase):
    """Schema for user response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }
    )
    
    email: EmailStr = Field(
        ...,
        description="Email address",
        json_schema_extra={"example": "user@example.com"}
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Password",
        json_schema_extra={"example": "SecurePass123"}
    )


class Token(BaseModel):
    """Schema for access token response."""
    access_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    """Schema for full token response with refresh token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Schema for password change request."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
