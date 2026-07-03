"""
VoicePro TTS – Programmatic SEO Page Generator
Generates one landing page per language+country combination.
Run:  python generate_pseo_pages.py
Output: templates/tts/<slug>.html  (one file per language)
"""

import os, json, re
from app import VOICE_MAPPING

# ──────────────────────────────────────────────────────────────
#  MASTER LANGUAGE DATA  (100 + entries)
# ──────────────────────────────────────────────────────────────
LANGUAGES = [
    # code, language_name, country, flag, native_name, voice_count
    ("hi-IN",  "Hindi",        "India",        "🇮🇳", "हिन्दी",         5),
    ("mr-IN",  "Marathi",      "India",        "🇮🇳", "मराठी",           2),
    ("gu-IN",  "Gujarati",     "India",        "🇮🇳", "ગુજરાતી",         2),
    ("ta-IN",  "Tamil",        "India",        "🇮🇳", "தமிழ்",           2),
    ("te-IN",  "Telugu",       "India",        "🇮🇳", "తెలుగు",           2),
    ("kn-IN",  "Kannada",      "India",        "🇮🇳", "ಕನ್ನಡ",           2),
    ("ml-IN",  "Malayalam",    "India",        "🇮🇳", "മലയാളം",         2),
    ("bn-IN",  "Bengali",      "India",        "🇮🇳", "বাংলা",           2),
    ("pa-IN",  "Punjabi",      "India",        "🇮🇳", "ਪੰਜਾਬੀ",         2),
    ("or-IN",  "Odia",         "India",        "🇮🇳", "ଓଡ଼ିଆ",           2),
    ("bn-BD",  "Bengali",      "Bangladesh",   "🇧🇩", "বাংলা",           2),
    ("ur-PK",  "Urdu",         "Pakistan",     "🇵🇰", "اردو",            2),
    ("ne-NP",  "Nepali",       "Nepal",        "🇳🇵", "नेपाली",           2),
    ("si-LK",  "Sinhala",      "Sri Lanka",    "🇱🇰", "සිංහල",           2),
    ("en-US",  "English",      "United States","🇺🇸", "English",         8),
    ("en-GB",  "English",      "United Kingdom","🇬🇧","English",         4),
    ("en-AU",  "English",      "Australia",    "🇦🇺", "English",         2),
    ("en-IN",  "English",      "India",        "🇮🇳", "English",         2),
    ("en-CA",  "English",      "Canada",       "🇨🇦", "English",         2),
    ("en-ZA",  "English",      "South Africa", "🇿🇦", "English",         2),
    ("en-NG",  "English",      "Nigeria",      "🇳🇬", "English",         2),
    ("es-ES",  "Spanish",      "Spain",        "🇪🇸", "Español",         2),
    ("es-MX",  "Spanish",      "Mexico",       "🇲🇽", "Español",         2),
    ("es-AR",  "Spanish",      "Argentina",    "🇦🇷", "Español",         2),
    ("es-CO",  "Spanish",      "Colombia",     "🇨🇴", "Español",         2),
    ("es-US",  "Spanish",      "United States","🇺🇸", "Español",         2),
    ("fr-FR",  "French",       "France",       "🇫🇷", "Français",        2),
    ("fr-CA",  "French",       "Canada",       "🇨🇦", "Français",        2),
    ("de-DE",  "German",       "Germany",      "🇩🇪", "Deutsch",         2),
    ("de-AT",  "German",       "Austria",      "🇦🇹", "Deutsch",         2),
    ("it-IT",  "Italian",      "Italy",        "🇮🇹", "Italiano",        2),
    ("pt-BR",  "Portuguese",   "Brazil",       "🇧🇷", "Português",       2),
    ("pt-PT",  "Portuguese",   "Portugal",     "🇵🇹", "Português",       2),
    ("nl-NL",  "Dutch",        "Netherlands",  "🇳🇱", "Nederlands",      2),
    ("sv-SE",  "Swedish",      "Sweden",       "🇸🇪", "Svenska",         2),
    ("nb-NO",  "Norwegian",    "Norway",       "🇳🇴", "Norsk",           2),
    ("da-DK",  "Danish",       "Denmark",      "🇩🇰", "Dansk",           2),
    ("fi-FI",  "Finnish",      "Finland",      "🇫🇮", "Suomi",           2),
    ("pl-PL",  "Polish",       "Poland",       "🇵🇱", "Polski",          2),
    ("cs-CZ",  "Czech",        "Czech Republic","🇨🇿","Čeština",         2),
    ("sk-SK",  "Slovak",       "Slovakia",     "🇸🇰", "Slovenčina",      2),
    ("hu-HU",  "Hungarian",    "Hungary",      "🇭🇺", "Magyar",          2),
    ("ro-RO",  "Romanian",     "Romania",      "🇷🇴", "Română",          2),
    ("bg-BG",  "Bulgarian",    "Bulgaria",     "🇧🇬", "Български",       2),
    ("hr-HR",  "Croatian",     "Croatia",      "🇭🇷", "Hrvatski",        2),
    ("uk-UA",  "Ukrainian",    "Ukraine",      "🇺🇦", "Українська",      2),
    ("ru-RU",  "Russian",      "Russia",       "🇷🇺", "Русский",         2),
    ("el-GR",  "Greek",        "Greece",       "🇬🇷", "Ελληνικά",        2),
    ("tr-TR",  "Turkish",      "Turkey",       "🇹🇷", "Türkçe",          2),
    ("ja-JP",  "Japanese",     "Japan",        "🇯🇵", "日本語",           3),
    ("zh-CN",  "Chinese",      "China",        "🇨🇳", "中文 (普通话)",     3),
    ("zh-TW",  "Chinese",      "Taiwan",       "🇹🇼", "中文 (繁體)",       2),
    ("zh-HK",  "Cantonese",    "Hong Kong",    "🇭🇰", "粵語",             2),
    ("ko-KR",  "Korean",       "South Korea",  "🇰🇷", "한국어",           2),
    ("vi-VN",  "Vietnamese",   "Vietnam",      "🇻🇳", "Tiếng Việt",      2),
    ("th-TH",  "Thai",         "Thailand",     "🇹🇭", "ภาษาไทย",         2),
    ("id-ID",  "Indonesian",   "Indonesia",    "🇮🇩", "Bahasa Indonesia", 2),
    ("ms-MY",  "Malay",        "Malaysia",     "🇲🇾", "Bahasa Melayu",   2),
    ("fil-PH", "Filipino",     "Philippines",  "🇵🇭", "Filipino",        2),
    ("ar-SA",  "Arabic",       "Saudi Arabia", "🇸🇦", "العربية",         2),
    ("ar-EG",  "Arabic",       "Egypt",        "🇪🇬", "العربية",         2),
    ("fa-IR",  "Persian",      "Iran",         "🇮🇷", "فارسی",           2),
    ("he-IL",  "Hebrew",       "Israel",       "🇮🇱", "עברית",           2),
    ("ka-GE",  "Georgian",     "Georgia",      "🇬🇪", "ქართული",         2),
    ("sw-KE",  "Swahili",      "Kenya",        "🇰🇪", "Kiswahili",       2),
    ("am-ET",  "Amharic",      "Ethiopia",     "🇪🇹", "አማርኛ",           2),
    ("zu-ZA",  "Zulu",         "South Africa", "🇿🇦", "isiZulu",         2),
    ("af-ZA",  "Afrikaans",    "South Africa", "🇿🇦", "Afrikaans",       2),
    ("lv-LV",  "Latvian",      "Latvia",       "🇱🇻", "Latviešu",        2),
    ("lt-LT",  "Lithuanian",   "Lithuania",    "🇱🇹", "Lietuvių",        2),
    ("et-EE",  "Estonian",     "Estonia",      "🇪🇪", "Eesti",           2),
    ("az-AZ",  "Azerbaijani",  "Azerbaijan",   "🇦🇿", "Azərbaycan",      2),
    ("kk-KZ",  "Kazakh",       "Kazakhstan",   "🇰🇿", "Қазақша",         2),
    ("uz-UZ",  "Uzbek",        "Uzbekistan",   "🇺🇿", "Oʻzbek",          2),
    ("sq-AL",  "Albanian",     "Albania",      "🇦🇱", "Shqip",           2),
    ("mk-MK",  "Macedonian",   "North Macedonia","🇲🇰","Македонски",     2),
    ("bs-BA",  "Bosnian",      "Bosnia",       "🇧🇦", "Bosanski",        2),
    ("sr-RS",  "Serbian",      "Serbia",       "🇷🇸", "Српски",          2),
    ("sl-SI",  "Slovenian",    "Slovenia",     "🇸🇮", "Slovenščina",     2),
    ("mt-MT",  "Maltese",      "Malta",        "🇲🇹", "Malti",           2),
    ("cy-GB",  "Welsh",        "Wales",        "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "Cymraeg",        2),
    ("ga-IE",  "Irish",        "Ireland",      "🇮🇪", "Gaeilge",         2),
    ("ca-ES",  "Catalan",      "Spain",        "🇪🇸", "Català",          2),
    ("is-IS",  "Icelandic",    "Iceland",      "🇮🇸", "Íslenska",        2),
    ("mn-MN",  "Mongolian",    "Mongolia",     "🇲🇳", "Монгол",          2),
    ("km-KH",  "Khmer",        "Cambodia",     "🇰🇭", "ភាសាខ្មែរ",       2),
    ("lo-LA",  "Lao",          "Laos",         "🇱🇦", "ລາວ",             2),
    ("my-MM",  "Burmese",      "Myanmar",      "🇲🇲", "မြန်မာ",           2),
    ("ps-AF",  "Pashto",       "Afghanistan",  "🇦🇫", "پښتو",            2),
    ("yo-NG",  "Yoruba",       "Nigeria",      "🇳🇬", "Yorùbá",          2),
    ("ha-NG",  "Hausa",        "Nigeria",      "🇳🇬", "Hausa",           2),
    ("so-SO",  "Somali",       "Somalia",      "🇸🇴", "Soomaali",        2),
    ("jv-ID",  "Javanese",     "Indonesia",    "🇮🇩", "Basa Jawa",       2),
    ("gl-ES",  "Galician",     "Spain",        "🇪🇸", "Galego",          2),
    ("eu-ES",  "Basque",       "Spain",        "🇪🇸", "Euskara",         2),
    ("hy-AM",  "Armenian",     "Armenia",      "🇦🇲", "Հայerեն",         2),
    ("tk-TM",  "Turkmen",      "Turkmenistan", "🇹🇲", "Türkmençe",       2),
    ("ky-KG",  "Kyrgyz",       "Kyrgyzstan",   "🇰🇬", "Кыргызча",        2),
    ("nl-BE",  "Dutch",        "Belgium",      "🇧🇪", "Nederlands",      2),
    ("fr-BE",  "French",       "Belgium",      "🇧🇪", "Français",        2),
    ("de-CH",  "German",       "Switzerland",  "🇨🇭", "Deutsch",         2),
    ("fr-CH",  "French",       "Switzerland",  "🇨🇭", "Français",        2),
    ("ar-AE",  "Arabic",       "UAE",          "🇦🇪", "العربية",         2),
    ("ar-MA",  "Arabic",       "Morocco",      "🇲🇦", "العربية",         2),
]

# ──────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────
def slug(code):
    """hi-IN → hindi-text-to-speech-india"""
    lang_map = {
        "hi": "hindi", "mr": "marathi", "gu": "gujarati", "ta": "tamil",
        "te": "telugu", "kn": "kannada", "ml": "malayalam", "bn": "bengali",
        "pa": "punjabi", "or": "odia", "ur": "urdu", "ne": "nepali",
        "si": "sinhala", "en": "english", "es": "spanish", "fr": "french",
        "de": "german", "it": "italian", "pt": "portuguese", "nl": "dutch",
        "sv": "swedish", "nb": "norwegian", "da": "danish", "fi": "finnish",
        "pl": "polish", "cs": "czech", "sk": "slovak", "hu": "hungarian",
        "ro": "romanian", "bg": "bulgarian", "hr": "croatian", "uk": "ukrainian",
        "ru": "russian", "el": "greek", "tr": "turkish", "ja": "japanese",
        "zh": "chinese", "ko": "korean", "vi": "vietnamese", "th": "thai",
        "id": "indonesian", "ms": "malay", "fil": "filipino", "ar": "arabic",
        "fa": "persian", "he": "hebrew", "ka": "georgian", "sw": "swahili",
        "am": "amharic", "zu": "zulu", "af": "afrikaans", "lv": "latvian",
        "lt": "lithuanian", "et": "estonian", "az": "azerbaijani", "kk": "kazakh",
        "uz": "uzbek", "sq": "albanian", "mk": "macedonian", "bs": "bosnian",
        "sr": "serbian", "sl": "slovenian", "mt": "maltese", "cy": "welsh",
        "ga": "irish", "ca": "catalan", "is": "icelandic", "mn": "mongolian",
        "km": "khmer", "lo": "lao", "my": "burmese", "ps": "pashto",
        "yo": "yoruba", "ha": "hausa", "so": "somali", "jv": "javanese",
        "gl": "galician", "eu": "basque", "hy": "armenian", "tk": "turkmen",
        "ky": "kyrgyz", "yue": "cantonese",
    }
    country_map = {
        "IN": "india", "BD": "bangladesh", "PK": "pakistan", "NP": "nepal",
        "LK": "sri-lanka", "US": "usa", "GB": "uk", "AU": "australia",
        "CA": "canada", "ZA": "south-africa", "NG": "nigeria", "ES": "spain",
        "MX": "mexico", "AR": "argentina", "CO": "colombia", "FR": "france",
        "DE": "germany", "AT": "austria", "IT": "italy", "BR": "brazil",
        "PT": "portugal", "NL": "netherlands", "SE": "sweden", "NO": "norway",
        "DK": "denmark", "FI": "finland", "PL": "poland", "CZ": "czech-republic",
        "SK": "slovakia", "HU": "hungary", "RO": "romania", "BG": "bulgaria",
        "HR": "croatia", "UA": "ukraine", "RU": "russia", "GR": "greece",
        "TR": "turkey", "JP": "japan", "CN": "china", "TW": "taiwan",
        "HK": "hong-kong", "KR": "south-korea", "VN": "vietnam", "TH": "thailand",
        "ID": "indonesia", "MY": "malaysia", "PH": "philippines", "SA": "saudi-arabia",
        "EG": "egypt", "IR": "iran", "IL": "israel", "GE": "georgia",
        "KE": "kenya", "ET": "ethiopia", "LV": "latvia", "LT": "lithuania",
        "EE": "estonia", "AZ": "azerbaijan", "KZ": "kazakhstan", "UZ": "uzbekistan",
        "AL": "albania", "MK": "north-macedonia", "BA": "bosnia", "RS": "serbia",
        "SI": "slovenia", "MT": "malta", "IE": "ireland", "IS": "iceland",
        "MN": "mongolia", "KH": "cambodia", "LA": "laos", "MM": "myanmar",
        "AF": "afghanistan", "SO": "somalia", "AM": "armenia", "TM": "turkmenistan",
        "KG": "kyrgyzstan", "BE": "belgium", "CH": "switzerland", "AE": "uae",
        "MA": "morocco",
    }
    parts = code.split("-")
    lang_part = lang_map.get(parts[0], parts[0].lower())
    country_part = country_map.get(parts[1] if len(parts) > 1 else "", "")
    return f"{lang_part}-text-to-speech-{country_part}" if country_part else f"{lang_part}-text-to-speech"


def sample_text(code, lang_name):
    samples = {
        "hi-IN": "नमस्ते! VoicePro AI आपके टेक्स्ट को शानदार आवाज़ में बदलता है।",
        "mr-IN": "नमस्कार! VoicePro AI तुमच्या मजकुराचे आवाजात रूपांतर करते.",
        "gu-IN": "નમસ્તે! VoicePro AI તમારા ટેક્સ્ટને અવાજમાં બદલે છે.",
        "ta-IN": "வணக்கம்! VoicePro AI உங்கள் உரையை குரலாக மாற்றுகிறது.",
        "te-IN": "నమస్కారం! VoicePro AI మీ వచనాన్ని కంఠస్వరంగా మారుస్తుంది.",
        "kn-IN": "ನಮಸ್ಕಾರ! VoicePro AI ನಿಮ್ಮ ಪಠ್ಯವನ್ನು ಧ್ವನಿಗೆ ಪರಿವರ್ತಿಸುತ್ತದೆ.",
        "ml-IN": "നമസ്കാരം! VoicePro AI നിങ്ങളുടെ ടെക്‌സ്‌റ്റ് ശബ്ദമാക്കി മാറ്റുന്നു.",
        "bn-IN": "নমস্কার! VoicePro AI আপনার টেক্সটকে কণ্ঠস্বরে রূপান্তরিত করে।",
        "pa-IN": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! VoicePro AI ਤੁਹਾਡੇ ਟੈਕਸਟ ਨੂੰ ਆਵਾਜ਼ ਵਿੱਚ ਬਦਲਦਾ ਹੈ।",
        "ja-JP": "こんにちは！VoicePro AIがテキストを音声に変換します。",
        "zh-CN": "你好！VoicePro AI 将您的文字转换为自然语音。",
        "zh-TW": "您好！VoicePro AI 將您的文字轉換為自然語音。",
        "zh-HK": "你好！VoicePro AI 將您嘅文字轉換為自然語音。",
        "ko-KR": "안녕하세요! VoicePro AI가 텍스트를 음성으로 변환합니다.",
        "ar-SA": "مرحباً! يحوّل VoicePro AI نصك إلى صوت طبيعي.",
        "ar-EG": "أهلاً! يحوّل VoicePro AI نصك إلى صوت طبيعي.",
        "fa-IR": "سلام! VoicePro AI متن شما را به گفتار تبدیل می‌کند.",
        "he-IL": "!שלום! VoicePro AI ממיר את הטקסט שלך לדיבור טבעי",
        "ru-RU": "Привет! VoicePro AI превращает ваш текст в речь.",
        "uk-UA": "Привіт! VoicePro AI перетворює ваш текст на мову.",
        "el-GR": "Γεια σας! Το VoicePro AI μετατρέπει το κείμενό σας σε φωνή.",
        "tr-TR": "Merhaba! VoicePro AI metninizi doğal sese dönüştürür.",
        "th-TH": "สวัสดี! VoicePro AI แปลงข้อความของคุณเป็นเสียงพูดที่เป็นธรรมชาติ",
        "vi-VN": "Xin chào! VoicePro AI chuyển đổi văn bản của bạn thành giọng nói.",
        "id-ID": "Halo! VoicePro AI mengubah teks Anda menjadi suara alami.",
        "ms-MY": "Helo! VoicePro AI menukar teks anda kepada suara semula jadi.",
        "sw-KE": "Habari! VoicePro AI inabadilisha maandishi yako kuwa sauti ya asili.",
        "am-ET": "ሰላም! VoicePro AI ጽሑፍዎን ወደ ተፈጥሮ ድምጽ ይቀይረዋል።",
        "bn-BD": "হ্যালো! VoicePro AI আপনার টেক্সটকে প্রাকৃতিক কণ্ঠে পরিণত করে।",
        "ne-NP": "नमस्ते! VoicePro AI तपाईंको पाठलाई आवाजमा रूपान्तरण गर्छ।",
        "si-LK": "ආයුබෝවන්! VoicePro AI ඔබේ පෙළ ස්වාභාවික කටහඬකට පරිවර්තනය කරයි.",
        "ur-PK": "ہیلو! VoicePro AI آپ کے متن کو قدرتی آواز میں بدلتا ہے۔",
        "ka-GE": "გამარჯობა! VoicePro AI თქვენს ტექსტს ბუნებრივ მეტყველებად გარდაქმნის.",
        "mn-MN": "Сайн уу! VoicePro AI таны текстийг байгалийн дуу хоолой болгон хувиргадаг.",
        "km-KH": "សួស្ដី! VoicePro AI បំប្លែងអត្ថបទរបស់អ្នកទៅជាសំឡេងធម្មជាតិ។",
    }
    default = f"Hello! VoicePro AI converts your {lang_name} text to natural speech instantly."
    return samples.get(code, default)


def use_cases(lang_name, country):
    return [
        f"YouTube voiceovers in {lang_name}",
        f"E-learning audio for {country} students",
        f"Podcast narration in {lang_name}",
        f"IVR / phone system voices in {lang_name}",
        f"Accessibility tools for {country}",
        f"Social media reels & short videos",
        f"Business presentations & demos",
        f"Audiobook creation in {lang_name}",
    ]


def faq_items(lang_name, country, code):
    return [
        {
            "q": f"Is {lang_name} Text to Speech free?",
            "a": f"Yes! VoicePro {lang_name} TTS is 100% free — no login, no credit card, no daily limit. Generate unlimited {lang_name} audio and download as MP3 or WAV."
        },
        {
            "q": f"How many {lang_name} voices are available?",
            "a": f"VoicePro offers multiple neural {lang_name} voices — male, female, young, mature, and professional variants — all powered by Microsoft's Azure Neural engine."
        },
        {
            "q": f"Can I use this {lang_name} TTS for YouTube videos?",
            "a": f"Absolutely. Audio generated with VoicePro is royalty-free. Use it in YouTube videos, Instagram Reels, TikTok, podcasts, and commercial projects without any attribution."
        },
        {
            "q": f"Does it support {lang_name} script correctly?",
            "a": f"Yes. VoicePro uses Unicode-native neural voices specifically trained on {lang_name} ({country}) data, ensuring correct pronunciation, intonation, and script rendering."
        },
        {
            "q": "What is the character limit?",
            "a": "Up to 5,000 characters (~700 words / 4–5 minutes of audio) per request. No daily cap. For longer content, split into sections."
        },
        {
            "q": f"How does VoicePro compare to Google TTS for {lang_name}?",
            "a": f"VoicePro uses Microsoft Edge Neural TTS — the same technology as Azure Cognitive Services — which delivers comparable or superior naturalness for {lang_name}, especially for regional accents and prosody."
        },
    ]


# ──────────────────────────────────────────────────────────────
#  HTML TEMPLATE
# ──────────────────────────────────────────────────────────────
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-X7HBHXRYG5"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-X7HBHXRYG5');
</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9707682105347147" crossorigin="anonymous"></script>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta_title}</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{meta_keywords}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://www.texttoaudiomp3.site/tts/{slug}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.texttoaudiomp3.site/tts/{slug}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:image" content="https://drive.google.com/uc?export=view&id=1gIwweRVbUUHktRLA8aluUD4nvig0kR_2">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0a0f1a">
<link rel="icon" type="image/png" href="/favicon.png">
<script type="application/ld+json">{schema_json}</script>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  :root{{
    --bg:#d8dee9;
    --card:#ffffff;
    --border:rgba(15,23,42,0.12);
    --borderH:rgba(59,158,255,0.4);
    --a1:#1d4ed8;
    --a2:#6d28d9;
    --a3:#db2777;
    --txt:#0f172a;
    --txt2:#334155;
    --muted:#64748b;
    --panel:#edf2f7;
    --ok:#10b981;
    --grid-line:rgba(0,0,0,0.02);
    --shadow:0 10px 30px -5px rgba(0,0,0,0.04),0 8px 16px -6px rgba(0,0,0,0.04);
    --nav-bg:#ffffff;
  }}
  [data-theme="dark"]{{
    --bg:#070b12;
    --card:rgba(255,255,255,0.032);
    --border:rgba(255,255,255,0.07);
    --borderH:rgba(59,158,255,0.38);
    --a1:#3b9eff;
    --a2:#7c5fe6;
    --a3:#e94fa3;
    --txt:#dde4f0;
    --txt2:#b8c4d8;
    --muted:#6e7e98;
    --panel:#0c1220;
    --ok:#3dd68c;
    --grid-line:rgba(255,255,255,0.012);
    --shadow:none;
    --nav-bg:#070b12;
  }}
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
  html{{scroll-behavior:smooth;}}
  body{{background:var(--bg);color:var(--txt);font-family:'DM Sans',sans-serif;min-height:100vh;display:flex;flex-direction:column;-webkit-font-smoothing:antialiased;}}
  body::before{{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse 80% 50% at 20% 10%,rgba(59,158,255,0.055) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 80% 80%,rgba(124,95,230,0.045) 0%,transparent 60%),repeating-linear-gradient(0deg,transparent,transparent 63px,rgba(255,255,255,0.012) 64px),repeating-linear-gradient(90deg,transparent,transparent 63px,rgba(255,255,255,0.012) 64px);}}
  body>*{{position:relative;z-index:1;}}
  h1,h2,h3,h4{{font-family:'Syne',sans-serif;letter-spacing:-0.02em;line-height:1.15;}}
  .tg{{background:linear-gradient(130deg,var(--a1) 0%,var(--a2) 50%,var(--a3) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
  .mono{{font-family:'Space Mono',monospace;}}
  .glass-nav{{background:var(--nav-bg);backdrop-filter:blur(24px);border-bottom:1px solid var(--border);opacity:0.96;}}
  .nav-btn{{padding:7px 14px;border-radius:10px;font-size:.85rem;font-weight:500;transition:all .18s;color:var(--muted);border:none;background:transparent;cursor:pointer;font-family:'DM Sans',sans-serif;text-decoration:none;display:inline-block;}}
  .nav-btn:hover{{color:var(--a1);background:rgba(59,158,255,0.09);}}
  .glass{{background:var(--card);backdrop-filter:blur(16px);border:1px solid var(--border);border-radius:22px;box-shadow:var(--shadow);}}
  .btn-primary{{background:linear-gradient(135deg,var(--a1),var(--a2),var(--a3));background-size:220%;border:none;border-radius:14px;color:#fff;font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;letter-spacing:.02em;padding:15px 28px;cursor:pointer;width:100%;transition:background-position .45s,transform .15s,box-shadow .3s;box-shadow:0 4px 28px rgba(59,158,255,0.24);}}
  .btn-primary:hover{{background-position:right;box-shadow:0 6px 36px rgba(59,158,255,0.4);}}
  .btn-primary:disabled{{opacity:.5;cursor:not-allowed;}}
  textarea{{background:var(--panel);border:1.5px solid var(--border);border-radius:14px;color:var(--txt);font-family:'DM Sans',sans-serif;font-size:.96rem;line-height:1.65;padding:14px 18px 24px;width:100%;outline:none;resize:none;transition:border-color .2s,box-shadow .2s;min-height:120px;max-height:400px;overflow-y:auto;}}
  textarea:focus{{border-color:var(--a1);box-shadow:0 0 0 3px rgba(59,158,255,0.13);}}
  textarea::placeholder{{color:var(--muted);}}
  select{{appearance:none;background:var(--panel);border:1px solid var(--border);border-radius:12px;color:var(--txt);font-family:'DM Sans',sans-serif;font-size:.9rem;padding:11px 36px 11px 14px;outline:none;cursor:pointer;width:100%;transition:border-color .2s;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='11' height='11' viewBox='0 0 12 12'%3E%3Cpath fill='%236e7e98' d='M6 8L1 3h10z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;}}
  select:focus{{border-color:var(--a1);}}
  select option{{background:var(--bg);color:var(--txt);}}
  input[type=range]{{-webkit-appearance:none;width:100%;background:transparent;cursor:pointer;}}
  input[type=range]::-webkit-slider-runnable-track{{height:5px;background:rgba(255,255,255,0.09);border-radius:3px;}}
  input[type=range]::-webkit-slider-thumb{{-webkit-appearance:none;height:18px;width:18px;border-radius:50%;background:linear-gradient(135deg,var(--a1),var(--a2));cursor:pointer;margin-top:-6.5px;border:2px solid rgba(255,255,255,0.88);box-shadow:0 0 10px rgba(59,158,255,0.55);}}
  .ctrl{{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:14px 16px;}}
  .slbl{{display:block;font-family:'Syne',sans-serif;font-size:.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;}}
  .wave{{display:flex;align-items:center;gap:4px;height:34px;}}
  .wave-bar{{width:3px;height:12px;background:linear-gradient(180deg,var(--a1),var(--a2));border-radius:2px;animation:wv 1s ease-in-out infinite;}}
  .wave-bar:nth-child(2){{animation-delay:.1s}} .wave-bar:nth-child(3){{animation-delay:.2s}} .wave-bar:nth-child(4){{animation-delay:.3s}} .wave-bar:nth-child(5){{animation-delay:.4s}}
  @keyframes wv{{0%,100%{{height:12px}}50%{{height:28px}}}}
  .spinner{{width:20px;height:20px;border:3px solid rgba(255,255,255,0.18);border-top-color:#fff;border-radius:50%;animation:sp .8s linear infinite;display:inline-block;vertical-align:middle;}}
  @keyframes sp{{to{{transform:rotate(360deg)}}}}
  .toast{{position:fixed;bottom:22px;right:22px;background:rgba(8,13,24,0.97);backdrop-filter:blur(14px);border:1px solid var(--border);border-radius:14px;padding:13px 20px;color:var(--txt);transform:translateY(120px);opacity:0;transition:all .3s cubic-bezier(.34,1.56,.64,1);z-index:99999;max-width:320px;font-size:.88rem;}}
  .toast.on{{transform:translateY(0);opacity:1;}}
  .hidden{{display:none!important;}}
  .badge-pill{{display:inline-block;background:rgba(59,158,255,0.1);border:1px solid rgba(59,158,255,0.2);border-radius:100px;padding:5px 16px;font-size:.74rem;font-weight:700;color:var(--a1);letter-spacing:.6px;font-family:'Syne',sans-serif;}}
  .faq-item{{border:1px solid var(--border);border-radius:16px;overflow:hidden;margin-bottom:10px;transition:border-color .2s;}}
  .faq-item:hover{{border-color:rgba(59,158,255,0.28);}}
  .faq-q{{padding:19px 22px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;font-weight:700;font-family:'Syne',sans-serif;font-size:.95rem;color:var(--txt);background:rgba(255,255,255,0.02);transition:background .15s;user-select:none;}}
  .faq-q:hover{{background:rgba(59,158,255,0.05);}}
  .faq-q .faq-chev{{color:var(--a1);transition:transform .25s;font-size:.78rem;flex-shrink:0;margin-left:12px;}}
  .faq-item.open .faq-chev{{transform:rotate(180deg);}}
  .faq-a{{max-height:0;overflow:hidden;transition:max-height .38s ease,padding .25s;}}
  .faq-item.open .faq-a{{max-height:220px;padding:0 22px 20px;}}
  .faq-a p{{color:var(--txt2);font-size:.91rem;line-height:1.78;}}
  .feature-card{{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:26px;transition:border-color .25s,box-shadow .25s,transform .2s;}}
  .feature-card:hover{{border-color:var(--borderH);box-shadow:0 0 24px rgba(59,158,255,0.07);transform:translateY(-2px);}}
  .use-tag{{display:inline-block;background:rgba(59,158,255,0.09);border:1px solid rgba(59,158,255,0.18);border-radius:100px;padding:6px 16px;font-size:.82rem;color:var(--a1);margin:4px;font-weight:500;}}
  .pro-footer{{background:rgba(5,8,14,0.97);border-top:1px solid var(--border);padding:52px 24px 0;margin-top:auto;}}
  .footer-link{{display:block;color:var(--muted);text-decoration:none;font-size:.875rem;padding:4px 0;transition:color .18s,padding-left .18s;}}
  .footer-link:hover{{color:var(--a1);padding-left:4px;}}
  .footer-heading{{font-family:'Syne',sans-serif;font-weight:700;font-size:.7rem;letter-spacing:1.6px;text-transform:uppercase;color:var(--muted);margin-bottom:14px;}}
  audio{{accent-color:var(--a1);width:100%;border-radius:10px;margin-bottom:14px;display:block;}}
  #result-area{{border-top:1px solid var(--border);padding-top:22px;margin-top:22px;}}
  .lang-pill{{display:inline-block;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:100px;padding:5px 14px;font-size:.8rem;color:var(--muted);margin:3px;text-decoration:none;transition:all .18s;}}
  .lang-pill:hover{{border-color:var(--a1);color:var(--a1);background:rgba(59,158,255,0.07);}}
  .nav-desktop{{display:flex;}}
  .nav-mobile-btn{{display:none;}}
  @media(max-width:768px){{.nav-desktop{{display:none;}}.nav-mobile-btn{{display:block;}}}}
</style>
</head>
<body>

<!-- NAV -->
<nav class="glass-nav" style="position:fixed;top:0;width:100%;z-index:50;">
  <div style="max-width:1100px;margin:0 auto;padding:0 20px;display:flex;align-items:center;justify-content:space-between;height:60px;">
    <a href="/" style="display:flex;align-items:center;gap:10px;text-decoration:none;">
      <div style="width:36px;height:36px;background:linear-gradient(135deg,var(--a1),var(--a2));border-radius:10px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 16px rgba(59,158,255,0.35);">
        <i class="fa-solid fa-microphone-lines" style="color:#fff;font-size:.88rem;"></i>
      </div>
      <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.08rem;">Voice<span style="color:var(--a1);">Pro</span></span>
    </a>
    <div class="nav-desktop" style="align-items:center;gap:6px;">
      <a href="/" class="nav-btn"><i class="fa-solid fa-house" style="margin-right:5px;"></i>Home</a>
      <a href="/about.html" class="nav-btn"><i class="fa-solid fa-circle-info" style="margin-right:5px;"></i>About</a>
      <a href="/contact.html" class="nav-btn"><i class="fa-solid fa-headset" style="margin-right:5px;"></i>Contact</a>
      <a href="/privacy.html" class="nav-btn"><i class="fa-solid fa-shield-halved" style="margin-right:5px;"></i>Privacy</a>
      <button onclick="toggleTheme()" class="nav-btn" id="theme-btn" style="display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:10px;padding:0;cursor:pointer;" aria-label="Toggle theme">
        <i class="fa-solid fa-moon"></i>
      </button>
    </div>
    <button class="nav-mobile-btn" onclick="document.getElementById('mob-menu').classList.toggle('hidden')"
      style="background:none;border:none;color:var(--muted);font-size:1.2rem;cursor:pointer;">
      <i class="fa-solid fa-bars"></i>
    </button>
  </div>
  <div id="mob-menu" class="hidden"
    style="background:var(--bg);border-top:1px solid var(--border);padding:14px;display:flex;flex-direction:column;gap:6px;">
    <a href="/" class="nav-btn" style="text-align:left;"><i class="fa-solid fa-house" style="margin-right:8px;"></i>Home</a>
    <a href="/about.html" class="nav-btn"><i class="fa-solid fa-circle-info" style="margin-right:8px;"></i>About</a>
    <a href="/contact.html" class="nav-btn"><i class="fa-solid fa-headset" style="margin-right:8px;"></i>Contact</a>
    <a href="/privacy.html" class="nav-btn"><i class="fa-solid fa-shield-halved" style="margin-right:8px;"></i>Privacy</a>
    <button onclick="toggleTheme()" class="nav-btn" id="theme-btn-mob" style="text-align:left;display:flex;align-items:center;gap:8px;cursor:pointer;">
      <i class="fa-solid fa-moon"></i>Toggle Theme
    </button>
  </div>
</nav>

<!-- HERO -->
<section style="padding:100px 20px 48px;max-width:1100px;margin:0 auto;text-align:center;">
  <div style="margin-bottom:16px;">
    <span style="font-size:2.8rem;">{flag}</span>
  </div>
  <div class="badge-pill" style="margin-bottom:18px;">✦ FREE {lang_upper} TEXT TO SPEECH 2026 ✦</div>
  <h1 style="font-size:clamp(1.9rem,5vw,3.2rem);font-weight:800;margin-bottom:16px;">
    <span class="tg">Free {lang_name} Text to Speech</span><br>
    <span style="font-size:clamp(1.1rem,2.5vw,1.6rem);color:var(--txt2);font-weight:600;">{country} · Neural AI Voice Generator</span>
  </h1>
  <p style="color:var(--txt2);font-size:1.02rem;max-width:640px;margin:0 auto 28px;line-height:1.78;">
    Convert {lang_name} text to natural speech instantly. {voice_count} neural voices, MP3/WAV download, 
    no login required. The best free {lang_name} TTS tool for {country} in 2026.
  </p>
  <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:10px;">
    <span style="background:rgba(61,214,140,0.1);border:1px solid rgba(61,214,140,0.2);color:var(--ok);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-check" style="margin-right:5px;"></i>100% Free</span>
    <span style="background:rgba(59,158,255,0.1);border:1px solid rgba(59,158,255,0.2);color:var(--a1);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-bolt" style="margin-right:5px;"></i>Instant MP3</span>
    <span style="background:rgba(124,95,230,0.1);border:1px solid rgba(124,95,230,0.2);color:var(--a2);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-robot" style="margin-right:5px;"></i>Neural AI Voice</span>
    <span style="background:rgba(233,79,163,0.1);border:1px solid rgba(233,79,163,0.2);color:var(--a3);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-user-slash" style="margin-right:5px;"></i>No Login</span>
  </div>
</section>

<!-- TTS STUDIO WIDGET -->
<section style="max-width:860px;margin:0 auto;padding:0 18px 56px;">
  <div class="glass" style="padding:30px;">
    <h2 style="font-size:1.2rem;font-weight:700;margin-bottom:22px;display:flex;align-items:center;gap:9px;">
      <i class="fa-solid fa-microphone-lines" style="color:var(--a1);"></i>
      {lang_name} Voice Generator — Live Studio
    </h2>

    <!-- Sample text button -->
    <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
      <button onclick="loadSample()" style="background:rgba(59,158,255,0.1);border:1px solid rgba(59,158,255,0.2);color:var(--a1);border-radius:9px;padding:7px 14px;font-size:.8rem;font-weight:600;cursor:pointer;font-family:'DM Sans',sans-serif;">
        <i class="fa-solid fa-magic-wand-sparkles" style="margin-right:5px;"></i>Load Sample {lang_name} Text
      </button>
      <span style="font-size:.78rem;color:var(--muted);">or type your own below</span>
    </div>

    <div style="margin-bottom:18px;">
      <span class="slbl"><i class="fa-solid fa-align-left" style="margin-right:5px;"></i>Your {lang_name} Text</span>
      <textarea id="txt" rows="5" placeholder="Type or paste {lang_name} text here… (up to 5000 characters)" oninput="onTxt(this)"></textarea>
      <div style="display:flex;justify-content:space-between;margin-top:12px;font-size:.76rem;color:var(--muted);">
        <span><span id="cc">0</span> / 5000</span>
        <span>~<span id="te">0</span> sec audio</span>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-bottom:18px;">
      <div>
        <span class="slbl"><i class="fa-solid fa-language" style="margin-right:5px;color:var(--a1);"></i>Language</span>
        <select id="sel-lang" onchange="syncLang(this.value)">
          <option value="{lang_code}" selected>{flag} {lang_name} ({country})</option>
        </select>
      </div>
      <div>
        <span class="slbl"><i class="fa-solid fa-robot" style="margin-right:5px;color:var(--a2);"></i>Voice</span>
        <select id="sel-voice">
          <optgroup label="General Voices">
            <option value="female-1">👩 Female 1 – Natural</option>
            <option value="female-2">👩‍🦰 Female 2 – Soft</option>
            <option value="female-3">👩‍💼 Female 3 – Pro</option>
            <option value="male-1">👨 Male 1 – Deep</option>
            <option value="male-2">👨‍🦰 Male 2 – Friendly</option>
            <option value="male-3">👨‍💼 Male 3 – Authority</option>
            <option value="young">🧒 Young Voice</option>
            <option value="old">🧓 Mature Voice</option>
          </optgroup>
          <optgroup label="Kids (1-15)">
            <option value="kid-f1">👧 Lily (Age 7) – Kid Female</option>
            <option value="kid-f2">👧 Chloe (Age 10) – Kid Female</option>
            <option value="kid-m1">👦 Mason (Age 8) – Kid Male</option>
            <option value="kid-m2">👦 Logan (Age 12) – Kid Male</option>
          </optgroup>
          <optgroup label="Teens (15-20)">
            <option value="teen-f1">👩 Sophia (Age 17) – Teen Female</option>
            <option value="teen-f2">👩 Emma (Age 19) – Teen Female</option>
            <option value="teen-m1">👨 Ethan (Age 16) – Teen Male</option>
            <option value="teen-m2">👨 Noah (Age 18) – Teen Male</option>
          </optgroup>
          <optgroup label="Young Adults (20-40)">
            <option value="young-f1">👩‍🦰 Aria (Age 25) – Female Natural</option>
            <option value="young-f2">👩 Jenny (Age 28) – Female Friendly</option>
            <option value="young-f3">👩‍💼 Sara (Age 32) – Female Pro</option>
            <option value="young-m1">👨‍🦰 Guy (Age 26) – Male Natural</option>
            <option value="young-m2">👨‍💼 Roger (Age 30) – Male Pro</option>
            <option value="young-m3">👨 Ryan (Age 34) – Male Deep</option>
          </optgroup>
          <optgroup label="Middle-Aged (40-60)">
            <option value="mid-f1">👩‍🦳 Michelle (Age 45) – Female Exec</option>
            <option value="mid-f2">👩‍🦳 Helen (Age 52) – Female Warm</option>
            <option value="mid-m1">👨‍🦳 Steffan (Age 48) – Male Presenter</option>
            <option value="mid-m2">👨‍🦳 Brian (Age 55) – Male Narrator</option>
          </optgroup>
          <optgroup label="Seniors (60-90)">
            <option value="senior-f1">👵 Abigail (Age 68) – Senior Female</option>
            <option value="senior-f2">👵 Esther (Age 75) – Senior Female</option>
            <option value="senior-m1">👴 Arthur (Age 70) – Senior Male</option>
            <option value="senior-m2">👴 Thomas (Age 82) – Senior Male</option>
          </optgroup>
        </select>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px;">
      <div class="ctrl">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:9px;">
          <span style="font-size:.78rem;font-weight:600;color:var(--muted);"><i class="fa-solid fa-gauge-high" style="color:var(--ok);margin-right:4px;"></i>Speed</span>
          <span id="badge-rate" class="mono" style="font-size:.76rem;background:rgba(61,214,140,0.1);color:var(--ok);padding:2px 8px;border-radius:20px;">1.0x</span>
        </div>
        <input type="range" id="sl-rate" min="0.5" max="2.0" step="0.1" value="1.0" oninput="document.getElementById('badge-rate').textContent=parseFloat(this.value).toFixed(1)+'x'">
        <div style="display:flex;justify-content:space-between;font-size:.68rem;color:var(--muted);margin-top:3px;"><span>🐢</span><span>⚡</span></div>
      </div>
      <div class="ctrl">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:9px;">
          <span style="font-size:.78rem;font-weight:600;color:var(--muted);"><i class="fa-solid fa-music" style="color:var(--a2);margin-right:4px;"></i>Pitch</span>
          <span id="badge-pitch" class="mono" style="font-size:.76rem;background:rgba(124,95,230,0.1);color:var(--a2);padding:2px 8px;border-radius:20px;">+0</span>
        </div>
        <input type="range" id="sl-pitch" min="-10" max="10" step="1" value="0" oninput="document.getElementById('badge-pitch').textContent=(this.value>=0?'+':'')+this.value">
        <div style="display:flex;justify-content:space-between;font-size:.68rem;color:var(--muted);margin-top:3px;"><span>🔽</span><span>🔼</span></div>
      </div>
      <div class="ctrl">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:9px;">
          <span style="font-size:.78rem;font-weight:600;color:var(--muted);"><i class="fa-solid fa-volume-high" style="color:var(--a1);margin-right:4px;"></i>Volume</span>
          <span id="badge-vol" class="mono" style="font-size:.76rem;background:rgba(59,158,255,0.1);color:var(--a1);padding:2px 8px;border-radius:20px;">100%</span>
        </div>
        <input type="range" id="sl-vol" min="0" max="100" step="5" value="100" oninput="document.getElementById('badge-vol').textContent=this.value+'%'">
        <div style="display:flex;justify-content:space-between;font-size:.68rem;color:var(--muted);margin-top:3px;"><span>🔇</span><span>🔊</span></div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:2fr 1fr;gap:12px;margin-bottom:24px;">
      <div>
        <span class="slbl"><i class="fa-solid fa-palette" style="color:#f472b6;margin-right:5px;"></i>Speaking Style</span>
        <select id="sel-style">
          <option value="general">🗣️ General</option>
          <option value="cheerful">😊 Cheerful</option>
          <option value="newscast-formal">📜 Newscast Formal</option>
          <option value="narration-professional">🎬 Narration Pro</option>
          <option value="friendly">🤝 Friendly</option>
          <option value="poetry-reading">📖 Poetry</option>
          <option value="documentary-narration">🎥 Documentary</option>
          <option value="customerservice">📞 Customer Service</option>
        </select>
      </div>
      <div>
        <span class="slbl"><i class="fa-solid fa-file-audio" style="color:#fb923c;margin-right:5px;"></i>Format</span>
        <select id="sel-fmt">
          <option value="mp3">MP3</option>
          <option value="wav">WAV (Studio)</option>
        </select>
      </div>
    </div>

    <button id="gen-btn" class="btn-primary" onclick="doGenerate()">
      <span id="gen-lbl"><i class="fa-solid fa-wand-magic-sparkles" style="margin-right:8px;"></i>Generate {lang_name} Voice</span>
    </button>

    <div id="result-area" class="hidden">
      <!-- Custom Player UI -->
      <div style="background:rgba(255,255,255,0.015);border:1px solid var(--border);border-radius:16px;padding:18px 20px;margin-bottom:18px;">
        <!-- Top row -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <i class="fa-solid fa-square-check" style="color:var(--ok);font-size:1.25rem;"></i>
            <div>
              <div style="font-weight:700;color:var(--ok);font-size:.9rem;font-family:'Syne',sans-serif;">Audio Ready!</div>
              <div id="custom-player-meta" style="font-size:.74rem;color:var(--muted);margin-top:1px;">Edge TTS · en-US-AriaNeural · English (US)</div>
            </div>
          </div>
          <div id="custom-player-badge" class="badge-pill" style="margin:0;font-size:.7rem;background:rgba(59,158,255,0.1);color:var(--a1);border:1px solid rgba(59,158,255,0.15);text-transform:capitalize;">👩 Natural Female</div>
        </div>
        <!-- Waveform Player control bar -->
        <div style="display:flex;align-items:center;gap:12px;background:var(--panel);border-radius:12px;padding:10px 14px;border:1px solid var(--border);">
          <button id="play-pause-btn" onclick="togglePlayPause()" style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--a1),var(--a2));border:none;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:.85rem;box-shadow:0 0 10px rgba(59,158,255,0.25);transition:transform .15s;" onmouseover="this.style.transform='scale(1.08)'" onmouseout="this.style.transform='none'">
            <i class="fa-solid fa-play" id="play-pause-icon"></i>
          </button>
          <span id="player-time-current" style="font-size:.72rem;font-family:'Space Mono',monospace;color:var(--txt2);min-width:32px;">0:00</span>
          <!-- Seekable waveform timeline track -->
          <div id="player-timeline" onclick="seekAudio(event)" style="flex:1;height:32px;position:relative;cursor:pointer;display:flex;align-items:center;background:var(--bg);border-radius:6px;overflow:hidden;border:1px solid var(--border);">
            <!-- Waveform bars -->
            <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:space-between;padding:0 6px;opacity:0.35;pointer-events:none;">
              <div style="width:2px;height:8px;background:var(--a1);border-radius:1px;"></div>
              <div style="width:2px;height:14px;background:var(--a1);border-radius:1px;"></div>
              <div style="width:2px;height:10px;background:var(--a1);border-radius:1px;"></div>
              <div style="width:2px;height:18px;background:var(--a1);border-radius:1px;"></div>
              <div style="width:2px;height:12px;background:var(--a1);border-radius:1px;"></div>
              <div style="width:2px;height:16px;background:var(--a2);border-radius:1px;"></div>
              <div style="width:2px;height:8px;background:var(--a2);border-radius:1px;"></div>
              <div style="width:2px;height:18px;background:var(--a2);border-radius:1px;"></div>
              <div style="width:2px;height:14px;background:var(--a3);border-radius:1px;"></div>
              <div style="width:2px;height:10px;background:var(--a3);border-radius:1px;"></div>
              <div style="width:2px;height:16px;background:var(--a3);border-radius:1px;"></div>
              <div style="width:2px;height:8px;background:var(--a3);border-radius:1px;"></div>
            </div>
            <div id="player-progress" style="width:0%;height:100%;background:linear-gradient(90deg, rgba(59,158,255,0.15) 0%, rgba(124,95,230,0.15) 100%);border-right:2px solid var(--a3);transition:width 0.15s linear;"></div>
          </div>
          <span id="player-time-duration" style="font-size:.72rem;font-family:'Space Mono',monospace;color:var(--txt2);min-width:32px;text-align:right;">0:00</span>
        </div>
      </div>
      <audio id="player" style="display:none;"></audio>
      <div style="display:flex;gap:10px;margin-bottom:10px;">
        <button onclick="doDownload('mp3')" style="flex:1;background:rgba(61,214,140,0.12);border:1px solid rgba(61,214,140,0.28);color:var(--ok);border-radius:12px;padding:12px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;font-size:.85rem;">
          <i class="fa-solid fa-download" style="margin-right:6px;"></i>MP3
        </button>
        <button onclick="doDownload('wav')" style="flex:1;background:rgba(124,95,230,0.12);border:1px solid rgba(124,95,230,0.28);color:var(--a2);border-radius:12px;padding:12px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;font-size:.85rem;">
          <i class="fa-solid fa-download" style="margin-right:6px;"></i>WAV
        </button>
        <button onclick="copyAudioLink()" style="flex:1;background:rgba(59,158,255,0.12);border:1px solid rgba(59,158,255,0.28);color:var(--a1);border-radius:12px;padding:12px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;font-size:.85rem;">
          <i class="fa-solid fa-link" style="margin-right:6px;"></i>Copy Link
        </button>
      </div>
      <button onclick="doGenerate()" style="width:100%;background:rgba(59,158,255,0.08);border:1px solid rgba(59,158,255,0.2);color:var(--a1);border-radius:12px;padding:11px;font-weight:600;cursor:pointer;font-family:'Syne',sans-serif;font-size:.88rem;">
        <i class="fa-solid fa-rotate-right" style="margin-right:6px;"></i>Regenerate
      </button>
    </div>
  </div>
</section>

{voices_table_html}

<!-- USE CASES -->
<section style="max-width:1100px;margin:0 auto;padding:0 18px 56px;">
  <h2 style="font-size:clamp(1.4rem,3vw,2rem);font-weight:800;margin-bottom:8px;text-align:center;">
    Who Uses <span class="tg">{lang_name} TTS</span>?
  </h2>
  <p style="text-align:center;color:var(--muted);font-size:.92rem;margin-bottom:28px;">Popular use cases for {lang_name} voice generation in {country}</p>
  <div style="text-align:center;">
    {use_case_tags}
  </div>
</section>

<!-- FEATURES -->
<section style="max-width:1100px;margin:0 auto;padding:0 18px 56px;">
  <h2 style="font-size:clamp(1.4rem,3vw,2rem);font-weight:800;margin-bottom:28px;text-align:center;">
    Why VoicePro for <span class="tg">{lang_name}</span>?
  </h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;">
    <div class="feature-card">
      <div style="font-size:1.9rem;margin-bottom:14px;">🧠</div>
      <h3 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:8px;">{lang_name}-Native Neural Voices</h3>
      <p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Voices trained specifically on {lang_name} ({country}) native speaker data. Correct pronunciation, natural intonation, and authentic regional accent.</p>
    </div>
    <div class="feature-card">
      <div style="font-size:1.9rem;margin-bottom:14px;">⚡</div>
      <h3 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:8px;">Instant MP3 / WAV Download</h3>
      <p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">No queues, no waiting. Generate up to 5,000 characters (~5 min of audio) in seconds. Download MP3 for web or WAV for studio quality.</p>
    </div>
    <div class="feature-card">
      <div style="font-size:1.9rem;margin-bottom:14px;">🎛️</div>
      <h3 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:8px;">Full Voice Control</h3>
      <p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Adjust speed (0.5x–2x), pitch (−10 to +10), volume, and speaking style. 8 voice characters and 16 styles — fully customizable.</p>
    </div>
    <div class="feature-card">
      <div style="font-size:1.9rem;margin-bottom:14px;">🔒</div>
      <h3 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:8px;">No Login, No Tracking</h3>
      <p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">No account required. Your {lang_name} text is processed on-demand and never stored, sold, or shared. 100% private.</p>
    </div>
    <div class="feature-card">
      <div style="font-size:1.9rem;margin-bottom:14px;">🆓</div>
      <h3 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:8px;">Commercial Use Included</h3>
      <p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Generated {lang_name} audio is yours. Use it in YouTube videos, courses, podcasts, IVR systems, or any commercial project — royalty-free.</p>
    </div>
    <div class="feature-card">
      <div style="font-size:1.9rem;margin-bottom:14px;">📱</div>
      <h3 style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:8px;">Works on Any Device</h3>
      <p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Fully responsive on mobile, tablet, and desktop. No app download needed — works directly in your browser on iOS, Android, and PC.</p>
    </div>
  </div>
</section>

<!-- FAQ -->
<section style="max-width:780px;margin:0 auto;padding:0 18px 64px;">
  <h2 style="font-size:clamp(1.4rem,3vw,2rem);font-weight:800;margin-bottom:8px;text-align:center;">
    Frequently Asked <span class="tg">Questions</span>
  </h2>
  <p style="text-align:center;color:var(--muted);font-size:.92rem;margin-bottom:28px;">About {lang_name} Text to Speech</p>
  {faq_html}
</section>

<!-- RELATED LANGUAGES -->
<section style="max-width:1100px;margin:0 auto;padding:0 18px 64px;">
  <h2 style="font-size:1.3rem;font-weight:800;margin-bottom:16px;text-align:center;">
    Explore Other <span class="tg">Languages</span>
  </h2>
  <div style="text-align:center;max-width:800px;margin:0 auto;">
    {related_links}
  </div>
</section>

<!-- FOOTER -->
<footer class="pro-footer">
  <div style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr;gap:40px;padding-bottom:44px;border-bottom:1px solid var(--border);">
    <div>
      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.2rem;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
        <div style="width:32px;height:32px;background:linear-gradient(135deg,var(--a1),var(--a2));border-radius:9px;display:flex;align-items:center;justify-content:center;">
          <i class="fa-solid fa-microphone-lines" style="color:#fff;font-size:.8rem;"></i>
        </div>
        Voice<span style="color:var(--a1);">Pro</span>
      </div>
      <p style="color:var(--muted);font-size:.875rem;line-height:1.75;margin-bottom:8px;">Free {lang_name} Text-to-Speech. Neural AI voices, instant MP3 download. No login — ever.</p>
    </div>
    <div>
      <p class="footer-heading">Navigation</p>
      <a href="/" class="footer-link">Home / Studio</a>
      <a href="/blog.html" class="footer-link">Blog</a>
      <a href="/about.html" class="footer-link">About Us</a>
      <a href="/contact.html" class="footer-link">Contact</a>
    </div>
    <div>
      <p class="footer-heading">Legal</p>
      <a href="/privacy.html" class="footer-link">Privacy Policy</a>
      <a href="/terms.html" class="footer-link">Terms of Service</a>
    </div>
  </div>
  <div style="max-width:1100px;margin:0 auto;padding:20px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
    <p style="color:var(--muted);font-size:.8rem;">&copy; 2026 VoicePro TTS Studio · {lang_name} Text to Speech · {country}</p>
    <p style="color:var(--muted);font-size:.78rem;"><span style="color:var(--a1);font-weight:600;">Free AI TTS 2026</span></p>
  </div>
</footer>

<div id="toast" class="toast">
  <div style="display:flex;align-items:center;gap:10px;">
    <i id="toast-icon" class="fa-solid fa-circle-check" style="color:var(--ok);font-size:1rem;"></i>
    <span id="toast-msg">Success!</span>
  </div>
</div>

<script>
  const LANG_CODE = "{lang_code}";
  const LANG_NAME = "{lang_name}";
  const SAMPLE_TEXT = {sample_json};
  let lastAudio = null, lastFile = null;

  function loadSample() {{
    const t = document.getElementById('txt');
    t.value = SAMPLE_TEXT;
    onTxt(t);
    showToast('Sample ' + LANG_NAME + ' text loaded!');
  }}

  function syncLang(v) {{ /* lang already fixed for this page */ }}

  function onTxt(el) {{
    let c = el.value.length;
    if (c > 5000) {{ el.value = el.value.substring(0, 5000); c = 5000; }}
    document.getElementById('cc').textContent = c;
    document.getElementById('te').textContent = Math.ceil(c / 15);
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }}

  function showToast(msg, type='ok') {{
    const e=document.getElementById('toast'), ic=document.getElementById('toast-icon'), tx=document.getElementById('toast-msg');
    ic.className = type==='ok' ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-exclamation';
    ic.style.color = type==='ok' ? 'var(--ok)' : '#f87171';
    tx.textContent = msg; e.classList.add('on');
    setTimeout(() => e.classList.remove('on'), 3500);
  }}

  async function doGenerate() {{
    const text = document.getElementById('txt').value.trim();
    if (!text) {{ showToast('Please enter ' + LANG_NAME + ' text first!', 'err'); return; }}
    const btn = document.getElementById('gen-btn'), lbl = document.getElementById('gen-lbl');
    btn.disabled = true;
    lbl.innerHTML = '<span class="spinner"></span><span style="margin-left:9px;">Generating…</span>';
    document.getElementById('result-area').classList.add('hidden');

    const fd = new FormData();
    fd.append('text', text);
    fd.append('language', LANG_CODE);
    fd.append('voice_type', document.getElementById('sel-voice').value);
    fd.append('rate', parseFloat(document.getElementById('sl-rate').value).toFixed(2));
    fd.append('pitch', document.getElementById('sl-pitch').value);
    fd.append('volume', document.getElementById('sl-vol').value);
    fd.append('style', document.getElementById('sel-style').value);
    fd.append('format', document.getElementById('sel-fmt').value);
    fd.append('response_type', 'base64');

    try {{
      const r = await fetch('/generate', {{ method: 'POST', body: fd }});
      const d = await r.json();
      if (d.success) {{
        lastAudio = d.audio_data; lastFile = d.filename;
        document.getElementById('player').src = d.audio_data;
        
        // Update custom player UI
        const selVal = document.getElementById('sel-voice').value;
        const selOpt = document.querySelector('#sel-voice option[value="' + selVal + '"]');
        const voiceName = selOpt ? selOpt.textContent.replace(/^[^\s]+\s+/, '') : selVal;
        
        document.getElementById('custom-player-meta').textContent = d.method + ' · ' + voiceName + ' · ' + LANG_NAME;
        
        let badge = 'Natural';
        if (selVal.includes('kid')) badge = 'Kid';
        else if (selVal.includes('teen')) badge = 'Teen';
        else if (selVal.includes('young')) badge = 'Young Adult';
        else if (selVal.includes('mid')) badge = 'Middle-Aged';
        else if (selVal.includes('senior')) badge = 'Senior';
        else if (selVal === 'old') badge = 'Mature';
        else if (selVal === 'young') badge = 'Young';
        
        document.getElementById('custom-player-badge').textContent = badge;
        
        document.getElementById('gen-info').textContent = d.method + ' · ' + (d.voice_used || '') + ' · ' + LANG_CODE;
        document.getElementById('result-area').classList.remove('hidden');
        showToast(LANG_NAME + ' audio ready! 🎉');
      }} else {{
        showToast(d.error || 'Generation failed', 'err');
      }}
    }} catch(e) {{
      showToast('Network error — please retry', 'err');
    }} finally {{
      btn.disabled = false;
      lbl.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles" style="margin-right:8px;"></i>Generate {lang_name} Voice';
    }}
  }}

  function doDownload(type) {{
    if (!lastAudio) {{ showToast('No audio yet.', 'err'); return; }}
    const ext = type === 'wav' ? 'wav' : 'mp3';
    const fn = (lastFile || 'voicepro_' + LANG_CODE + '_' + Date.now()).replace(/\\.[^.]+$/, '') + '.' + ext;
    const a = document.createElement('a');
    a.href = lastAudio; a.download = fn;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    showToast('Downloading ' + ext.toUpperCase() + '… 🎵');
  }}

  function copyAudioLink() {{
    if (!lastAudio) {{ showToast('Generate audio first!', 'err'); return; }}
    navigator.clipboard.writeText(lastAudio)
      .then(() => showToast('Audio link copied! 📋'))
      .catch(() => showToast('Copy failed', 'err'));
  }}

  function toggleFaq(id) {{
    const item = document.getElementById(id);
    const wasOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(el => el.classList.remove('open'));
    if (!wasOpen) item.classList.add('open');
  }}

  function toggleTheme() {{
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const target = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', target);
    localStorage.setItem('theme', target);
    updateThemeIcons();
  }}

  function updateThemeIcons() {{
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    const btn = document.getElementById('theme-btn');
    const btnMob = document.getElementById('theme-btn-mob');
    const iconClass = theme === 'light' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
    if (btn) btn.innerHTML = '<i class="' + iconClass + '"></i>';
    if (btnMob) btnMob.innerHTML = '<i class="' + iconClass + '" style="margin-right:8px;"></i>Toggle Theme';
  }}

  /* ── CUSTOM PLAYER CONTROLS ── */
  function togglePlayPause() {{
    const audio = document.getElementById('player');
    if (!audio) return;
    if (audio.paused) {{
      audio.play();
    }} else {{
      audio.pause();
    }}
  }}

  function seekAudio(e) {{
    const audio = document.getElementById('player');
    if (!audio || !audio.duration) return;
    const rect = document.getElementById('player-timeline').getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    audio.currentTime = pct * audio.duration;
  }}

  function formatTime(secs) {{
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }}

  function initCustomPlayer() {{
    const audio = document.getElementById('player');
    if (!audio) return;
    
    audio.addEventListener('play', () => {{
      const icon = document.getElementById('play-pause-icon');
      if (icon) icon.className = 'fa-solid fa-pause';
    }});
    
    audio.addEventListener('pause', () => {{
      const icon = document.getElementById('play-pause-icon');
      if (icon) icon.className = 'fa-solid fa-play';
    }});
    
    audio.addEventListener('timeupdate', () => {{
      const cur = audio.currentTime;
      const dur = audio.duration || 0;
      const pct = dur > 0 ? (cur / dur) * 100 : 0;
      const prog = document.getElementById('player-progress');
      if (prog) prog.style.width = pct + '%';
      const curTxt = document.getElementById('player-time-current');
      if (curTxt) curTxt.textContent = formatTime(cur);
      const durTxt = document.getElementById('player-time-duration');
      if (durTxt && audio.duration) durTxt.textContent = formatTime(dur);
    }});
    
    audio.addEventListener('loadedmetadata', () => {{
      const durTxt = document.getElementById('player-time-duration');
      if (durTxt && audio.duration) durTxt.textContent = formatTime(audio.duration);
    }});

    audio.addEventListener('ended', () => {{
      const icon = document.getElementById('play-pause-icon');
      if (icon) icon.className = 'fa-solid fa-play';
      const prog = document.getElementById('player-progress');
      if (prog) prog.style.width = '0%';
      const curTxt = document.getElementById('player-time-current');
      if (curTxt) curTxt.textContent = '0:00';
    }});
  }}

  document.addEventListener('DOMContentLoaded', () => {{
    updateThemeIcons();
    initCustomPlayer();
  }});
</script>
</body>
</html>"""


# ──────────────────────────────────────────────────────────────
#  BUILD PAGES
ALL_VOICES_DEFINITION = [
    { 'id': 'female-1', 'name': 'Female 1 – Natural', 'icon': '👩', 'badge': 'Female (Adult)' },
    { 'id': 'female-2', 'name': 'Female 2 – Soft', 'icon': '👩‍🦰', 'badge': 'Female (Soft)' },
    { 'id': 'female-3', 'name': 'Female 3 – Pro', 'icon': '👩‍💼', 'badge': 'Female (Professional)' },
    { 'id': 'male-1', 'name': 'Male 1 – Deep', 'icon': '👨', 'badge': 'Male (Adult)' },
    { 'id': 'male-2', 'name': 'Male 2 – Friendly', 'icon': '👨‍🦰', 'badge': 'Male (Friendly)' },
    { 'id': 'male-3', 'name': 'Male 3 – Authority', 'icon': '👨‍💼', 'badge': 'Male (Authority)' },
    { 'id': 'young', 'name': 'Young Voice', 'icon': '🧒', 'badge': 'Child / Energetic' },
    { 'id': 'old', 'name': 'Mature Voice', 'icon': '🧓', 'badge': 'Senior / Seasoned' },
    { 'id': 'kid-f1', 'name': 'Lily (Age 7) – Kid Female', 'icon': '👧', 'badge': 'Kid (Female)' },
    { 'id': 'kid-f2', 'name': 'Chloe (Age 10) – Kid Female', 'icon': '👧', 'badge': 'Kid (Female)' },
    { 'id': 'kid-m1', 'name': 'Mason (Age 8) – Kid Male', 'icon': '👦', 'badge': 'Kid (Male)' },
    { 'id': 'kid-m2', 'name': 'Logan (Age 12) – Kid Male', 'icon': '👦', 'badge': 'Kid (Male)' },
    { 'id': 'teen-f1', 'name': 'Sophia (Age 17) – Teen Female', 'icon': '👩', 'badge': 'Teen (Female)' },
    { 'id': 'teen-f2', 'name': 'Emma (Age 19) – Teen Female', 'icon': '👩', 'badge': 'Teen (Female)' },
    { 'id': 'teen-m1', 'name': 'Ethan (Age 16) – Teen Male', 'icon': '👨', 'badge': 'Teen (Male)' },
    { 'id': 'teen-m2', 'name': 'Noah (Age 18) – Teen Male', 'icon': '👨', 'badge': 'Teen (Male)' },
    { 'id': 'young-f1', 'name': 'Aria (Age 25) – Female Natural', 'icon': '👩‍🦰', 'badge': 'Young Adult (Female)' },
    { 'id': 'young-f2', 'name': 'Jenny (Age 28) – Female Friendly', 'icon': '👩', 'badge': 'Young Adult (Female)' },
    { 'id': 'young-f3', 'name': 'Sara (Age 32) – Female Pro', 'icon': '👩‍💼', 'badge': 'Young Adult (Female)' },
    { 'id': 'young-m1', 'name': 'Guy (Age 26) – Male Natural', 'icon': '👨‍🦰', 'badge': 'Young Adult (Male)' },
    { 'id': 'young-m2', 'name': 'Roger (Age 30) – Male Professional', 'icon': '👨‍💼', 'badge': 'Young Adult (Male)' },
    { 'id': 'young-m3', 'name': 'Ryan (Age 34) – Male Deep', 'icon': '👨', 'badge': 'Young Adult (Male)' },
    { 'id': 'mid-f1', 'name': 'Michelle (Age 45) – Female Executive', 'icon': '👩‍🦳', 'badge': 'Middle-Aged (Female)' },
    { 'id': 'mid-f2', 'name': 'Helen (Age 52) – Female Warm', 'icon': '👩‍🦳', 'badge': 'Middle-Aged (Female)' },
    { 'id': 'mid-m1', 'name': 'Steffan (Age 48) – Male Presenter', 'icon': '👨‍🦳', 'badge': 'Middle-Aged (Male)' },
    { 'id': 'mid-m2', 'name': 'Brian (Age 55) – Male Narrator', 'icon': '👨‍🦳', 'badge': 'Middle-Aged (Male)' },
    { 'id': 'senior-f1', 'name': 'Abigail (Age 68) – Senior Female', 'icon': '👵', 'badge': 'Senior (Female)' },
    { 'id': 'senior-f2', 'name': 'Esther (Age 75) – Senior Female', 'icon': '👵', 'badge': 'Senior (Female)' },
    { 'id': 'senior-m1', 'name': 'Arthur (Age 70) – Senior Male', 'icon': '👴', 'badge': 'Senior (Male)' },
    { 'id': 'senior-m2', 'name': 'Thomas (Age 82) – Senior Male', 'icon': '👴', 'badge': 'Senior (Male)' }
]

def get_voice_for_table(lang: str, voice_type: str):
    voice = VOICE_MAPPING.get((lang, voice_type))
    if voice:
        return voice, "Direct Model"
    
    is_male = 'm' in voice_type.lower() or 'male' in voice_type.lower()
    fallback_sequence = ['male-1', 'female-1'] if is_male else ['female-1', 'male-1']
    
    for gender_vt in fallback_sequence:
        v = VOICE_MAPPING.get((lang, gender_vt))
        if v:
            return v, f"Language Fallback ({gender_vt})"
            
    lang_prefix = lang.split('-')[0]
    for gender_vt in fallback_sequence:
        for k, v in VOICE_MAPPING.items():
            if k[0].startswith(lang_prefix) and k[1] == gender_vt:
                return v, f"Regional Fallback ({gender_vt})"
                
    return 'en-US-AriaNeural', "Global Fallback"


# ──────────────────────────────────────────────────────────────
#  BUILD PAGES
# ──────────────────────────────────────────────────────────────
def build_page(entry):
    code, lang_name, country, flag, native_name, voice_count = entry
    page_slug = slug(code)
    html_lang = code.split("-")[0]

    meta_title = f"Free {lang_name} Text to Speech {country} – AI Voice Generator MP3 | VoicePro 2026"
    meta_desc  = (f"Convert {lang_name} text to speech free online. {voice_count} neural AI voices for {country}. "
                  f"Instant MP3/WAV download, no login. Best {lang_name} TTS tool 2026.")
    meta_kw    = (f"{lang_name.lower()} text to speech, {lang_name.lower()} tts, {lang_name.lower()} voice generator, "
                  f"free {lang_name.lower()} tts {country.lower()}, {lang_name.lower()} ai voice, "
                  f"{native_name} text to speech, {code} tts, free tts {country.lower()}")
    og_title   = f"Free {lang_name} Text to Speech – VoicePro TTS Studio {country}"

    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": f"VoicePro {lang_name} TTS Studio",
        "url": f"https://www.texttoaudiomp3.site/tts/{page_slug}",
        "description": meta_desc,
        "applicationCategory": "MultimediaApplication",
        "operatingSystem": "Web Browser",
        "inLanguage": code,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.9", "reviewCount": "1200"}
    }

    # Use cases
    uc_tags = "\n".join(f'<span class="use-tag">✓ {uc}</span>' for uc in use_cases(lang_name, country))

    # FAQ
    faq_blocks = []
    for i, faq in enumerate(faq_items(lang_name, country, code)):
        fid = f"faq{i+1}"
        open_cls = " open" if i == 0 else ""
        faq_blocks.append(f"""<div class="faq-item{open_cls}" id="{fid}">
  <div class="faq-q" onclick="toggleFaq('{fid}')"><span>{faq['q']}</span><i class="fa-solid fa-chevron-down faq-chev"></i></div>
  <div class="faq-a"><p>{faq['a']}</p></div>
</div>""")
    faq_html = "\n".join(faq_blocks)

    # Related language links (pick ~20 others)
    related = [e for e in LANGUAGES if e[0] != code][:20]
    related_links = "\n".join(
        f'<a href="/tts/{slug(e[0])}" class="lang-pill">{e[3]} {e[1]} ({e[2]})</a>'
        for e in related
    )

    # Generate Voice table HTML
    voices_rows = []
    for v in ALL_VOICES_DEFINITION:
        model, mapping_type = get_voice_for_table(code, v['id'])
        gender_age = v['badge']
        emoji = v['icon']
        char_name = v['name'].split("–")[0].strip()
        voices_rows.append(f"""
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:12px 18px;font-weight:600;">{emoji} {char_name}</td>
          <td style="padding:12px 18px;"><span class="badge-pill" style="margin:0;font-size:.68rem;background:rgba(124,95,230,0.08);color:var(--a2);border:1px solid rgba(124,95,230,0.12);">{gender_age}</span></td>
          <td style="padding:12px 18px;font-family:\'Space Mono\',monospace;font-size:.76rem;color:var(--muted);">{model}</td>
          <td style="padding:12px 18px;font-size:.78rem;color:var(--txt2);">{mapping_type}</td>
        </tr>""")
    
    voices_rows_html = "".join(voices_rows)
    voices_table_html = f"""
<!-- VOICE PROFILES TABLE -->
<section style="max-width:920px;margin:0 auto 56px;padding:0 18px;">
  <h2 style="font-size:clamp(1.4rem,3vw,1.9rem);font-weight:800;margin-bottom:8px;text-align:center;">
    Available <span class="tg">{lang_name} Voice Profiles</span>
  </h2>
  <p style="text-align:center;color:var(--muted);font-size:.9rem;margin-bottom:24px;">Explore the full list of neural voice models available for {lang_name} ({country}) speech generation.</p>
  <div style="overflow-x:auto;background:var(--card);border:1px solid var(--border);border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,0.02);">
    <table style="width:100%;border-collapse:collapse;text-align:left;font-size:.88rem;color:var(--txt);">
      <thead>
        <tr style="border-bottom:1px solid var(--border);background:rgba(255,255,255,0.015);">
          <th style="padding:14px 18px;font-weight:700;color:var(--muted);font-family:\'Syne\',sans-serif;">Voice Character</th>
          <th style="padding:14px 18px;font-weight:700;color:var(--muted);font-family:\'Syne\',sans-serif;">Gender / Age</th>
          <th style="padding:14px 18px;font-weight:700;color:var(--muted);font-family:\'Syne\',sans-serif;">Neural Model ID</th>
          <th style="padding:14px 18px;font-weight:700;color:var(--muted);font-family:\'Syne\',sans-serif;">Mapping Type</th>
        </tr>
      </thead>
      <tbody>
        {voices_rows_html}
      </tbody>
    </table>
  </div>
</section>"""

    page = PAGE_TEMPLATE.format(
        html_lang=html_lang,
        meta_title=meta_title,
        meta_desc=meta_desc,
        meta_keywords=meta_kw,
        og_title=og_title,
        slug=page_slug,
        schema_json=json.dumps(schema, ensure_ascii=False),
        flag=flag,
        lang_upper=lang_name.upper(),
        lang_name=lang_name,
        lang_code=code,
        country=country,
        voice_count=voice_count,
        native_name=native_name,
        sample_json=json.dumps(sample_text(code, lang_name), ensure_ascii=False),
        use_case_tags=uc_tags,
        faq_html=faq_html,
        related_links=related_links,
        voices_table_html=voices_table_html,
    )
    return page_slug, page


def main():
    out_dir = os.path.join("templates", "tts")
    os.makedirs(out_dir, exist_ok=True)

    manifest = []
    for entry in LANGUAGES:
        page_slug, html = build_page(entry)
        filepath = os.path.join(out_dir, f"{page_slug}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        manifest.append({
            "code": entry[0], "lang": entry[1], "country": entry[2],
            "slug": page_slug, "url": f"/tts/{page_slug}"
        })
        print(f"  [OK]  {filepath}")

    # Write manifest JSON
    with open(os.path.join("templates", "tts_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nGenerated {len(manifest)} pSEO pages -> templates/tts/")
    print(f"Manifest -> templates/tts_manifest.json")
    return manifest


if __name__ == "__main__":
    main()
