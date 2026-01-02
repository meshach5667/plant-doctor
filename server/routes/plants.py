from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import PlantCreate, PlantUpdate, PlantResponse
from routes.dependencies import get_current_user
from models import User, Plant
from services import get_routine_service

router = APIRouter(prefix="/plants", tags=["Plants"])


@router.post("/", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    plant_data: PlantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new plant"""
    db_plant = Plant(
        **plant_data.model_dump(),
        owner_id=current_user.id
    )
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    
    # Create default routine checks for the plant
    routine_service = get_routine_service(db)
    routine_service.create_default_checks_for_plant(
        user_id=current_user.id,
        plant_id=db_plant.id,
        plant_type=db_plant.plant_type
    )
    
    return db_plant


@router.get("/", response_model=List[PlantResponse])
async def get_plants(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all plants for current user"""
    plants = db.query(Plant).filter(Plant.owner_id == current_user.id).all()
    return plants


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(
    plant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific plant"""
    plant = db.query(Plant).filter(
        Plant.id == plant_id,
        Plant.owner_id == current_user.id
    ).first()
    
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    
    return plant


@router.put("/{plant_id}", response_model=PlantResponse)
async def update_plant(
    plant_id: int,
    update_data: PlantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a plant"""
    plant = db.query(Plant).filter(
        Plant.id == plant_id,
        Plant.owner_id == current_user.id
    ).first()
    
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(plant, field, value)
    
    db.commit()
    db.refresh(plant)
    return plant


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a plant"""
    plant = db.query(Plant).filter(
        Plant.id == plant_id,
        Plant.owner_id == current_user.id
    ).first()
    
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    
    db.delete(plant)
    db.commit()
    return None
