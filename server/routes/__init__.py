from routes.auth import router as auth_router
from routes.farm import router as farm_router
from routes.diagnosis import router as diagnosis_router
from routes.routines import router as routines_router

__all__ = [
    "auth_router",
    "farm_router", 
    "diagnosis_router",
    "routines_router"
]
