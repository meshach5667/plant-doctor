from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import FarmCropCreate, FarmCropUpdate, FarmCropResponse, FarmSummary, CropType
from routes.dependencies import get_current_user
from models import User, FarmCrop, CropType as ModelCropType
from services import get_routine_service

router = APIRouter(prefix="/farm", tags=["Farm"])


@router.post("/crops", response_model=FarmCropResponse, status_code=status.HTTP_201_CREATED)
async def add_crop_to_farm(
    crop_data: FarmCropCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a crop type to your farm.
    
    This tells Plant Doctor what you grow so it can send you relevant routine checks.
    For example, if you add 'tomato', you'll receive tomato-specific care reminders.
    """
    # Check if user already has this crop type
    existing = db.query(FarmCrop).filter(
        FarmCrop.owner_id == current_user.id,
        FarmCrop.crop_type == crop_data.crop_type,
        FarmCrop.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have {crop_data.crop_type.value} on your farm"
        )
    
    # Create the farm crop entry
    db_crop = FarmCrop(
        crop_type=crop_data.crop_type,
        location=crop_data.location,
        notes=crop_data.notes,
        owner_id=current_user.id,
        is_active=True
    )
    db.add(db_crop)
    db.commit()
    db.refresh(db_crop)
    
    # Create default routine checks for this crop
    routine_service = get_routine_service(db)
    routine_service.create_default_checks_for_crop(
        user_id=current_user.id,
        crop_type=ModelCropType(crop_data.crop_type.value),
        farm_crop_id=db_crop.id
    )
    
    return db_crop


@router.get("/crops", response_model=List[FarmCropResponse])
async def get_farm_crops(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all crops on your farm"""
    crops = db.query(FarmCrop).filter(
        FarmCrop.owner_id == current_user.id,
        FarmCrop.is_active == True
    ).all()
    return crops


@router.get("/summary", response_model=FarmSummary)
async def get_farm_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a summary of your farm - what crops you grow"""
    crops = db.query(FarmCrop).filter(
        FarmCrop.owner_id == current_user.id,
        FarmCrop.is_active == True
    ).all()
    
    crop_types = list(set([crop.crop_type.value for crop in crops]))
    
    return FarmSummary(
        total_crops=len(crops),
        crops=crops,
        crop_types=crop_types
    )


@router.get("/crops/{crop_id}", response_model=FarmCropResponse)
async def get_farm_crop(
    crop_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific crop from your farm"""
    crop = db.query(FarmCrop).filter(
        FarmCrop.id == crop_id,
        FarmCrop.owner_id == current_user.id
    ).first()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found on your farm"
        )
    
    return crop


@router.put("/crops/{crop_id}", response_model=FarmCropResponse)
async def update_farm_crop(
    crop_id: int,
    update_data: FarmCropUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a crop on your farm (location, notes, active status)"""
    crop = db.query(FarmCrop).filter(
        FarmCrop.id == crop_id,
        FarmCrop.owner_id == current_user.id
    ).first()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found on your farm"
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(crop, field, value)
    
    db.commit()
    db.refresh(crop)
    return crop


@router.delete("/crops/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_crop_from_farm(
    crop_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a crop from your farm.
    
    This will also delete all routine checks associated with this crop type.
    """
    crop = db.query(FarmCrop).filter(
        FarmCrop.id == crop_id,
        FarmCrop.owner_id == current_user.id
    ).first()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found on your farm"
        )
    
    # Delete associated routine checks
    routine_service = get_routine_service(db)
    routine_service.delete_checks_for_crop(
        user_id=current_user.id,
        crop_type=crop.crop_type
    )
    
    # Delete the farm crop
    db.delete(crop)
    db.commit()
    return None


@router.get("/supported-crops", response_model=List[dict])
async def get_supported_crops():
    """Get list of supported crop types"""
    return [
        {
            "type": CropType.TOMATO.value,
            "name": "Tomato",
            "emoji": "🍅",
            "description": "Tomato plants - detect early blight, late blight, mosaic virus, and more"
        },
        {
            "type": CropType.POTATO.value,
            "name": "Potato",
            "emoji": "🥔",
            "description": "Potato plants - detect early blight, late blight, and healthy plants"
        },
        {
            "type": CropType.PEPPER.value,
            "name": "Pepper (Bell)",
            "emoji": "🌶️",
            "description": "Bell pepper plants - detect bacterial spot and healthy plants"
        }
    ]
