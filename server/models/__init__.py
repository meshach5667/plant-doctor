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
    plants = relationship("Plant", back_populates="owner")
    diagnoses = relationship("Diagnosis", back_populates="user")
    routine_checks = relationship("RoutineCheck", back_populates="user")


class Plant(Base):
    """Plant model for tracking user's plants"""
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    plant_type = Column(String(100), nullable=False)  # e.g., Tomato, Potato, Pepper
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)  # Where the plant is located
    planted_date = Column(DateTime, nullable=True)
    image_url = Column(String(500), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="plants")
    diagnoses = relationship("Diagnosis", back_populates="plant")
    routine_checks = relationship("RoutineCheck", back_populates="plant")


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
    user_id = Column(Integer, ForeignKey("users.id"))
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="diagnoses")
    plant = relationship("Plant", back_populates="diagnoses")


class RoutineCheck(Base):
    """Routine check model for scheduled plant maintenance"""
    __tablename__ = "routine_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(Enum(FrequencyType), default=FrequencyType.WEEKLY)
    next_check_date = Column(DateTime, nullable=False)
    last_check_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    check_type = Column(String(100), nullable=False)  # watering, fertilizing, pruning, etc.
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="routine_checks")
    plant = relationship("Plant", back_populates="routine_checks")


class DiseaseInfo(Base):
    """Disease information database for treatment recommendations"""
    __tablename__ = "disease_info"
    
    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String(255), unique=True, index=True, nullable=False)
    plant_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=False)
    causes = Column(Text, nullable=True)
    treatment = Column(Text, nullable=False)
    prevention = Column(Text, nullable=False)
    severity = Column(String(50), nullable=True)  # mild, moderate, severe
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
