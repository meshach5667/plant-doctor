"""
Application configuration module.
Loads settings from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from functools import lru_cache
from typing import List, Tuple
import os
import secrets


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All sensitive values should be set via environment variables in production.
    """
    
    # Application
    APP_NAME: str = "Plant Doctor API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./plant_doctor.db",
        description="Database connection URL"
    )
    
    # JWT Authentication
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT encoding. MUST be set in production!"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        default=60,
        description="Maximum requests per minute per IP"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="List of allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    
    # Model paths
    MODEL_PATH: str = Field(
        default_factory=lambda: os.path.join(os.path.dirname(__file__), "model", "plantDoctor.h5")
    )
    TFLITE_MODEL_PATH: str = Field(
        default_factory=lambda: os.path.join(os.path.dirname(__file__), "model", "plantDoctor.tflite")
    )
    
    # Image settings
    IMAGE_SIZE: Tuple[int, int] = (256, 256)
    MAX_IMAGE_SIZE_MB: int = Field(default=10, description="Maximum upload image size in MB")
    
    # Class names for prediction (based on PlantVillage dataset)
    CLASS_NAMES: List[str] = [
        "Pepper__bell___Bacterial_spot",
        "Pepper__bell___healthy",
        "Potato___Early_blight",
        "Potato___healthy",
        "Potato___Late_blight",
        "Tomato__Target_Spot",
        "Tomato__Tomato_mosaic_virus",
        "Tomato__Tomato_YellowLeaf__Curl_Virus",
        "Tomato_Bacterial_spot",
        "Tomato_Early_blight",
        "Tomato_healthy",
        "Tomato_Late_blight",
        "Tomato_Leaf_Mold",
        "Tomato_Septoria_leaf_spot",
        "Tomato_Spider_mites_Two_spotted_spider_mite"
    ]
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {allowed}")
        return v.lower()
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Settings are loaded once and cached for performance.
    Call get_settings.cache_clear() to reload if needed.
    """
    return Settings()
