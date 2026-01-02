from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Plant Doctor API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./plant_doctor.db"
    
    # Model paths
    MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "model", "plantDoctor.h5")
    TFLITE_MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "model", "plantDoctor.tflite")
    
    # Image settings
    IMAGE_SIZE: tuple = (256, 256)
    
    # Class names for prediction (based on PlantVillage dataset)
    CLASS_NAMES: list = [
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
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
