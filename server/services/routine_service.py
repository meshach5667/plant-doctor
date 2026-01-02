from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from models import RoutineCheck, Plant, User, FrequencyType
from schemas import (
    RoutineCheckCreate,
    RoutineCheckUpdate,
    RoutineCheckResponse,
    UpcomingChecks,
    RoutineNotification
)

logger = logging.getLogger(__name__)


class RoutineCheckService:
    """Service for managing routine plant checks"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_routine_check(
        self, 
        user_id: int, 
        check_data: RoutineCheckCreate
    ) -> RoutineCheck:
        """Create a new routine check"""
        db_check = RoutineCheck(
            title=check_data.title,
            description=check_data.description,
            frequency=check_data.frequency,
            check_type=check_data.check_type,
            next_check_date=check_data.next_check_date,
            notes=check_data.notes,
            plant_id=check_data.plant_id,
            user_id=user_id,
            is_active=True
        )
        self.db.add(db_check)
        self.db.commit()
        self.db.refresh(db_check)
        return db_check
    
    def get_routine_check(self, check_id: int, user_id: int) -> Optional[RoutineCheck]:
        """Get a specific routine check"""
        return self.db.query(RoutineCheck).filter(
            RoutineCheck.id == check_id,
            RoutineCheck.user_id == user_id
        ).first()
    
    def get_user_routine_checks(
        self, 
        user_id: int, 
        active_only: bool = True,
        plant_id: Optional[int] = None
    ) -> List[RoutineCheck]:
        """Get all routine checks for a user"""
        query = self.db.query(RoutineCheck).filter(RoutineCheck.user_id == user_id)
        
        if active_only:
            query = query.filter(RoutineCheck.is_active == True)
        
        if plant_id:
            query = query.filter(RoutineCheck.plant_id == plant_id)
        
        return query.order_by(RoutineCheck.next_check_date).all()
    
    def update_routine_check(
        self, 
        check_id: int, 
        user_id: int, 
        update_data: RoutineCheckUpdate
    ) -> Optional[RoutineCheck]:
        """Update a routine check"""
        db_check = self.get_routine_check(check_id, user_id)
        if not db_check:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_check, field, value)
        
        self.db.commit()
        self.db.refresh(db_check)
        return db_check
    
    def delete_routine_check(self, check_id: int, user_id: int) -> bool:
        """Delete a routine check"""
        db_check = self.get_routine_check(check_id, user_id)
        if not db_check:
            return False
        
        self.db.delete(db_check)
        self.db.commit()
        return True
    
    def complete_routine_check(
        self, 
        check_id: int, 
        user_id: int, 
        notes: Optional[str] = None
    ) -> Optional[RoutineCheck]:
        """Mark a routine check as completed and schedule next occurrence"""
        db_check = self.get_routine_check(check_id, user_id)
        if not db_check:
            return None
        
        # Update last check date
        db_check.last_check_date = datetime.utcnow()
        
        # Add completion notes if provided
        if notes:
            db_check.notes = notes
        
        # Calculate next check date based on frequency
        db_check.next_check_date = self._calculate_next_check_date(
            db_check.frequency
        )
        
        self.db.commit()
        self.db.refresh(db_check)
        return db_check
    
    def _calculate_next_check_date(self, frequency: FrequencyType) -> datetime:
        """Calculate the next check date based on frequency"""
        now = datetime.utcnow()
        
        if frequency == FrequencyType.DAILY:
            return now + timedelta(days=1)
        elif frequency == FrequencyType.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == FrequencyType.BIWEEKLY:
            return now + timedelta(weeks=2)
        elif frequency == FrequencyType.MONTHLY:
            return now + timedelta(days=30)
        else:
            return now + timedelta(weeks=1)  # Default to weekly
    
    def get_upcoming_checks(self, user_id: int) -> UpcomingChecks:
        """Get upcoming checks organized by urgency"""
        now = datetime.utcnow()
        today_end = now.replace(hour=23, minute=59, second=59)
        week_end = now + timedelta(days=7)
        
        active_checks = self.get_user_routine_checks(user_id, active_only=True)
        
        due_today = []
        due_this_week = []
        overdue = []
        
        for check in active_checks:
            if check.next_check_date < now:
                overdue.append(check)
            elif check.next_check_date <= today_end:
                due_today.append(check)
            elif check.next_check_date <= week_end:
                due_this_week.append(check)
        
        return UpcomingChecks(
            due_today=due_today,
            due_this_week=due_this_week,
            overdue=overdue
        )
    
    def get_notifications(self, user_id: int) -> List[RoutineNotification]:
        """Get notification payloads for due checks"""
        upcoming = self.get_upcoming_checks(user_id)
        notifications = []
        
        # Add overdue notifications (highest priority)
        for check in upcoming.overdue:
            plant_name = None
            if check.plant_id:
                plant = self.db.query(Plant).filter(Plant.id == check.plant_id).first()
                plant_name = plant.name if plant else None
            
            notifications.append(RoutineNotification(
                check_id=check.id,
                title=f"Overdue: {check.title}",
                message=f"Your {check.check_type} check was due on {check.next_check_date.strftime('%Y-%m-%d')}",
                check_type=check.check_type,
                plant_name=plant_name,
                due_date=check.next_check_date,
                is_overdue=True
            ))
        
        # Add due today notifications
        for check in upcoming.due_today:
            plant_name = None
            if check.plant_id:
                plant = self.db.query(Plant).filter(Plant.id == check.plant_id).first()
                plant_name = plant.name if plant else None
            
            notifications.append(RoutineNotification(
                check_id=check.id,
                title=f"Due Today: {check.title}",
                message=f"Time for your {check.check_type} check!",
                check_type=check.check_type,
                plant_name=plant_name,
                due_date=check.next_check_date,
                is_overdue=False
            ))
        
        return notifications
    
    def create_default_checks_for_plant(
        self, 
        user_id: int, 
        plant_id: int, 
        plant_type: str
    ) -> List[RoutineCheck]:
        """Create default routine checks for a new plant"""
        default_checks = self._get_default_checks_for_plant_type(plant_type)
        created_checks = []
        
        for check_data in default_checks:
            db_check = RoutineCheck(
                title=check_data["title"],
                description=check_data["description"],
                frequency=check_data["frequency"],
                check_type=check_data["check_type"],
                next_check_date=datetime.utcnow() + timedelta(days=check_data["initial_delay_days"]),
                plant_id=plant_id,
                user_id=user_id,
                is_active=True
            )
            self.db.add(db_check)
            created_checks.append(db_check)
        
        self.db.commit()
        for check in created_checks:
            self.db.refresh(check)
        
        return created_checks
    
    def _get_default_checks_for_plant_type(self, plant_type: str) -> List[dict]:
        """Get default routine checks based on plant type"""
        plant_type_lower = plant_type.lower()
        
        # Common checks for all plants
        common_checks = [
            {
                "title": f"Water {plant_type}",
                "description": f"Check soil moisture and water your {plant_type} if needed",
                "frequency": FrequencyType.DAILY,
                "check_type": "watering",
                "initial_delay_days": 0
            },
            {
                "title": f"Check {plant_type} for pests",
                "description": f"Inspect leaves and stems for signs of pest damage",
                "frequency": FrequencyType.WEEKLY,
                "check_type": "pest_check",
                "initial_delay_days": 3
            },
            {
                "title": f"Check {plant_type} for diseases",
                "description": f"Look for discoloration, spots, or unusual growth patterns",
                "frequency": FrequencyType.WEEKLY,
                "check_type": "disease_check",
                "initial_delay_days": 4
            },
            {
                "title": f"Fertilize {plant_type}",
                "description": f"Apply balanced fertilizer to support healthy growth",
                "frequency": FrequencyType.BIWEEKLY,
                "check_type": "fertilizing",
                "initial_delay_days": 7
            }
        ]
        
        # Plant-specific checks
        if "tomato" in plant_type_lower:
            common_checks.extend([
                {
                    "title": "Prune tomato suckers",
                    "description": "Remove suckers growing between main stem and branches",
                    "frequency": FrequencyType.WEEKLY,
                    "check_type": "pruning",
                    "initial_delay_days": 14
                },
                {
                    "title": "Check tomato support",
                    "description": "Ensure stakes/cages are secure as plant grows",
                    "frequency": FrequencyType.WEEKLY,
                    "check_type": "general",
                    "initial_delay_days": 7
                }
            ])
        elif "potato" in plant_type_lower:
            common_checks.append({
                "title": "Hill potato soil",
                "description": "Add soil around stems to encourage tuber development",
                "frequency": FrequencyType.BIWEEKLY,
                "check_type": "general",
                "initial_delay_days": 14
            })
        elif "pepper" in plant_type_lower:
            common_checks.append({
                "title": "Support pepper plants",
                "description": "Check if plants need staking as fruit develops",
                "frequency": FrequencyType.WEEKLY,
                "check_type": "general",
                "initial_delay_days": 21
            })
        
        return common_checks


def get_routine_service(db: Session) -> RoutineCheckService:
    """Factory function to get routine check service"""
    return RoutineCheckService(db)
