"""
Security utilities for JWT authentication and password hashing.
Production-ready implementation with best practices.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Password hashing configuration
# bcrypt has a 72-byte input limit; enforce truncation to avoid backend errors
BCRYPT_MAX_BYTES = 72
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increase rounds for production security
)


class SecurityConfig:
    """
    Security configuration loaded from environment.
    Should be initialized from Settings in config.py
    """
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    @classmethod
    def configure(
        cls,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        """Configure security settings from application config."""
        cls.secret_key = secret_key
        cls.algorithm = algorithm
        cls.access_token_expire_minutes = access_token_expire_minutes
        cls.refresh_token_expire_days = refresh_token_expire_days


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: str  # Subject (user_id)
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    type: str  # Token type: "access" or "refresh"


def _truncate_password(password: str) -> str:
    """
    Truncate a password so its UTF-8 encoding is at most BCRYPT_MAX_BYTES.
    
    This preserves valid UTF-8 by decoding with 'ignore' if the slice cuts
    through a multi-byte character.
    """
    if not isinstance(password, str):
        password = str(password)

    encoded = password.encode("utf-8")
    if len(encoded) <= BCRYPT_MAX_BYTES:
        return password

    truncated = encoded[:BCRYPT_MAX_BYTES].decode("utf-8", "ignore")
    logger.warning(
        "Password exceeds bcrypt 72-byte limit; truncating before hashing/verification."
    )
    return truncated


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    truncated = _truncate_password(plain_password)
    return pwd_context.verify(truncated, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    truncated = _truncate_password(password)
    return pwd_context.hash(truncated)


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject claim (typically user_id)
        expires_delta: Optional custom expiration time
        additional_claims: Optional additional claims to include
        
    Returns:
        Encoded JWT token string
    """
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=SecurityConfig.access_token_expire_minutes)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(
        to_encode,
        SecurityConfig.secret_key,
        algorithm=SecurityConfig.algorithm
    )


def create_refresh_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: The subject claim (typically user_id)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT refresh token string
    """
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=SecurityConfig.refresh_token_expire_days)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "refresh"
    }
    
    return jwt.encode(
        to_encode,
        SecurityConfig.secret_key,
        algorithm=SecurityConfig.algorithm
    )


def verify_token(token: str, token_type: str = "access") -> Optional[TokenPayload]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token string
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            SecurityConfig.secret_key,
            algorithms=[SecurityConfig.algorithm]
        )
        
        # Validate token type
        if payload.get("type") != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            return None
        
        return TokenPayload(
            sub=payload["sub"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            type=payload["type"]
        )
        
    except JWTError as e:
        logger.debug(f"Token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None
