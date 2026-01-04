"""
Pydantic schemas for request/response validation.
"""
from schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
)

from schemas.plant import (
    CropType,
    FarmCropCreate,
    FarmCropUpdate,
    FarmCropResponse,
    FarmSummary
)

from schemas.diagnosis import (
    DiagnosisResult,
    DiagnosisResponse,
    PredictionResponse,
    DiagnosisHistory
)

from schemas.routine import (
    FrequencyType,
    CheckType,
    RoutineCheckBase,
    RoutineCheckCreate,
    RoutineCheckUpdate,
    RoutineCheckResponse,
    RoutineCheckComplete,
    UpcomingChecks,
    RoutineNotification
)

__all__ = [
    # User schemas
    "UserCreate", 
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenResponse",
    "TokenRefresh",
    "PasswordChange",
    # Farm crop schemas
    "CropType",
    "FarmCropCreate",
    "FarmCropUpdate",
    "FarmCropResponse",
    "FarmSummary",
    # Diagnosis schemas
    "DiagnosisResult",
    "DiagnosisResponse",
    "PredictionResponse",
    "DiagnosisHistory",
    # Routine schemas
    "FrequencyType",
    "CheckType",
    "RoutineCheckBase",
    "RoutineCheckCreate",
    "RoutineCheckUpdate",
    "RoutineCheckResponse",
    "RoutineCheckComplete",
    "UpcomingChecks",
    "RoutineNotification"
]
