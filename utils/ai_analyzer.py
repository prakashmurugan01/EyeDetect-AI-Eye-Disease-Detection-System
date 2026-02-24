"""
AI Medical Analyzer — GPT-4 powered bilingual (English + Tamil) explanations.
Falls back to pre-written content if OpenAI is unavailable.
"""

FALLBACK_DATA = {
    'cataract': {
        'english': (
            "Cataract is a clouding of the eye's natural lens, causing blurry or hazy vision. "
            "It develops slowly over time and is the leading cause of reversible blindness worldwide. "
            "Surgery is highly effective and restores clear vision."
        ),
        'tamil': (
            "கண்புரை என்பது கண்ணின் இயற்கையான லென்ஸ் மேகமூட்டமடைவதால் "
            "மங்கலான அல்லது தெளிவற்ற பார்வை ஏற்படும் நிலை. "
            "இது மெதுவாக வளர்கிறது மற்றும் அறுவை சிகிச்சை மூலம் குணப்படுத்தலாம்."
        ),
        'symptoms': "Blurry or cloudy vision\nSensitivity to light and glare\nFaded or yellowed colors\nDouble vision in one eye\nFrequent changes in glasses prescription",
        'causes': "Natural aging process (most common)\nDiabetes and high blood sugar\nProlonged UV radiation exposure\nEye injuries or trauma\nLong-term steroid medication use",
        'treatment': "Cataract removal surgery (phacoemulsification)\nIntraocular lens (IOL) implantation\nRegular monitoring for early-stage cataracts\nUpdating glasses or contact lens prescription",
        'prevention': "Wear UV-protective sunglasses outdoors\nMaintain controlled blood sugar levels\nEat a diet rich in antioxidants (vitamins C and E)\nAvoid smoking and excessive alcohol\nSchedule regular eye examinations",
    },
    'diabetic_retinopathy': {
        'english': (
            "Diabetic retinopathy damages the blood vessels in the retina due to prolonged high blood sugar. "
            "It is a leading cause of vision loss in working-age adults. "
            "Early detection and blood sugar control are crucial to prevent blindness."
        ),
        'tamil': (
            "நீரிழிவு விழித்திரை நோய் என்பது நீண்டகால அதிக இரத்த சர்க்கரையால் "
            "விழித்திரையில் உள்ள இரத்த நாளங்கள் பாதிக்கப்படும் நிலை. "
            "சர்க்கரையை கட்டுப்படுத்துவது மிக முக்கியம்."
        ),
        'symptoms': "Floaters or dark spots in vision\nBlurred or fluctuating vision\nDark or empty areas in your field of vision\nDifficulty seeing colors clearly\nSudden vision loss in severe cases",
        'causes': "Prolonged uncontrolled diabetes (Type 1 or 2)\nHigh blood pressure (hypertension)\nHigh cholesterol levels\nPregnancy-related diabetes complications\nLong duration of diabetes without treatment",
        'treatment': "Laser photocoagulation therapy\nAnti-VEGF injections (Avastin, Lucentis)\nVitrectomy surgery for advanced cases\nStrict blood sugar and blood pressure control",
        'prevention': "Monitor and control blood glucose levels daily\nRegular diabetic eye exams (annually at minimum)\nControl blood pressure and cholesterol\nMaintain healthy weight and exercise regularly\nAvoid smoking completely",
    },
    'glaucoma': {
        'english': (
            "Glaucoma is a group of eye diseases that damage the optic nerve due to elevated intraocular pressure. "
            "Often called the 'silent thief of sight,' it progresses without symptoms until significant vision loss occurs. "
            "Early treatment can halt progression."
        ),
        'tamil': (
            "கண் அழுத்த நோய் என்பது கண்ணினுள் அதிகரித்த அழுத்தம் பார்வை நரம்பை "
            "பாதிக்கும் ஒரு கண் நோய். 'பார்வையின் அமைதியான திருடன்' என்று அழைக்கப்படுகிறது. "
            "ஆரம்பகால சிகிச்சை முக்கியம்."
        ),
        'symptoms': "Gradual loss of peripheral (side) vision\nTunnel vision in advanced stages\nSevere eye pain (acute angle-closure type)\nHeadache, nausea and vomiting (acute type)\nHalos around lights at night",
        'causes': "Elevated intraocular pressure (IOP)\nFamily history of glaucoma\nAge above 60 years\nThin cornea or optic nerve abnormality\nLong-term corticosteroid use",
        'treatment': "Eye drop medications to reduce eye pressure\nLaser trabeculoplasty\nGlaucoma filtration surgery (trabeculectomy)\nMinimally invasive glaucoma surgery (MIGS)\nRegular IOP monitoring",
        'prevention': "Regular comprehensive eye exams after age 40\nKnow your family eye health history\nExercise regularly to reduce eye pressure\nProtect eyes from injury\nTake prescribed eye drops consistently",
    },
    'normal': {
        'english': (
            "Your eye appears healthy with no signs of cataract, diabetic retinopathy, or glaucoma detected. "
            "Continue maintaining good eye health habits and schedule regular check-ups. "
            "Prevention is the best way to protect your vision for life."
        ),
        'tamil': (
            "உங்கள் கண் ஆரோக்கியமாக உள்ளது. கண்புரை, நீரிழிவு விழித்திரை நோய் "
            "அல்லது கண் அழுத்த நோயின் அறிகுறிகள் ஏதும் கண்டறியப்படவில்லை. "
            "தொடர்ந்து கண் பரிசோதனை செய்யவும்."
        ),
        'symptoms': "No disease symptoms detected\nVision appears to be within normal range\nEye structures look healthy\nNo abnormal pressure signs",
        'causes': "No pathological causes identified\nContinue preventive care\nMonitor any new vision changes\nMaintain healthy lifestyle habits",
        'treatment': "No treatment required at this time\nAnnual comprehensive eye examination\nUpdate corrective lenses if needed\nMaintain current healthy habits",
        'prevention': "Annual comprehensive eye exam\nWear UV-protective sunglasses outdoors\nEat a balanced diet rich in leafy greens and omega-3\nLimit screen time and follow 20-20-20 rule\nStay hydrated and exercise regularly",
    },
}

DISCLAIMER = (
    "⚠️ AI Screening Only: This result is generated by an artificial intelligence model "
    "and is intended for preliminary screening purposes only. It does NOT constitute a "
    "medical diagnosis. Please consult a qualified, certified ophthalmologist for proper "
    "examination, diagnosis, and treatment. Do not make medical decisions based solely on this result."
)


def analyze(disease: str, confidence: float) -> dict:
    """
    Generate bilingual medical analysis for the detected disease.
    Tries GPT-4 first, falls back to pre-written content.
    """
    if disease == 'normal':
        severity = 'MILD'
    elif confidence >= 85:
        severity = 'SEVERE'
    elif confidence >= 70:
        severity = 'MODERATE'
    else:
        severity = 'MILD'

    # Try OpenAI GPT-4
    try:
        from openai import OpenAI
        from django.conf import settings

        if not settings.OPENAI_API_KEY:
            raise ValueError("No API key")

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""You are an expert ophthalmologist creating a patient-friendly medical report.

Disease detected: {disease.replace('_', ' ').title()}
AI Confidence: {confidence:.1f}%
Severity: {severity}

Respond ONLY with a valid JSON object using these EXACT keys:
{{
  "english": "2-3 sentence clear patient-friendly explanation in English",
  "tamil": "Same explanation fully translated in Tamil script",
  "symptoms": "5 symptoms, one per line (no bullets/numbers)",
  "causes": "5 causes, one per line (no bullets/numbers)",
  "treatment": "4 treatment options, one per line",
  "prevention": "5 prevention tips, one per line",
  "disclaimer": "Standard medical disclaimer"
}}

Keep language simple for a general patient audience. Be accurate and compassionate.
"""

        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.4,
        )

        import json
        raw = resp.choices[0].message.content.strip()
        # Strip markdown code blocks if present
        raw = raw.replace('```json', '').replace('```', '').strip()
        data = json.loads(raw)
        data['severity'] = severity
        data.setdefault('disclaimer', DISCLAIMER)
        return data

    except Exception as e:
        print(f"OpenAI analysis error: {e} — using fallback")

    # Fallback to pre-written content
    fb = FALLBACK_DATA.get(disease, FALLBACK_DATA['normal'])
    return {
        'english': fb['english'],
        'tamil': fb['tamil'],
        'symptoms': fb['symptoms'],
        'causes': fb['causes'],
        'treatment': fb['treatment'],
        'prevention': fb['prevention'],
        'severity': severity,
        'disclaimer': DISCLAIMER,
    }
