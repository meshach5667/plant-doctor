from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DiagnosisResult(BaseModel):
    """Result from AI model prediction"""
    disease_name: str
    confidence: float = Field(..., ge=0, le=1)
    is_healthy: bool
    detected_crop: str  # What crop type was detected (tomato, potato, pepper)
    description: Optional[str] = None
    treatment: Optional[str] = None
    prevention: Optional[str] = None


class DiagnosisResponse(BaseModel):
    id: int
    image_url: str
    disease_name: str
    confidence: float
    is_healthy: bool
    detected_crop: Optional[str] = None
    description: Optional[str] = None
    treatment: Optional[str] = None
    prevention: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    """Response for image prediction endpoint"""
    success: bool
    diagnosis: DiagnosisResult
    recommendations: List[str] = []
    message: str = "Diagnosis completed successfully"


class DiagnosisHistory(BaseModel):
    """User's diagnosis history"""
    total_diagnoses: int
    healthy_count: int
    diseased_count: int
    diagnoses: List[DiagnosisResponse]
