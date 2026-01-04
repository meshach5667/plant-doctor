from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class FrequencyType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class CropType(str, enum.Enum):
    TOMATO = "tomato"
    POTATO = "potato"
    PEPPER = "pepper"


class User(Base):
    """User model for plant doctor app"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farm_crops = relationship("FarmCrop", back_populates="owner")
    diagnoses = relationship("Diagnosis", back_populates="user")
    routine_checks = relationship("RoutineCheck", back_populates="user")


class FarmCrop(Base):
    """Crops that user grows on their farm - determines what routine checks they receive"""
    __tablename__ = "farm_crops"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_type = Column(Enum(CropType), nullable=False)  # tomato, potato, pepper
    location = Column(String(255), nullable=True)  # Optional: where on the farm
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="farm_crops")
    routine_checks = relationship("RoutineCheck", back_populates="farm_crop")


class Diagnosis(Base):
    """Diagnosis model for storing plant disease diagnoses"""
    __tablename__ = "diagnoses"
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(500), nullable=False)
    disease_name = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    treatment = Column(Text, nullable=True)
    prevention = Column(Text, nullable=True)
    is_healthy = Column(Boolean, default=False)
    detected_crop = Column(String(100), nullable=True)  # What crop was detected in the image
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="diagnoses")


class RoutineCheck(Base):
    """Routine check model for scheduled farm maintenance based on crops"""
    __tablename__ = "routine_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(Enum(FrequencyType), default=FrequencyType.WEEKLY)
    next_check_date = Column(DateTime, nullable=False)
    last_check_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    check_type = Column(String(100), nullable=False)  # watering, fertilizing, pruning, pest_check, etc.
    crop_type = Column(Enum(CropType), nullable=False)  # Which crop this check is for
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    farm_crop_id = Column(Integer, ForeignKey("farm_crops.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="routine_checks")
    farm_crop = relationship("FarmCrop", back_populates="routine_checks")


class DiseaseInfo(Base):
    """Disease information database for treatment recommendations"""
    __tablename__ = "disease_info"
    
    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String(255), unique=True, index=True, nullable=False)
    crop_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=False)
    causes = Column(Text, nullable=True)
    treatment = Column(Text, nullable=False)
    prevention = Column(Text, nullable=False)
    severity = Column(String(50), nullable=True)  # mild, moderate, severe
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

