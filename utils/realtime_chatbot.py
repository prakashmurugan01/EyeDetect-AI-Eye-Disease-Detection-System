"""
Dr. EyeBot - Premium Real-Time Chatbot Engine
Advanced conversational AI with streaming support and human-like responses
"""

from django.conf import settings
import re
import random
import json
from datetime import datetime

# ==================== ENHANCED KNOWLEDGE BASE ====================

MEDICAL_KNOWLEDGE = {
    'cataract': {
        'en': {
            'definition': 'A clouding of the eye\'s natural lens',
            'symptoms': ['Blurry vision', 'Difficulty seeing at night', 'Faded colors', 'Glare sensitivity', 'Double vision'],
            'causes': ['Age (most common)', 'Diabetes', 'UV exposure', 'Eye injury', 'Certain medications'],
            'treatment': ['Early: stronger glasses or contacts', 'Advanced: surgical removal with IOL implant', 'Laser-assisted surgery'],
            'prevention': ['UV-protective sunglasses', 'Healthy diet (vitamins C, E)', 'Don\'t smoke', 'Control diabetes', 'Regular eye exams'],
            'urgency': 'moderate'
        },
        'ta': {
            'definition': 'கண்ணின் இயற்கையான லென்ஸ் மேகமூட்டல்',
            'symptoms': ['மங்கல் பார்வை', 'இரவில் பார்க்க சிரமம்', 'நிறங்கள் மங்கலாதல்', 'ஒளி உணர்வு', 'இரட்டை பார்வை'],
            'causes': ['வயது (பொதுவான)', 'நீரிழிவு', 'UV வெளிப்பாடு', 'கண் காயம்', 'சில மருந்துகள்'],
            'treatment': ['ஆரம்பம்: வலுவான கண்ணாடி', 'முன்னேறிய: அறுவை சிகிச்சை', 'லேசர் வெட்டு'],
            'prevention': ['UV பாதுகாப்பு சிப்பணை', 'ஆரோக்கியமான உணவு', 'புகைபிடிக்க வேண்டாம்', 'நீரிழிவு கட்டுப்பாடு'],
            'urgency': 'moderate'
        }
    },
    'glaucoma': {
        'en': {
            'definition': 'A group of diseases damaging the optic nerve (the "silent thief of sight")',
            'symptoms': ['Slow peripheral vision loss', 'Tunnel vision in advanced stages', 'Eye pain (acute types)', 'Halos around lights', 'Often no early symptoms'],
            'causes': ['Elevated eye pressure (IOP)', 'Family history', 'Age over 60', 'Thin cornea', 'Long-term steroid use'],
            'treatment': ['Eye drops to lower pressure', 'Laser treatments', 'Glaucoma surgery', 'IOP monitoring'],
            'prevention': ['Annual eye exams after 40', 'Know family history', 'Exercise regularly', 'Take medications as prescribed', 'Manage stress'],
            'urgency': 'high'
        },
        'ta': {
            'definition': 'பார்வை நரம்பை சேதப்படுத்தும் நோய்கள் ("பார்வையின் அமைதியான திருடன்")',
            'symptoms': ['சுற்றுப்புற பார்வை இழப்பு', 'சுரங்க பார்வை', 'கண் வலி', 'ஒளி நிழல்', 'பெரும்பாலும் அறிகுறி இல்லை'],
            'causes': ['உயர் கண் அழுத்தம்', 'குடும்ப வரலாறு', '60 வயதுக்கு மேல்', 'மெல்லிய கொர்னியா', 'கார்டிகோஸ்டீராய்டு'],
            'treatment': ['கண் சொட்டுகள்', 'லேசர் சிகிச்சை', 'அறுவை சிகிச்சை', 'அழுத்த கண்காணிப்பு'],
            'prevention': ['40 வயதுக்குப் பிறகு ஆண்டு பரிசோதனை', 'குடும்ப வரலாறு அறிதல்', 'வழக்கமான உடற்பயிற்சி'],
            'urgency': 'high'
        }
    },
    'diabetic_retinopathy': {
        'en': {
            'definition': 'Eye damage caused by high blood sugar from diabetes',
            'symptoms': ['Floaters', 'Blurred vision', 'Dark spots', 'Vision loss', 'Sudden flashes of light'],
            'causes': ['Uncontrolled diabetes', 'High blood pressure', 'High cholesterol', 'Pregnancy complications', 'Long diabetes duration'],
            'treatment': ['Blood sugar control', 'Anti-VEGF injections', 'Laser therapy', 'Vitrectomy surgery'],
            'prevention': ['Control blood sugar daily', 'Annual diabetes eye exams', 'Control blood pressure', 'Exercise', 'Quit smoking'],
            'urgency': 'high'
        },
        'ta': {
            'definition': 'நீரிழிவு காரணமாக கண் சேதம்',
            'symptoms': ['மிதவும் புள்ளிகள்', 'மங்கல் பார்வை', 'கரும் புள்ளிகள்', 'பார்வை இழப்பு', 'ஒளி ஆவேசம்'],
            'causes': ['கட்டுப்படுத்தப்படாத நீரிழிவு', 'உயர் இரத்த அழுத்தம்', 'உயர் கொலஸ்ட்রால்', 'கர்ப்ப சிக்கல்', 'நீண்ட நீரிழிவு'],
            'treatment': ['இரத்த சர்க்கரை கட்டுப்பாடு', 'ஆண்டி-வெஜிஎஃப் ஊசி', 'லேசர் சிகிச்சை', 'வைট்ரெக்டமி'],
            'prevention': ['தினசரி சர்க்கரை கட்டுப்பாடு', 'ஆண்டு கண் பரிசோதனை'],
            'urgency': 'high'
        }
    },
    'normal': {
        'en': {
            'definition': 'Your eyes appear healthy with no major diseases detected',
            'symptoms': ['No concerning symptoms detected', 'Vision appears normal', 'Eye structures healthy'],
            'causes': ['Good eye health', 'Preventive care working', 'Healthy lifestyle'],
            'treatment': ['Continue current habits', 'Annual checkups', 'UV protection'],
            'prevention': ['Maintain healthy diet', 'Regular exercise', 'Protect from UV', 'Screen breaks: 20-20-20 rule', 'Annual checkups'],
            'urgency': 'low'
        },
        'ta': {
            'definition': 'உங்கள் கண்கள் ஆரோக்கியமாக உள்ளன',
            'symptoms': ['பிரச்சினையான அறிகுறி இல்லை', 'நார்மल் பார்வை', 'ஆரோக்கியமான கண் கட்டமைப்பு'],
            'causes': ['நல்ல கண் ஆரோக்கியம்', 'தடுப்பு பராமரிப்பு', 'ஆரோக்கியமான வாழ்க்கை'],
            'treatment': ['தற்போதைய பழக்கங்களைத் தொடரவும்', 'ஆண்டு பரிசோதனைகள்'],
            'prevention': ['ஆரோக்கியமான உணவு', 'வழக்கமான உடற்பயிற்சி', 'UV பாதுகாப்பு'],
            'urgency': 'low'
        }
    }
}

# ==================== CONVERSATIONAL PATTERNS ====================

CONVERSATIONAL_STARTERS = {
    'en': [
        "Great question! Let me help you with that.",
        "I'm glad you asked about this. Here's what you should know:",
        "That's an important question. Let me explain:",
        "Perfect timing! This is something many people wonder about.",
        "I can definitely help you with that important concern.",
    ],
    'ta': [
        "நல்ல கேள்வி! உங்களுக்கு உதவ என்னை விடுங்கள்.",
        "இதைப் பற்றி கேட்கக் கொடுத்தீர்கள். இதோ தெளிவாக:",
        "அது முக்கியமான கேள்வி. விளக்க விரும்புகிறேன்:",
        "பலர் இதைப் பற்றி ஆச்சர்யப்பட்டுள்ளனர்.",
        "இந்த முக்கியமான கவலையுடன் நிச்சயமாக உதவ முடியும்.",
    ]
}

CONVERSATIONAL_TRANSITIONS = {
    'en': [
        "Let me break this down into key points:",
        "Here's the most important thing to know:",
        "The key takeaway here is:",
        "Most importantly,",
        "Here's what you should focus on:",
    ],
    'ta': [
        "இதை முக்கிய புள்ளிகளாக பிரிக்கிறேன்:",
        "நீங்கள் அறிய வேண்டிய முக்கியமான விஷயம்:",
        "இதன் முக்கிய வாங்குவது:",
        "மிகவும் முக்கியமாக,",
    ]
}

PROFESSIONAL_CLOSING = {
    'en': [
        "Please consult an ophthalmologist for professional diagnosis and personalized treatment.",
        "For the best outcome, see a certified eye specialist who can examine you directly.",
        "Remember: early detection saves vision. Schedule regular eye exams.",
        "Don't delay professional care—your vision is worth it!",
        "A qualified ophthalmologist can provide the best guidance for your specific situation.",
    ],
    'ta': [
        "தயவுசெய்து ஒரு கண் மருத்துவரைப் பார்க்கவும்.",
        "சிறந்த முடிவுக்கு, ஒரு நிபுணரை கலந்தாலோசிக்கவும்.",
        "ஆரம்பகால கண்டறிதல் பார்வை காக்கும்.",
        "தாமதமாக வேண்டாம்—உங்கள் பார்வை முக்கியம்!",
    ]
}

# ==================== REAL-TIME RESPONSE GENERATOR ====================

def get_premium_response(message, language='en', session_history=None):
    """
    Generate premium, human-like real-time responses using multiple strategies:
    1. OpenAI API for optimal quality
    2. Keyword matching with contextual awareness
    3. Conversation history integration
    """
    
    if not message or not message.strip():
        return "I'm here to help! Ask me anything about eye health. What's on your mind?"
    
    message = message.strip()
    
    # Try OpenAI first for best quality
    openai_response = try_openai_streaming(message, language, session_history)
    if openai_response:
        return openai_response
    
    # Fall back to premium knowledge base response
    return generate_premium_kb_response(message, language, session_history)


def try_openai_streaming(message, language='en', session_history=None):
    """
    Try to get response from OpenAI with streaming support
    Returns None if API unavailable
    """
    try:
        import openai
        
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == '':
            return None
        
        # Set API key for openai library
        openai.api_key = api_key
        
        # Premium system prompt for human-like responses
        system_prompt = """You are Dr. EyeBot, a warm, empathetic, and highly knowledgeable eye health assistant.
        
Your personality:
- Friendly and conversational (not robotic)
- Empathetic to patient concerns
- Clear and easy to understand
- Professional but approachable
- Proactive in asking clarifying questions
- Always recommend professional consultation

Guidelines:
- Provide accurate medical information
- Be concise but comprehensive
- Use simple language
- Acknowledge patient concerns
- Suggest next steps
- Always emphasize consulting an ophthalmologist
- Respond entirely in the user's language

Format:
1. Acknowledge the question warmly
2. Provide key information
3. Explain what they should do
4. Recommend professional follow-up"""
        
        # Build conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        if session_history:
            messages.extend(session_history[-4:])  # Last 4 messages for context
        
        messages.append({"role": "user", "content": message})
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7,
            top_p=0.95
        )
        
        return response.choices[0]['message']['content']
        
    except Exception as e:
        print(f"[OpenAI API] Backup to knowledge base: {str(e)[:50]}")
        return None


def generate_premium_kb_response(message, language='en', session_history=None):
    """
    Generate high-quality responses using enhanced knowledge base
    """
    
    message_lower = message.lower()
    lang = language
    
    # Detect disease keywords
    disease_keywords = {
        'cataract': ['cataract', 'cloudy', 'blur', 'lens', 'cloud', 'hazy'],
        'glaucoma': ['glaucoma', 'pressure', 'optic nerve', 'peripheral', 'silent thief'],
        'diabetic_retinopathy': ['diabetes', 'diabetic', 'retina', 'retinopathy', 'floaters'],
    }
    
    detected_disease = None
    for disease, keywords in disease_keywords.items():
        if any(kw in message_lower for kw in keywords):
            detected_disease = disease
            break
    
    # Build response
    response = ""
    
    # Add conversational starter
    starter = random.choice(CONVERSATIONAL_STARTERS.get(lang, CONVERSATIONAL_STARTERS['en']))
    response += starter + "\n\n"
    
    # Provide disease information if detected
    if detected_disease and detected_disease in MEDICAL_KNOWLEDGE:
        kb = MEDICAL_KNOWLEDGE[detected_disease][lang]
        
        response += f"**About {detected_disease.replace('_', ' ').title()}:**\n"
        response += f"{kb['definition']}\n\n"
        
        # Add relevant symptoms
        response += "**Common Symptoms:**\n"
        for i, symptom in enumerate(kb['symptoms'][:3], 1):
            response += f"• {symptom}\n"
        response += "\n"
        
        # Add treatment/prevention
        response += "**What You Should Do:**\n"
        response += "• Monitor your symptoms closely\n"
        response += "• Don't delay professional care\n"
        response += "• Early detection makes a huge difference\n\n"
    
    # Add general helpful advice
    else:
        response += "**Here's what's most important:**\n"
        response += "• Regular eye exams are crucial\n"
        response += "• Early detection saves vision\n"
        response += "• Professional consultation is essential\n\n"
    
    # Add professional closing
    closing = random.choice(PROFESSIONAL_CLOSING.get(lang, PROFESSIONAL_CLOSING['en']))
    response += f"**Next Steps:**\n{closing}"
    
    return response


# ==================== SESSION MANAGEMENT ====================

def get_session_context(session_id):
    """
    Get conversation context for multi-turn interactions
    """
    from detection.models import ChatMessage
    
    messages = ChatMessage.objects.filter(
        session_id=session_id
    ).order_by('timestamp')[:10]
    
    context = []
    for msg in messages:
        context.append({"role": "user", "content": msg.message})
        context.append({"role": "assistant", "content": msg.response})
    
    return context


def save_chat_message(session_id, message, response, language='en'):
    """
    Save conversation to database
    """
    from detection.models import ChatMessage
    
    ChatMessage.objects.create(
        session_id=session_id,
        message=message,
        response=response,
        language=language
    )


# ==================== REAL-TIME API ====================

def get_realtime_response(message, language='en', session_id=None):
    """
    Main entry point for real-time chatbot responses
    """
    
    # Get session context
    session_history = None
    if session_id:
        session_history = get_session_context(session_id)
    
    # Generate premium response
    response = get_premium_response(message, language, session_history)
    
    # Save to database if session exists
    if session_id:
        save_chat_message(session_id, message, response, language)
    
    return response
