import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional
import tensorflow as tf
from fastapi import UploadFile, HTTPException
import os
import logging

from config import get_settings
from schemas import DiagnosisResult
from services.disease_data import get_disease_info

settings = get_settings()
logger = logging.getLogger(__name__)


class DiagnosisService:
    """Service for plant disease diagnosis using AI model"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if DiagnosisService._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the trained model"""
        try:
            model_path = settings.MODEL_PATH
            if os.path.exists(model_path):
                DiagnosisService._model = tf.keras.models.load_model(model_path)
                logger.info(f"Model loaded successfully from {model_path}")
            else:
                logger.warning(f"Model not found at {model_path}")
                DiagnosisService._model = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            DiagnosisService._model = None
    
    @property
    def model(self):
        return DiagnosisService._model
    
    @property
    def is_model_loaded(self) -> bool:
        return DiagnosisService._model is not None
    
    async def preprocess_image(self, image_file: UploadFile) -> np.ndarray:
        """Preprocess image for model prediction"""
        try:
            # Read image bytes
            contents = await image_file.read()
            
            # Open image with PIL
            image = Image.open(io.BytesIO(contents))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to model input size
            image = image.resize(settings.IMAGE_SIZE)
            
            # Convert to numpy array and normalize
            img_array = np.array(image) / 255.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    def predict(self, img_array: np.ndarray) -> Tuple[str, float]:
        """Make prediction using the model"""
        if not self.is_model_loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        try:
            # Get predictions
            predictions = self.model.predict(img_array, verbose=0)
            
            # Get predicted class index and confidence
            predicted_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_idx])
            
            # Get class name
            class_name = settings.CLASS_NAMES[predicted_idx]
            
            return class_name, confidence
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    
    async def diagnose(self, image_file: UploadFile) -> DiagnosisResult:
        """Complete diagnosis pipeline"""
        # Preprocess image
        img_array = await self.preprocess_image(image_file)
        
        # Reset file pointer for potential saving
        await image_file.seek(0)
        
        # Make prediction
        class_name, confidence = self.predict(img_array)
        
        # Get disease information
        disease_info = get_disease_info(class_name)
        
        # Detect crop type from class name
        detected_crop = self._get_crop_from_class(class_name)
        
        # Create diagnosis result
        result = DiagnosisResult(
            disease_name=disease_info["disease_name"],
            confidence=confidence,
            is_healthy=disease_info["is_healthy"],
            detected_crop=detected_crop,
            description=disease_info["description"],
            treatment=disease_info["treatment"],
            prevention=disease_info["prevention"]
        )
        
        return result
    
    def _get_crop_from_class(self, class_name: str) -> str:
        """Extract crop type from class name"""
        class_lower = class_name.lower()
        if class_lower.startswith("tomato"):
            return "tomato"
        elif class_lower.startswith("potato"):
            return "potato"
        elif class_lower.startswith("pepper"):
            return "pepper"
        return "unknown"
    
    def get_recommendations(self, class_name: str) -> list:
        """Get care recommendations for a diagnosis"""
        disease_info = get_disease_info(class_name)
        return disease_info.get("recommendations", [])
    
    def get_all_supported_diseases(self) -> list:
        """Get list of all diseases the model can diagnose"""
        return [
            {
                "class_name": name,
                "plant_type": name.split("_")[0].replace("__", " "),
                "is_disease": "healthy" not in name.lower()
            }
            for name in settings.CLASS_NAMES
        ]


# Singleton instance
diagnosis_service = DiagnosisService()
