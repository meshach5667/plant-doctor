from routes.auth import router as auth_router
from routes.plants import router as plants_router
from routes.diagnosis import router as diagnosis_router
from routes.routines import router as routines_router

__all__ = [
    "auth_router",
    "plants_router", 
    "diagnosis_router",
    "routines_router"
]
