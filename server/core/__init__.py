"""
Core module for Plant Doctor API.
Contains middleware, security, exceptions, and shared utilities.
"""
from core.security import (
    SecurityConfig,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password,
)
from core.exceptions import (
    AppException,
    AuthenticationException,
    ConflictException,
)
from core.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from core.handlers import register_exception_handlers

__all__ = [
    # Security
    "SecurityConfig",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_password_hash",
    "verify_password",
    # Exceptions
    "AppException",
    "AuthenticationException",
    "ConflictException",
    # Middleware
    "RequestLoggingMiddleware",
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    # Handlers
    "register_exception_handlers",
]
