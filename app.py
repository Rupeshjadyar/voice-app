from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import asyncio
from datetime import datetime
import base64
import json
from upstash_redis import Redis
import tempfile
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ------------------ TTS Libraries Availability Flags ------------------
try:
    import edge_tts
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

# ------------------ Flask App Setup ------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ------------------ Redis (Upstash) Configuration ------------------
try:
    redis = Redis(
        url=os.getenv("KV_REST_API_URL"),
        token=os.getenv("KV_REST_API_TOKEN")
    )
    redis.ping()
    print("✅ Connected to Upstash Redis")
except Exception as e:
    print(f"❌ Redis Connection Error: {e}")
    redis = None

TEMP_FOLDER = tempfile.gettempdir()
os.makedirs(TEMP_FOLDER, exist_ok=True)

# ------------------ 15+ Languages with Multiple Voice Types ------------------
VOICE_MAPPING = {
    # English (US) - Multiple variants
    ('en-US', 'female-1'): 'en-US-AriaNeural',
    ('en-US', 'female-2'): 'en-US-JennyNeural',
    ('en-US', 'female-3'): 'en-US-SaraNeural',
    ('en-US', 'male-1'): 'en-US-GuyNeural',
    ('en-US', 'male-2'): 'en-US-RogerNeural',
    ('en-US', 'male-3'): 'en-US-SteffanNeural',
    ('en-US', 'young'): 'en-US-AshleyNeural',
    ('en-US', 'old'): 'en-US-JaneNeural',
    
    # English (UK)
    ('en-GB', 'female-1'): 'en-GB-SoniaNeural',
    ('en-GB', 'female-2'): 'en-GB-LibbyNeural',
    ('en-GB', 'male-1'): 'en-GB-RyanNeural',
    ('en-GB', 'male-2'): 'en-GB-AlfieNeural',
    
    # Hindi
    ('hi-IN', 'female-1'): 'hi-IN-SwaraNeural',
    ('hi-IN', 'female-2'): 'hi-IN-KavyaNeural',
    ('hi-IN', 'male-1'): 'hi-IN-MadhurNeural',
    ('hi-IN', 'male-2'): 'hi-IN-PrabhatNeural',
    
    # Spanish (Spain)
    ('es-ES', 'female-1'): 'es-ES-ElviraNeural',
    ('es-ES', 'female-2'): 'es-ES-AbrilNeural',
    ('es-ES', 'male-1'): 'es-ES-AlvaroNeural',
    ('es-ES', 'male-2'): 'es-ES-AlejandroNeural',
    
    # Spanish (Mexico)
    ('es-MX', 'female-1'): 'es-MX-DaliaNeural',
    ('es-MX', 'male-1'): 'es-MX-JorgeNeural',
    
    # French
    ('fr-FR', 'female-1'): 'fr-FR-DeniseNeural',
    ('fr-FR', 'female-2'): 'fr-FR-BrigitteNeural',
    ('fr-FR', 'male-1'): 'fr-FR-HenriNeural',
    ('fr-FR', 'male-2'): 'fr-FR-AlainNeural',
    
    # German
    ('de-DE', 'female-1'): 'de-DE-KatjaNeural',
    ('de-DE', 'female-2'): 'de-DE-ElkeNeural',
    ('de-DE', 'male-1'): 'de-DE-ConradNeural',
    ('de-DE', 'male-2'): 'de-DE-BerndNeural',
    
    # Japanese
    ('ja-JP', 'female-1'): 'ja-JP-NanamiNeural',
    ('ja-JP', 'female-2'): 'ja-JP-AyumiNeural',
    ('ja-JP', 'male-1'): 'ja-JP-KeitaNeural',
    ('ja-JP', 'male-2'): 'ja-JP-DaichiNeural',
    
    # Chinese (Mandarin)
    ('zh-CN', 'female-1'): 'zh-CN-XiaoxiaoNeural',
    ('zh-CN', 'female-2'): 'zh-CN-XiaoyiNeural',
    ('zh-CN', 'male-1'): 'zh-CN-YunxiNeural',
    ('zh-CN', 'male-2'): 'zh-CN-YunyangNeural',
    
    # Korean
    ('ko-KR', 'female-1'): 'ko-KR-SunHiNeural',
    ('ko-KR', 'female-2'): 'ko-KR-JiMinNeural',
    ('ko-KR', 'male-1'): 'ko-KR-InJoonNeural',
    
    # Russian
    ('ru-RU', 'female-1'): 'ru-RU-DariyaNeural',
    ('ru-RU', 'female-2'): 'ru-RU-SvetlanaNeural',
    ('ru-RU', 'male-1'): 'ru-RU-MikhailNeural',
    
    # Italian
    ('it-IT', 'female-1'): 'it-IT-ElsaNeural',
    ('it-IT', 'male-1'): 'it-IT-DiegoNeural',
    
    # Portuguese (Brazil)
    ('pt-BR', 'female-1'): 'pt-BR-FranciscaNeural',
    ('pt-BR', 'male-1'): 'pt-BR-AntonioNeural',
    
    # Arabic
    ('ar-SA', 'female-1'): 'ar-SA-ZariyahNeural',
    ('ar-SA', 'male-1'): 'ar-SA-HamedNeural',
    
    # Dutch
    ('nl-NL', 'female-1'): 'nl-NL-ColetteNeural',
    ('nl-NL', 'male-1'): 'nl-NL-MaartenNeural',
    
    # Swedish
    ('sv-SE', 'female-1'): 'sv-SE-HilleviNeural',
    ('sv-SE', 'male-1'): 'sv-SE-MattiasNeural',
    
    # Turkish
    ('tr-TR', 'female-1'): 'tr-TR-EmelNeural',
    ('tr-TR', 'male-1'): 'tr-TR-AhmetNeural',
    
    # Polish
    ('pl-PL', 'female-1'): 'pl-PL-ZofiaNeural',
    ('pl-PL', 'male-1'): 'pl-PL-MarekNeural',
    
    # Default Fallback
    ('default', 'default'): 'en-US-AriaNeural'
}

# Language display names
LANGUAGES = [
    {"code": "en-US", "name": "English (USA)", "flag": "🇺🇸"},
    {"code": "en-GB", "name": "English (UK)", "flag": "🇬🇧"},
    {"code": "hi-IN", "name": "Hindi (India)", "flag": "🇮🇳"},
    {"code": "es-ES", "name": "Spanish (Spain)", "flag": "🇪🇸"},
    {"code": "es-MX", "name": "Spanish (Mexico)", "flag": "🇲🇽"},
    {"code": "fr-FR", "name": "French (France)", "flag": "🇫🇷"},
    {"code": "de-DE", "name": "German (Germany)", "flag": "🇩🇪"},
    {"code": "ja-JP", "name": "Japanese (Japan)", "flag": "🇯🇵"},
    {"code": "zh-CN", "name": "Chinese (Mandarin)", "flag": "🇨🇳"},
    {"code": "ko-KR", "name": "Korean (South Korea)", "flag": "🇰🇷"},
    {"code": "ru-RU", "name": "Russian (Russia)", "flag": "🇷🇺"},
    {"code": "it-IT", "name": "Italian (Italy)", "flag": "🇮🇹"},
    {"code": "pt-BR", "name": "Portuguese (Brazil)", "flag": "🇧🇷"},
    {"code": "ar-SA", "name": "Arabic (Saudi Arabia)", "flag": "🇸🇦"},
    {"code": "nl-NL", "name": "Dutch (Netherlands)", "flag": "🇳🇱"},
    {"code": "sv-SE", "name": "Swedish (Sweden)", "flag": "🇸🇪"},
    {"code": "tr-TR", "name": "Turkish (Turkey)", "flag": "🇹🇷"},
    {"code": "pl-PL", "name": "Polish (Poland)", "flag": "🇵🇱"},
]

# Voice types with descriptions
VOICE_TYPES = [
    {"id": "female-1", "name": "Female 1 (Natural)", "icon": "👩"},
    {"id": "female-2", "name": "Female 2 (Soft)", "icon": "👩‍🦰"},
    {"id": "female-3", "name": "Female 3 (Professional)", "icon": "👩‍💼"},
    {"id": "male-1", "name": "Male 1 (Deep)", "icon": "👨"},
    {"id": "male-2", "name": "Male 2 (Friendly)", "icon": "👨‍🦰"},
    {"id": "male-3", "name": "Male 3 (Authoritative)", "icon": "👨‍💼"},
    {"id": "young", "name": "Young Voice", "icon": "🧒"},
    {"id": "old", "name": "Mature Voice", "icon": "🧓"},
]

# ------------------ Routes ------------------
@app.route('/')
def home():
    return render_template('index.html', languages=LANGUAGES, voice_types=VOICE_TYPES)

@app.route('/api/languages')
def get_languages():
    return jsonify(LANGUAGES)

@app.route('/api/voice-types')
def get_voice_types():
    return jsonify(VOICE_TYPES)

@app.route('/stats')
def stats():
    total = 0
    today = 0
    popular_langs = []
    
    if redis:
        try:
            total = int(redis.get("total_translations") or 0)
            today_key = f"count_{datetime.now().strftime('%Y-%m-%d')}"
            today = int(redis.get(today_key) or 0)
            
            # Get popular languages
            popular_langs = redis.zrevrange("popular_languages", 0, 4, withscores=True)
            print(f"📊 Stats - Total: {total}, Today: {today}")
        except Exception as e:
            logging.error(f"Redis stats error: {e}")
    
    return jsonify({
        "total": total, 
        "today": today,
        "popular_languages": popular_langs
    })

@app.route('/convert', methods=['POST'])
def convert():
    if not EDGE_AVAILABLE and not GTTS_AVAILABLE and not PYTTSX3_AVAILABLE:
        return jsonify({'error': 'No TTS library installed. Please install edge-tts, gtts, or pyttsx3.'}), 500

    try:
        text = request.form.get('text', '').strip()
        lang = request.form.get('language', 'en-US')
        voice_type = request.form.get('voice_type', 'female-1')
        
        # Advanced parameters
        rate = request.form.get('rate', '0')
        pitch = request.form.get('pitch', '0')
        volume = request.form.get('volume', '100')
        style = request.form.get('style', 'general')
        emotion = request.form.get('emotion', 'neutral')
        format_type = request.form.get('format', 'mp3')
        quality = request.form.get('quality', 'high')

        if not text:
            return jsonify({'error': 'Please enter text to convert'}), 400
        
        # Log request
        logging.info(f"TTS Request: lang={lang}, voice={voice_type}, text length={len(text)}")
        
        # Voice selection logic
        voice_key = (lang, voice_type)
        voice = VOICE_MAPPING.get(voice_key)
        
        if not voice:
            # Try with just language and base type
            base_type = voice_type.split('-')[0] if '-' in voice_type else voice_type
            voice = VOICE_MAPPING.get((lang, base_type))
            
        if not voice:
            voice = VOICE_MAPPING.get((lang, 'female-1'))
            
        if not voice:
            voice = "en-US-AriaNeural"
        
        filename = f"tts_{uuid.uuid4().hex}.{format_type}"
        filepath = os.path.join(TEMP_FOLDER, filename)
        success = False
        method_used = "none"

        # Try Edge TTS first (best quality)
        if EDGE_AVAILABLE:
            try:
                async def generate_edge():
                    # Convert rate format (edge-tts expects percentage or +/-)
                    rate_str = f"{rate}%" if rate != '0' else '+0%'
                    pitch_str = f"{pitch}Hz" if pitch != '0' else '0Hz'
                    
                    # Create communicate object with all parameters
                    communicate = edge_tts.Communicate(
                        text, 
                        voice,
                        rate=rate_str,
                        pitch=pitch_str,
                        volume=f"+{volume}%" if volume != '100' else '+0%'
                    )
                    
                    # Add style if supported
                    if style != 'general':
                        communicate = edge_tts.Communicate(
                            f"<mstts:express-as style='{style}'>{text}</mstts:express-as>",
                            voice
                        )
                    
                    await communicate.save(filepath)
                
                asyncio.run(generate_edge())
                if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                    success = True
                    method_used = "edge-tts"
                    logging.info(f"✅ Edge TTS successful: {filename}")
            except Exception as e:
                logging.error(f"Edge TTS Error: {e}")

        # Fallback to gTTS
        if not success and GTTS_AVAILABLE:
            try:
                tts = gTTS(text, lang=lang[:2], slow=(quality == 'low'))
                tts.save(filepath)
                if os.path.exists(filepath):
                    success = True
                    method_used = "gtts"
                    logging.info(f"✅ gTTS successful: {filename}")
            except Exception as e:
                logging.error(f"gTTS Error: {e}")

        # Final fallback to pyttsx3
        if not success and PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                engine.save_to_file(text, filepath)
                engine.runAndWait()
                if os.path.exists(filepath):
                    success = True
                    method_used = "pyttsx3"
                    logging.info(f"✅ pyttsx3 successful: {filename}")
            except Exception as e:
                logging.error(f"pyttsx3 Error: {e}")

        if not success or not os.path.exists(filepath):
            return jsonify({'error': 'Audio generation failed with all available methods'}), 500

        # Redis Update - FIXED: Removed pipeline, using direct commands
        if redis:
            try:
                redis.incr("total_translations")
                redis.incr(f"count_{datetime.now().strftime('%Y-%m-%d')}")
                redis.zincrby("popular_languages", 1, lang)
                
                # Debug print
                total_now = redis.get("total_translations")
                print(f"📈 Total Now: {total_now}")
            except Exception as e:
                logging.error(f"Redis update error: {e}")

        # Check if client wants base64 or file
        response_type = request.form.get('response_type', 'base64')
        
        if response_type == 'file':
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            # Send as base64
            with open(filepath, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Clean up
            try:
                os.remove(filepath)
            except:
                pass

            return jsonify({
                "success": True,
                "audio_data": f"data:audio/{format_type};base64,{audio_base64}",
                "filename": f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}",
                "method": method_used,
                "voice_used": voice,
                "format": format_type,
                "total_translations": total_now if redis else None
            })

    except Exception as e:
        logging.error(f"Conversion error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/preview-voice', methods=['POST'])
def preview_voice():
    """Preview a voice with a sample text"""
    try:
        lang = request.json.get('language', 'en-US')
        voice_type = request.json.get('voice_type', 'female-1')
        
        sample_texts = {
            'en-US': "Hello, this is a preview of my voice.",
            'hi-IN': "नमस्ते, यह मेरी आवाज़ का पूर्वावलोकन है।",
            'es-ES': "Hola, esta es una vista previa de mi voz.",
            'fr-FR': "Bonjour, voici un aperçu de ma voix.",
            'de-DE': "Hallo, dies ist eine Vorschau meiner Stimme.",
            'ja-JP': "こんにちは、これは私の声のプレビューです。",
            'zh-CN': "你好，这是我的声音预览。",
        }
        
        text = sample_texts.get(lang, "This is a voice preview.")
        
        # Get voice
        voice = VOICE_MAPPING.get((lang, voice_type), VOICE_MAPPING.get(('en-US', 'female-1')))
        
        if EDGE_AVAILABLE and voice:
            filename = f"preview_{uuid.uuid4().hex}.mp3"
            filepath = os.path.join(TEMP_FOLDER, filename)
            
            async def generate_preview():
                await edge_tts.Communicate(text, voice).save(filepath)
            
            asyncio.run(generate_preview())
            
            with open(filepath, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            os.remove(filepath)
            
            return jsonify({
                "success": True,
                "audio_data": f"data:audio/mp3;base64,{audio_base64}"
            })
        
        return jsonify({"success": False, "error": "Preview not available"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Test route to check Redis connection
@app.route('/test-redis')
def test_redis():
    if not redis:
        return jsonify({"status": "error", "message": "Redis not connected"})
    
    try:
        # Test increment
        redis.incr("test_counter")
        value = redis.get("test_counter")
        return jsonify({
            "status": "success", 
            "message": "Redis is working!",
            "test_counter": value
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)