from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserCreate, UserResponse, UserLogin, Token, UserUpdate
from services import get_auth_service
from routes.dependencies import get_current_user
from models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    auth_service = get_auth_service(db)
    user = auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    auth_service = get_auth_service(db)
    token = auth_service.login(login_data.email, login_data.password)
    return token


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    auth_service = get_auth_service(db)
    
    # Check if new email is already taken
    if update_data.email and update_data.email != current_user.email:
        existing = auth_service.get_user_by_email(update_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if new username is already taken
    if update_data.username and update_data.username != current_user.username:
        existing = auth_service.get_user_by_username(update_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update user fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user
