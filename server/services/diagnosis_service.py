import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional
import tensorflow as tf
from fastapi import UploadFile, HTTPException
import os
import logging
import json

from config import get_settings
from schemas import DiagnosisResult
from services.disease_data import get_disease_info

settings = get_settings()
logger = logging.getLogger(__name__)

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')


def _clean_config(config):
    """Remove unsupported keys and fix dtype policy for model config compatibility."""
    unsupported_keys = ['quantization_config']
    
    if isinstance(config, dict):
        # Handle DTypePolicy - convert to simple string
        if config.get('class_name') == 'DTypePolicy':
            return config.get('config', {}).get('name', 'float32')
        
        cleaned = {}
        for k, v in config.items():
            if k in unsupported_keys:
                continue
            # Handle dtype field specially
            if k == 'dtype' and isinstance(v, dict) and v.get('class_name') == 'DTypePolicy':
                cleaned[k] = v.get('config', {}).get('name', 'float32')
            else:
                cleaned[k] = _clean_config(v)
        return cleaned
    elif isinstance(config, list):
        return [_clean_config(item) for item in config]
    return config


class DiagnosisService:
    """Service for plant disease diagnosis using AI model"""
    
    _instance = None
    _model = None
    _model_loaded = False
    _load_error = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not DiagnosisService._model_loaded:
            self._load_model()
    
    def _load_model(self):
        """Load the trained model with compatibility handling"""
        try:
            # Get absolute path to model
            model_path = settings.MODEL_PATH
            if not os.path.isabs(model_path):
                base_dir = os.path.dirname(os.path.dirname(__file__))
                model_path = os.path.join(base_dir, model_path)
            
            logger.info(f"Attempting to load model from: {model_path}")
            
            if not os.path.exists(model_path):
                error_msg = f"Model file not found at {model_path}"
                logger.error(error_msg)
                DiagnosisService._model = None
                DiagnosisService._model_loaded = True
                DiagnosisService._load_error = error_msg
                return
            
            # Try different loading methods for compatibility
            load_methods = [
                # Method 1: Standard load with compile=False
                ("standard", lambda: tf.keras.models.load_model(model_path, compile=False)),
                # Method 2: Build model architecture and load weights
                ("rebuild", lambda: self._rebuild_and_load_weights(model_path)),
                # Method 3: Legacy h5 format loading  
                ("legacy", lambda: self._load_legacy_h5_model(model_path)),
            ]
            
            for method_name, load_method in load_methods:
                try:
                    logger.info(f"Attempting load method: {method_name}...")
                    DiagnosisService._model = load_method()
                    DiagnosisService._model_loaded = True
                    DiagnosisService._load_error = None
                    logger.info(f"Model loaded successfully using method: {method_name}")
                    logger.info(f"Model input shape: {DiagnosisService._model.input_shape}")
                    return
                except Exception as method_error:
                    logger.warning(f"Load method '{method_name}' failed: {str(method_error)[:200]}")
                    continue
            
            # All methods failed
            error_msg = "All model loading methods failed. Please re-save the model in a compatible format."
            logger.error(error_msg)
            DiagnosisService._model = None
            DiagnosisService._model_loaded = True
            DiagnosisService._load_error = error_msg
                
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            logger.error(error_msg, exc_info=True)
            DiagnosisService._model = None
            DiagnosisService._model_loaded = True
            DiagnosisService._load_error = error_msg
    
    def _rebuild_and_load_weights(self, model_path: str):
        """Rebuild model architecture and load weights from h5 file"""
        # Build the same architecture as in train.ipynb
        # Note: The model has 16 output classes (from CLASS_NAMES in config)
        # but let's check the actual output from the saved model
        num_classes = len(settings.CLASS_NAMES)
        IMAGE_SIZE = 224
        CHANNELS = 3
        
        model = tf.keras.Sequential([
            # Rescaling layer (converts 0-255 pixels to 0-1)
            tf.keras.layers.Rescaling(1./255, input_shape=(IMAGE_SIZE, IMAGE_SIZE, CHANNELS)),
            
            # Convolutional Blocks
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            
            # Flatten and Dense Layers
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(num_classes, activation='softmax')  # Output layer
        ])
        
        # Load weights from h5 file
        model.load_weights(model_path)
        
        return model
    
    def _load_legacy_h5_model(self, model_path: str):
        """Load model using legacy h5 format with config cleaning"""
        import h5py
        
        with h5py.File(model_path, 'r') as f:
            model_config = f.attrs.get('model_config')
            if model_config is None:
                raise ValueError("No model_config found in h5 file")
            
            if isinstance(model_config, bytes):
                model_config = model_config.decode('utf-8')
            
            config_dict = json.loads(model_config)
            # Clean the config by removing unsupported keys
            config_dict = _clean_config(config_dict)
            
            # Build model from config
            model = tf.keras.models.model_from_json(json.dumps(config_dict))
            # Load weights
            model.load_weights(model_path)
            return model
    
    def reload_model(self):
        """Force reload the model"""
        DiagnosisService._model = None
        DiagnosisService._model_loaded = False
        DiagnosisService._load_error = None
        self._load_model()
    
    @property
    def model(self):
        return DiagnosisService._model
    
    @property
    def is_model_loaded(self) -> bool:
        return DiagnosisService._model is not None
    
    @property
    def load_error(self) -> Optional[str]:
        return DiagnosisService._load_error
    
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
            
            # Resize to model input size (224x224)
            image = image.resize(settings.IMAGE_SIZE)
            
            # Convert to numpy array
            # NOTE: Do NOT normalize here - the model has a Rescaling layer
            # that handles the 0-255 to 0-1 conversion
            img_array = np.array(image, dtype=np.float32)
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    def predict(self, img_array: np.ndarray) -> Tuple[str, float]:
        """Make prediction using the model"""
        if not self.is_model_loaded:
            error_detail = self.load_error if self.load_error else "Model not loaded"
            logger.error(f"Prediction failed: {error_detail}")
            raise HTTPException(status_code=503, detail=error_detail)
        
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
