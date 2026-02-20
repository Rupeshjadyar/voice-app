from flask import Flask, render_template, request, jsonify
import os
import uuid
import asyncio
from datetime import datetime
import base64
from upstash_redis import Redis

# TTS Libraries
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

app = Flask(__name__)

# Redis Connection (Works automatically on Vercel)
try:
    redis = Redis.from_env()
except Exception:
    redis = None

# Vercel fix: Use /tmp for temporary audio processing
TEMP_FOLDER = "/tmp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Language & Voice Configurations
VOICE_MAPPING = {
    ('hi', 'male1'): 'hi-IN-MadhurNeural',
    ('hi', 'male2'): 'hi-IN-MadhurNeural',
    ('hi', 'female1'): 'hi-IN-SwaraNeural',
    ('hi', 'female2'): 'hi-IN-NeerjaNeural',
    ('hi', 'emotional'): 'hi-IN-NeerjaNeural',
    ('en', 'male1'): 'en-US-GuyNeural',
    ('en', 'male2'): 'en-US-DavisNeural',
    ('en', 'female1'): 'en-US-AriaNeural',
    ('en', 'female2'): 'en-US-JennyNeural',
    ('en-uk', 'female1'): 'en-GB-SoniaNeural',
    ('pa', 'male1'): 'pa-IN-GurpreetNeural',
    ('ur', 'female1'): 'ur-PK-GulNeural',
    ('bn', 'female1'): 'bn-IN-TanishaaNeural',
    ('te', 'female1'): 'te-IN-ShrutiNeural',
    ('ta', 'female1'): 'ta-IN-PallaviNeural',
    ('default'): 'en-US-AriaNeural'
}
DEFAULT_VOICE = 'en-US-AriaNeural'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/stats')
def stats():
    if redis:
        try:
            total = redis.get("total_translations") or 0
            today = redis.get(f"count_{datetime.now().date()}") or 0
            return jsonify({'total': int(total), 'today': int(today)})
        except:
            pass
    return jsonify({'total': 'Live', 'today': 'Active'})

@app.route('/convert', methods=['POST'])
def convert():
    if not EDGE_AVAILABLE and not GTTS_AVAILABLE:
        return jsonify({'error': 'No TTS library installed'}), 500

    try:
        text = request.form.get('text', '').strip()
        lang = request.form.get('language', 'hi')
        vtype = request.form.get('voice_type', 'female1')
        rate = request.form.get('rate', '0')
        pitch = request.form.get('pitch', '0')

        if not text:
            return jsonify({'error': 'Please enter some text!'}), 400
        
        voice = VOICE_MAPPING.get((lang, vtype), VOICE_MAPPING.get((lang, 'female1'), DEFAULT_VOICE))
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(TEMP_FOLDER, filename)
        success = False

        if EDGE_AVAILABLE:
            try:
                async def generate():
                    comm = edge_tts.Communicate(
                        text, voice,
                        rate=f"{rate}%" if rate.startswith(('-', '+')) else f"+{rate}%",
                        pitch=f"{pitch}Hz" if pitch.startswith(('-', '+')) else f"+{pitch}Hz"
                    )
                    await comm.save(filepath)
                asyncio.run(generate())
                success = True
            except: pass

        if not success and GTTS_AVAILABLE:
            try:
                g_lang = lang if len(lang) == 2 else 'en'
                tts = gTTS(text, lang=g_lang)
                tts.save(filepath)
                success = True
            except: pass

        if not success or not os.path.exists(filepath):
            return jsonify({'error': 'Failed to generate audio'}), 500

        # Increment Stats in Redis
        if redis:
            try:
                redis.incr("total_translations")
                redis.incr(f"count_{datetime.now().date()}")
            except: pass

        with open(filepath, "rb") as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')

        os.remove(filepath)
        return jsonify({
            'success': True,
            'audio_data': f"data:audio/mp3;base64,{b64}",
            'filename': f"voice_{datetime.now().strftime('%H%M')}.mp3"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)