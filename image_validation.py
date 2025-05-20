import tensorflow as tf
from tensorflow import keras
import tempfile
from keras._tf_keras.keras.models import load_model
from keras._tf_keras.keras.preprocessing.image import img_to_array, load_img
from PIL import Image  # Add this import for better image format handling
import os

MODEL_PATH = "app/eco_action_model.h5"

# Check if model file exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

# Load the model
try:
    model = load_model(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Error loading model: {e}")

def validate_image(image):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(image.file.read())
            temp_file_path = temp_file.name

        # Open and validate the image format
        try:
            with Image.open(temp_file_path) as img:
                img.verify()  # Verify it's a valid image
                img = Image.open(temp_file_path)  # Reopen image for processing
                img = img.convert("RGB")  # Ensure it's in RGB mode

        except Exception as e:
            raise ValueError(f"Invalid image format: {e}")

        # Process the valid image
        img = img.resize((224, 224))
        img_array = img_to_array(img) / 255.0
        img_array = img_array.reshape((1, 224, 224, 3))

        # Predict with the model
        prediction = model.predict(img_array)
        return prediction[0][0] > 0.5  # Return True if eco-friendly, False otherwise

    except Exception as e:
        raise RuntimeError(f"Error validating image: {e}")
    finally:
        # Clean up temporary file
        if "temp_file_path" in locals():
            try:
                os.remove(temp_file_path)
            except Exception as cleanup_error:
                print(f"Error cleaning up temporary file: {cleanup_error}")
