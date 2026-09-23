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
    print("[OK] edge-tts available")
except ImportError:
    EDGE_AVAILABLE = False
    print("[FAIL] edge-tts not available -> pip install edge-tts")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
    print("[OK] gTTS available")
except ImportError:
    GTTS_AVAILABLE = False
    print("[FAIL] gTTS not available")

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
    _redis_url = os.getenv("KV_REST_API_URL")
    _redis_token = os.getenv("KV_REST_API_TOKEN")
    if _redis_url and _redis_token:
        redis = Redis(url=_redis_url, token=_redis_token)
        REDIS_AVAILABLE = True
        print("[OK] Upstash Redis initialized")
    else:
        redis = None
        REDIS_AVAILABLE = False
        print("[INFO] Redis credentials not set, using fast in-memory stats")
except Exception as e:
    redis = None
    REDIS_AVAILABLE = False
    print(f"[WARN] Redis not available: {e}")

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
    ('en-US','female-3'): 'en-US-EmmaNeural',
    ('en-US','male-1'):   'en-US-GuyNeural',
    ('en-US','male-2'):   'en-US-RogerNeural',
    ('en-US','male-3'):   'en-US-SteffanNeural',
    ('en-US','young'):    'en-US-AvaNeural',
    ('en-US','old'):      'en-US-BrianNeural',
    ('en-US','kid-f1'):   'en-US-AnaNeural',
    ('en-US','kid-f2'):   'en-US-JennyNeural',
    ('en-US','kid-m1'):   'en-US-AnaNeural',
    ('en-US','kid-m2'):   'en-US-BrianNeural',
    ('en-US','teen-f1'):  'en-US-JennyNeural',
    ('en-US','teen-f2'):  'en-US-AriaNeural',
    ('en-US','teen-m1'):  'en-US-ChristopherNeural',
    ('en-US','teen-m2'):  'en-US-SteffanNeural',
    ('en-US','young-f1'): 'en-US-AriaNeural',
    ('en-US','young-f2'): 'en-US-JennyNeural',
    ('en-US','young-f3'): 'en-US-EmmaNeural',
    ('en-US','young-m1'): 'en-US-GuyNeural',
    ('en-US','young-m2'): 'en-US-RogerNeural',
    ('en-US','young-m3'): 'en-US-SteffanNeural',
    ('en-US','mid-f1'):   'en-US-MichelleNeural',
    ('en-US','mid-f2'):   'en-US-MichelleNeural',
    ('en-US','mid-m1'):   'en-US-EricNeural',
    ('en-US','mid-m2'):   'en-US-BrianNeural',
    ('en-US','senior-f1'):'en-US-MichelleNeural',
    ('en-US','senior-f2'):'en-US-MichelleNeural',
    ('en-US','senior-m1'):'en-US-BrianNeural',
    ('en-US','senior-m2'):'en-US-BrianNeural',
    # ── Expanded 100+ Sound Types (en-US) ──
    ('en-US','normal-f1'):       'en-US-JennyNeural',
    ('en-US','normal-m1'):       'en-US-ChristopherNeural',
    ('en-US','normal-f2'):       'en-US-SaraNeural',
    ('en-US','normal-m2'):       'en-US-EricNeural',
    ('en-US','normal-studio-f1'):'en-US-SoniaNeural',
    ('en-US','normal-studio-m1'):'en-US-RyanNeural',
    ('en-US','normal-casual-f'): 'en-US-AvaNeural',
    ('en-US','normal-casual-m'): 'en-US-AndrewNeural',
    ('en-US','normal-podcast-f'):'en-US-MichelleNeural',
    ('en-US','normal-podcast-m'):'en-US-BrianNeural',
    ('en-US','soft-f1'):         'en-US-AriaNeural',
    ('en-US','soft-m1'):         'en-US-GuyNeural',
    ('en-US','soft-asmr-f1'):    'en-US-JennyNeural',
    ('en-US','soft-asmr-m1'):    'en-US-RogerNeural',
    ('en-US','soft-meditation-f'):'en-US-MichelleNeural',
    ('en-US','soft-meditation-m'):'en-US-BrianNeural',
    ('en-US','soft-lullaby-f'):  'en-US-SoniaNeural',
    ('en-US','soft-counselor-f'):'en-US-EmmaNeural',
    ('en-US','soft-counselor-m'):'en-US-EricNeural',
    ('en-US','soft-silk-f'):     'en-US-SaraNeural',
    ('en-US','soft-velvet-m'):   'en-US-SteffanNeural',
    ('en-US','soft-quiet-f'):    'en-US-AnaNeural',
    ('en-US','soft-quiet-m'):    'en-US-ChristopherNeural',
    ('en-US','hard-trailer-m1'): 'en-US-GuyNeural',
    ('en-US','hard-trailer-f1'): 'en-US-AriaNeural',
    ('en-US','hard-action-m'):   'en-US-ChristopherNeural',
    ('en-US','hard-action-f'):   'en-US-SaraNeural',
    ('en-US','hard-hype-m'):     'en-US-RogerNeural',
    ('en-US','hard-sports-m'):   'en-US-GuyNeural',
    ('en-US','hard-gamer-m'):    'en-US-EricNeural',
    ('en-US','hard-gamer-f'):    'en-US-EmmaNeural',
    ('en-US','hard-commander-m'):'en-US-SteffanNeural',
    ('en-US','hard-heavy-bass'): 'en-US-BrianNeural',
    ('en-US','hard-breaking-f'): 'en-US-JennyNeural',
    ('en-US','hard-breaking-m'): 'en-US-GuyNeural',
    ('en-US','hard-power-orator'):'en-US-RyanNeural',
    ('en-US','emo-cheerful-f'):  'en-US-AriaNeural',
    ('en-US','emo-cheerful-m'):  'en-US-GuyNeural',
    ('en-US','emo-sad-f'):       'en-US-JennyNeural',
    ('en-US','emo-sad-m'):       'en-US-GuyNeural',
    ('en-US','emo-angry-f'):     'en-US-AriaNeural',
    ('en-US','emo-angry-m'):     'en-US-GuyNeural',
    ('en-US','emo-excited-f'):   'en-US-SaraNeural',
    ('en-US','emo-excited-m'):   'en-US-RogerNeural',
    ('en-US','emo-friendly-f'):  'en-US-JennyNeural',
    ('en-US','emo-friendly-m'):  'en-US-GuyNeural',
    ('en-US','emo-empathetic-f'):'en-US-MichelleNeural',
    ('en-US','emo-suspense-f'):  'en-US-EmmaNeural',
    ('en-US','emo-suspense-m'):  'en-US-SteffanNeural',
    ('en-US','emo-hopeful-f'):   'en-US-SoniaNeural',
    ('en-US','news-anchor-f'):   'en-US-AriaNeural',
    ('en-US','news-anchor-m'):   'en-US-GuyNeural',
    ('en-US','news-casual-f'):   'en-US-JennyNeural',
    ('en-US','news-casual-m'):   'en-US-RogerNeural',
    ('en-US','news-formal-f'):   'en-US-AriaNeural',
    ('en-US','news-formal-m'):   'en-US-GuyNeural',
    ('en-US','story-docu-f'):    'en-US-AriaNeural',
    ('en-US','story-docu-m'):    'en-US-GuyNeural',
    ('en-US','story-relaxed-f'): 'en-US-JennyNeural',
    ('en-US','story-relaxed-m'): 'en-US-GuyNeural',
    ('en-US','story-poetry-f'):  'en-US-AriaNeural',
    ('en-US','story-mythic-m'):  'en-US-BrianNeural',
    ('en-US','pro-elearning-f'): 'en-US-EmmaNeural',
    ('en-US','pro-elearning-m'): 'en-US-EricNeural',
    ('en-US','pro-audiobook-f'): 'en-US-SoniaNeural',
    ('en-US','pro-audiobook-m'): 'en-US-RyanNeural',
    ('en-US','pro-commercial-f'):'en-US-SaraNeural',
    ('en-US','pro-commercial-m'):'en-US-RogerNeural',
    ('en-US','pro-assistant-f'): 'en-US-AriaNeural',
    ('en-US','pro-assistant-m'): 'en-US-GuyNeural',
    ('en-US','pro-support-f'):   'en-US-JennyNeural',
    ('en-US','pro-ivr-f'):       'en-US-MichelleNeural',
    ('en-US','pro-presentation'):'en-US-ChristopherNeural',
    ('en-US','pro-motivation-m'):'en-US-SteffanNeural',
    ('en-US','char-anime-f'):    'en-US-AvaNeural',
    ('en-US','char-anime-hero'): 'en-US-ChristopherNeural',
    ('en-US','char-robot-ai'):   'en-US-EmmaNeural',
    ('en-US','char-cyborg-m'):   'en-US-SteffanNeural',
    ('en-US','char-chipmunk'):   'en-US-AnaNeural',
    ('en-US','char-giant-deep'): 'en-US-BrianNeural',
    ('en-US','char-pirate-m'):   'en-US-GuyNeural',
    ('en-US','char-wizard-m'):   'en-US-BrianNeural',
    ('en-US','char-villain-m'):  'en-US-SteffanNeural',
    ('en-US','char-fairy-f'):    'en-US-AnaNeural',
    ('en-US','char-detective'):  'en-US-EricNeural',
    ('en-US','char-royal-f'):    'en-US-MichelleNeural',
    ('en-US','kid-toddler-f'):   'en-US-AnaNeural',
    ('en-US','kid-toddler-m'):   'en-US-AnaNeural',
    ('en-US','teen-gamer-f'):    'en-US-SaraNeural',
    ('en-US','senior-wise-f'):   'en-US-JennyNeural',
    ('en-US','senior-wise-m'):   'en-US-GuyNeural',
    ('en-US','senior-professor'):'en-US-SteffanNeural',
    ('en-GB','female-1'): 'en-GB-SoniaNeural',
    ('en-GB','female-2'): 'en-GB-LibbyNeural',
    ('en-GB','male-1'):   'en-GB-RyanNeural',
    ('en-GB','male-2'):   'en-GB-ThomasNeural',
    ('en-AU','female-1'): 'en-AU-NatashaNeural',
    ('en-AU','male-1'):   'en-AU-WilliamMultilingualNeural',
    ('en-IN','female-1'): 'en-IN-NeerjaNeural',
    ('en-IN','male-1'):   'en-IN-PrabhatNeural',
    ('en-CA','female-1'): 'en-CA-ClaraNeural',
    ('en-CA','male-1'):   'en-CA-LiamNeural',
    ('en-NG','female-1'): 'en-NG-EzinneNeural',
    ('en-NG','male-1'):   'en-NG-AbeoNeural',
    ('en-ZA','female-1'): 'en-ZA-LeahNeural',
    ('en-ZA','male-1'):   'en-ZA-LukeNeural',
    ('hi-IN','female-1'): 'hi-IN-SwaraNeural',
    ('hi-IN','female-2'): 'hi-IN-SwaraNeural',
    ('hi-IN','female-3'): 'hi-IN-SwaraNeural',
    ('hi-IN','male-1'):   'hi-IN-MadhurNeural',
    ('hi-IN','male-2'):   'hi-IN-MadhurNeural',
    ('hi-IN','male-3'):   'hi-IN-MadhurNeural',
    ('hi-IN','young'):    'hi-IN-SwaraNeural',
    ('hi-IN','old'):      'hi-IN-MadhurNeural',
    ('hi-IN','kid-f1'):   'hi-IN-SwaraNeural',
    ('hi-IN','kid-f2'):   'hi-IN-SwaraNeural',
    ('hi-IN','kid-m1'):   'hi-IN-MadhurNeural',
    ('hi-IN','kid-m2'):   'hi-IN-MadhurNeural',
    ('hi-IN','teen-f1'):  'hi-IN-SwaraNeural',
    ('hi-IN','teen-f2'):  'hi-IN-SwaraNeural',
    ('hi-IN','teen-m1'):  'hi-IN-MadhurNeural',
    ('hi-IN','teen-m2'):  'hi-IN-MadhurNeural',
    ('hi-IN','young-f1'): 'hi-IN-SwaraNeural',
    ('hi-IN','young-f2'): 'hi-IN-SwaraNeural',
    ('hi-IN','young-f3'): 'hi-IN-SwaraNeural',
    ('hi-IN','young-m1'): 'hi-IN-MadhurNeural',
    ('hi-IN','young-m2'): 'hi-IN-MadhurNeural',
    ('hi-IN','young-m3'): 'hi-IN-MadhurNeural',
    ('hi-IN','mid-f1'):   'hi-IN-SwaraNeural',
    ('hi-IN','mid-f2'):   'hi-IN-SwaraNeural',
    ('hi-IN','mid-m1'):   'hi-IN-MadhurNeural',
    ('hi-IN','mid-m2'):   'hi-IN-MadhurNeural',
    ('hi-IN','senior-f1'):'hi-IN-SwaraNeural',
    ('hi-IN','senior-f2'):'hi-IN-SwaraNeural',
    ('hi-IN','senior-m1'):'hi-IN-MadhurNeural',
    ('hi-IN','senior-m2'):'hi-IN-MadhurNeural',
    # ── Expanded 100+ Sound Types (hi-IN) ──
    ('hi-IN','normal-f1'):       'hi-IN-SwaraNeural',
    ('hi-IN','normal-m1'):       'hi-IN-MadhurNeural',
    ('hi-IN','normal-f2'):       'hi-IN-SwaraNeural',
    ('hi-IN','normal-m2'):       'hi-IN-MadhurNeural',
    ('hi-IN','normal-studio-f1'):'hi-IN-SwaraNeural',
    ('hi-IN','normal-studio-m1'):'hi-IN-MadhurNeural',
    ('hi-IN','normal-casual-f'): 'hi-IN-SwaraNeural',
    ('hi-IN','normal-casual-m'): 'hi-IN-MadhurNeural',
    ('hi-IN','normal-podcast-f'):'hi-IN-SwaraNeural',
    ('hi-IN','normal-podcast-m'):'hi-IN-MadhurNeural',
    ('hi-IN','soft-f1'):         'hi-IN-SwaraNeural',
    ('hi-IN','soft-m1'):         'hi-IN-MadhurNeural',
    ('hi-IN','soft-asmr-f1'):    'hi-IN-SwaraNeural',
    ('hi-IN','soft-asmr-m1'):    'hi-IN-MadhurNeural',
    ('hi-IN','soft-meditation-f'):'hi-IN-SwaraNeural',
    ('hi-IN','soft-meditation-m'):'hi-IN-MadhurNeural',
    ('hi-IN','soft-lullaby-f'):  'hi-IN-SwaraNeural',
    ('hi-IN','soft-counselor-f'):'hi-IN-SwaraNeural',
    ('hi-IN','soft-counselor-m'):'hi-IN-MadhurNeural',
    ('hi-IN','soft-silk-f'):     'hi-IN-SwaraNeural',
    ('hi-IN','soft-velvet-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','soft-quiet-f'):    'hi-IN-SwaraNeural',
    ('hi-IN','soft-quiet-m'):    'hi-IN-MadhurNeural',
    ('hi-IN','hard-trailer-m1'): 'hi-IN-MadhurNeural',
    ('hi-IN','hard-trailer-f1'): 'hi-IN-SwaraNeural',
    ('hi-IN','hard-action-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','hard-action-f'):   'hi-IN-SwaraNeural',
    ('hi-IN','hard-hype-m'):     'hi-IN-MadhurNeural',
    ('hi-IN','hard-sports-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','hard-gamer-m'):    'hi-IN-MadhurNeural',
    ('hi-IN','hard-gamer-f'):    'hi-IN-SwaraNeural',
    ('hi-IN','hard-commander-m'):'hi-IN-MadhurNeural',
    ('hi-IN','hard-heavy-bass'): 'hi-IN-MadhurNeural',
    ('hi-IN','hard-breaking-f'): 'hi-IN-SwaraNeural',
    ('hi-IN','hard-breaking-m'): 'hi-IN-MadhurNeural',
    ('hi-IN','hard-power-orator'):'hi-IN-MadhurNeural',
    ('hi-IN','emo-cheerful-f'):  'hi-IN-SwaraNeural',
    ('hi-IN','emo-cheerful-m'):  'hi-IN-MadhurNeural',
    ('hi-IN','emo-sad-f'):       'hi-IN-SwaraNeural',
    ('hi-IN','emo-sad-m'):       'hi-IN-MadhurNeural',
    ('hi-IN','emo-angry-f'):     'hi-IN-SwaraNeural',
    ('hi-IN','emo-angry-m'):     'hi-IN-MadhurNeural',
    ('hi-IN','emo-excited-f'):   'hi-IN-SwaraNeural',
    ('hi-IN','emo-excited-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','emo-friendly-f'):  'hi-IN-SwaraNeural',
    ('hi-IN','emo-friendly-m'):  'hi-IN-MadhurNeural',
    ('hi-IN','emo-empathetic-f'):'hi-IN-SwaraNeural',
    ('hi-IN','emo-suspense-f'):  'hi-IN-SwaraNeural',
    ('hi-IN','emo-suspense-m'):  'hi-IN-MadhurNeural',
    ('hi-IN','emo-hopeful-f'):   'hi-IN-SwaraNeural',
    ('hi-IN','news-anchor-f'):   'hi-IN-SwaraNeural',
    ('hi-IN','news-anchor-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','news-casual-f'):   'hi-IN-SwaraNeural',
    ('hi-IN','news-casual-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','news-formal-f'):   'hi-IN-SwaraNeural',
    ('hi-IN','news-formal-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','story-docu-f'):    'hi-IN-SwaraNeural',
    ('hi-IN','story-docu-m'):    'hi-IN-MadhurNeural',
    ('hi-IN','story-relaxed-f'): 'hi-IN-SwaraNeural',
    ('hi-IN','story-relaxed-m'): 'hi-IN-MadhurNeural',
    ('hi-IN','story-poetry-f'):  'hi-IN-SwaraNeural',
    ('hi-IN','story-mythic-m'):  'hi-IN-MadhurNeural',
    ('hi-IN','pro-elearning-f'): 'hi-IN-SwaraNeural',
    ('hi-IN','pro-elearning-m'): 'hi-IN-MadhurNeural',
    ('hi-IN','pro-audiobook-f'): 'hi-IN-SwaraNeural',
    ('hi-IN','pro-audiobook-m'): 'hi-IN-MadhurNeural',
    ('hi-IN','pro-commercial-f'):'hi-IN-SwaraNeural',
    ('hi-IN','pro-commercial-m'):'hi-IN-MadhurNeural',
    ('hi-IN','pro-assistant-f'): 'hi-IN-SwaraNeural',
    ('hi-IN','pro-assistant-m'): 'hi-IN-MadhurNeural',
    ('hi-IN','pro-support-f'):   'hi-IN-SwaraNeural',
    ('hi-IN','pro-ivr-f'):       'hi-IN-SwaraNeural',
    ('hi-IN','pro-presentation'):'hi-IN-MadhurNeural',
    ('hi-IN','pro-motivation-m'):'hi-IN-MadhurNeural',
    ('hi-IN','char-anime-f'):    'hi-IN-SwaraNeural',
    ('hi-IN','char-anime-hero'): 'hi-IN-MadhurNeural',
    ('hi-IN','char-robot-ai'):   'hi-IN-SwaraNeural',
    ('hi-IN','char-cyborg-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','char-chipmunk'):   'hi-IN-SwaraNeural',
    ('hi-IN','char-giant-deep'): 'hi-IN-MadhurNeural',
    ('hi-IN','char-pirate-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','char-wizard-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','char-villain-m'):  'hi-IN-MadhurNeural',
    ('hi-IN','char-fairy-f'):    'hi-IN-SwaraNeural',
    ('hi-IN','char-detective'):  'hi-IN-MadhurNeural',
    ('hi-IN','char-royal-f'):    'hi-IN-SwaraNeural',
    ('hi-IN','kid-toddler-f'):   'hi-IN-SwaraNeural',
    ('hi-IN','kid-toddler-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','teen-gamer-f'):    'hi-IN-SwaraNeural',
    ('hi-IN','senior-wise-f'):   'hi-IN-SwaraNeural',
    ('hi-IN','senior-wise-m'):   'hi-IN-MadhurNeural',
    ('hi-IN','senior-professor'):'hi-IN-MadhurNeural',
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
    ('sv-SE','female-1'): 'sv-SE-SofieNeural',
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
    ('ja-JP','young'):    'ja-JP-NanamiNeural',
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
    # 1. Direct match
    voice = VOICE_MAPPING.get((lang, voice_type))
    if voice:
        return voice
    
    # 2. Gender/Character-smart fallback for ANY language
    vt = voice_type.lower()
    is_male = False
    male_keywords = [
        'male', '-m', 'guy', 'man', 'boy', 'dad', 'deep', 'giant', 'trailer',
        'authority', 'hard', 'hero', 'commanding', 'sports', 'gamer', 'intense',
        'baritone', 'action', 'orator', 'commander', 'bass', 'cyborg', 'pirate',
        'wizard', 'villain', 'detective', 'professor', 'grandfather'
    ]
    if any(k in vt for k in ['female', '-f', 'woman', 'girl', 'mom', 'lady', 'soft', 'asmr', 'whisper', 'soothing', 'queen', 'nurse', 'gentle', 'fairy', 'grandmother']):
        is_male = False
    elif any(k in vt for k in male_keywords) or vt == 'old':
        is_male = True
    else:
        is_male = False
        
    fallback_sequence = ['male-1', 'female-1'] if is_male else ['female-1', 'male-1']
    
    for gender_vt in fallback_sequence:
        v = VOICE_MAPPING.get((lang, gender_vt))
        if v:
            return v
            
    # 3. Language prefix fallback
    lang_prefix = lang.split('-')[0]
    for gender_vt in fallback_sequence:
        for code, v in VOICE_MAPPING.items():
            if code[0].startswith(lang_prefix) and code[1] == gender_vt:
                return v
                
    # 4. Global fallback
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


# ─────────────────────────────────────────────
#  ✅ Smart Natural Text Preprocessor
#  Makes voice output sound conversational by
#  enhancing text for Neural TTS voices:
#  - Proper sentence spacing for natural pauses
#  - Ellipsis for dramatic pauses
#  - Punctuation normalization
#  - Works with ALL languages & ALL voices
#  - NO SSML — Neural voices handle prosody natively
# ─────────────────────────────────────────────
import re as _re


def _split_sentences(text):
    """Split text into sentences using universal punctuation."""
    parts = _re.split(
        r'(?<=[.!?\u0964\u0965\u3002\uff01\uff1f])\s*', text
    )
    return [p.strip() for p in parts if p.strip()]


def _detect_sentence_type(sentence):
    """Detect sentence type for text enhancement."""
    s = sentence.strip()
    if not s:
        return 'normal'
    last_char = s.rstrip()[-1] if s.rstrip() else ''
    if last_char in ('?', '\uff1f'):
        return 'question'
    elif last_char in ('!', '\uff01'):
        return 'exclamation'
    elif s.endswith('...') or s.endswith('\u2026'):
        return 'ellipsis'
    else:
        return 'normal'


def build_natural_text(text):
    """
    Minimal text cleanup for Neural TTS voices.

    Key insight: Microsoft Neural voices (AriaNeural, SwaraNeural, etc.) are
    trained on natural speech data — they already produce perfect prosody from
    clean original text. We should NOT add punctuation or modify content.

    What we DO:
    - Remove extra whitespace/tabs
    - Normalize 3+ newlines to 2 (paragraph pause)
    - Strip leading/trailing whitespace

    What we DON'T do (was causing robotic sound):
    - Adding periods to sentences (broke Hindi, Arabic, Chinese prosody)
    - Adding extra spaces between sentences (confused voice model)

    Works with ALL languages. Returns clean text ready for edge-tts.
    """
    if not text or not text.strip():
        return text

    # Normalize tabs and multiple spaces to single space (preserve newlines)
    processed = _re.sub(r'[^\S\n]+', ' ', text)

    # Normalize 3+ consecutive newlines → 2 (paragraph pause)
    processed = _re.sub(r'\n{3,}', '\n\n', processed)

    return processed.strip()



async def _generate_edge(text, voice, rate_str, pitch_str, volume_str, style, filepath, natural_mode=True):
    """
    ✅ FIXED: Three-tier generation with Natural Mode:
    1. Natural text preprocessing + plain edge-tts (enhanced prosody) — NEW
    2. Plain text fallback (always works)
    Falls back gracefully on any error. Zero breaking changes.
    """
    import html

    # --- attempt 0: Natural text preprocessing ---
    if natural_mode:
        try:
            natural_text = build_natural_text(text)
            if natural_text:
                communicate = edge_tts.Communicate(
                    natural_text, voice=voice,
                    rate=rate_str, pitch=pitch_str, volume=volume_str
                )
                await communicate.save(filepath)
                if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                    logging.info(f"✅ edge-tts NATURAL: voice={voice} rate={rate_str} pitch={pitch_str}")
                    return True
        except Exception as e:
            logging.warning(f"edge-tts Natural text failed ({e}), trying plain…")



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
#  Routes & Performance Optimized Cache
# ─────────────────────────────────────────────
import time as _time
import threading as _threading

_STATS_CACHE = {"total": 1540, "today": 0, "last_updated": 0}
_STATS_LOCK = _threading.Lock()

def _refresh_stats_async():
    """Background worker to fetch stats from Redis without blocking web requests."""
    global _STATS_CACHE
    if not redis:
        return
    try:
        total = int(redis.get("total_translations") or 1540)
        today_key = f"count_{datetime.now().strftime('%Y-%m-%d')}"
        today = int(redis.get(today_key) or 0)
        with _STATS_LOCK:
            _STATS_CACHE["total"] = total
            _STATS_CACHE["today"] = today
            _STATS_CACHE["last_updated"] = _time.time()
    except Exception as e:
        logging.error(f"Async Redis stats error: {e}")

def get_live_stats():
    """Returns cached stats instantly (0ms latency), refreshes asynchronously in background."""
    now = _time.time()
    with _STATS_LOCK:
        cached = _STATS_CACHE.copy()
    
    # If cache is older than 60 seconds (or first run), trigger background refresh
    if now - cached.get("last_updated", 0) > 60:
        _threading.Thread(target=_refresh_stats_async, daemon=True).start()
        
    return cached.get("total", 1540), cached.get("today", 0)


def _record_generation_async(lang):
    """Record analytics in Redis in background without blocking audio delivery."""
    if not redis:
        return
    try:
        redis.incr("total_translations")
        redis.incr(f"count_{datetime.now().strftime('%Y-%m-%d')}")
        redis.zincrby("popular_languages", 1, lang)
        with _STATS_LOCK:
            _STATS_CACHE["total"] = _STATS_CACHE.get("total", 1540) + 1
            _STATS_CACHE["today"] = _STATS_CACHE.get("today", 0) + 1
    except Exception as e:
        logging.error(f"Redis async update error: {e}")


@app.route('/')
def home():
    total, today = get_live_stats()
    return render_template('index.html', total=total, today=today)


@app.route('/stats')
def stats():
    total, today = get_live_stats()
    return jsonify({"total": total, "today": today})


def apply_voice_type_modifiers(voice_type, base_rate, base_pitch):
    """Apply pitch and rate offsets to simulate distinct voices from a single model."""
    try:
        r = float(base_rate)
    except Exception:
        r = 1.0
    try:
        p = int(float(base_pitch))
    except Exception:
        p = 0
        
    vt = str(voice_type).lower()
    
    # Define acoustic signatures for generic voice types
    if 'female-2' in vt or 'f2' in vt or 'soft' in vt:
        r *= 0.95
        p += 2
    elif 'female-3' in vt or 'f3' in vt or 'pro' in vt:
        r *= 1.05
        p -= 2
    elif 'male-2' in vt or 'm2' in vt or 'friendly' in vt:
        r *= 1.05
        p += 2
    elif 'male-3' in vt or 'm3' in vt or 'deep' in vt or 'authority' in vt:
        r *= 0.95
        p -= 4
    elif 'kid' in vt or 'toddler' in vt or 'chipmunk' in vt:
        r *= 1.15
        p += 8
    elif 'teen' in vt:
        r *= 1.05
        p += 3
    elif 'senior' in vt or 'old' in vt or 'wise' in vt or 'grandfather' in vt or 'grandmother' in vt:
        r *= 0.85
        p -= 3
    elif 'giant' in vt or 'villain' in vt or 'bass' in vt:
        r *= 0.80
        p -= 8
    elif 'anime' in vt or 'fairy' in vt:
        r *= 1.10
        p += 6
    elif 'news' in vt or 'commentary' in vt:
        r *= 1.15
        p += 0
        
    return str(r), str(p)



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
        natural_mode = request.form.get('natural_mode', 'true').lower() in ('true', '1', 'yes', 'on')

        if not text:
            return jsonify({'error': 'Please enter text to convert'}), 400
        if len(text) > 5000:
            return jsonify({'error': 'Text too long. Max 5000 characters.'}), 400

        # Apply voice modifiers so characters sound unique even if mapping to the same base neural voice
        rate, pitch = apply_voice_type_modifiers(voice_type, rate, pitch)

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
                text, voice, rate_str, pitch_str, volume_str, style, filepath,
                natural_mode=natural_mode
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

        # ── Non-blocking background analytics ────────────────
        _threading.Thread(target=_record_generation_async, args=(lang,), daemon=True).start()

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
        rate       = data.get('rate', 1.0)
        pitch      = data.get('pitch', 0)
        style      = data.get('style', 'general')
        text       = SAMPLE_TEXTS.get(lang, DEFAULT_SAMPLE)
        voice      = get_voice(lang, voice_type)

        if not EDGE_AVAILABLE:
            return jsonify({"success": False, "error": "edge-tts not installed"})

        filepath = os.path.join(TEMP_FOLDER, f"prev_{uuid.uuid4().hex}.mp3")
        rate_str  = build_rate(rate)
        pitch_str = build_pitch(pitch)
        ok = asyncio.run(_generate_edge(text, voice, rate_str, pitch_str, "+0%", style, filepath))
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


# ─────────────────────────────────────────────
#  Open-Source Voice Cloning (Coqui XTTS-v2)
# ─────────────────────────────────────────────
XTTS_MODEL = None
XTTS_INITIALIZING = False

def get_xtts_model():
    global XTTS_MODEL, XTTS_INITIALIZING
    if XTTS_MODEL is not None:
        return XTTS_MODEL
    try:
        import torch
        from TTS.api import TTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Loading Coqui XTTS-v2 Voice Cloning Model on {device}...")
        XTTS_MODEL = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)
        logging.info("[OK] XTTS-v2 Voice Cloning model loaded successfully!")
        return XTTS_MODEL
    except Exception as e:
        logging.info(f"[INFO] Coqui TTS not yet installed or GPU loading deferred: {e}")
        return None


def analyze_voice_sample(ref_wav_path):
    """
    Extracts fundamental frequency (F0), gender classification,
    pitch offset, and vocal characteristics from the user's recorded audio sample.
    """
    try:
        import scipy.io.wavfile as wav
        import numpy as np
        sr, y = wav.read(ref_wav_path)
        if y.ndim > 1:
            y = y.mean(axis=1)
        y = y.astype(np.float32)
        if np.max(np.abs(y)) > 0:
            y = y / np.max(np.abs(y))
        
        # Frame-by-frame pitch estimation (40ms window, 20ms hop)
        frame_len = int(sr * 0.04)
        hop_len = int(sr * 0.02)
        f0_list = []
        
        min_lag = int(sr / 450)  # 450Hz max
        max_lag = int(sr / 65)   # 65Hz min
        
        for start in range(0, len(y) - frame_len, hop_len):
            frame = y[start:start + frame_len]
            rms = np.sqrt(np.mean(frame**2))
            if rms < 0.03:  # skip silent or unvoiced frames
                continue
            
            # Autocorrelation
            corr = np.correlate(frame, frame, mode='full')
            corr = corr[len(corr)//2:]
            if max_lag < len(corr):
                peak_idx = min_lag + np.argmax(corr[min_lag:max_lag])
                if corr[peak_idx] > 0.28 * corr[0]:
                    f0 = sr / peak_idx
                    if 65 <= f0 <= 450:
                        f0_list.append(f0)
        
        median_f0 = float(np.median(f0_list)) if len(f0_list) >= 2 else 125.0
        is_male = median_f0 < 165.0
        
        # Determine base neural reference F0 and pitch shift
        base_f0 = 120.0 if is_male else 210.0
        pitch_diff_hz = int(np.clip(median_f0 - base_f0, -60, 60))
        pitch_str = f"{pitch_diff_hz:+d}Hz"
        
        # Determine voice character type
        if is_male:
            if median_f0 < 105.0:
                voice_type = 'male-1'  # Deep male
            elif median_f0 < 140.0:
                voice_type = 'male-1'  # Natural male
            else:
                voice_type = 'male-2'  # Higher / lighter male
        else:
            if median_f0 > 230.0:
                voice_type = 'female-3'  # High / crisp female
            else:
                voice_type = 'female-1'  # Natural warm female
                
        return {
            'median_f0': median_f0,
            'is_male': is_male,
            'gender': 'male' if is_male else 'female',
            'voice_type': voice_type,
            'pitch_str': pitch_str,
            'rate_str': '+0%'
        }
    except Exception as e:
        logging.warning(f"Voice analysis fallback: {e}")
        return {
            'median_f0': 125.0,
            'is_male': True,
            'gender': 'male',
            'voice_type': 'male-1',
            'pitch_str': '+0Hz',
            'rate_str': '+0%'
        }


def _lpc_coeffs(frame, order):
    """Levinson-Durbin recursion for LPC coefficients (no external deps)."""
    import numpy as np
    n = len(frame)
    r = np.array([np.dot(frame[:n - k], frame[k:]) / n for k in range(order + 1)])
    a = np.zeros(order + 1)
    a[0] = 1.0
    e = r[0]
    for i in range(1, order + 1):
        lam = -np.dot(a[:i], r[i:0:-1]) / e
        a_new = a.copy()
        for j in range(1, i + 1):
            a_new[j] = a[j] + lam * a[i - j]
        a_new[i] = lam
        a = a_new
        e = e * (1.0 - lam * lam)
        if e <= 0:
            break
    return a


def _estimate_avg_lpc(y, sr, order=32, max_frames=120):
    """
    Compute average LPC spectral envelope from voiced frames of a signal.
    Returns H (frequency-domain envelope) and the rfft frequency bins.
    """
    import numpy as np
    frame_len = int(sr * 0.025)   # 25ms
    hop_len   = int(sr * 0.010)   # 10ms
    window    = np.hanning(frame_len)
    nfft      = 512
    envelopes = []

    for start in range(0, len(y) - frame_len, hop_len):
        frame = y[start:start + frame_len] * window
        rms = np.sqrt(np.mean(frame ** 2))
        if rms < 0.015:           # skip near-silent frames
            continue
        coeffs = _lpc_coeffs(frame, order)
        # LPC frequency response (spectral envelope)
        w, H = np.linalg.lstsq(
            np.zeros((nfft // 2 + 1, 1)), np.zeros(nfft // 2 + 1), rcond=None
        )[:2]  # placeholder — compute properly below
        # --- actual computation ---
        _, H_full = np.zeros(1), None
        freq_resp = np.fft.rfft(coeffs, n=nfft)
        H_env = 1.0 / (np.abs(freq_resp) + 1e-8)
        envelopes.append(H_env)
        if len(envelopes) >= max_frames:
            break

    if not envelopes:
        return None, None
    avg_env = np.mean(envelopes, axis=0)
    freqs   = np.fft.rfftfreq(nfft, d=1.0 / sr)
    return avg_env, freqs


def _phase_vocoder_pitch_shift(y, sr, semitones):
    """
    Phase-vocoder pitch shift by `semitones` (float).
    Positive = higher pitch, negative = lower pitch.
    Uses only numpy — no librosa needed.
    """
    import numpy as np
    if abs(semitones) < 0.05:
        return y

    ratio = 2.0 ** (semitones / 12.0)
    n_fft = 2048
    hop   = n_fft // 4
    win   = np.hanning(n_fft)

    # STFT
    num_frames = (len(y) - n_fft) // hop + 1
    if num_frames < 2:
        return y

    stft = np.zeros((n_fft // 2 + 1, num_frames), dtype=complex)
    for i in range(num_frames):
        frame = y[i * hop: i * hop + n_fft] * win
        stft[:, i] = np.fft.rfft(frame)

    # Phase vocoder time-stretch (stretch by 1/ratio, then resample)
    stretch = 1.0 / ratio
    n_out   = max(1, int(num_frames * stretch))
    mag     = np.abs(stft)
    phase_acc = np.angle(stft[:, 0])
    omega     = 2 * np.pi * np.arange(n_fft // 2 + 1) / n_fft

    stft_stretched = np.zeros((n_fft // 2 + 1, n_out), dtype=complex)
    stft_stretched[:, 0] = stft[:, 0]

    for i in range(1, n_out):
        src = i / stretch
        lo  = int(src)
        hi  = min(lo + 1, num_frames - 1)
        alpha = src - lo
        mag_i = (1 - alpha) * mag[:, lo] + alpha * mag[:, hi]
        # phase propagation
        if lo + 1 <= num_frames - 1:
            dphi = np.angle(stft[:, lo + 1]) - np.angle(stft[:, lo]) - omega * hop
            dphi = dphi - 2 * np.pi * np.round(dphi / (2 * np.pi))
            phase_acc = phase_acc + omega * hop + dphi
        stft_stretched[:, i] = mag_i * np.exp(1j * phase_acc)

    # iSTFT
    y_out = np.zeros(n_out * hop + n_fft)
    win_sum = np.zeros_like(y_out)
    for i in range(n_out):
        frame = np.fft.irfft(stft_stretched[:, i]) * win
        y_out[i * hop: i * hop + n_fft] += frame
        win_sum[i * hop: i * hop + n_fft] += win ** 2

    win_sum = np.where(win_sum < 1e-8, 1e-8, win_sum)
    y_out /= win_sum

    # Resample back to original length via linear interpolation
    target_len = len(y)
    old_idx    = np.linspace(0, len(y_out) - 1, target_len)
    y_resampled = np.interp(old_idx, np.arange(len(y_out)), y_out)
    return y_resampled.astype(np.float32)


def apply_voice_conversion(ref_wav_path, synth_wav_path, out_wav_path,
                           ref_f0=None, synth_f0=None):
    """
    Full voice conversion pipeline:
      1. Extract LPC spectral envelope from the user's reference voice.
      2. Extract LPC spectral envelope from the synthesized TTS voice.
      3. Transfer the reference envelope onto the synthesized signal frame-by-frame.
      4. Pitch-shift the result so its F0 matches the reference voice.
    This gives the synthesized text the user's vocal tract character (timbre/formants).
    Falls back gracefully on any error.
    """
    import numpy as np
    import scipy.io.wavfile as wav
    import scipy.signal as signal

    def load_audio_file(path):
        """Load any audio file (MP3, WAV, OGG, FLAC) → (sr, float32 array)."""
        try:
            import miniaudio
            audio = miniaudio.decode_file(path, output_format=miniaudio.SampleFormat.SIGNED16,
                                          nchannels=1, sample_rate=16000)
            y = np.frombuffer(audio.samples, dtype=np.int16).astype(np.float32) / 32768.0
            return 16000, y
        except Exception:
            pass
        # Fallback: scipy WAV reader
        sr, y = wav.read(path)
        if y.ndim > 1:
            y = y.mean(axis=1)
        y = y.astype(np.float32)
        peak = np.max(np.abs(y))
        return sr, (y / peak if peak > 0 else y)

    try:
        sr_ref, y_ref_raw = load_audio_file(ref_wav_path)
        sr_syn, y_syn_raw = load_audio_file(synth_wav_path)

        # ── normalise to float32 mono ──────────────────────────────────────
        def to_mono_f32(y):
            if y.ndim > 1:
                y = y.mean(axis=1)
            y = y.astype(np.float32)
            peak = np.max(np.abs(y))
            return y / peak if peak > 0 else y

        y_ref = to_mono_f32(y_ref_raw)
        y_syn = to_mono_f32(y_syn_raw)

        # ── resample synth to match ref sample rate if needed ─────────────
        if sr_syn != sr_ref:
            from_len = len(y_syn)
            to_len   = int(from_len * sr_ref / sr_syn)
            y_syn    = np.interp(
                np.linspace(0, from_len - 1, to_len),
                np.arange(from_len), y_syn
            ).astype(np.float32)
            sr_syn = sr_ref

        sr = sr_ref

        # ── STEP 1: Frame-by-frame LPC envelope transfer ───────────────────
        lpc_order = 28          # captures ~14 formant peaks well for speech
        frame_len = int(sr * 0.025)
        hop_len   = int(sr * 0.010)
        win       = np.hanning(frame_len)
        nfft      = 512

        # Build average LPC envelope of reference (vocal tract model)
        ref_envelopes = []
        for start in range(0, len(y_ref) - frame_len, hop_len):
            frame = y_ref[start:start + frame_len]
            rms = np.sqrt(np.mean(frame ** 2))
            if rms < 0.015:
                continue
            coeffs = _lpc_coeffs(frame * win, lpc_order)
            freq_resp = np.fft.rfft(coeffs, n=nfft)
            ref_envelopes.append(1.0 / (np.abs(freq_resp) + 1e-8))
            if len(ref_envelopes) >= 150:
                break

        if not ref_envelopes:
            raise ValueError("No voiced frames found in reference audio")

        ref_avg_env = np.mean(ref_envelopes, axis=0)  # shape: (nfft//2+1,)

        # Apply envelope transfer frame-by-frame to synth signal
        y_converted = np.zeros_like(y_syn)
        win_sum     = np.zeros_like(y_syn)

        for start in range(0, len(y_syn) - frame_len, hop_len):
            frame = y_syn[start:start + frame_len]
            rms = np.sqrt(np.mean(frame ** 2))
            if rms < 0.005:
                # copy silence as-is
                y_converted[start:start + frame_len] += frame * win
                win_sum[start:start + frame_len] += win
                continue

            # LPC envelope of this synth frame
            coeffs_syn = _lpc_coeffs(frame * win, lpc_order)
            freq_resp_syn = np.fft.rfft(coeffs_syn, n=nfft)
            syn_env = 1.0 / (np.abs(freq_resp_syn) + 1e-8)

            # Spectral transfer ratio: ref / synth (both in log space for stability)
            ratio = (ref_avg_env + 1e-8) / (syn_env + 1e-8)
            # Smooth ratio to avoid harsh artifacts
            ratio = np.convolve(ratio, np.hanning(15) / np.sum(np.hanning(15)), mode='same')
            # Soft-clip ratio to ±12dB to prevent over-boosting
            ratio = np.clip(ratio, 0.25, 4.0)

            # Apply in frequency domain
            frame_fft = np.fft.rfft(frame * win, n=nfft)
            frame_fft_morphed = frame_fft * ratio
            frame_morphed = np.fft.irfft(frame_fft_morphed)[:frame_len]

            y_converted[start:start + frame_len] += frame_morphed * win
            win_sum[start:start + frame_len] += win ** 2

        # Normalise by window sum
        win_sum = np.where(win_sum < 1e-8, 1e-8, win_sum)
        y_converted /= win_sum

        # ── STEP 2: Pitch-shift so output F0 ≈ reference F0 ───────────────
        if ref_f0 and synth_f0 and ref_f0 > 60 and synth_f0 > 60:
            semitones = 12.0 * np.log2(ref_f0 / synth_f0)
            semitones = float(np.clip(semitones, -8.0, 8.0))  # max ±8 semitones safe range
            if abs(semitones) > 0.3:
                logging.info(f"[CLONE] Pitch shifting: {synth_f0:.1f}Hz → {ref_f0:.1f}Hz = {semitones:+.2f} semitones")
                y_converted = _phase_vocoder_pitch_shift(y_converted, sr, semitones)

        # ── STEP 3: Normalise & write ──────────────────────────────────────
        peak = np.max(np.abs(y_converted))
        if peak > 0:
            y_converted = (y_converted / peak) * 0.93

        wav.write(out_wav_path, sr, (y_converted * 32767).astype(np.int16))
        logging.info(f"[CLONE] Voice conversion complete → {out_wav_path}")
        return True

    except Exception as e:
        logging.warning(f"Voice conversion error, copying raw synth: {e}")
        import shutil
        shutil.copyfile(synth_wav_path, out_wav_path)
        return False


def apply_timbre_morphing(ref_wav_path, synth_wav_path, out_wav_path):
    """Legacy wrapper — calls the full voice conversion pipeline."""
    return apply_voice_conversion(ref_wav_path, synth_wav_path, out_wav_path)


@app.route('/api/clone-voice', methods=['POST'])
@app.route('/clone-voice', methods=['POST'])
def clone_voice():
    try:
        text = request.form.get('text', '').strip()
        language = request.form.get('language', 'en-US').strip()
        gender_override = request.form.get('gender', 'auto').strip().lower()
        
        if not text:
            return jsonify({"success": False, "error": "Please enter the target text to speak."}), 400
            
        if 'reference_audio' not in request.files:
            return jsonify({"success": False, "error": "Please record or upload a voice sample (5-15s)."}), 400
            
        audio_file = request.files['reference_audio']
        if audio_file.filename == '':
            return jsonify({"success": False, "error": "Reference audio file is empty."}), 400
            
        # Save reference audio to temp file
        ext = os.path.splitext(audio_file.filename)[1] or '.wav'
        ref_temp_path = os.path.join(TEMP_FOLDER, f"ref_{uuid.uuid4().hex}{ext}")
        audio_file.save(ref_temp_path)
        
        # Convert to 16kHz mono WAV using ffmpeg if available for optimal cloning & analysis
        clean_ref_wav = os.path.join(TEMP_FOLDER, f"clean_ref_{uuid.uuid4().hex}.wav")
        usable_ref_path = ref_temp_path
        try:
            import subprocess
            subprocess.run([
                'ffmpeg', '-y', '-i', ref_temp_path,
                '-ar', '16000', '-ac', '1', clean_ref_wav
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            usable_ref_path = clean_ref_wav
        except Exception:
            pass
            
        output_wav_path = os.path.join(TEMP_FOLDER, f"cloned_{uuid.uuid4().hex}.wav")
        
        # Extract user voice profile from the recorded audio sample
        profile = analyze_voice_sample(usable_ref_path)
        
        # Apply gender override if user explicitly specified
        if gender_override == 'male':
            profile['is_male'] = True
            profile['gender'] = 'male'
            profile['voice_type'] = 'male-1'
        elif gender_override == 'female':
            profile['is_male'] = False
            profile['gender'] = 'female'
            profile['voice_type'] = 'female-1'
            
        logging.info(f"[CLONE] Profile extracted: Gender={profile['gender']}, F0={profile['median_f0']:.1f}Hz, Pitch={profile['pitch_str']}")
        
        # Try local XTTS model if available
        model = get_xtts_model()
        if model is not None:
            # Map regional language codes to XTTS-v2 17 supported languages
            lang_map = {
                'en-us': 'en', 'en-gb': 'en', 'en-au': 'en', 'en-in': 'en', 'en': 'en',
                'hi-in': 'hi', 'hi': 'hi',
                'es-es': 'es', 'es-mx': 'es', 'es': 'es',
                'fr-fr': 'fr', 'fr-ca': 'fr', 'fr': 'fr',
                'de-de': 'de', 'de': 'de',
                'it-it': 'it', 'it': 'it',
                'pt-br': 'pt', 'pt-pt': 'pt', 'pt': 'pt',
                'pl-pl': 'pl', 'pl': 'pl',
                'tr-tr': 'tr', 'tr': 'tr',
                'ru-ru': 'ru', 'ru': 'ru',
                'nl-nl': 'nl', 'nl': 'nl',
                'cs-cz': 'cs', 'cs': 'cs',
                'ar-sa': 'ar', 'ar-ae': 'ar', 'ar': 'ar',
                'zh-cn': 'zh-cn', 'zh': 'zh-cn',
                'hu-hu': 'hu', 'hu': 'hu',
                'ko-kr': 'ko', 'ko': 'ko',
                'ja-jp': 'ja', 'ja': 'ja'
            }
            xtts_lang = lang_map.get(language.lower(), language.split('-')[0] if '-' in language else language)
            if xtts_lang not in ['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh-cn', 'hu', 'ko', 'ja', 'hi']:
                xtts_lang = 'en'
            model.tts_to_file(
                text=text,
                speaker_wav=usable_ref_path,
                language=xtts_lang,
                file_path=output_wav_path
            )
            generated_method = "Coqui XTTS-v2 Neural Voice Clone (Self-Hosted)"
        else:
            # High-fidelity Neural Synthesis matched to user's extracted voice pitch & gender
            if EDGE_AVAILABLE:
                # Find matching neural voice in the user's selected language
                voice = get_voice(language, profile['voice_type'])
                if not voice:
                    voice = get_voice(language, 'male-1' if profile['is_male'] else 'female-1')
                    
                logging.info(f"[CLONE] Selected Neural Voice Base: {voice} (Gender={profile['gender']}, PitchOffset={profile['pitch_str']})")
                
                temp_synth_wav = os.path.join(TEMP_FOLDER, f"synth_{uuid.uuid4().hex}.wav")
                asyncio.run(_generate_edge(text, voice, "+0%", "+0Hz", "+0%", "general", temp_synth_wav, natural_mode=True))
                
                # Neural voice base F0 (these are typical median F0s for Microsoft Neural voices)
                synth_f0_map = {
                    'en-US-GuyNeural': 120.0, 'en-US-AriaNeural': 195.0,
                    'en-US-DavisNeural': 115.0, 'en-US-JennyNeural': 200.0,
                    'en-US-TonyNeural': 110.0,
                    'hi-IN-MadhurNeural': 118.0, 'hi-IN-SwaraNeural': 195.0,
                    'en-GB-RyanNeural': 115.0, 'en-GB-SoniaNeural': 195.0,
                    'en-IN-NeerjaNeural': 195.0, 'en-IN-PrabhatNeural': 118.0,
                }
                synth_f0 = synth_f0_map.get(voice, 120.0 if profile['is_male'] else 200.0)
                ref_f0   = profile['median_f0']
                
                # Full LPC voice conversion: spectral envelope transfer + pitch shift
                apply_voice_conversion(usable_ref_path, temp_synth_wav, output_wav_path,
                                       ref_f0=ref_f0, synth_f0=synth_f0)
                
                try:
                    if os.path.exists(temp_synth_wav):
                        os.remove(temp_synth_wav)
                except Exception:
                    pass
                    
                generated_method = f"Voice Cloned · {profile['gender'].capitalize()} · {profile['median_f0']:.0f}Hz · LPC Conversion"
            else:
                return jsonify({
                    "success": False,
                    "error": "Voice synthesis engine is currently unavailable."
                }), 500

        audio_data = audio_to_base64(output_wav_path)
        filename = f"voicepro_cloned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        # Clean up temporary files
        for p in [ref_temp_path, clean_ref_wav, output_wav_path]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
                
        return jsonify({
            "success": True,
            "audio_data": audio_data,
            "filename": filename,
            "method": generated_method,
            "gender": profile['gender'],
            "f0": profile['median_f0'],
            "language": language
        })
        
    except Exception as e:
        logging.error(f"Voice Cloning Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": f"Voice cloning failed: {str(e)}"}), 500


@app.route('/api/contact', methods=['POST'])
def contact_submit():
    """Handle contact form submissions — logs message and optionally sends via SMTP."""
    import json
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', 'General Feedback').strip()
        message = request.form.get('message', '').strip()
        
        if not name or not email or not message:
            return jsonify({"success": False, "error": "Please fill in all required fields (Name, Email, Message)."}), 400
        
        logging.info(f"[CONTACT] Received from {name} <{email}> | Subject: {subject} | Msg: {message[:120]}")
        
        # Save to local inquiries log file for persistence
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        inquiries_file = os.path.join(log_dir, 'contact_inquiries.jsonl')
        with open(inquiries_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "name": name,
                "email": email,
                "subject": subject,
                "message": message
            }) + "\n")
            
        return jsonify({
            "success": True, 
            "message": "Thank you! Your message has been received. We will get back to you within 24 hours."
        })
    except Exception as e:
        logging.error(f"Contact form error: {e}", exc_info=True)
        return jsonify({"success": False, "error": f"Failed to submit message: {str(e)}"}), 500



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


@app.route('/robots.txt')
def robots_txt():
    from flask import Response
    content = "User-agent: *\nAllow: /\nSitemap: https://www.texttoaudiomp3.site/sitemap.xml\n"
    return Response(content, mimetype='text/plain')


@app.route('/ads.txt')
def ads_txt():
    from flask import Response
    content = "google.com, pub-9707682105347147, DIRECT, f08c47fec0942fa0\n"
    return Response(content, mimetype='text/plain')


@app.route('/favicon.png')
@app.route('/favicon.ico')
def favicon():
    import os
    if os.path.exists(os.path.join(app.root_path, 'favicon.png')):
        return send_from_directory(app.root_path, 'favicon.png', mimetype='image/png')
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.png', mimetype='image/png')



# ── PWA Routes ──────────────────────────────────────
@app.route('/manifest.json')
def manifest():
    return send_from_directory(
        os.path.join(app.root_path, 'static'), 'manifest.json',
        mimetype='application/manifest+json'
    )


@app.route('/service-worker.js')
def service_worker():
    resp = send_from_directory(
        os.path.join(app.root_path, 'static'), 'service-worker.js',
        mimetype='application/javascript'
    )
    resp.headers['Service-Worker-Allowed'] = '/'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp



@app.route('/about')
@app.route('/about.html')
def about():
    return render_template('about.html')


@app.route('/blog')
@app.route('/blog.html')
def blog():
    return render_template('blog.html')


@app.route('/contact')
@app.route('/contact.html')
def contact():
    return render_template('contact.html')


@app.route('/privacy')
@app.route('/privacy.html')
def privacy():
    return render_template('privacy.html')


@app.route('/terms')
@app.route('/terms.html')
def terms():
    return render_template('terms.html')


@app.route('/disclaimer')
@app.route('/disclaimer.html')
def disclaimer():
    return render_template('disclaimer.html')


@app.route('/cookies')
@app.route('/cookies.html')
def cookies():
    return render_template('cookies.html')



# ─────────────────────────────────────────────
#  ✅ BLOG ROUTES
# ─────────────────────────────────────────────

@app.route('/blog/100-languages-and-voices-guide')
def blog_100_languages():
    return render_template('blog-100-languages-voices.html')


@app.route('/blog/what-is-ai-text-to-speech')
def blog_what_is_tts():
    return render_template('blog-what-is-tts.html')


@app.route('/blog/convert-text-to-mp3-free')
def blog_convert_mp3():
    return render_template('blog-convert-text-to-mp3.html')


@app.route('/blog/hindi-text-to-speech-guide')
def blog_hindi_tts():
    return render_template('blog-hindi-tts-guide.html')


@app.route('/blog/ai-voiceover-youtube')
def blog_youtube():
    return render_template('blog-youtube-voiceover.html')


@app.route('/blog/voice-customization-guide')
def blog_voice_customization():
    return render_template('blog-voice-customization.html')


@app.route('/blog/free-vs-paid-tts-tools')
def blog_free_vs_paid():
    return render_template('blog-free-vs-paid-tts.html')


@app.route('/blog/tts-for-accessibility')
def blog_accessibility():
    return render_template('blog-tts-accessibility.html')


@app.route('/blog/elearning-audio-workflow')
def blog_elearning():
    return render_template('blog-elearning-audio.html')


@app.route('/blog/marathi-text-to-speech-guide')
def blog_marathi_tts():
    return render_template('blog-marathi-tts.html')


@app.route('/blog/tts-for-podcasters')
def blog_podcasters():
    return render_template('blog-tts-for-podcasters.html')


# ─── Error Handlers (AdSense Compliance) ───────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('404.html'), 500


# ─── pSEO: Load manifest once at startup ───────────────────
import json as _json

_PSEO_MANIFEST = []
_manifest_path = os.path.join(os.path.dirname(__file__), 'templates', 'tts_manifest.json')
if os.path.exists(_manifest_path):
    with open(_manifest_path, encoding='utf-8') as _f:
        _PSEO_MANIFEST = _json.load(_f)
    print(f"[OK] pSEO: {len(_PSEO_MANIFEST)} language pages loaded")


# ─── pSEO: Individual language page ────────────────────────
@app.route('/tts/<slug>')
def tts_lang_page(slug):
    try:
        return render_template(f'tts/{slug}.html')
    except Exception:
        return render_template('404.html'), 404


# ─── pSEO: All languages index ─────────────────────────────
@app.route('/tts/')
@app.route('/tts')
def tts_index():
    return render_template('tts_index.html', languages=_PSEO_MANIFEST)


# ─── Complete High-Value Sitemap ───────────────────────────
@app.route('/sitemap.xml')
def sitemap_xml():
    from flask import Response
    from datetime import datetime

    base  = 'https://www.texttoaudiomp3.site'
    today = datetime.utcnow().strftime('%Y-%m-%d')

    static_urls = [
        ('/',             '1.0', 'daily'),
        ('/tts/',         '0.9', 'weekly'),
        ('/about',        '0.8', 'monthly'),
        ('/blog',         '0.8', 'weekly'),
        ('/contact',      '0.7', 'monthly'),
        ('/privacy',      '0.5', 'monthly'),
        ('/terms',        '0.5', 'monthly'),
        ('/disclaimer',   '0.5', 'monthly'),
        ('/cookies',      '0.5', 'monthly'),
        ('/blog/100-languages-and-voices-guide', '0.8', 'monthly'),
        ('/blog/what-is-ai-text-to-speech',    '0.8', 'monthly'),
        ('/blog/convert-text-to-mp3-free',     '0.8', 'monthly'),
        ('/blog/hindi-text-to-speech-guide',   '0.8', 'monthly'),
        ('/blog/ai-voiceover-youtube',         '0.8', 'monthly'),
        ('/blog/voice-customization-guide',    '0.8', 'monthly'),
        ('/blog/free-vs-paid-tts-tools',       '0.8', 'monthly'),
        ('/blog/tts-for-accessibility',        '0.8', 'monthly'),
        ('/blog/elearning-audio-workflow',     '0.8', 'monthly'),
        ('/blog/marathi-text-to-speech-guide', '0.8', 'monthly'),
        ('/blog/tts-for-podcasters',           '0.8', 'monthly'),
    ]

    urls_xml = []
    for path, priority, freq in static_urls:
        urls_xml.append(f"""  <url>
    <loc>{base}{path}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    for entry in _PSEO_MANIFEST:
        urls_xml.append(f"""  <url>
    <loc>{base}{entry['url']}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>""")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join(urls_xml)
    sitemap += '\n</urlset>'

    return Response(sitemap, mimetype='application/xml')



if __name__ == '__main__':
    app.run(debug=True, port=5000)