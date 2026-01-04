from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid

from database import get_db
from schemas import (
    DiagnosisResponse, 
    PredictionResponse, 
    DiagnosisHistory
)
from routes.dependencies import get_current_user, get_current_user_optional
from models import User, Diagnosis
from services import diagnosis_service, get_disease_info
from config import get_settings

settings = get_settings()
router = APIRouter(prefix="/diagnosis", tags=["Diagnosis"])

# Directory to save uploaded images
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/predict", response_model=PredictionResponse)
async def predict_disease(
    image: UploadFile = File(..., description="Plant leaf image for diagnosis"),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    🔍 Upload a plant image and get instant AI diagnosis!
    
    Simply take a picture of your plant leaf and our AI will:
    - Detect what crop it is (tomato, potato, or pepper)
    - Diagnose any diseases
    - Provide treatment recommendations
    - Give prevention tips
    
    Works without login for quick checks, but login to save your diagnosis history.
    """
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Get diagnosis from AI model
    diagnosis_result = await diagnosis_service.diagnose(image)
    
    # Get recommendations
    class_name = None
    for name in settings.CLASS_NAMES:
        if diagnosis_result.disease_name in name or name.replace("_", " ") == diagnosis_result.disease_name:
            class_name = name
            break
    
    recommendations = []
    if class_name:
        recommendations = diagnosis_service.get_recommendations(class_name)
    
    # Save to database if user is authenticated
    if current_user:
        # Save image
        file_extension = image.filename.split(".")[-1] if "." in image.filename else "jpg"
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        await image.seek(0)
        contents = await image.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Create diagnosis record
        db_diagnosis = Diagnosis(
            image_url=f"/uploads/{filename}",
            disease_name=diagnosis_result.disease_name,
            confidence=diagnosis_result.confidence,
            description=diagnosis_result.description,
            treatment=diagnosis_result.treatment,
            prevention=diagnosis_result.prevention,
            is_healthy=diagnosis_result.is_healthy,
            detected_crop=diagnosis_result.detected_crop,
            user_id=current_user.id
        )
        db.add(db_diagnosis)
        db.commit()
    
    return PredictionResponse(
        success=True,
        diagnosis=diagnosis_result,
        recommendations=recommendations,
        message="Diagnosis completed successfully"
    )


@router.get("/history", response_model=DiagnosisHistory)
async def get_diagnosis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get diagnosis history for current user"""
    diagnoses = db.query(Diagnosis).filter(
        Diagnosis.user_id == current_user.id
    ).order_by(Diagnosis.created_at.desc()).all()
    
    healthy_count = sum(1 for d in diagnoses if d.is_healthy)
    diseased_count = len(diagnoses) - healthy_count
    
    return DiagnosisHistory(
        total_diagnoses=len(diagnoses),
        healthy_count=healthy_count,
        diseased_count=diseased_count,
        diagnoses=diagnoses
    )


@router.get("/history/{diagnosis_id}", response_model=DiagnosisResponse)
async def get_diagnosis_detail(
    diagnosis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific diagnosis"""
    diagnosis = db.query(Diagnosis).filter(
        Diagnosis.id == diagnosis_id,
        Diagnosis.user_id == current_user.id
    ).first()
    
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )
    
    return diagnosis


@router.get("/diseases", response_model=List[dict])
async def get_supported_diseases():
    """Get list of all diseases the model can diagnose"""
    return diagnosis_service.get_all_supported_diseases()


@router.get("/disease-info/{disease_class}")
async def get_disease_details(disease_class: str):
    """Get detailed information about a specific disease"""
    info = get_disease_info(disease_class)
    if info.get("description") == "Disease information not available for this condition.":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease information not found for: {disease_class}"
        )
    return info


@router.get("/model-status")
async def get_model_status():
    """Check if the AI model is loaded and ready"""
    return {
        "model_loaded": diagnosis_service.is_model_loaded,
        "model_path": settings.MODEL_PATH,
        "supported_classes": len(settings.CLASS_NAMES),
        "image_size": settings.IMAGE_SIZE
    }
