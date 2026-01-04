from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CropType(str, Enum):
    TOMATO = "tomato"
    POTATO = "potato"
    PEPPER = "pepper"


class FarmCropCreate(BaseModel):
    """Add a crop type to your farm"""
    crop_type: CropType
    location: Optional[str] = Field(None, max_length=255, description="Where on the farm")
    notes: Optional[str] = None


class FarmCropUpdate(BaseModel):
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class FarmCropResponse(BaseModel):
    id: int
    crop_type: CropType
    location: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FarmSummary(BaseModel):
    """Summary of user's farm crops"""
    total_crops: int
    crops: List[FarmCropResponse]
    crop_types: List[str]  # List of unique crop types on farm

