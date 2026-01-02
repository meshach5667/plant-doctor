from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PlantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    plant_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = None
    planted_date: Optional[datetime] = None
    image_url: Optional[str] = None


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    plant_type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = None
    planted_date: Optional[datetime] = None
    image_url: Optional[str] = None


class PlantResponse(PlantBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
