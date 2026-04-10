from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import uuid
import asyncio
from datetime import datetime
import base64
import logging
import tempfile
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
#  TTS Libraries
# ─────────────────────────────────────────────
try:
    import edge_tts
    EDGE_AVAILABLE = True
    print("✅ edge-tts available")
except ImportError:
    EDGE_AVAILABLE = False
    print("❌ edge-tts not available  →  pip install edge-tts")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
    print("✅ gTTS available")
except ImportError:
    GTTS_AVAILABLE = False
    print("❌ gTTS not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

# ─────────────────────────────────────────────
#  Redis (optional)
# ─────────────────────────────────────────────
try:
    from upstash_redis import Redis
    redis = Redis(url=os.getenv("KV_REST_API_URL"), token=os.getenv("KV_REST_API_TOKEN"))
    redis.ping()
    REDIS_AVAILABLE = True
    print("✅ Upstash Redis connected")
except Exception as e:
    redis = None
    REDIS_AVAILABLE = False
    print(f"⚠️  Redis not available: {e}")

# ─────────────────────────────────────────────
#  Flask
# ─────────────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
TEMP_FOLDER = tempfile.gettempdir()
os.makedirs(TEMP_FOLDER, exist_ok=True)

# ─────────────────────────────────────────────
#  Voice Mapping
# ─────────────────────────────────────────────
VOICE_MAPPING = {
    ('en-US','female-1'): 'en-US-AriaNeural',
    ('en-US','female-2'): 'en-US-JennyNeural',
    ('en-US','female-3'): 'en-US-SaraNeural',
    ('en-US','male-1'):   'en-US-GuyNeural',
    ('en-US','male-2'):   'en-US-RogerNeural',
    ('en-US','male-3'):   'en-US-SteffanNeural',
    ('en-US','young'):    'en-US-AshleyNeural',
    ('en-US','old'):      'en-US-JaneNeural',
    ('en-GB','female-1'): 'en-GB-SoniaNeural',
    ('en-GB','female-2'): 'en-GB-LibbyNeural',
    ('en-GB','male-1'):   'en-GB-RyanNeural',
    ('en-GB','male-2'):   'en-GB-AlfieNeural',
    ('en-AU','female-1'): 'en-AU-NatashaNeural',
    ('en-AU','male-1'):   'en-AU-WilliamNeural',
    ('en-IN','female-1'): 'en-IN-NeerjaNeural',
    ('en-IN','male-1'):   'en-IN-PrabhatNeural',
    ('en-CA','female-1'): 'en-CA-ClaraNeural',
    ('en-CA','male-1'):   'en-CA-LiamNeural',
    ('en-NG','female-1'): 'en-NG-EzinneNeural',
    ('en-NG','male-1'):   'en-NG-AbeoNeural',
    ('en-ZA','female-1'): 'en-ZA-LeahNeural',
    ('en-ZA','male-1'):   'en-ZA-LukeNeural',
    ('hi-IN','female-1'): 'hi-IN-SwaraNeural',
    ('hi-IN','female-2'): 'hi-IN-AnanyaNeural',
    ('hi-IN','female-3'): 'hi-IN-SwaraNeural',
    ('hi-IN','male-1'):   'hi-IN-MadhurNeural',
    ('hi-IN','male-2'):   'hi-IN-PrabhatNeural',
    ('hi-IN','male-3'):   'hi-IN-MadhurNeural',
    ('hi-IN','young'):    'hi-IN-AnanyaNeural',
    ('hi-IN','old'):      'hi-IN-MadhurNeural',
    ('mr-IN','female-1'): 'mr-IN-AarohiNeural',
    ('mr-IN','male-1'):   'mr-IN-ManoharNeural',
    ('gu-IN','female-1'): 'gu-IN-DhwaniNeural',
    ('gu-IN','male-1'):   'gu-IN-NiranjanNeural',
    ('bn-IN','female-1'): 'bn-IN-TanishaaNeural',
    ('bn-IN','male-1'):   'bn-IN-BashkarNeural',
    ('bn-BD','female-1'): 'bn-BD-NabanitaNeural',
    ('bn-BD','male-1'):   'bn-BD-PradeepNeural',
    ('ta-IN','female-1'): 'ta-IN-PallaviNeural',
    ('ta-IN','male-1'):   'ta-IN-ValluvarNeural',
    ('te-IN','female-1'): 'te-IN-ShrutiNeural',
    ('te-IN','male-1'):   'te-IN-MohanNeural',
    ('kn-IN','female-1'): 'kn-IN-SapnaNeural',
    ('kn-IN','male-1'):   'kn-IN-GaganNeural',
    ('ml-IN','female-1'): 'ml-IN-SobhanaNeural',
    ('ml-IN','male-1'):   'ml-IN-MidhunNeural',
    ('pa-IN','female-1'): 'pa-IN-OjasNeural',
    ('pa-IN','male-1'):   'pa-IN-OjasNeural',
    ('or-IN','female-1'): 'or-IN-SubhasiniNeural',
    ('or-IN','male-1'):   'or-IN-SukantNeural',
    ('ur-PK','female-1'): 'ur-PK-UzmaNeural',
    ('ur-PK','male-1'):   'ur-PK-AsadNeural',
    ('si-LK','female-1'): 'si-LK-ThiliniNeural',
    ('si-LK','male-1'):   'si-LK-SameeraNeural',
    ('ne-NP','female-1'): 'ne-NP-HemkalaNeural',
    ('ne-NP','male-1'):   'ne-NP-SagarNeural',
    ('es-ES','female-1'): 'es-ES-ElviraNeural',
    ('es-ES','male-1'):   'es-ES-AlvaroNeural',
    ('es-MX','female-1'): 'es-MX-DaliaNeural',
    ('es-MX','male-1'):   'es-MX-JorgeNeural',
    ('es-AR','female-1'): 'es-AR-ElenaNeural',
    ('es-AR','male-1'):   'es-AR-TomasNeural',
    ('es-CO','female-1'): 'es-CO-SalomeNeural',
    ('es-CO','male-1'):   'es-CO-GonzaloNeural',
    ('es-US','female-1'): 'es-US-PalomaNeural',
    ('es-US','male-1'):   'es-US-AlonsoNeural',
    ('fr-FR','female-1'): 'fr-FR-DeniseNeural',
    ('fr-FR','male-1'):   'fr-FR-HenriNeural',
    ('fr-CA','female-1'): 'fr-CA-SylvieNeural',
    ('fr-CA','male-1'):   'fr-CA-JeanNeural',
    ('de-DE','female-1'): 'de-DE-KatjaNeural',
    ('de-DE','male-1'):   'de-DE-ConradNeural',
    ('de-AT','female-1'): 'de-AT-IngridNeural',
    ('de-AT','male-1'):   'de-AT-JonasNeural',
    ('it-IT','female-1'): 'it-IT-ElsaNeural',
    ('it-IT','male-1'):   'it-IT-DiegoNeural',
    ('pt-BR','female-1'): 'pt-BR-FranciscaNeural',
    ('pt-BR','male-1'):   'pt-BR-AntonioNeural',
    ('pt-PT','female-1'): 'pt-PT-RaquelNeural',
    ('pt-PT','male-1'):   'pt-PT-DuarteNeural',
    ('nl-NL','female-1'): 'nl-NL-ColetteNeural',
    ('nl-NL','male-1'):   'nl-NL-MaartenNeural',
    ('sv-SE','female-1'): 'sv-SE-HilleviNeural',
    ('sv-SE','male-1'):   'sv-SE-MattiasNeural',
    ('nb-NO','female-1'): 'nb-NO-PernilleNeural',
    ('nb-NO','male-1'):   'nb-NO-FinnNeural',
    ('da-DK','female-1'): 'da-DK-ChristelNeural',
    ('da-DK','male-1'):   'da-DK-JeppeNeural',
    ('fi-FI','female-1'): 'fi-FI-NooraNeural',
    ('fi-FI','male-1'):   'fi-FI-HarriNeural',
    ('pl-PL','female-1'): 'pl-PL-ZofiaNeural',
    ('pl-PL','male-1'):   'pl-PL-MarekNeural',
    ('cs-CZ','female-1'): 'cs-CZ-VlastaNeural',
    ('cs-CZ','male-1'):   'cs-CZ-AntoninNeural',
    ('sk-SK','female-1'): 'sk-SK-ViktoriaNeural',
    ('sk-SK','male-1'):   'sk-SK-LukasNeural',
    ('hu-HU','female-1'): 'hu-HU-NoemiNeural',
    ('hu-HU','male-1'):   'hu-HU-TamasNeural',
    ('ro-RO','female-1'): 'ro-RO-AlinaNeural',
    ('ro-RO','male-1'):   'ro-RO-EmilNeural',
    ('ru-RU','female-1'): 'ru-RU-SvetlanaNeural',
    ('ru-RU','male-1'):   'ru-RU-DmitryNeural',
    ('uk-UA','female-1'): 'uk-UA-PolinaNeural',
    ('uk-UA','male-1'):   'uk-UA-OstapNeural',
    ('el-GR','female-1'): 'el-GR-AthinaNeural',
    ('el-GR','male-1'):   'el-GR-NestorasNeural',
    ('bg-BG','female-1'): 'bg-BG-KalinaNeural',
    ('bg-BG','male-1'):   'bg-BG-BorislavNeural',
    ('hr-HR','female-1'): 'hr-HR-GabrijelaNeural',
    ('hr-HR','male-1'):   'hr-HR-SreckoNeural',
    ('tr-TR','female-1'): 'tr-TR-EmelNeural',
    ('tr-TR','male-1'):   'tr-TR-AhmetNeural',
    ('ja-JP','female-1'): 'ja-JP-NanamiNeural',
    ('ja-JP','male-1'):   'ja-JP-KeitaNeural',
    ('ja-JP','young'):    'ja-JP-AoiNeural',
    ('zh-CN','female-1'): 'zh-CN-XiaoxiaoNeural',
    ('zh-CN','male-1'):   'zh-CN-YunxiNeural',
    ('zh-CN','young'):    'zh-CN-XiaoyiNeural',
    ('zh-TW','female-1'): 'zh-TW-HsiaoChenNeural',
    ('zh-TW','male-1'):   'zh-TW-YunJheNeural',
    ('zh-HK','female-1'): 'zh-HK-HiuMaanNeural',
    ('zh-HK','male-1'):   'zh-HK-WanLungNeural',
    ('ko-KR','female-1'): 'ko-KR-SunHiNeural',
    ('ko-KR','male-1'):   'ko-KR-InJoonNeural',
    ('vi-VN','female-1'): 'vi-VN-HoaiMyNeural',
    ('vi-VN','male-1'):   'vi-VN-NamMinhNeural',
    ('th-TH','female-1'): 'th-TH-PremwadeeNeural',
    ('th-TH','male-1'):   'th-TH-NiwatNeural',
    ('id-ID','female-1'): 'id-ID-GadisNeural',
    ('id-ID','male-1'):   'id-ID-ArdiNeural',
    ('ms-MY','female-1'): 'ms-MY-YasminNeural',
    ('ms-MY','male-1'):   'ms-MY-OsmanNeural',
    ('ar-SA','female-1'): 'ar-SA-ZariyahNeural',
    ('ar-SA','male-1'):   'ar-SA-HamedNeural',
    ('ar-EG','female-1'): 'ar-EG-SalmaNeural',
    ('ar-EG','male-1'):   'ar-EG-ShakirNeural',
    ('fa-IR','female-1'): 'fa-IR-DilaraNeural',
    ('fa-IR','male-1'):   'fa-IR-FaridNeural',
    ('he-IL','female-1'): 'he-IL-HilaNeural',
    ('he-IL','male-1'):   'he-IL-AvriNeural',
    ('ka-GE','female-1'): 'ka-GE-EkaNeural',
    ('ka-GE','male-1'):   'ka-GE-GiorgiNeural',
    ('sw-KE','female-1'): 'sw-KE-ZuriNeural',
    ('sw-KE','male-1'):   'sw-KE-RafikiNeural',
    ('am-ET','female-1'): 'am-ET-MekdesNeural',
    ('am-ET','male-1'):   'am-ET-AmehaNeural',
    ('zu-ZA','female-1'): 'zu-ZA-ThandoNeural',
    ('zu-ZA','male-1'):   'zu-ZA-ThembaNeural',
    ('af-ZA','female-1'): 'af-ZA-AdriNeural',
    ('af-ZA','male-1'):   'af-ZA-WillemNeural',
    ('fil-PH','female-1'):'fil-PH-BlessicaNeural',
    ('fil-PH','male-1'):  'fil-PH-AngeloNeural',
}

GTTS_LANG_MAP = {
    'en-US':'en','en-GB':'en','en-AU':'en','en-IN':'en','en-CA':'en',
    'hi-IN':'hi','mr-IN':'mr','gu-IN':'gu','bn-IN':'bn','ta-IN':'ta',
    'te-IN':'te','kn-IN':'kn','ml-IN':'ml','pa-IN':'pa','ur-PK':'ur',
    'es-ES':'es','es-MX':'es','fr-FR':'fr','fr-CA':'fr',
    'de-DE':'de','it-IT':'it','pt-BR':'pt','pt-PT':'pt',
    'nl-NL':'nl','sv-SE':'sv','nb-NO':'no','da-DK':'da','fi-FI':'fi',
    'pl-PL':'pl','cs-CZ':'cs','hu-HU':'hu','ro-RO':'ro','ru-RU':'ru',
    'uk-UA':'uk','el-GR':'el','tr-TR':'tr',
    'ja-JP':'ja','zh-CN':'zh-CN','zh-TW':'zh-TW','ko-KR':'ko',
    'vi-VN':'vi','th-TH':'th','id-ID':'id','ms-MY':'ms',
    'ar-SA':'ar','ar-EG':'ar','fa-IR':'fa','he-IL':'iw',
    'af-ZA':'af','sw-KE':'sw',
}

SAMPLE_TEXTS = {
    'en-US':"Hello! This is a voice preview. Enjoy!",
    'hi-IN':"नमस्ते! यह एक आवाज़ का प्रीव्यू है।",
    'mr-IN':"नमस्कार! हे एक आवाज प्रिव्ह्यू आहे.",
    'ta-IN':"வணக்கம்! இது ஒரு குரல் முன்னோட்டம்.",
    'te-IN':"నమస్కారం! ఇది ఒక వాయిస్ ప్రివ్యూ.",
    'es-ES':"¡Hola! Esta es una vista previa de voz.",
    'fr-FR':"Bonjour! Voici un aperçu de ma voix.",
    'de-DE':"Hallo! Dies ist eine Sprachvorschau.",
    'ja-JP':"こんにちは！これは音声プレビューです。",
    'zh-CN':"你好！这是语音预览。",
    'ko-KR':"안녕하세요! 이것은 음성 미리보기입니다.",
    'ar-SA':"مرحباً! هذه معاينة صوتية.",
}
DEFAULT_SAMPLE = "Hello! This is a voice preview. Enjoy!"


def get_voice(lang: str, voice_type: str) -> str:
    voice = VOICE_MAPPING.get((lang, voice_type))
    if voice:
        return voice
    voice = VOICE_MAPPING.get((lang, 'female-1'))
    if voice:
        return voice
    lang_prefix = lang.split('-')[0]
    for vt in ['female-1', 'male-1']:
        for code, v in VOICE_MAPPING.items():
            if code[0].startswith(lang_prefix) and code[1] == vt:
                return v
    return 'en-US-AriaNeural'


# ─────────────────────────────────────────────
#  ✅ FIXED: Rate/Pitch/Volume builders
#  edge-tts expects: rate="+10%" pitch="+5Hz" volume="+0%"
#  rate range: -50% to +100%  (0.5x = -50%, 2.0x = +100%)
#  pitch range: -200Hz to +200Hz  (semitone offset * 10Hz)
#  volume range: -100% to +100%
# ─────────────────────────────────────────────
def build_rate(val):
    """
    Frontend sends float like 0.85, 1.0, 1.2
    edge-tts rate = percentage relative to 1.0
    1.0 → +0%,  0.85 → -15%,  1.2 → +20%,  0.5 → -50%
    """
    try:
        r = float(val)
        r = max(0.5, min(2.0, r))          # clamp to safe range
        pct = round((r - 1.0) * 100)
        return f"+{pct}%" if pct >= 0 else f"{pct}%"
    except Exception:
        return "+0%"


def build_pitch(val):
    """
    Frontend sends int like -5, 0, +5
    edge-tts pitch = Hz offset (semitone * 10Hz works well)
    -5 → -50Hz,  0 → +0Hz,  +5 → +50Hz
    """
    try:
        p = int(float(val))
        p = max(-10, min(10, p))           # clamp
        hz = p * 10
        return f"+{hz}Hz" if hz >= 0 else f"{hz}Hz"
    except Exception:
        return "+0Hz"


def build_volume(val):
    """
    Frontend sends 0-100 integer
    edge-tts volume = relative %: 100 → +0%, 50 → -50%, 0 → -100%
    """
    try:
        v = int(float(val))
        v = max(0, min(100, v))
        diff = v - 100                     # 100→0, 80→-20, 50→-50
        return f"+{diff}%" if diff >= 0 else f"{diff}%"
    except Exception:
        return "+0%"


# ─────────────────────────────────────────────
#  Speaking Style → edge-tts SSML style name
# ─────────────────────────────────────────────
STYLE_MAP = {
    'general':                None,          # no SSML needed
    'cheerful':               'cheerful',
    'sad':                    'sad',
    'angry':                  'angry',
    'excited':                'excited',
    'friendly':               'friendly',
    'newscast':               'newscast',
    'newscast-casual':        'newscast-casual',
    'newscast-formal':        'newscast-formal',
    'assistant':              'assistant',
    'customerservice':        'customerservice',
    'narration-professional': 'narration-professional',
    'narration-relaxed':      'narration-relaxed',
    'poetry-reading':         'poetry-reading',
    'sports-commentary':      'sports-commentary',
    'documentary-narration':  'documentary-narration',
}

# Only these voices support express-as SSML in edge-tts
STYLE_CAPABLE_VOICES = {
    'zh-CN-XiaoxiaoNeural','zh-CN-XiaoyiNeural','zh-CN-YunyangNeural',
    'zh-CN-YunxiNeural','zh-CN-XiaohanNeural',
    'en-US-AriaNeural','en-US-GuyNeural','en-US-JennyNeural','en-US-SaraNeural',
    'en-US-DavisNeural','en-US-TonyNeural','en-US-NancyNeural',
    'en-GB-SoniaNeural','en-GB-RyanNeural',
    'de-DE-KatjaNeural','de-DE-ConradNeural',
    'fr-FR-DeniseNeural','fr-FR-HenriNeural',
    'it-IT-ElsaNeural','it-IT-DiegoNeural',
    'pt-BR-FranciscaNeural',
    'es-ES-ElviraNeural','es-ES-AlvaroNeural',
    'es-MX-DaliaNeural','es-MX-JorgeNeural',
    'ja-JP-NanamiNeural',
    'ko-KR-SunHiNeural','ko-KR-InJoonNeural',
}


async def _generate_edge(text, voice, rate_str, pitch_str, volume_str, style, filepath):
    """
    ✅ FIXED: Tries with SSML style first (for capable voices),
    falls back to plain text on any error.
    """
    ssml_style = STYLE_MAP.get(style)

    # --- attempt 1: with SSML style (if voice supports it) ---
    if ssml_style and voice in STYLE_CAPABLE_VOICES:
        try:
            ssml = (
                f'<speak version="1.0" '
                f'xmlns="http://www.w3.org/2001/10/synthesis" '
                f'xmlns:mstts="http://www.w3.org/2001/mstts" '
                f'xml:lang="en-US">'
                f'<voice name="{voice}">'
                f'<mstts:express-as style="{ssml_style}">'
                f'{text}'
                f'</mstts:express-as>'
                f'</voice></speak>'
            )
            communicate = edge_tts.Communicate(
                ssml, voice=voice,
                rate=rate_str, pitch=pitch_str, volume=volume_str
            )
            await communicate.save(filepath)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                logging.info(f"✅ edge-tts SSML: voice={voice} rate={rate_str} pitch={pitch_str} style={ssml_style}")
                return True
        except Exception as e:
            logging.warning(f"edge-tts SSML style failed ({e}), retrying plain…")

    # --- attempt 2: plain text (always works, applies rate/pitch/volume) ---
    try:
        communicate = edge_tts.Communicate(
            text, voice=voice,
            rate=rate_str, pitch=pitch_str, volume=volume_str
        )
        await communicate.save(filepath)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
            logging.info(f"✅ edge-tts plain: voice={voice} rate={rate_str} pitch={pitch_str}")
            return True
    except Exception as e:
        logging.error(f"edge-tts plain error: {e}")

    return False


def audio_to_base64(filepath, fmt='mp3'):
    with open(filepath, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    mime = 'audio/wav' if fmt == 'wav' else 'audio/mpeg'
    return f"data:{mime};base64,{data}"


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/stats')
def stats():
    total, today = 1540, 0
    if redis:
        try:
            total = int(redis.get("total_translations") or 1540)
            today_key = f"count_{datetime.now().strftime('%Y-%m-%d')}"
            today = int(redis.get(today_key) or 0)
        except Exception as e:
            logging.error(f"Redis stats error: {e}")
    return jsonify({"total": total, "today": today})


@app.route('/generate', methods=['POST'])
def generate():
    if not any([EDGE_AVAILABLE, GTTS_AVAILABLE, PYTTSX3_AVAILABLE]):
        return jsonify({'error': 'No TTS library installed. Run: pip install edge-tts'}), 500

    try:
        text       = request.form.get('text', '').strip()
        lang       = request.form.get('language', 'en-US')
        voice_type = request.form.get('voice_type', 'female-1')
        rate       = request.form.get('rate', '1.0')
        pitch      = request.form.get('pitch', '0')
        volume     = request.form.get('volume', '100')
        style      = request.form.get('style', 'general')
        fmt        = request.form.get('format', 'mp3')

        if not text:
            return jsonify({'error': 'Please enter text to convert'}), 400
        if len(text) > 5000:
            return jsonify({'error': 'Text too long. Max 5000 characters.'}), 400

        voice = get_voice(lang, voice_type)

        # ✅ Build correct edge-tts parameter strings
        rate_str   = build_rate(rate)
        pitch_str  = build_pitch(pitch)
        volume_str = build_volume(volume)

        logging.info(
            f"TTS request → lang={lang} voice={voice} "
            f"rate={rate}→{rate_str} pitch={pitch}→{pitch_str} "
            f"vol={volume}→{volume_str} style={style}"
        )

        filename = f"vp_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(TEMP_FOLDER, filename)
        success  = False
        method   = "none"

        # ── 1. edge-tts ──────────────────────────────────────
        if EDGE_AVAILABLE:
            ok = asyncio.run(_generate_edge(
                text, voice, rate_str, pitch_str, volume_str, style, filepath
            ))
            if ok:
                success = True
                method  = "Edge TTS"
            else:
                logging.warning("Edge TTS failed, trying gTTS fallback")

        # ── 2. gTTS fallback ─────────────────────────────────
        if not success and GTTS_AVAILABLE:
            try:
                gtts_lang = GTTS_LANG_MAP.get(lang, 'en')
                # gTTS doesn't support rate/pitch — use slow=True if rate < 0.85
                slow = float(rate) < 0.85
                gTTS(text=text, lang=gtts_lang, slow=slow).save(filepath)
                if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                    success = True
                    method  = "Google TTS"
                    logging.info("✅ gTTS fallback OK")
            except Exception as e:
                logging.error(f"gTTS error: {e}")

        # ── 3. pyttsx3 fallback ──────────────────────────────
        if not success and PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                # pyttsx3 rate: default ~200 wpm. Scale by user rate.
                engine.setProperty('rate', int(float(rate) * 175))
                engine.save_to_file(text, filepath)
                engine.runAndWait()
                if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                    success = True
                    method  = "System TTS"
            except Exception as e:
                logging.error(f"pyttsx3 error: {e}")

        if not success:
            return jsonify({'error': 'Audio generation failed. Please try again.'}), 500

        # ── Redis stats ──────────────────────────────────────
        if redis:
            try:
                redis.incr("total_translations")
                redis.incr(f"count_{datetime.now().strftime('%Y-%m-%d')}")
                redis.zincrby("popular_languages", 1, lang)
            except Exception as e:
                logging.error(f"Redis update error: {e}")

        audio_data = audio_to_base64(filepath, fmt)
        try:
            os.remove(filepath)
        except Exception:
            pass

        return jsonify({
            "success":    True,
            "audio_data": audio_data,
            "filename":   f"voicepro_{lang}_{voice_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "method":     method,
            "voice_used": voice,
            "language":   lang,
            "voice_type": voice_type,
            # echo back applied values for debugging
            "applied_rate":  rate_str,
            "applied_pitch": pitch_str,
            "applied_vol":   volume_str,
            "applied_style": style,
        })

    except Exception as e:
        logging.error(f"Generate error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/convert', methods=['POST'])
def convert():
    return generate()


@app.route('/preview-voice', methods=['POST'])
def preview_voice():
    try:
        data       = request.get_json()
        lang       = data.get('language', 'en-US')
        voice_type = data.get('voice_type', 'female-1')
        text       = SAMPLE_TEXTS.get(lang, DEFAULT_SAMPLE)
        voice      = get_voice(lang, voice_type)

        if not EDGE_AVAILABLE:
            return jsonify({"success": False, "error": "edge-tts not installed"})

        filepath = os.path.join(TEMP_FOLDER, f"prev_{uuid.uuid4().hex}.mp3")
        ok = asyncio.run(_generate_edge(text, voice, "+0%", "+0Hz", "+0%", "general", filepath))
        if not ok:
            return jsonify({"success": False, "error": "Preview generation failed"})

        audio_data = audio_to_base64(filepath)
        try:
            os.remove(filepath)
        except Exception:
            pass

        return jsonify({"success": True, "audio_data": audio_data, "voice": voice, "language": lang})

    except Exception as e:
        logging.error(f"Preview error: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/voices/<lang>')
def voices_for_lang(lang):
    result = []
    for key, voice_name in VOICE_MAPPING.items():
        if key[0] == lang:
            result.append({"voice_type": key[1], "edge_voice": voice_name})
    return jsonify(result)


@app.route('/test-redis')
def test_redis():
    if not redis:
        return jsonify({"status": "error", "message": "Redis not connected"})
    try:
        redis.incr("test_counter")
        return jsonify({"status": "success", "counter": redis.get("test_counter")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.root_path, 'sitemap.xml')


@app.route('/about.html')
def about():
    return render_template('about.html')


@app.route('/blog.html')
def blog():
    return render_template('blog.html')


@app.route('/contact.html')
def contact():
    return render_template('contact.html')


@app.route('/privacy.html')
def privacy():
    return render_template('privacy.html')


@app.route('/terms.html')
def terms():
    return render_template('terms.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)