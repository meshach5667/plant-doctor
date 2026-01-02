from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import (
    RoutineCheckCreate,
    RoutineCheckUpdate,
    RoutineCheckResponse,
    RoutineCheckComplete,
    UpcomingChecks,
    RoutineNotification
)
from routes.dependencies import get_current_user
from models import User
from services import get_routine_service

router = APIRouter(prefix="/routines", tags=["Routine Checks"])


@router.post("/", response_model=RoutineCheckResponse, status_code=status.HTTP_201_CREATED)
async def create_routine_check(
    check_data: RoutineCheckCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new routine check"""
    routine_service = get_routine_service(db)
    check = routine_service.create_routine_check(current_user.id, check_data)
    return check


@router.get("/", response_model=List[RoutineCheckResponse])
async def get_routine_checks(
    active_only: bool = True,
    plant_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all routine checks for current user"""
    routine_service = get_routine_service(db)
    checks = routine_service.get_user_routine_checks(
        current_user.id, 
        active_only=active_only,
        plant_id=plant_id
    )
    return checks


@router.get("/upcoming", response_model=UpcomingChecks)
async def get_upcoming_checks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming routine checks organized by urgency"""
    routine_service = get_routine_service(db)
    return routine_service.get_upcoming_checks(current_user.id)


@router.get("/notifications", response_model=List[RoutineNotification])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notification payloads for due and overdue checks.
    
    This endpoint is designed to be called periodically by the mobile app
    to check for routine checks that need attention.
    """
    routine_service = get_routine_service(db)
    return routine_service.get_notifications(current_user.id)


@router.get("/{check_id}", response_model=RoutineCheckResponse)
async def get_routine_check(
    check_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific routine check"""
    routine_service = get_routine_service(db)
    check = routine_service.get_routine_check(check_id, current_user.id)
    
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine check not found"
        )
    
    return check


@router.put("/{check_id}", response_model=RoutineCheckResponse)
async def update_routine_check(
    check_id: int,
    update_data: RoutineCheckUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a routine check"""
    routine_service = get_routine_service(db)
    check = routine_service.update_routine_check(check_id, current_user.id, update_data)
    
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine check not found"
        )
    
    return check


@router.post("/{check_id}/complete", response_model=RoutineCheckResponse)
async def complete_routine_check(
    check_id: int,
    completion_data: RoutineCheckComplete = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a routine check as completed.
    
    This will update the last_check_date to now and schedule the next
    check based on the frequency setting.
    """
    routine_service = get_routine_service(db)
    notes = completion_data.notes if completion_data else None
    check = routine_service.complete_routine_check(check_id, current_user.id, notes)
    
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine check not found"
        )
    
    return check


@router.delete("/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_routine_check(
    check_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a routine check"""
    routine_service = get_routine_service(db)
    success = routine_service.delete_routine_check(check_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine check not found"
        )
    
    return None
