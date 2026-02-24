from django.contrib import admin
from .models import Patient, Detection, ChatMessage


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'name', 'age', 'gender', 'phone', 'created_at']
    search_fields = ['name', 'patient_id', 'phone']
    list_filter = ['gender', 'created_at']
    readonly_fields = ['patient_id', 'created_at']


@admin.register(Detection)
class DetectionAdmin(admin.ModelAdmin):
    list_display = ['detection_id', 'patient', 'predicted_disease',
                    'confidence_score', 'severity', 'detection_date']
    search_fields = ['detection_id', 'patient__name', 'predicted_disease']
    list_filter = ['predicted_disease', 'severity', 'detection_date']
    readonly_fields = ['detection_id', 'detection_date']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'language', 'message', 'timestamp']
    list_filter = ['language', 'timestamp']
    search_fields = ['session_id', 'message']
