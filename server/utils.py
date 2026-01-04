"""
Utility functions for Plant Doctor API
"""
import tensorflow as tf
import os
from config import get_settings

settings = get_settings()


def convert_model_to_tflite(
    h5_model_path: str = None,
    output_path: str = None,
    quantize: bool = True
) -> str:
    """
    Convert Keras H5 model to TFLite format for mobile/offline usage.
    
    Args:
        h5_model_path: Path to the H5 model file (default: from settings)
        output_path: Output path for TFLite model (default: from settings)
        quantize: Whether to apply quantization for smaller model size
        
    Returns:
        Path to the saved TFLite model
    """
    h5_model_path = h5_model_path or settings.MODEL_PATH
    output_path = output_path or settings.TFLITE_MODEL_PATH
    
    if not os.path.exists(h5_model_path):
        raise FileNotFoundError(f"Model not found at {h5_model_path}")
    
    # Load the Keras model
    model = tf.keras.models.load_model(h5_model_path)
    
    # Create TFLite converter
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    if quantize:
        # Apply post-training quantization for smaller model size
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # Convert the model
    tflite_model = converter.convert()
    
    # Save the TFLite model
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"TFLite model saved to: {output_path}")
    print(f"Original model size: {os.path.getsize(h5_model_path) / 1024 / 1024:.2f} MB")
    print(f"TFLite model size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
    
    return output_path


if __name__ == "__main__":
    # Run model conversion when executed directly
    print("Converting model to TFLite format...")
    try:
        convert_model_to_tflite()
        print("Conversion successful!")
    except Exception as e:
        print(f"Conversion failed: {e}")
