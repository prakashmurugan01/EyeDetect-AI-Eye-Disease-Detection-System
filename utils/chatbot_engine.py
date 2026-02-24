"""
Dr. EyeBot - Smart Bilingual Eye Health Chatbot
Works with or without OpenAI API using intelligent fallback knowledge base
"""

from django.conf import settings
import re

# Comprehensive Eye Health Knowledge Base
KNOWLEDGE_BASE_EN = {
    'symptoms': {
        'keywords': ['symptom', 'sign', 'bleeding', 'vision', 'blur', 'floater', 'pain', 'itchy', 'red'],
        'responses': [
            "Common eye symptoms include blurred vision, eye pain, redness, floaters, and light sensitivity. "
            "If you experience sudden vision loss, severe pain, or bleeding, see an ophthalmologist immediately.",
            "Eye symptoms can indicate various conditions. Mild symptoms like dryness may respond to artificial tears, "
            "but persistent symptoms need professional evaluation."
        ]
    },
    'prevention': {
        'keywords': ['prevent', 'care', 'protect', 'health', 'maintain', 'keep'],
        'responses': [
            "Protect your eyes by: wearing UV-protective sunglasses, taking screen breaks every 20 minutes, "
            "eating antioxidant-rich foods, staying hydrated, and exercising regularly.",
            "Annual eye exams are crucial for early detection of diseases. Manage diabetes and blood pressure "
            "to prevent serious eye conditions."
        ]
    },
    'treatment': {
        'keywords': ['treat', 'cure', 'medicine', 'drop', 'surgery', 'laser', 'fix'],
        'responses': [
            "Eye treatments vary by condition: drops for dry eyes, surgery for cataracts, lasers for diabetic retinopathy. "
            "Always consult an ophthalmologist for proper diagnosis and treatment options.",
            "Modern treatments are highly effective. Early detection significantly improves outcomes. "
            "Don't delay seeking professional help."
        ]
    },
    'disease': {
        'keywords': ['disease', 'disorder', 'condition', 'problem', 'issue'],
        'responses': [
            "Major eye diseases include cataracts, glaucoma, diabetic retinopathy, and macular degeneration. "
            "Our AI screening helps detect these, but professional examination is essential for diagnosis.",
            "Many eye diseases are preventable or treatable when caught early. Regular checkups save vision."
        ]
    },
    'diagnostic': {
        'keywords': ['diagnose', 'detect', 'test', 'screen', 'scan', 'check'],
        'responses': [
            "Our eye disease detection system uses advanced AI for preliminary screening. "
            "Always confirm with a certified ophthalmologist for official diagnosis.",
            "Professional eye exams include vision tests, pressure measurements, and retinal imaging."
        ]
    },
    'doctor': {
        'keywords': ['doctor', 'doctor', 'specialist', 'ophthalmologist', 'optometrist', 'appointment'],
        'responses': [
            "For eye concerns, consult an ophthalmologist (medical doctor) rather than an optometrist. "
            "Ophthalmologists can diagnose and treat all eye diseases.",
            "Schedule regular eye exams, especially if you have diabetes, family history of eye disease, or are over 40."
        ]
    },
    'emergency': {
        'keywords': ['emergency', 'urgent', 'sudden', 'severe', 'acute', 'immediately'],
        'responses': [
            "EMERGENCY: Seek immediate care for sudden vision loss, severe eye pain, chemical splashes, "
            "or eye trauma. Go to the nearest emergency room.",
            "Don't wait for emergency situations. Regular checkups prevent most urgent eye conditions."
        ]
    },
    'general': {
        'keywords': [],
        'responses': [
            "Hello! I'm Dr. EyeBot, your AI eye health assistant. I can help with questions about eye diseases, "
            "prevention, and when to see a specialist. How can I help?",
            "Feel free to ask about eye symptoms, diseases, treatment options, or prevention tips. "
            "Remember to consult a professional ophthalmologist for diagnosis."
        ]
    }
}

KNOWLEDGE_BASE_TA = {
    'symptoms': {
        'keywords': ['அறிகுறி', 'கண்ணை', 'பார்வை', 'வலி', 'சிவப்பு', 'மங்கல்'],
        'responses': [
            "கண்ணின் பொதுவான அறிகுறிகள்: மங்கல் பார்வை, கண் வலி, சிவப்பு நிறம், மிதவும் புள்ளிகள், ஒளி உணர்வு. "
            "திடீர் பார்வை இழப்பு அல்லது கடுமையான வலி இருந்தால் உடனடியாக கண் மருத்துவரைப் பார்க்கவும்.",
            "கண் அறிகுறிகள் பல்வேறு நோய்களைக் குறிக்கும். சிறிய அறிகுறிகள் வீட்டு சிகிச்சையுடன் சரியாகலாம், "
            "ஆனால் நீடித்த அறிகுறிகளுக்கு தொழிலாதார மূல்யায়ன தேவை."
        ]
    },
    'prevention': {
        'keywords': ['தடுக்க', 'பராமரிப்பு', 'பாதுகாப்பு', 'ஆரோக்கியம்'],
        'responses': [
            "உங்கள் கண்களைப் பாதுகாக்க: UV பாதுகாப்பு கண்ணாடி அணிதல், 20 நிமிடங்களுக்கு பிறகு திரை இடைவெளி விடுதல், "
            "ஆக்ஸிஜனேற்றும் உணவு சாப்பிடுதல், நீர் குடிதல், உடற்பயிற்சி செய்தல்.",
            "ஆண்டுக்கு ஒரு முறை கண் பரிசோதனை மிக முக்கியம். நீரிழிவு மற்றும் உயர் இரத்த அழுத்தத்தைக் கட்டுப்படுத்தவும்."
        ]
    },
    'treatment': {
        'keywords': ['சிகிச்சை', 'மருந்து', 'வெட்டுதல்', 'சொட்டு'],
        'responses': [
            "கண் நோய்களின் சிகிச்சைகள் வெவ்வேறு: உலர் கண்களுக்கு சொட்டுகள், கண்புரைக்கு அறுவை சிகிச்சை, "
            "நீரிழிவு விழித்திரைக்கு லேசர். எப்போதும் கண் மருத்துவரை கலந்தாலோசிக்கவும்.",
            "நவீன சிகிச்சைகள் மிகவும் பயனுள்ளவை. ஆரம்பகালத் கண்டறிதல் சிறந்த முடிவுகளைக் கொடுக்கும்."
        ]
    },
    'disease': {
        'keywords': ['நோய்', 'கண் பிரச்சினை'],
        'responses': [
            "முக்கிய கண் நோய்கள்: கண்புரை, கண் அழுத்த நோய், நீரிழிவு விழித்திரை, மாக்குலர் சிதைவு. "
            "எங்கள் AI பாலை ஆரம்ப பரிசோதனை செய்கிறது, ஆனால் முறையான கண் மருத்துவரின் ஆலோசனை அவசியம்.",
            "பல கண் நோய்கள் தடுக்கக்கூடியவை அல்லது ஆரம்பத்திலேயே குணப்படுத்தக்கூடியவை."
        ]
    },
    'general': {
        'keywords': [],
        'responses': [
            "வணக்கம்! நான் டாக்டர் ஐ-பாட், உங்கள் AI கண் ஆரோக்கிய உதவியாளர். "
            "கண் நோய்கள், தடுப்பு, சிகிச்சை பற்றி கேட்கலாம். நன்றி!",
            "கண் அறிகுறிகள், நோய்கள், சிகிச்சை விருப்பங்கள் பற்றி கேளுங்கள். "
            "ஒரு தொழிலாளர் கண் மருத்துவரைக் கலந்தாலோசிக்க மறக்க வேண்டாம்."
        ]
    }
}


def get_smart_response(message, language='en'):
    """
    Get intelligent chatbot response using knowledge base.
    Matches keywords and returns contextual responses.
    """
    kb = KNOWLEDGE_BASE_TA if language == 'ta' else KNOWLEDGE_BASE_EN
    message_lower = message.lower()
    
    # Find matching category
    for category, data in kb.items():
        keywords = data.get('keywords', [])
        if keywords:
            if any(keyword in message_lower for keyword in keywords):
                import random
                return random.choice(data['responses'])
    
    # Default response
    import random
    return random.choice(kb['general']['responses'])


def get_openai_response(message, language='en', session_history=None):
    """
    Try to get response from OpenAI GPT-4.
    Returns None if API unavailable.
    """
    try:
        from openai import OpenAI
        
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == '':
            return None  # No API key configured
        
        client = OpenAI(api_key=api_key)
        
        lang_name = 'Tamil' if language == 'ta' else 'English'
        system_msg = (
            f"You are Dr. EyeBot, a friendly and expert ophthalmology assistant. "
            f"Answer ONLY eye health related questions. Be concise, warm, and practical. "
            f"Always recommend consulting a certified ophthalmologist for diagnosis. "
            f"Respond ENTIRELY in {lang_name}. "
            f"Keep responses under 150 words."
        )
        
        # Build message history
        messages = [{"role": "system", "content": system_msg}]
        if session_history:
            messages.extend(session_history)
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"[INFO] OpenAI API failed: {str(e)[:100]}")
        return None


def get_chatbot_response(message, language='en', session_history=None):
    """
    Main chatbot response function.
    Tries OpenAI first, falls back to knowledge base.
    """
    if not message or not message.strip():
        return "Please ask a question about eye health." if language == 'en' else "கண் ஆரோக்கியம் பற்றி கேட்கவும்."
    
    message = message.strip()
    
    # Try OpenAI first
    openai_response = get_openai_response(message, language, session_history)
    if openai_response:
        return openai_response
    
    # Fall back to knowledge base
    kb_response = get_smart_response(message, language)
    return kb_response
