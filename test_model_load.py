#!/usr/bin/env python
"""Test script to verify model loading"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eye_detection.settings')
django.setup()

from utils.predictor import EyePredictor

print("\n" + "="*60)
print("TESTING MODEL LOAD - EYE DISEASE PREDICTION ENGINE")
print("="*60)

# Test model loading
predictor = EyePredictor()

if predictor.model is not None:
    print("✅ SUCCESS: Model loaded successfully!")
    print(f"   Model type: {type(predictor.model)}")
    print(f"   Model name: {predictor.model.name}")
else:
    print("❌ FAILED: Model could not be loaded")

# Check file paths
from django.conf import settings
model_path = str(settings.ML_MODEL_PATH)
print(f"\n📁 Model path configured: {model_path}")
print(f"   Path exists: {os.path.exists(model_path)}")

if os.path.exists(model_path):
    size_mb = os.path.getsize(model_path) / (1024*1024)
    print(f"   File size: {size_mb:.2f} MB")

print("\n" + "="*60)
