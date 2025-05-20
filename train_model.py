import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow import keras
from keras._tf_keras.keras.preprocessing.image import ImageDataGenerator

# Enable Data Augmentation to artificially expand the dataset
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,         # Random rotation
    width_shift_range=0.2,     # Random horizontal shift
    height_shift_range=0.2,    # Random vertical shift
    shear_range=0.2,           # Shearing transformation
    zoom_range=0.2,            # Random zoom
    horizontal_flip=True,      # Random horizontal flip
    fill_mode='nearest'        # Fill in pixels for augmented images
)

# Load images from the dataset
train_generator = train_datagen.flow_from_directory(
    'data/',                 # Path to the dataset
    target_size=(224, 224),  # Resize all images to 224x224 pixels
    batch_size=16,           # Batch size for training
    class_mode='binary',     # Binary classification (eco-friendly vs non-eco-friendly)
    shuffle=True             # Shuffle the dataset
)

# Model Architecture
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(1, activation='sigmoid')  # Binary output: eco-friendly or not
])

# Compile the Model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the Model
print(f"Training on {train_generator.samples} samples...")
model.fit(train_generator, epochs=10, steps_per_epoch=train_generator.samples // train_generator.batch_size)

# Save the Model
model.save('app/eco_action_model.h5')
print("Model training complete. Model saved as 'app/eco_action_model.h5'")
