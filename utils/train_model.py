"""
Eye Disease AI Model Training Script
Uses ResNet50 transfer learning for ~95% accuracy.
Run this from the utils/ directory or project root.

Usage:
    cd eye_disease_project
    python utils/train_model.py

Requirements:
    - Dataset in dataset/train/<class>/ and dataset/test/<class>/
    - Classes: cataract, diabetic_retinopathy, glaucoma, normal
    - 800+ images per class recommended
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Add parent dir to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras import layers, Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
)
from tensorflow.keras.optimizers import Adam
import numpy as np

# ── Configuration ──────────────────────────────────────────────────────────
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS_FROZEN = 20       # Train only top layers first
EPOCHS_FINE_TUNE = 30    # Fine-tune last ResNet block
CLASSES = 4
LR_INITIAL = 1e-3
LR_FINE_TUNE = 1e-5

TRAIN_DIR = '../dataset/train'
TEST_DIR = '../dataset/test'
MODEL_OUT = '../ml_models/eye_disease_model.h5'
LOG_DIR = '../logs/training'

os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


# ── Data Augmentation ──────────────────────────────────────────────────────
print("🔄 Setting up data generators...")

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=False,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.1,
    brightness_range=[0.8, 1.2],
    fill_mode='nearest',
    validation_split=0.2,
)

test_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True,
)

val_gen = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False,
)

test_gen = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False,
)

print(f"✅ Train: {train_gen.n} images | Val: {val_gen.n} | Test: {test_gen.n}")
print(f"   Classes: {train_gen.class_indices}")


# ── Build Model ────────────────────────────────────────────────────────────
print("\n🏗️  Building ResNet50 model...")

base = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
)
base.trainable = False  # Freeze base for phase 1

inp = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x = base(inp, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)
x = layers.Dense(512, activation='relu')(x)
x = layers.Dropout(0.5)(x)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.3)(x)
x = layers.Dense(128, activation='relu')(x)
x = layers.Dropout(0.2)(x)
output = layers.Dense(CLASSES, activation='softmax')(x)

model = Model(inp, output)
model.summary()

# ── Phase 1: Train Top Layers ───────────────────────────────────────────────
print("\n🚀 Phase 1: Training top layers (base frozen)...")

model.compile(
    optimizer=Adam(learning_rate=LR_INITIAL),
    loss='categorical_crossentropy',
    metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
)

callbacks_p1 = [
    EarlyStopping(monitor='val_accuracy', patience=7,
                  restore_best_weights=True, verbose=1),
    ModelCheckpoint(MODEL_OUT, save_best_only=True,
                    monitor='val_accuracy', verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                      patience=4, min_lr=1e-6, verbose=1),
    TensorBoard(log_dir=LOG_DIR + '/phase1'),
]

history1 = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS_FROZEN,
    callbacks=callbacks_p1,
    verbose=1,
)

# ── Phase 2: Fine-tune ──────────────────────────────────────────────────────
print("\n🔧 Phase 2: Fine-tuning last ResNet block...")

# Unfreeze last 30 layers
for layer in base.layers[-30:]:
    layer.trainable = True

model.compile(
    optimizer=Adam(learning_rate=LR_FINE_TUNE),
    loss='categorical_crossentropy',
    metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
)

callbacks_p2 = [
    EarlyStopping(monitor='val_accuracy', patience=10,
                  restore_best_weights=True, verbose=1),
    ModelCheckpoint(MODEL_OUT, save_best_only=True,
                    monitor='val_accuracy', verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.3,
                      patience=5, min_lr=1e-8, verbose=1),
    TensorBoard(log_dir=LOG_DIR + '/phase2'),
]

history2 = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS_FINE_TUNE,
    callbacks=callbacks_p2,
    verbose=1,
    initial_epoch=len(history1.history['loss']),
)

# ── Evaluate ────────────────────────────────────────────────────────────────
print("\n📊 Evaluating on test set...")
loss, acc, auc = model.evaluate(test_gen, verbose=1)
print(f"\n✅ Test Accuracy: {acc * 100:.1f}%  |  AUC: {auc:.3f}")

# ── Confusion Matrix ────────────────────────────────────────────────────────
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

test_gen.reset()
y_pred_probs = model.predict(test_gen, verbose=1)
y_pred = np.argmax(y_pred_probs, axis=1)
y_true = test_gen.classes

class_names = list(test_gen.class_indices.keys())
print("\n📋 Classification Report:")
print(classification_report(y_true, y_pred, target_names=class_names))

# Save confusion matrix plot
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names)
plt.title(f'Confusion Matrix — Test Accuracy: {acc * 100:.1f}%')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig('../ml_models/confusion_matrix.png', dpi=150)
plt.close()

# Save training history plot
all_acc = history1.history['accuracy'] + history2.history['accuracy']
all_val_acc = history1.history['val_accuracy'] + history2.history['val_accuracy']

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(all_acc, label='Train Accuracy')
plt.plot(all_val_acc, label='Val Accuracy')
plt.axvline(x=len(history1.history['accuracy']) - 1,
            color='r', linestyle='--', label='Fine-tune start')
plt.title('Accuracy')
plt.legend()

all_loss = history1.history['loss'] + history2.history['loss']
all_val_loss = history1.history['val_loss'] + history2.history['val_loss']
plt.subplot(1, 2, 2)
plt.plot(all_loss, label='Train Loss')
plt.plot(all_val_loss, label='Val Loss')
plt.axvline(x=len(history1.history['loss']) - 1,
            color='r', linestyle='--', label='Fine-tune start')
plt.title('Loss')
plt.legend()
plt.tight_layout()
plt.savefig('../ml_models/training_history.png', dpi=150)
plt.close()

print(f"\n✅ Model saved: {MODEL_OUT}")
print("✅ Plots saved: confusion_matrix.png, training_history.png")
print(f"\n🎯 Final Test Accuracy: {acc * 100:.1f}%")
