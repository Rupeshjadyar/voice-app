from flask import Flask, render_template, request, jsonify
import os
import uuid
import asyncio
from datetime import datetime
import base64
import json

# TTS Libraries
try:
    import edge_tts
    EDGE_AVAILABLE = True
    print("Edge-TTS: Available")
except ImportError:
    EDGE_AVAILABLE = False
    print("Edge-TTS: Not installed")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
    print("gTTS: Available")
except ImportError:
    GTTS_AVAILABLE = False
    print("gTTS: Not installed")

app = Flask(__name__)

# Folders
TEMP_FOLDER = "/tmp"
os.makedirs(TEMP_FOLDER, exist_ok=True)
STATS_FILE = "stats.json"

# Language & Voice Configurations
LANGUAGES = {
    'hi': '🇮🇳 Hindi', 'bn': '🇧🇩 Bengali', 'te': '🇮🇳 Telugu', 'ta': '🇮🇳 Tamil',
    'mr': '🇮🇳 Marathi', 'gu': '🇮🇳 Gujarati', 'kn': '🇮🇳 Kannada', 'ml': '🇮🇳 Malayalam',
    'pa': '🇮🇳 Punjabi', 'ur': '🇵🇰 Urdu', 'en': '🇺🇸 English (US)', 'en-uk': '🇬🇧 English (UK)',
    'es': '🇪🇸 Spanish', 'fr': '🇫🇷 French', 'de': '🇩🇪 German', 'ar': '🇸🇦 Arabic',
}

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

# --- Analytics Functions ---
def load_stats():
    if not os.path.exists(STATS_FILE):
        return {'total': 0, 'today': 0, 'date': str(datetime.now().date())}
    
    with open(STATS_FILE, 'r') as f:
        data = json.load(f)
    
    # Reset 'today' if the date has changed
    today_date = str(datetime.now().date())
    if data.get('date') != today_date:
        data['today'] = 0
        data['date'] = today_date
        save_stats(data)
        
    return data

def save_stats(data):
    with open(STATS_FILE, 'w') as f:
        json.dump(data, f)

def increment_usage():
    data = load_stats()
    data['total'] += 1
    data['today'] += 1
    save_stats(data)
# -----------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/stats')
def stats():
    return jsonify(load_stats())

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
        if len(text) > 5000:
            return jsonify({'error': 'Text is too long (Max 5000 chars)'}), 500

        voice = VOICE_MAPPING.get((lang, vtype), VOICE_MAPPING.get((lang, 'female1'), DEFAULT_VOICE))
        print(f"Voice: {voice} | Rate: {rate}% | Pitch: {pitch}Hz | Lang: {lang}")

        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(TEMP_FOLDER, filename)
        success = False

        # Edge-TTS (Preferred)
        if EDGE_AVAILABLE:
            try:
                async def generate():
                    comm = edge_tts.Communicate(
                        text,
                        voice,
                        rate=f"{rate}%" if rate.startswith(('-', '+')) else f"+{rate}%",
                        pitch=f"{pitch}Hz" if pitch.startswith(('-', '+')) else f"+{pitch}Hz"
                    )
                    await comm.save(filepath)
                asyncio.run(generate())
                success = True
                print("Edge-TTS → OK")
            except Exception as e:
                print(f"Edge-TTS error: {e}")
                if os.path.exists(filepath):
                    os.remove(filepath)

        # gTTS Fallback
        if not success and GTTS_AVAILABLE:
            try:
                g_lang = lang if len(lang) == 2 else 'en'
                tts = gTTS(text, lang=g_lang, slow=False)
                tts.save(filepath)
                success = True
                print("gTTS fallback → OK")
            except Exception as e:
                print(f"gTTS error: {e}")

        if not success or not os.path.exists(filepath) or os.path.getsize(filepath) < 200:
            return jsonify({'error': 'Failed to generate audio'}), 500

        # Increment Stats only on success
        increment_usage()

        # Send audio
        with open(filepath, "rb") as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')

        # Cleanup
        try:
            os.remove(filepath)
        except:
            pass

        return jsonify({
            'success': True,
            'audio_data': f"data:audio/mp3;base64,{b64}",
            'filename': f"voice_{datetime.now().strftime('%Y%m%d_%H%M')}.mp3"
        })

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Ultimate TTS running...")
    print(f"Edge-TTS: {EDGE_AVAILABLE} | gTTS: {GTTS_AVAILABLE}")
    app.run(debug=True, port=5000)



    