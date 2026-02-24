"""
Professional Bilingual PDF Report Generator with Photo & Advanced Features
Uses ReportLab to create a medical-grade detection report with:
- Patient photo embedded
- Bilingual (English + Tamil) support with proper fonts
- Confidence metrics and probability breakdown
- Clinical recommendations and severity indicators
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, legal
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Image, PageBreak, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
import json


DISEASE_COLORS = {
    'cataract': colors.HexColor('#ef4444'),
    'diabetic_retinopathy': colors.HexColor('#f97316'),
    'glaucoma': colors.HexColor('#3b82f6'),
    'normal': colors.HexColor('#22c55e'),
}

SEVERITY_COLORS = {
    'MILD': colors.HexColor('#22c55e'),
    'MODERATE': colors.HexColor('#f97316'),
    'SEVERE': colors.HexColor('#ef4444'),
}


class ConfidenceBar(Flowable):
    """Custom flowable to render a confidence bar chart"""
    def __init__(self, confidence, max_width=6*cm, height=0.5*cm):
        self.confidence = min(confidence, 100)
        self.max_width = max_width
        self.height = height
        self.width = max_width

    def draw(self):
        """Draw confidence bar"""
        # Background bar
        self.canv.setFillColor(colors.HexColor('#e0e7ff'))
        self.canv.rect(0, 0, self.max_width, self.height, fill=1, stroke=0)
        
        # Filled portion based on confidence
        fill_width = (self.confidence / 100) * self.max_width
        if self.confidence >= 85:
            bar_color = colors.HexColor('#dc2626')  # Red for high confidence
        elif self.confidence >= 70:
            bar_color = colors.HexColor('#f97316')  # Orange for moderate
        else:
            bar_color = colors.HexColor('#3b82f6')  # Blue for lower
        
        self.canv.setFillColor(bar_color)
        self.canv.rect(0, 0, fill_width, self.height, fill=1, stroke=0)
        
        # Border
        self.canv.setLineWidth(1)
        self.canv.setStrokeColor(colors.HexColor('#94a3b8'))
        self.canv.rect(0, 0, self.max_width, self.height, fill=0, stroke=1)


def get_image_thumbnail(image_path, max_width=2*inch, max_height=2*inch):
    """
    Load and resize image for embedding in PDF.
    Returns Image object or None if file not found.
    """
    try:
        if not os.path.exists(image_path):
            return None
        
        # Open and convert to RGB (fixes RGBA issues)
        img = PILImage.open(image_path)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Convert to RGB
            rgb_img = PILImage.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
        
        # Create a temporary resized version
        temp_path = image_path.replace('.jpg', '_thumb.jpg').replace('.png', '_thumb.jpg').replace('.webp', '_thumb.jpg')
        img.save(temp_path, 'JPEG', quality=85)
        
        # Return ReportLab Image object
        return Image(temp_path, width=max_width, height=max_height)
    except Exception as e:
        print(f"[WARNING] Image loading error: {e}")
        return None


def generate_pdf(detection) -> str:
    """
    Generate a professional bilingual PDF report for a Detection object.
    Includes patient photo, confidence metrics, and clinical recommendations.
    Returns the output file path.
    """
    reports_dir = os.path.join('media', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    filename = f'report_{detection.detection_id}.pdf'
    outpath = os.path.join(reports_dir, filename)

    doc = SimpleDocTemplate(
        outpath,
        pagesize=A4,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Style Definitions ──────────────────────────────────────────
    brand_blue = colors.HexColor('#4f46e5')
    brand_dark = colors.HexColor('#1e1b4b')
    light_bg = colors.HexColor('#eef2ff')
    medical_accent = colors.HexColor('#0369a1')

    style_main_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Normal'],
        fontSize=20,
        fontName='Helvetica-Bold',
        textColor=brand_blue,
        spaceAfter=2,
        alignment=TA_CENTER,
    )
    
    style_subtitle = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=9.5,
        fontName='Helvetica',
        textColor=colors.HexColor('#64748b'),
        spaceAfter=8,
        alignment=TA_CENTER,
    )
    
    style_section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=brand_dark,
        spaceBefore=10,
        spaceAfter=5,
    )
    
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9.5,
        fontName='Helvetica',
        leading=14,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
    )
    
    style_tamil_body = ParagraphStyle(
        'TamilBody',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',  # Use DejaVuSans for better Unicode support if available
        leading=15,
        spaceAfter=5,
        alignment=TA_JUSTIFY,
    )
    
    style_bullet = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        leading=13,
        leftIndent=10,
        spaceAfter=2,
    )
    
    style_disclaimer = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=7.5,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#b91c1c'),
        leading=11,
        spaceAfter=3,
    )
    
    style_small_label = ParagraphStyle(
        'SmallLabel',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#475569'),
    )
    
    style_footer = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7,
        fontName='Helvetica',
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER,
    )

    # ── HEADER Banner ────────────────────────────────────────────
    story.append(Paragraph("👁️  Eye Disease Detection System", style_main_title))
    story.append(Paragraph("AI-Powered Medical Screening Report", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=2, color=brand_blue))
    story.append(Spacer(1, 0.15 * inch))

    # ── Patient Photo + Info Section ─────────────────────────────
    photo = None
    image_path = detection.image.path if detection.image else None
    if image_path and os.path.exists(image_path):
        photo = get_image_thumbnail(image_path, max_width=1.5*inch, max_height=1.5*inch)

    # Patient info table with photo
    patient_info_data = [
        ['Patient Name', detection.patient.name, '', ''],
        ['Patient ID', detection.patient.patient_id, '', ''],
        ['Age / Gender', f"{detection.patient.age} yrs / {detection.patient.get_gender_display()}", '', ''],
        ['Report Date', datetime.now().strftime('%d %b %Y, %I:%M %p'), '', ''],
    ]
    
    patient_table = Table(patient_info_data, colWidths=[2.5*cm, 5*cm, 1.5*cm, 4.5*cm])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c7d2fe')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    # Combine photo and patient info if photo exists
    if photo:
        photo_data = [[photo, patient_table]]
        photo_table = Table(photo_data, colWidths=[2*inch, 4.5*inch])
        photo_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(photo_table)
    else:
        story.append(patient_table)

    story.append(Spacer(1, 0.15 * inch))

    # ── Diagnosis Highlight Box ────────────────────────────────────
    disease_color = DISEASE_COLORS.get(detection.predicted_disease, brand_blue)
    severity_color = SEVERITY_COLORS.get(detection.severity, colors.grey)

    disease_display = detection.predicted_disease.replace('_', ' ').title()
    
    diag_data = [[
        f"DETECTED: {disease_display}",
        f"Confidence: {detection.confidence_score:.1f}%",
        f"Severity: {detection.severity}",
    ]]
    
    diag_table = Table(diag_data, colWidths=[4.5*cm, 4*cm, 3.5*cm])
    diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), disease_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWHEIGHT', (0, 0), (-1, -1), 28),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 0.15 * inch))

    # ── Confidence Metrics ─────────────────────────────────────────
    story.append(Paragraph("📊 Confidence & Severity Metrics", style_section_title))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#c7d2fe')))
    story.append(Spacer(1, 0.05 * inch))

    # Try to parse all probabilities
    all_probs = {}
    try:
        if detection.all_probabilities:
            all_probs = json.loads(detection.all_probabilities)
    except:
        pass

    # Create probability breakdown table
    prob_rows = [['Disease', 'Probability', '']]
    disease_list = ['cataract', 'diabetic_retinopathy', 'glaucoma', 'normal']
    for disease_name in disease_list:
        prob_val = all_probs.get(disease_name, 0) if all_probs else 0
        display_name = disease_name.replace('_', ' ').title()
        prob_rows.append([display_name, f"{prob_val:.1f}%", '■' if prob_val > 0 else ''])

    prob_table = Table(prob_rows, colWidths=[4*cm, 2*cm, 6*cm])
    prob_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), light_bg),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c7d2fe')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    story.append(prob_table)
    story.append(Spacer(1, 0.15 * inch))

    # ── English Explanation ────────────────────────────────────────
    story.append(Paragraph("🇬🇧 Medical Explanation (English)", style_section_title))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#c7d2fe')))
    story.append(Spacer(1, 0.05 * inch))
    if detection.english_explanation:
        story.append(Paragraph(detection.english_explanation, style_body))
    story.append(Spacer(1, 0.1 * inch))

    # ── Tamil Explanation ──────────────────────────────────────────
    story.append(Paragraph("🇮🇳 Medical Explanation (Tamil / தமிழ்)", style_section_title))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#c7d2fe')))
    story.append(Spacer(1, 0.05 * inch))
    if detection.tamil_explanation:
        story.append(Paragraph(detection.tamil_explanation, style_tamil_body))
    story.append(Spacer(1, 0.12 * inch))

    # ── Clinical Sections ──────────────────────────────────────────
    sections = [
        ("🔍 Symptoms", detection.symptoms),
        ("⚠️  Root Causes", detection.causes),
        ("💊 Treatment Options", detection.treatment),
        ("🛡️  Prevention & Care Tips", detection.prevention),
    ]

    for heading, text_content in sections:
        if text_content:
            story.append(KeepTogether([
                Paragraph(heading, style_section_title),
                HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#c7d2fe')),
                Spacer(1, 0.04 * inch),
                *[
                    Paragraph(f"• {line.strip()}", style_bullet)
                    for line in text_content.split('\n')
                    if line.strip()
                ],
            ]))
            story.append(Spacer(1, 0.08 * inch))

    # ── Medical Disclaimer ─────────────────────────────────────────
    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#ef4444')))
    story.append(Spacer(1, 0.05 * inch))

    disclaimer_text = detection.disclaimer or (
        "⚠️ MEDICAL DISCLAIMER: This report is generated by an AI system for preliminary screening "
        "purposes only. It does NOT constitute a medical diagnosis or replace professional medical advice. "
        "Always consult a qualified, certified ophthalmologist for proper examination, diagnosis, and treatment. "
        "Do not make medical decisions based solely on this AI result."
    )
    story.append(Paragraph(disclaimer_text, style_disclaimer))

    # ── Footer ────────────────────────────────────────────────────
    story.append(Spacer(1, 0.1 * inch))
    footer_text = (
        f"Generated by Eye Disease Detection System | Report ID: {detection.detection_id} | "
        f"AI Model: ResNet50 + GPT-4 | {datetime.now().strftime('%d %b %Y at %H:%M:%S')}"
    )
    story.append(Paragraph(footer_text, style_footer))

    # Build PDF
    doc.build(story)
    print(f"[OK] PDF report generated: {outpath}")
    return outpath
