from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FrequencyType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class CheckType(str, Enum):
    WATERING = "watering"
    FERTILIZING = "fertilizing"
    PRUNING = "pruning"
    PEST_CHECK = "pest_check"
    DISEASE_CHECK = "disease_check"
    REPOTTING = "repotting"
    GENERAL = "general"


class RoutineCheckBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    frequency: FrequencyType = FrequencyType.WEEKLY
    check_type: CheckType = CheckType.GENERAL
    plant_id: Optional[int] = None
    notes: Optional[str] = None


class RoutineCheckCreate(RoutineCheckBase):
    next_check_date: datetime


class RoutineCheckUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    frequency: Optional[FrequencyType] = None
    check_type: Optional[CheckType] = None
    next_check_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class RoutineCheckResponse(RoutineCheckBase):
    id: int
    next_check_date: datetime
    last_check_date: Optional[datetime] = None
    is_active: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoutineCheckComplete(BaseModel):
    """Mark a routine check as completed"""
    notes: Optional[str] = None


class UpcomingChecks(BaseModel):
    """List of upcoming routine checks"""
    due_today: List[RoutineCheckResponse] = []
    due_this_week: List[RoutineCheckResponse] = []
    overdue: List[RoutineCheckResponse] = []


class RoutineNotification(BaseModel):
    """Notification payload for routine checks"""
    check_id: int
    title: str
    message: str
    check_type: str
    plant_name: Optional[str] = None
    due_date: datetime
    is_overdue: bool = False
