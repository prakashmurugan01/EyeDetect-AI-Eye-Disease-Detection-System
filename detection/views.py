from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.db.models import Count
import json
import uuid
import os

from .models import Patient, Detection, ChatMessage


# ── Lazy load utilities to avoid startup crash if TF not installed ──────────

def get_predictor():
    from utils.predictor import predictor
    return predictor


def get_analyzer():
    from utils.ai_analyzer import analyze
    return analyze


def generate_report(detection):
    try:
        from utils.pdf_generator import generate_pdf
        return generate_pdf(detection)
    except Exception as e:
        print(f"PDF generation error: {e}")
        return None


# ── VIEWS ───────────────────────────────────────────────────────────────────

def home(request):
    total_patients = Patient.objects.count()
    total_detections = Detection.objects.count()

    # Disease distribution for hero stats
    disease_stats = (
        Detection.objects
        .values('predicted_disease')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    context = {
        'total_patients': total_patients,
        'total_detections': total_detections,
        'disease_stats': list(disease_stats),
    }
    return render(request, 'home.html', context)


def upload(request):
    if request.method == 'POST':
        eye_image = request.FILES.get('eye_image')
        if not eye_image:
            return render(request, 'upload.html', {'error': 'Please upload an eye image.'})

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
        if eye_image.content_type not in allowed_types:
            return render(request, 'upload.html', {
                'error': 'Invalid file type. Please upload JPG, PNG, or WEBP.'
            })

        # Patient info
        name = request.POST.get('patient_name', 'Anonymous').strip() or 'Anonymous'
        age = int(request.POST.get('patient_age', 0) or 0)
        gender = request.POST.get('patient_gender', 'O')
        phone = request.POST.get('patient_phone', '').strip()

        # Save image
        ext = os.path.splitext(eye_image.name)[1].lower() or '.jpg'
        filename = f'uploads/{uuid.uuid4().hex}{ext}'
        path = default_storage.save(filename, eye_image)
        full_path = default_storage.path(path)

        # Run prediction
        predictor = get_predictor()
        pred = predictor.predict(full_path)

        # Run AI analysis
        analyze = get_analyzer()
        info = analyze(pred['disease'], pred['confidence'])

        # Get or create patient
        patient, _ = Patient.objects.get_or_create(
            name=name,
            defaults={'age': age, 'gender': gender, 'phone': phone}
        )
        if patient.age == 0 and age > 0:
            patient.age = age
            patient.save()

        # Create detection record
        det = Detection.objects.create(
            patient=patient,
            image=path,
            predicted_disease=pred['disease'],
            confidence_score=pred['confidence'],
            severity=pred['severity'],
            english_explanation=info.get('english', ''),
            tamil_explanation=info.get('tamil', ''),
            symptoms=info.get('symptoms', ''),
            causes=info.get('causes', ''),
            treatment=info.get('treatment', ''),
            prevention=info.get('prevention', ''),
            disclaimer=info.get('disclaimer', ''),
            all_probabilities=json.dumps(pred.get('all_probs', {})),
        )

        # Generate PDF report
        pdf_path = generate_report(det)
        if pdf_path:
            det.report_pdf = pdf_path.replace(str(default_storage.location) + '/', '')
            det.save()

        return redirect('result', detection_id=det.detection_id)

    return render(request, 'upload.html')


def result(request, detection_id):
    det = get_object_or_404(Detection, detection_id=detection_id)

    # Parse all probabilities
    try:
        all_probs = json.loads(det.all_probabilities) if det.all_probabilities else {}
    except Exception:
        all_probs = {}

    # Format symptoms / causes / treatment / prevention as lists
    def to_list(text):
        if not text:
            return []
        lines = [l.strip().lstrip('•-*').strip() for l in text.split('\n') if l.strip()]
        return lines

    context = {
        'det': det,
        'all_probs': all_probs,
        'symptoms_list': to_list(det.symptoms),
        'causes_list': to_list(det.causes),
        'treatment_list': to_list(det.treatment),
        'prevention_list': to_list(det.prevention),
        'disease_name': det.predicted_disease.replace('_', ' ').title(),
    }
    return render(request, 'result.html', context)


def download_pdf(request, detection_id):
    det = get_object_or_404(Detection, detection_id=detection_id)
    if det.report_pdf:
        filepath = default_storage.path(str(det.report_pdf))
        if os.path.exists(filepath):
            response = FileResponse(
                open(filepath, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = (
                f'attachment; filename="eye_report_{det.detection_id}.pdf"'
            )
            return response

    # If no PDF, regenerate
    pdf_path = generate_report(det)
    if pdf_path and os.path.exists(pdf_path):
        response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="eye_report_{det.detection_id}.pdf"'
        )
        return response

    raise Http404("Report not available.")


def webcam(request):
    return render(request, 'webcam.html')


@csrf_exempt
def webcam_predict(request):
    """API endpoint for webcam snapshot prediction."""
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'error': 'No image provided'}, status=400)

        filename = f'uploads/webcam_{uuid.uuid4().hex}.jpg'
        path = default_storage.save(filename, image_file)
        full_path = default_storage.path(path)

        predictor = get_predictor()
        pred = predictor.predict(full_path)

        return JsonResponse({
            'disease': pred['disease'],
            'disease_name': pred['disease'].replace('_', ' ').title(),
            'confidence': pred['confidence'],
            'severity': pred['severity'],
            'all_probs': pred.get('all_probs', {}),
        })
    return JsonResponse({'error': 'POST only'}, status=405)


def chatbot(request):
    return render(request, 'chatbot.html')


@csrf_exempt
def chat_api(request):
    """API endpoint for the bilingual eye health chatbot."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    message = data.get('message', '').strip()
    lang = data.get('language', 'en')
    session_id = data.get('session_id', str(uuid.uuid4()))

    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Premium real-time chatbot engine handles history internally

    # Use premium real-time chatbot engine (OpenAI with fallback to knowledge base)
    try:
        from utils.realtime_chatbot import get_realtime_response
        answer = get_realtime_response(message, language=lang, session_id=session_id)
    except Exception as e:
        print(f"[ERROR] Realtime chatbot engine error: {e}")
        # Ultimate fallback
        if lang == 'ta':
            answer = ("தொடர்ந்து ஆரோக்கியமாக இருக்க, ஒரு கண் மருத்துவரைப் பார்க்கவும். "
                      "உங்கள் கேள்விக்கு நன்றி!")
        else:
            answer = ("Thank you for your question. Please consult a certified ophthalmologist "
                      "for professional medical advice and diagnosis.")

    return JsonResponse({'response': answer, 'session_id': session_id})


def dashboard(request):
    total = Detection.objects.count()
    patients_total = Patient.objects.count()

    # Disease distribution
    disease_stats = list(
        Detection.objects
        .values('predicted_disease')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Severity distribution
    severity_stats = list(
        Detection.objects
        .values('severity')
        .annotate(count=Count('id'))
    )

    # Recent detections
    recent = Detection.objects.select_related('patient').all()[:15]

    # Monthly trend (last 6 months)
    from django.utils import timezone
    from datetime import timedelta
    import json as _json

    six_months_ago = timezone.now() - timedelta(days=180)
    monthly = {}
    detections_range = Detection.objects.filter(detection_date__gte=six_months_ago)
    for d in detections_range:
        key = d.detection_date.strftime('%b %Y')
        monthly[key] = monthly.get(key, 0) + 1

    context = {
        'total': total,
        'patients_total': patients_total,
        'disease_stats': disease_stats,
        'severity_stats': severity_stats,
        'recent': recent,
        'monthly_json': _json.dumps(monthly),
        'disease_json': _json.dumps({
            d['predicted_disease'].replace('_', ' ').title(): d['count']
            for d in disease_stats
        }),
    }
    return render(request, 'dashboard.html', context)


def history(request):
    """All detections list."""
    detections = Detection.objects.select_related('patient').all()
    return render(request, 'history.html', {'detections': detections})
