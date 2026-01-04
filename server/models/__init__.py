"""
SQLAlchemy models for the Plant Doctor database.
"""
from datetime import datetime, timezone
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship

from database import Base


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class FrequencyType(str, enum.Enum):
    """Frequency options for routine checks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class CropType(str, enum.Enum):
    """Supported crop types."""
    TOMATO = "tomato"
    POTATO = "potato"
    PEPPER = "pepper"


class User(Base):
    """
    User model for authentication and profile management.
    
    Attributes:
        id: Primary key
        email: Unique email address
        username: Unique username
        hashed_password: Bcrypt hashed password
        full_name: Optional display name
        is_active: Whether user can login
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    farm_crops = relationship("FarmCrop", back_populates="owner", cascade="all, delete-orphan")
    diagnoses = relationship("Diagnosis", back_populates="user", cascade="all, delete-orphan")
    routine_checks = relationship("RoutineCheck", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"


class FarmCrop(Base):
    """
    Crops that user grows on their farm.
    
    Determines what routine checks they receive for specific crops.
    """
    __tablename__ = "farm_crops"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_type = Column(Enum(CropType), nullable=False)
    location = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="farm_crops")
    routine_checks = relationship("RoutineCheck", back_populates="farm_crop")
    
    # Indexes
    __table_args__ = (
        Index("ix_farm_crops_owner_crop", "owner_id", "crop_type"),
    )
    
    def __repr__(self) -> str:
        return f"<FarmCrop(id={self.id}, type='{self.crop_type.value}')>"


class Diagnosis(Base):
    """
    Diagnosis model for storing plant disease diagnoses.
    
    Stores AI diagnosis results including confidence scores
    and treatment recommendations.
    """
    __tablename__ = "diagnoses"
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(500), nullable=False)
    disease_name = Column(String(255), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    treatment = Column(Text, nullable=True)
    prevention = Column(Text, nullable=True)
    is_healthy = Column(Boolean, default=False, nullable=False)
    detected_crop = Column(String(100), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="diagnoses")
    
    # Indexes
    __table_args__ = (
        Index("ix_diagnoses_user_created", "user_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Diagnosis(id={self.id}, disease='{self.disease_name}')>"


class RoutineCheck(Base):
    """
    Routine check model for scheduled farm maintenance.
    
    Stores scheduled tasks based on crop type with configurable
    frequency and tracking of completion.
    """
    __tablename__ = "routine_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(Enum(FrequencyType), default=FrequencyType.WEEKLY, nullable=False)
    next_check_date = Column(DateTime(timezone=True), nullable=False, index=True)
    last_check_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    check_type = Column(String(100), nullable=False)
    crop_type = Column(Enum(CropType), nullable=False)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    farm_crop_id = Column(Integer, ForeignKey("farm_crops.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="routine_checks")
    farm_crop = relationship("FarmCrop", back_populates="routine_checks")
    
    # Indexes
    __table_args__ = (
        Index("ix_routine_checks_user_active", "user_id", "is_active"),
        Index("ix_routine_checks_next_date", "next_check_date"),
    )
    
    def __repr__(self) -> str:
        return f"<RoutineCheck(id={self.id}, title='{self.title}')>"


# Export all models
__all__ = [
    "Base",
    "User",
    "FarmCrop",
    "Diagnosis",
    "RoutineCheck",
    "FrequencyType",
    "CropType",
]

