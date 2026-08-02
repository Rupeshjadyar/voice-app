import re

regions = {
    "🇮🇳 South Asia (India)": ["Hindi (India)", "Marathi (India)", "Gujarati (India)", "Tamil (India)", "Telugu (India)", "Kannada (India)", "Malayalam (India)", "Bengali (India)", "Punjabi (India)", "Odia (India)", "English (India)"],
    "🌏 South Asia (Others)": ["Bengali (Bangladesh)", "Urdu (Pakistan)", "Nepali (Nepal)", "Sinhala (Sri Lanka)"],
    "🗣️ English Variants": ["English (USA)", "English (UK)", "English (Australia)", "English (Canada)", "English (South Africa)", "English (Nigeria)"],
    "💃 Spanish Variants": ["Spanish (Spain)", "Spanish (Mexico)", "Spanish (Argentina)", "Spanish (Colombia)", "Spanish (USA)"],
    "🥐 French Variants": ["French (France)", "French (Canada)", "French (Belgium)", "French (Switzerland)"],
    "🥨 German Variants": ["German (Germany)", "German (Austria)", "German (Switzerland)"],
    "🏖️ Portuguese": ["Portuguese (Brazil)", "Portuguese (Portugal)"],
    "🌷 Dutch": ["Dutch (Netherlands)", "Dutch (Belgium)"],
    "🏮 East Asia": ["Japanese (Japan)", "Chinese (China)", "Chinese (Taiwan)", "Cantonese (Hong Kong)", "Korean (South Korea)"],
    "🏝️ Southeast Asia": ["Vietnamese (Vietnam)", "Thai (Thailand)", "Indonesian (Indonesia)", "Malay (Malaysia)", "Filipino (Philippines)", "Javanese (Indonesia)", "Khmer (Cambodia)", "Lao (Laos)", "Burmese (Myanmar)"],
    "🐪 Middle East & North Africa": ["Arabic (Saudi Arabia)", "Arabic (Egypt)", "Arabic (UAE)", "Arabic (Morocco)", "Persian (Iran)", "Hebrew (Israel)", "Pashto (Afghanistan)"],
    "❄️ Scandinavian": ["Swedish (Sweden)", "Norwegian (Norway)", "Danish (Denmark)", "Finnish (Finland)", "Icelandic (Iceland)"],
    "🏰 Central/Eastern Europe": ["Polish (Poland)", "Czech (Czech Republic)", "Slovak (Slovakia)", "Hungarian (Hungary)", "Romanian (Romania)", "Bulgarian (Bulgaria)", "Croatian (Croatia)", "Ukrainian (Ukraine)", "Russian (Russia)", "Serbian (Serbia)", "Slovenian (Slovenia)", "Bosnian (Bosnia)", "Macedonian (North Macedonia)", "Albanian (Albania)"],
    "🍷 Mediterranean": ["Greek (Greece)", "Italian (Italy)", "Turkish (Turkey)", "Maltese (Malta)", "Catalan (Spain)", "Galician (Spain)", "Basque (Spain)"],
    "🌲 Baltic": ["Latvian (Latvia)", "Lithuanian (Lithuania)", "Estonian (Estonia)"],
    "🍀 Celtic & British Isles": ["Welsh (Wales/UK)", "Irish (Ireland)"],
    "⛰️ Caucasus & Central Asia": ["Georgian (Georgia)", "Armenian (Armenia)", "Azerbaijani (Azerbaijan)", "Kazakh (Kazakhstan)", "Uzbek (Uzbekistan)", "Turkmen (Turkmenistan)", "Kyrgyz (Kyrgyzstan)", "Mongolian (Mongolia)"],
    "🦁 Africa": ["Swahili (Kenya)", "Amharic (Ethiopia)", "Zulu (South Africa)", "Afrikaans (South Africa)", "Yoruba (Nigeria)", "Hausa (Nigeria)", "Somali (Somalia)"]
}

def generate_slug(name):
    # e.g., Hindi (India)
    match = re.match(r"(.*)\s*\((.*)\)", name)
    if match:
        lang = match.group(1).strip()
        country = match.group(2).strip()
    else:
        lang = name
        country = ""
    
    if country == "Wales/UK":
        country = "UK"
    
    s = f"{lang}-text-to-speech-{country}".lower()
    s = s.replace(" ", "-")
    return s

html = """<!-- ALL LANGUAGES DIRECTORY -->
<section style="max-width:1200px;margin:0 auto;padding:48px 24px 60px;">
  <h2 style="font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(1.4rem,3vw,1.8rem);text-align:center;margin-bottom:8px;"><span class="tg">All Languages</span> — Free Text to Speech</h2>
  <p style="text-align:center;color:var(--muted);font-size:.9rem;margin-bottom:32px;">Generate natural AI voices in 100+ languages. Click any language to start.</p>
"""

link_style = "padding:6px 14px;background:var(--card);border:1px solid var(--border);border-radius:20px;font-size:.82rem;color:var(--txt2);text-decoration:none;transition:all .2s;white-space:nowrap;"

for region, langs in regions.items():
    html += f'  <!-- Group: {region} -->\n'
    html += f'  <h3 style="font-family:\'Syne\',sans-serif;font-weight:700;font-size:1rem;color:var(--a1);margin:24px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--border);">{region}</h3>\n'
    html += f'  <div style="display:flex;flex-wrap:wrap;gap:8px;">\n'
    
    for lang_name in langs:
        slug = generate_slug(lang_name)
        html += f'    <a href="/tts/{slug}" style="{link_style}">{lang_name}</a>\n'
    
    html += '  </div>\n\n'

html += "</section>\n"

with open("c:/Users/Rupesh/OneDrive/Desktop/python 12-02-2026/new _add page url/git/git/voice-app/scratch/languages_section.html", "w", encoding="utf-8") as f:
    f.write(html)
