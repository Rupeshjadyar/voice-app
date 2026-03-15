from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import uuid
import asyncio
from datetime import datetime
import base64
import json
import tempfile
import logging
from dotenv import load_dotenv

load_dotenv()

# ------------------ TTS Libraries ------------------
try:
    import edge_tts
    EDGE_AVAILABLE = True
    print("✅ edge-tts available")
except ImportError:
    EDGE_AVAILABLE = False
    print("❌ edge-tts not available")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
    print("✅ gTTS available")
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
    print("✅ pyttsx3 available")
except ImportError:
    PYTTSX3_AVAILABLE = False

# ------------------ Redis ------------------
try:
    from upstash_redis import Redis
    redis = Redis(
        url=os.getenv("KV_REST_API_URL"),
        token=os.getenv("KV_REST_API_TOKEN")
    )
    redis.ping()
    REDIS_AVAILABLE = True
    print("✅ Connected to Upstash Redis")
except Exception as e:
    print(f"❌ Redis not available: {e}")
    redis = None
    REDIS_AVAILABLE = False

# ------------------ Flask App ------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TEMP_FOLDER = tempfile.gettempdir()
os.makedirs(TEMP_FOLDER, exist_ok=True)

# ------------------ Voice Mapping (language, voice_type) -> edge-tts voice name ------------------
VOICE_MAPPING = {
    # English USA
    ('en-US', 'female-1'): 'en-US-AriaNeural',
    ('en-US', 'female-2'): 'en-US-JennyNeural',
    ('en-US', 'female-3'): 'en-US-SaraNeural',
    ('en-US', 'male-1'):   'en-US-GuyNeural',
    ('en-US', 'male-2'):   'en-US-RogerNeural',
    ('en-US', 'male-3'):   'en-US-SteffanNeural',
    ('en-US', 'young'):    'en-US-AshleyNeural',
    ('en-US', 'old'):      'en-US-JaneNeural',

    # English UK
    ('en-GB', 'female-1'): 'en-GB-SoniaNeural',
    ('en-GB', 'female-2'): 'en-GB-LibbyNeural',
    ('en-GB', 'female-3'): 'en-GB-MaisieNeural',
    ('en-GB', 'male-1'):   'en-GB-RyanNeural',
    ('en-GB', 'male-2'):   'en-GB-AlfieNeural',
    ('en-GB', 'male-3'):   'en-GB-OliverNeural',
    ('en-GB', 'young'):    'en-GB-MaisieNeural',
    ('en-GB', 'old'):      'en-GB-SoniaNeural',

    # Hindi
    ('hi-IN', 'female-1'): 'hi-IN-SwaraNeural',
    ('hi-IN', 'female-2'): 'hi-IN-AnanyaNeural',
    ('hi-IN', 'female-3'): 'hi-IN-SwaraNeural',
    ('hi-IN', 'male-1'):   'hi-IN-MadhurNeural',
    ('hi-IN', 'male-2'):   'hi-IN-PrabhatNeural',
    ('hi-IN', 'male-3'):   'hi-IN-MadhurNeural',
    ('hi-IN', 'young'):    'hi-IN-AnanyaNeural',
    ('hi-IN', 'old'):      'hi-IN-MadhurNeural',

    # Spanish Spain
    ('es-ES', 'female-1'): 'es-ES-ElviraNeural',
    ('es-ES', 'female-2'): 'es-ES-AbrilNeural',
    ('es-ES', 'female-3'): 'es-ES-IreneNeural',
    ('es-ES', 'male-1'):   'es-ES-AlvaroNeural',
    ('es-ES', 'male-2'):   'es-ES-AlejandroNeural',
    ('es-ES', 'male-3'):   'es-ES-GerardoNeural',
    ('es-ES', 'young'):    'es-ES-AbrilNeural',
    ('es-ES', 'old'):      'es-ES-ElviraNeural',

    # Spanish Mexico
    ('es-MX', 'female-1'): 'es-MX-DaliaNeural',
    ('es-MX', 'female-2'): 'es-MX-BeatrizNeural',
    ('es-MX', 'female-3'): 'es-MX-CarlotaNeural',
    ('es-MX', 'male-1'):   'es-MX-JorgeNeural',
    ('es-MX', 'male-2'):   'es-MX-GerardoNeural',
    ('es-MX', 'male-3'):   'es-MX-LibertoNeural',
    ('es-MX', 'young'):    'es-MX-BeatrizNeural',
    ('es-MX', 'old'):      'es-MX-DaliaNeural',

    # French
    ('fr-FR', 'female-1'): 'fr-FR-DeniseNeural',
    ('fr-FR', 'female-2'): 'fr-FR-BrigitteNeural',
    ('fr-FR', 'female-3'): 'fr-FR-CelesteNeural',
    ('fr-FR', 'male-1'):   'fr-FR-HenriNeural',
    ('fr-FR', 'male-2'):   'fr-FR-AlainNeural',
    ('fr-FR', 'male-3'):   'fr-FR-ClaudeNeural',
    ('fr-FR', 'young'):    'fr-FR-BrigitteNeural',
    ('fr-FR', 'old'):      'fr-FR-DeniseNeural',

    # German
    ('de-DE', 'female-1'): 'de-DE-KatjaNeural',
    ('de-DE', 'female-2'): 'de-DE-ElkeNeural',
    ('de-DE', 'female-3'): 'de-DE-AmalaNeural',
    ('de-DE', 'male-1'):   'de-DE-ConradNeural',
    ('de-DE', 'male-2'):   'de-DE-BerndNeural',
    ('de-DE', 'male-3'):   'de-DE-ChristophNeural',
    ('de-DE', 'young'):    'de-DE-ElkeNeural',
    ('de-DE', 'old'):      'de-DE-KatjaNeural',

    # Japanese
    ('ja-JP', 'female-1'): 'ja-JP-NanamiNeural',
    ('ja-JP', 'female-2'): 'ja-JP-AoiNeural',
    ('ja-JP', 'female-3'): 'ja-JP-MayuNeural',
    ('ja-JP', 'male-1'):   'ja-JP-KeitaNeural',
    ('ja-JP', 'male-2'):   'ja-JP-DaichiNeural',
    ('ja-JP', 'male-3'):   'ja-JP-NaokiNeural',
    ('ja-JP', 'young'):    'ja-JP-AoiNeural',
    ('ja-JP', 'old'):      'ja-JP-NanamiNeural',

    # Chinese
    ('zh-CN', 'female-1'): 'zh-CN-XiaoxiaoNeural',
    ('zh-CN', 'female-2'): 'zh-CN-XiaoyiNeural',
    ('zh-CN', 'female-3'): 'zh-CN-XiaohanNeural',
    ('zh-CN', 'male-1'):   'zh-CN-YunxiNeural',
    ('zh-CN', 'male-2'):   'zh-CN-YunyangNeural',
    ('zh-CN', 'male-3'):   'zh-CN-YunjianNeural',
    ('zh-CN', 'young'):    'zh-CN-XiaoyiNeural',
    ('zh-CN', 'old'):      'zh-CN-XiaoxiaoNeural',

    # Korean
    ('ko-KR', 'female-1'): 'ko-KR-SunHiNeural',
    ('ko-KR', 'female-2'): 'ko-KR-JiMinNeural',
    ('ko-KR', 'female-3'): 'ko-KR-SunHiNeural',
    ('ko-KR', 'male-1'):   'ko-KR-InJoonNeural',
    ('ko-KR', 'male-2'):   'ko-KR-HyunsuNeural',
    ('ko-KR', 'male-3'):   'ko-KR-InJoonNeural',
    ('ko-KR', 'young'):    'ko-KR-JiMinNeural',
    ('ko-KR', 'old'):      'ko-KR-SunHiNeural',

    # Russian
    ('ru-RU', 'female-1'): 'ru-RU-SvetlanaNeural',
    ('ru-RU', 'female-2'): 'ru-RU-DariyaNeural',
    ('ru-RU', 'female-3'): 'ru-RU-SvetlanaNeural',
    ('ru-RU', 'male-1'):   'ru-RU-DmitryNeural',
    ('ru-RU', 'male-2'):   'ru-RU-DmitryNeural',
    ('ru-RU', 'male-3'):   'ru-RU-DmitryNeural',
    ('ru-RU', 'young'):    'ru-RU-DariyaNeural',
    ('ru-RU', 'old'):      'ru-RU-SvetlanaNeural',

    # Italian
    ('it-IT', 'female-1'): 'it-IT-ElsaNeural',
    ('it-IT', 'female-2'): 'it-IT-IsabellaNeural',
    ('it-IT', 'female-3'): 'it-IT-FiammaNeural',
    ('it-IT', 'male-1'):   'it-IT-DiegoNeural',
    ('it-IT', 'male-2'):   'it-IT-BenignoNeural',
    ('it-IT', 'male-3'):   'it-IT-CalimeroNeural',
    ('it-IT', 'young'):    'it-IT-IsabellaNeural',
    ('it-IT', 'old'):      'it-IT-ElsaNeural',

    # Portuguese Brazil
    ('pt-BR', 'female-1'): 'pt-BR-FranciscaNeural',
    ('pt-BR', 'female-2'): 'pt-BR-BrendaNeural',
    ('pt-BR', 'female-3'): 'pt-BR-ElzaNeural',
    ('pt-BR', 'male-1'):   'pt-BR-AntonioNeural',
    ('pt-BR', 'male-2'):   'pt-BR-DonatoNeural',
    ('pt-BR', 'male-3'):   'pt-BR-FabioNeural',
    ('pt-BR', 'young'):    'pt-BR-BrendaNeural',
    ('pt-BR', 'old'):      'pt-BR-FranciscaNeural',

    # Arabic
    ('ar-SA', 'female-1'): 'ar-SA-ZariyahNeural',
    ('ar-SA', 'female-2'): 'ar-SA-ZariyahNeural',
    ('ar-SA', 'female-3'): 'ar-SA-ZariyahNeural',
    ('ar-SA', 'male-1'):   'ar-SA-HamedNeural',
    ('ar-SA', 'male-2'):   'ar-SA-HamedNeural',
    ('ar-SA', 'male-3'):   'ar-SA-HamedNeural',
    ('ar-SA', 'young'):    'ar-SA-ZariyahNeural',
    ('ar-SA', 'old'):      'ar-SA-HamedNeural',

    # Dutch
    ('nl-NL', 'female-1'): 'nl-NL-ColetteNeural',
    ('nl-NL', 'female-2'): 'nl-NL-FennaNeural',
    ('nl-NL', 'female-3'): 'nl-NL-ColetteNeural',
    ('nl-NL', 'male-1'):   'nl-NL-MaartenNeural',
    ('nl-NL', 'male-2'):   'nl-NL-MaartenNeural',
    ('nl-NL', 'male-3'):   'nl-NL-MaartenNeural',
    ('nl-NL', 'young'):    'nl-NL-FennaNeural',
    ('nl-NL', 'old'):      'nl-NL-ColetteNeural',

    # Swedish
    ('sv-SE', 'female-1'): 'sv-SE-HilleviNeural',
    ('sv-SE', 'female-2'): 'sv-SE-SofieNeural',
    ('sv-SE', 'female-3'): 'sv-SE-HilleviNeural',
    ('sv-SE', 'male-1'):   'sv-SE-MattiasNeural',
    ('sv-SE', 'male-2'):   'sv-SE-MattiasNeural',
    ('sv-SE', 'male-3'):   'sv-SE-MattiasNeural',
    ('sv-SE', 'young'):    'sv-SE-SofieNeural',
    ('sv-SE', 'old'):      'sv-SE-HilleviNeural',

    # Turkish
    ('tr-TR', 'female-1'): 'tr-TR-EmelNeural',
    ('tr-TR', 'female-2'): 'tr-TR-EmelNeural',
    ('tr-TR', 'female-3'): 'tr-TR-EmelNeural',
    ('tr-TR', 'male-1'):   'tr-TR-AhmetNeural',
    ('tr-TR', 'male-2'):   'tr-TR-AhmetNeural',
    ('tr-TR', 'male-3'):   'tr-TR-AhmetNeural',
    ('tr-TR', 'young'):    'tr-TR-EmelNeural',
    ('tr-TR', 'old'):      'tr-TR-AhmetNeural',

    # Polish
    ('pl-PL', 'female-1'): 'pl-PL-ZofiaNeural',
    ('pl-PL', 'female-2'): 'pl-PL-ZofiaNeural',
    ('pl-PL', 'female-3'): 'pl-PL-ZofiaNeural',
    ('pl-PL', 'male-1'):   'pl-PL-MarekNeural',
    ('pl-PL', 'male-2'):   'pl-PL-MarekNeural',
    ('pl-PL', 'male-3'):   'pl-PL-MarekNeural',
    ('pl-PL', 'young'):    'pl-PL-ZofiaNeural',
    ('pl-PL', 'old'):      'pl-PL-MarekNeural',
}

# gTTS language code mapping
GTTS_LANG_MAP = {
    'en-US': 'en', 'en-GB': 'en', 'hi-IN': 'hi', 'es-ES': 'es', 'es-MX': 'es',
    'fr-FR': 'fr', 'de-DE': 'de', 'ja-JP': 'ja', 'zh-CN': 'zh-CN', 'ko-KR': 'ko',
    'ru-RU': 'ru', 'it-IT': 'it', 'pt-BR': 'pt', 'ar-SA': 'ar', 'nl-NL': 'nl',
    'sv-SE': 'sv', 'tr-TR': 'tr', 'pl-PL': 'pl'
}

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

VOICE_TYPES = [
    {"id": "female-1", "name": "Female 1 (Natural)", "icon": "👩"},
    {"id": "female-2", "name": "Female 2 (Soft)", "icon": "👩‍🦰"},
    {"id": "female-3", "name": "Female 3 (Professional)", "icon": "👩‍💼"},
    {"id": "male-1",   "name": "Male 1 (Deep)", "icon": "👨"},
    {"id": "male-2",   "name": "Male 2 (Friendly)", "icon": "👨‍🦰"},
    {"id": "male-3",   "name": "Male 3 (Authoritative)", "icon": "👨‍💼"},
    {"id": "young",    "name": "Young Voice", "icon": "🧒"},
    {"id": "old",      "name": "Mature Voice", "icon": "🧓"},
]

SAMPLE_TEXTS = {
    'en-US': "Hello! This is a preview of my voice. I hope you like it!",
    'en-GB': "Hello! This is a preview of my voice. I hope you like it!",
    'hi-IN': "नमस्ते! यह मेरी आवाज़ का पूर्वावलोकन है। मुझे उम्मीद है आपको यह पसंद आएगी!",
    'es-ES': "¡Hola! Esta es una vista previa de mi voz. ¡Espero que te guste!",
    'es-MX': "¡Hola! Esta es una vista previa de mi voz. ¡Espero que te guste!",
    'fr-FR': "Bonjour! Voici un aperçu de ma voix. J'espère que vous aimez!",
    'de-DE': "Hallo! Dies ist eine Vorschau meiner Stimme. Ich hoffe, es gefällt Ihnen!",
    'ja-JP': "こんにちは！これは私の声のプレビューです。気に入っていただければ幸いです！",
    'zh-CN': "你好！这是我的声音预览。希望你喜欢！",
    'ko-KR': "안녕하세요! 제 목소리 미리보기입니다. 마음에 드시길 바랍니다!",
    'ru-RU': "Привет! Это предварительный просмотр моего голоса. Надеюсь, вам понравится!",
    'it-IT': "Ciao! Questa è un'anteprima della mia voce. Spero ti piaccia!",
    'pt-BR': "Olá! Esta é uma prévia da minha voz. Espero que você goste!",
    'ar-SA': "مرحباً! هذا معاينة لصوتي. أتمنى أن تعجبك!",
    'nl-NL': "Hallo! Dit is een voorbeeld van mijn stem. Ik hoop dat je het leuk vindt!",
    'sv-SE': "Hej! Det här är en förhandsvisning av min röst. Hoppas du gillar det!",
    'tr-TR': "Merhaba! Bu sesimin önizlemesi. Umarım beğenirsiniz!",
    'pl-PL': "Cześć! To jest podgląd mojego głosu. Mam nadzieję, że ci się spodoba!",
}


def get_voice(lang, voice_type):
    """Get voice name with proper fallback chain"""
    # Direct match
    voice = VOICE_MAPPING.get((lang, voice_type))
    if voice:
        return voice
    # Try female-1 as default for that language
    voice = VOICE_MAPPING.get((lang, 'female-1'))
    if voice:
        return voice
    # Absolute fallback
    return 'en-US-AriaNeural'


def build_rate_str(rate_val):
    """Convert float rate (0.5-2.0) to edge-tts format like +50% or -25%"""
    try:
        r = float(rate_val)
        # edge-tts rate: 1.0 = +0%, 1.5 = +50%, 0.5 = -50%
        percent = int((r - 1.0) * 100)
        if percent >= 0:
            return f"+{percent}%"
        else:
            return f"{percent}%"
    except:
        return "+0%"


def build_pitch_str(pitch_val):
    """Convert int pitch (-10 to 10) to edge-tts Hz format"""
    try:
        p = int(float(pitch_val))
        hz = p * 10  # each step = 10Hz
        if hz >= 0:
            return f"+{hz}Hz"
        else:
            return f"{hz}Hz"
    except:
        return "+0Hz"


def build_volume_str(volume_val):
    """Convert volume (0-100) to edge-tts format"""
    try:
        v = int(float(volume_val))
        diff = v - 100
        if diff >= 0:
            return f"+{diff}%"
        else:
            return f"{diff}%"
    except:
        return "+0%"


# ------------------ Routes ------------------
@app.route('/')
def home():
    return render_template('index.html', languages=LANGUAGES, voice_types=VOICE_TYPES)


@app.route('/stats')
def stats():
    total = 1540
    today = 12
    if redis:
        try:
            total = int(redis.get("total_translations") or 1540)
            today_key = f"count_{datetime.now().strftime('%Y-%m-%d')}"
            today = int(redis.get(today_key) or 0)
        except Exception as e:
            logging.error(f"Redis stats error: {e}")
    return jsonify({"total": total, "today": today})


@app.route('/convert', methods=['POST'])
def convert():
    if not EDGE_AVAILABLE and not GTTS_AVAILABLE and not PYTTSX3_AVAILABLE:
        return jsonify({'error': 'No TTS library installed. Run: pip install edge-tts'}), 500

    try:
        text = request.form.get('text', '').strip()
        lang = request.form.get('language', 'en-US')
        voice_type = request.form.get('voice_type', 'female-1')
        rate = request.form.get('rate', '1.0')
        pitch = request.form.get('pitch', '0')
        volume = request.form.get('volume', '100')
        style = request.form.get('style', 'general')
        format_type = request.form.get('format', 'mp3')

        if not text:
            return jsonify({'error': 'Please enter text to convert'}), 400

        if len(text) > 5000:
            return jsonify({'error': 'Text too long. Maximum 5000 characters allowed.'}), 400

        voice = get_voice(lang, voice_type)
        logging.info(f"TTS: lang={lang}, voice_type={voice_type}, voice={voice}, len={len(text)}")

        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(TEMP_FOLDER, filename)
        success = False
        method_used = "none"

        # ---- Edge TTS (Best Quality) ----
        if EDGE_AVAILABLE:
            try:
                rate_str = build_rate_str(rate)
                pitch_str = build_pitch_str(pitch)
                volume_str = build_volume_str(volume)

                async def generate_edge():
                    communicate = edge_tts.Communicate(
                        text=text,
                        voice=voice,
                        rate=rate_str,
                        pitch=pitch_str,
                        volume=volume_str
                    )
                    await communicate.save(filepath)

                asyncio.run(generate_edge())

                if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                    success = True
                    method_used = "Edge TTS"
                    logging.info(f"✅ Edge TTS OK: voice={voice}, rate={rate_str}, pitch={pitch_str}")
                else:
                    logging.warning("Edge TTS file empty or missing")
            except Exception as e:
                logging.error(f"Edge TTS Error: {e}")

        # ---- gTTS Fallback ----
        if not success and GTTS_AVAILABLE:
            try:
                gtts_lang = GTTS_LANG_MAP.get(lang, 'en')
                tts = gTTS(text=text, lang=gtts_lang, slow=False)
                tts.save(filepath)
                if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                    success = True
                    method_used = "Google TTS"
                    logging.info(f"✅ gTTS OK")
            except Exception as e:
                logging.error(f"gTTS Error: {e}")

        # ---- pyttsx3 Fallback ----
        if not success and PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', int(float(rate) * 150))
                engine.save_to_file(text, filepath)
                engine.runAndWait()
                if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                    success = True
                    method_used = "System TTS"
            except Exception as e:
                logging.error(f"pyttsx3 Error: {e}")

        if not success:
            return jsonify({'error': 'Audio generation failed. Please try again.'}), 500

        # ---- Redis Stats ----
        if redis:
            try:
                redis.incr("total_translations")
                redis.incr(f"count_{datetime.now().strftime('%Y-%m-%d')}")
                redis.zincrby("popular_languages", 1, lang)
            except Exception as e:
                logging.error(f"Redis update error: {e}")

        # ---- Return Response ----
        with open(filepath, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        try:
            os.remove(filepath)
        except:
            pass

        return jsonify({
            "success": True,
            "audio_data": f"data:audio/mp3;base64,{audio_base64}",
            "filename": f"voicepro_{lang}_{voice_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "method": method_used,
            "voice_used": voice,
            "language": lang,
            "voice_type": voice_type
        })

    except Exception as e:
        logging.error(f"Convert error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/preview-voice', methods=['POST'])
def preview_voice():
    try:
        data = request.get_json()
        lang = data.get('language', 'en-US')
        voice_type = data.get('voice_type', 'female-1')

        text = SAMPLE_TEXTS.get(lang, "Hello! This is a preview of my voice.")
        voice = get_voice(lang, voice_type)

        if not EDGE_AVAILABLE:
            return jsonify({"success": False, "error": "edge-tts not installed"})

        filename = f"preview_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(TEMP_FOLDER, filename)

        async def gen():
            await edge_tts.Communicate(text=text, voice=voice).save(filepath)

        asyncio.run(gen())

        if not os.path.exists(filepath) or os.path.getsize(filepath) < 500:
            return jsonify({"success": False, "error": "Preview generation failed"})

        with open(filepath, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode('utf-8')

        try:
            os.remove(filepath)
        except:
            pass

        return jsonify({
            "success": True,
            "audio_data": f"data:audio/mp3;base64,{audio_b64}",
            "voice": voice,
            "language": lang
        })

    except Exception as e:
        logging.error(f"Preview error: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/voices/<lang>')
def get_voices_for_lang(lang):
    """Return available voice types for a language"""
    available = []
    for vt in VOICE_TYPES:
        voice = VOICE_MAPPING.get((lang, vt['id']))
        if voice:
            available.append({**vt, "edge_voice": voice})
    return jsonify(available)


@app.route('/test-redis')
def test_redis():
    if not redis:
        return jsonify({"status": "error", "message": "Redis not connected"})
    try:
        redis.incr("test_counter")
        value = redis.get("test_counter")
        return jsonify({"status": "success", "test_counter": value})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.root_path, 'sitemap.xml')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
