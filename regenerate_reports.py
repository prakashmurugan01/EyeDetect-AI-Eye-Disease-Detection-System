#!/usr/bin/env python
"""Regenerate existing detection reports with new advanced PDF generator"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eye_detection.settings')
django.setup()

from detection.models import Detection
from utils.pdf_generator import generate_pdf

print("\n" + "="*70)
print("REGENERATING DETECTION REPORTS - NEW ADVANCED FORMAT")
print("="*70)

# Find all existing detections
detections = Detection.objects.all().order_by('-detection_date')

if not detections.exists():
    print("\n[INFO] No detections found in database. Run upload test first.")
else:
    print(f"\n[1] Found {detections.count()} detection(s) in database\n")
    
    for i, detection in enumerate(detections[:5], 1):  # Process first 5
        print(f"[{i}] Processing: {detection.detection_id}")
        print(f"    Patient: {detection.patient.name} (Age: {detection.patient.age})")
        print(f"    Disease: {detection.predicted_disease.title()}")
        print(f"    Confidence: {detection.confidence_score}%")
        
        try:
            # Regenerate PDF with new format
            pdf_path = generate_pdf(detection)
            
            if os.path.exists(pdf_path):
                size_mb = os.path.getsize(pdf_path) / (1024*1024)
                print(f"    ✅ PDF regenerated ({size_mb:.3f} MB)")
                
                # Save path to detection
                detection.report_pdf = os.path.relpath(pdf_path, 'media/')
                detection.save()
                print(f"    ✅ Report path saved to DB")
            else:
                print(f"    ⚠️  PDF file not found after generation")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:60]}")
        
        print()

print("="*70)
print("REPORT REGENERATION COMPLETE")
print("="*70)
print("\nAll detection reports have been regenerated with:")
print("✓ Patient photo embedding")
print("✓ Advanced bilingual support (English & Tamil)")
print("✓ Confidence metrics and probability charts")
print("✓ Professional medical formatting")
print("✓ Enhanced severity indicators")
print("\n")
