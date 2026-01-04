from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from models import User
from schemas import UserCreate, Token

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

# bcrypt has a 72-byte input limit; enforce truncation to avoid backend errors
BCRYPT_MAX_BYTES = 72

logger = logging.getLogger(__name__)

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        truncated = self._truncate_password(plain_password)
        return pwd_context.verify(truncated, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        truncated = self._truncate_password(password)
        return pwd_context.hash(truncated)

    def _truncate_password(self, password: str) -> str:
        """Truncate a password so its UTF-8 encoding is at most BCRYPT_MAX_BYTES.

        This preserves valid UTF-8 by decoding with 'ignore' if the slice cuts
        through a multi-byte character.
        """
        if not isinstance(password, str):
            password = str(password)

        b = password.encode("utf-8")
        if len(b) <= BCRYPT_MAX_BYTES:
            return password

        truncated = b[:BCRYPT_MAX_BYTES].decode("utf-8", "ignore")
        logger.warning("Password exceeds bcrypt 72-byte limit; truncating before hashing/verification.")
        return truncated
    
    def create_access_token(
        self, 
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[int]:
        """Decode JWT token and return user_id"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except JWTError:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def login(self, email: str, password: str) -> Token:
        """Login and return access token"""
        user = self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        access_token = self.create_access_token(
            data={"sub": str(user.id)}
        )
        
        return Token(access_token=access_token)


def get_auth_service(db: Session) -> AuthService:
    """Factory function to get auth service"""
    return AuthService(db)
