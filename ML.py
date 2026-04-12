#1st cell

import numpy as np
import pandas as pd

df = pd.read_csv("walking.csv")

# Remove unwanted columns
df = df.drop(columns=["timestamp", "stride_id"])

print(df.head())

#2 cell
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df["class"] = le.fit_transform(df["class"])

print(le.classes_)  # walk, run, limp
import collections
print(collections.Counter(df["class"]))

#3 cell

df["acc_mag"] = np.sqrt(df["acc_x"]**2 + df["acc_y"]**2 + df["acc_z"]**2)
df["gyr_mag"] = np.sqrt(df["gyr_x"]**2 + df["gyr_y"]**2 + df["gyr_z"]**2)

X = df[["acc_x","acc_y","acc_z","gyr_x","gyr_y","gyr_z","acc_mag","gyr_mag"]].values
y = df["class"].values

#4th cell

df["acc_mag"] = np.sqrt(df["acc_x"]**2 + df["acc_y"]**2 + df["acc_z"]**2)
df["gyr_mag"] = np.sqrt(df["gyr_x"]**2 + df["gyr_y"]**2 + df["gyr_z"]**2)

X = df[["acc_x","acc_y","acc_z","gyr_x","gyr_y","gyr_z","acc_mag","gyr_mag"]].values
y = df["class"].values

#5th cell
import numpy as np

WINDOW_SIZE = 100   # 1 sec (50Hz)
STEP_SIZE = 25     # overlap

def create_windows(X, y):
    X_w, y_w = [], []

    for i in range(0, len(X) - WINDOW_SIZE, STEP_SIZE):
        window = X[i:i+WINDOW_SIZE]
        labels = y[i:i+WINDOW_SIZE]

        # keep only pure windows
        if len(set(labels)) == 1:
            X_w.append(window)
            y_w.append(labels[0])

    return np.array(X_w), np.array(y_w)

X_w, y_w = create_windows(X, y)

print("Windowed shape:", X_w.shape)

#6th cell

# Augmentation functions
def add_noise(X, noise_level=0.01):
    noise = np.random.normal(0, noise_level, X.shape)
    return X + noise

def scale_signal(X, scale_range=(0.9, 1.1)):
    scale = np.random.uniform(scale_range[0], scale_range[1])
    return X * scale

def time_shift(X, shift_max=5):
    shift = np.random.randint(-shift_max, shift_max)
    return np.roll(X, shift, axis=1)

def augment_window(window):
    if np.random.rand() < 0.5:
        window = add_noise(window)
    if np.random.rand() < 0.5:
        window = scale_signal(window)
    if np.random.rand() < 0.5:
        window = time_shift(window)
    return window

def augment_dataset(X, y, factor=2):
    X_aug, y_aug = [], []

    for i in range(len(X)):
        for _ in range(factor):
            X_aug.append(augment_window(X[i]))
            y_aug.append(y[i])

    return np.array(X_aug), np.array(y_aug)

X_aug, y_aug = augment_dataset(X_w, y_w, factor=2)

X_final = np.concatenate([X_w, X_aug])
y_final = np.concatenate([y_w, y_aug])

print("Final dataset:", X_final.shape)

#7th cell

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X_final, y_final, test_size=0.2, random_state=42
)

#8th cell

import tensorflow as tf
from tensorflow.keras import layers

model = tf.keras.Sequential([
    layers.Conv1D(32, 5, activation='relu', input_shape=(WINDOW_SIZE, 8)),
    layers.BatchNormalization(),
    layers.MaxPooling1D(2),

    layers.Conv1D(64, 5, activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling1D(2),

    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.4),

    layers.Dense(3, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

#9th cell

early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

history = model.fit(
    X_train, y_train,
    epochs=40,
    batch_size=32,
    validation_data=(X_test, y_test),
    callbacks=[early_stop]
)

#10th cell

loss, acc = model.evaluate(X_test, y_test)
print(f"Final Accuracy: {acc*100:.2f}%")

#11 cell

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

with open("gait_model.tflite", "wb") as f:
    f.write(tflite_model)

from google.colab import files
files.download("gait_model.tflite")


import tensorflow as tf
import numpy as np

# The Keras model 'model' is already in memory from previous cells, so we don't need to load it.
# The problematic line was: model = tf.keras.models.load_model('gait_model.h5')

# You need representative data matching your model's input shape
def representative_dataset():
    for _ in range(100):
        # Corrected shape: (batch_size, WINDOW_SIZE, number_of_features)
        # WINDOW_SIZE is 100 and there are 8 features, so the shape is (1, 100, 8)
        data = np.random.rand(1, 100, 8).astype(np.float32) # Corrected input shape
        yield [data]

converter = tf.lite.TFLiteConverter.from_keras_model(model) # Use the existing Keras 'model' object
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type  = tf.float32   # keep float input for ease
converter.inference_output_type = tf.float32   # keep float output for ease

tflite_model = converter.convert()
with open('model_int8.tflite', 'wb') as f:
    f.write(tflite_model)

print("Done! Size:", len(tflite_model), "bytes")

!xxd -i gait_model.tflite > model.h

