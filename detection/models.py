from django.db import models
from django.utils import timezone
import uuid


def generate_patient_id():
    return 'PT' + uuid.uuid4().hex[:8].upper()


def generate_detection_id():
    return 'DT' + uuid.uuid4().hex[:8].upper()


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    patient_id = models.CharField(
        max_length=50, unique=True,
        default=generate_patient_id
    )
    name = models.CharField(max_length=200)
    age = models.IntegerField(default=0)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_id} – {self.name}"

    class Meta:
        ordering = ['-created_at']


class Detection(models.Model):
    SEVERITY_CHOICES = [
        ('MILD', 'Mild'),
        ('MODERATE', 'Moderate'),
        ('SEVERE', 'Severe'),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='detections'
    )
    detection_id = models.CharField(
        max_length=50, unique=True,
        default=generate_detection_id
    )
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    predicted_disease = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    english_explanation = models.TextField(blank=True)
    tamil_explanation = models.TextField(blank=True)
    symptoms = models.TextField(blank=True)
    causes = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    prevention = models.TextField(blank=True)
    disclaimer = models.TextField(blank=True)
    report_pdf = models.FileField(upload_to='reports/', null=True, blank=True)
    detection_date = models.DateTimeField(default=timezone.now)

    # Store all class probabilities as JSON-like string
    all_probabilities = models.TextField(blank=True, default='{}')

    def __str__(self):
        return f"{self.detection_id} – {self.predicted_disease}"

    def get_disease_display_name(self):
        return self.predicted_disease.replace('_', ' ').title()

    def get_severity_color(self):
        colors = {'MILD': '#16a34a', 'MODERATE': '#ea580c', 'SEVERE': '#dc2626'}
        return colors.get(self.severity, '#64748b')

    class Meta:
        ordering = ['-detection_date']


class ChatMessage(models.Model):
    session_id = models.CharField(max_length=100)
    message = models.TextField()
    response = models.TextField()
    language = models.CharField(max_length=5, default='en')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.language}] {self.session_id[:8]} — {self.message[:50]}"

    class Meta:
        ordering = ['timestamp']
