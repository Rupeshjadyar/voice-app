"""
VoicePro TTS – Programmatic SEO Page Generator
Generates one landing page per language+country combination.
Run:  python generate_pseo_pages.py
Output: templates/tts/<slug>.html  (one file per language)
"""

import os, json, re, datetime
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
PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-X7HBHXRYG5"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-X7HBHXRYG5');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9707682105347147" crossorigin="anonymous"></script>
<meta name="monetag" content="df392a699f813691935e38bba65c002d">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta_title}</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{meta_keywords}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta name="author" content="VoicePro TTS Studio">
<link rel="canonical" href="https://www.texttoaudiomp3.site/tts/{slug}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.texttoaudiomp3.site/tts/{slug}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:image" content="https://www.texttoaudiomp3.site/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{meta_desc}">
<meta name="theme-color" content="#0a0f1a">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
<link rel="manifest" href="/manifest.json">
<script type="application/ld+json">{schema_json}</script>
<script type="application/ld+json">{{
  "@context":"https://schema.org",
  "@type":"BreadcrumbList",
  "itemListElement":[
    {{"@type":"ListItem","position":1,"name":"Home","item":"https://www.texttoaudiomp3.site/"}},
    {{"@type":"ListItem","position":2,"name":"All Languages TTS","item":"https://www.texttoaudiomp3.site/tts/"}},
    {{"@type":"ListItem","position":3,"name":"{lang_name} Text to Speech","item":"https://www.texttoaudiomp3.site/tts/{slug}"}}
  ]
}}</script>
<script>(function(){{const t=localStorage.getItem('theme')||'light';document.documentElement.setAttribute('data-theme',t);}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  :root{{--bg:#d8dee9;--card:#ffffff;--border:rgba(15,23,42,0.12);--borderH:rgba(59,158,255,0.4);--a1:#1d4ed8;--a2:#6d28d9;--a3:#db2777;--txt:#0f172a;--txt2:#334155;--muted:#64748b;--panel:#edf2f7;--ok:#10b981;--grid-line:rgba(0,0,0,0.02);--shadow:0 10px 30px -5px rgba(0,0,0,0.04),0 8px 16px -6px rgba(0,0,0,0.04);--nav-bg:#ffffff;}}
  [data-theme="dark"]{{--bg:#070b12;--card:rgba(255,255,255,0.032);--border:rgba(255,255,255,0.07);--borderH:rgba(59,158,255,0.38);--a1:#3b9eff;--a2:#7c5fe6;--a3:#e94fa3;--txt:#dde4f0;--txt2:#b8c4d8;--muted:#6e7e98;--panel:#0c1220;--ok:#3dd68c;--grid-line:rgba(255,255,255,0.012);--shadow:none;--nav-bg:#070b12;}}
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
  html{{scroll-behavior:smooth;}}
  body{{background:var(--bg);color:var(--txt);font-family:'DM Sans',sans-serif;min-height:100vh;display:flex;flex-direction:column;-webkit-font-smoothing:antialiased;}}
  body::before{{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse 80% 50% at 20% 10%,rgba(59,158,255,0.055) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 80% 80%,rgba(124,95,230,0.045) 0%,transparent 60%),repeating-linear-gradient(0deg,transparent,transparent 63px,var(--grid-line) 64px),repeating-linear-gradient(90deg,transparent,transparent 63px,var(--grid-line) 64px);}}
  body>*{{position:relative;z-index:1;}}
  h1,h2,h3,h4,h5{{font-family:'Syne',sans-serif;letter-spacing:-0.02em;line-height:1.15;}}
  .tg{{background:linear-gradient(130deg,var(--a1) 0%,var(--a2) 50%,var(--a3) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
  .mono{{font-family:'Space Mono',monospace;}}
  .glass-nav{{background:var(--nav-bg);backdrop-filter:blur(24px);border-bottom:1px solid var(--border);opacity:0.96;}}
  .nav-btn{{padding:7px 14px;border-radius:10px;font-size:.85rem;font-weight:500;transition:all .18s;color:var(--muted);border:none;background:transparent;cursor:pointer;font-family:'DM Sans',sans-serif;text-decoration:none;display:inline-block;}}
  .nav-btn:hover,.nav-active{{color:var(--a1);background:rgba(59,158,255,0.09);}}
  .glass{{background:var(--card);backdrop-filter:blur(16px);border:1px solid var(--border);border-radius:22px;box-shadow:var(--shadow);}}
  .gcard{{background:var(--card);border:1px solid var(--border);border-radius:16px;box-shadow:var(--shadow);transition:border-color .25s,box-shadow .25s,transform .2s;}}
  .gcard:hover{{border-color:var(--borderH);box-shadow:0 0 28px rgba(59,158,255,0.08);transform:translateY(-1px);}}
  .ctrl{{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:14px 16px;}}
  .btn-primary{{background:linear-gradient(135deg,var(--a1),var(--a2),var(--a3));background-size:220%;border:none;border-radius:14px;color:#fff;font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;letter-spacing:0.02em;padding:15px 28px;cursor:pointer;width:100%;transition:background-position .45s,transform .15s,box-shadow .3s;box-shadow:0 4px 28px rgba(59,158,255,0.24);}}
  .btn-primary:hover{{background-position:right;box-shadow:0 6px 36px rgba(59,158,255,0.4);}}
  .btn-primary:active{{transform:scale(.976);}}
  .btn-primary:disabled{{opacity:.5;cursor:not-allowed;transform:none;}}
  textarea{{background:var(--panel);border:1.5px solid var(--border);border-radius:14px;color:var(--txt);font-family:'DM Sans',sans-serif;font-size:.96rem;line-height:1.65;padding:14px 18px 24px;width:100%;outline:none;resize:none;transition:border-color .2s,box-shadow .2s;min-height:120px;max-height:400px;overflow-y:auto;}}
  textarea:focus{{border-color:var(--a1);box-shadow:0 0 0 3px rgba(59,158,255,0.13);}}
  textarea::placeholder{{color:var(--muted);}}
  select{{appearance:none;background:var(--panel);border:1px solid var(--border);border-radius:12px;color:var(--txt);font-family:'DM Sans',sans-serif;font-size:.9rem;padding:11px 36px 11px 14px;outline:none;cursor:pointer;width:100%;transition:border-color .2s;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='11' height='11' viewBox='0 0 12 12'%3E%3Cpath fill='%236e7e98' d='M6 8L1 3h10z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;}}
  select:focus{{border-color:var(--a1);box-shadow:0 0 0 3px rgba(59,158,255,0.13);}}
  select option{{background:var(--bg);color:var(--txt);}}
  input[type=range]{{-webkit-appearance:none;width:100%;background:transparent;cursor:pointer;}}
  input[type=range]::-webkit-slider-runnable-track{{height:5px;background:var(--border);border-radius:3px;}}
  input[type=range]::-webkit-slider-thumb{{-webkit-appearance:none;height:18px;width:18px;border-radius:50%;background:linear-gradient(135deg,var(--a1),var(--a2));cursor:pointer;margin-top:-6.5px;border:2px solid rgba(255,255,255,0.88);box-shadow:0 0 10px rgba(59,158,255,0.55);transition:transform .2s;}}
  input[type=range]::-webkit-slider-thumb:hover{{transform:scale(1.28);}}
  .spinner{{width:20px;height:20px;border:3px solid rgba(255,255,255,0.18);border-top-color:#fff;border-radius:50%;animation:sp .8s linear infinite;display:inline-block;vertical-align:middle;}}
  @keyframes sp{{to{{transform:rotate(360deg)}}}}
  .toast{{position:fixed;bottom:22px;right:22px;background:rgba(8,13,24,0.97);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,0.12);border-radius:14px;padding:13px 20px;color:#f1f5f9;transform:translateY(120px);opacity:0;transition:all .3s cubic-bezier(.34,1.56,.64,1);z-index:99999;max-width:320px;font-size:.88rem;box-shadow:0 8px 32px rgba(0,0,0,0.3);}}
  .toast.on{{transform:translateY(0);opacity:1;}}
  .hidden{{display:none!important;}}
  .slbl{{display:block;font-family:'Syne',sans-serif;font-size:.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;}}
  .statc{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:18px;text-align:center;box-shadow:var(--shadow);transition:border-color .2s,box-shadow .2s;}}
  .statc:hover{{border-color:rgba(59,158,255,0.2);}}
  audio{{accent-color:var(--a1);width:100%;border-radius:10px;margin-bottom:14px;display:block;}}
  #result-area{{border-top:1px solid var(--border);padding-top:22px;margin-top:22px;}}
  .badge-pill{{display:inline-block;background:rgba(59,158,255,0.1);border:1px solid rgba(59,158,255,0.2);border-radius:100px;padding:5px 16px;font-size:.74rem;font-weight:700;color:var(--a1);letter-spacing:.6px;font-family:'Syne',sans-serif;}}
  .faq-item{{border:1px solid var(--border);border-radius:16px;overflow:hidden;margin-bottom:10px;transition:border-color .2s;}}
  .faq-item:hover{{border-color:rgba(59,158,255,0.28);}}
  .faq-q{{padding:19px 22px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;font-weight:700;font-family:'Syne',sans-serif;font-size:.95rem;color:var(--txt);background:rgba(255,255,255,0.02);transition:background .15s;user-select:none;}}
  .faq-q:hover{{background:rgba(59,158,255,0.05);}}
  .faq-q .faq-chev{{color:var(--a1);transition:transform .25s;font-size:.78rem;flex-shrink:0;margin-left:12px;}}
  .faq-item.open .faq-chev{{transform:rotate(180deg);}}
  .faq-a{{max-height:0;overflow:hidden;transition:max-height .38s ease,padding .25s;}}
  .faq-item.open .faq-a{{max-height:300px;padding:0 22px 20px;}}
  .faq-a p{{color:var(--txt2);font-size:.91rem;line-height:1.78;}}
  .feature-card{{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:26px;transition:border-color .25s,box-shadow .25s,transform .2s;}}
  .feature-card:hover{{border-color:var(--borderH);box-shadow:0 0 24px rgba(59,158,255,0.07);transform:translateY(-2px);}}
  .feature-icon{{width:46px;height:46px;border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:1.25rem;margin-bottom:16px;}}
  .lang-badge{{display:inline-block;background:rgba(59,158,255,0.09);border:1px solid rgba(59,158,255,0.18);border-radius:100px;padding:5px 14px;font-size:.8rem;color:var(--a1);margin:4px;font-weight:600;text-decoration:none;transition:all .2s;}}
  .lang-badge:hover{{background:rgba(59,158,255,0.18);transform:translateY(-1px);box-shadow:0 2px 10px rgba(59,158,255,0.15);}}
  .section-divider{{display:flex;align-items:center;gap:16px;margin-bottom:48px;}}
  .section-divider::before,.section-divider::after{{content:'';flex:1;height:1px;background:linear-gradient(90deg,transparent,var(--border),transparent);}}
  .section-label{{font-family:'Syne',sans-serif;font-size:.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);white-space:nowrap;}}
  .pro-footer{{background:rgba(5,8,14,0.97);border-top:1px solid var(--border);padding:52px 24px 0;margin-top:auto;}}
  .footer-heading{{font-family:'Syne',sans-serif;font-weight:700;font-size:.7rem;letter-spacing:1.6px;text-transform:uppercase;color:var(--muted);margin-bottom:14px;}}
  .footer-link{{display:block;color:var(--muted);text-decoration:none;font-size:.875rem;padding:4px 0;transition:color .18s,padding-left .18s;}}
  .footer-link:hover{{color:var(--a1);padding-left:4px;}}
  .tab-btn{{padding:10px 20px;border-radius:10px;font-size:.88rem;font-weight:600;border:none;cursor:pointer;transition:all .2s;font-family:'DM Sans',sans-serif;flex:1;text-align:center;}}
  .tab-btn.active{{background:linear-gradient(135deg,var(--a1),var(--a2));color:#fff;box-shadow:0 2px 12px rgba(59,158,255,0.3);}}
  .tab-btn:not(.active){{background:var(--panel);color:var(--muted);}}
  .use-tag{{display:inline-block;background:rgba(59,158,255,0.09);border:1px solid rgba(59,158,255,0.18);border-radius:100px;padding:6px 16px;font-size:.82rem;color:var(--a1);margin:4px;font-weight:500;}}
  .nav-desktop{{display:flex;}}
  .nav-mobile-btn{{display:none;}}
  .nav-mobile-menu{{display:none;}}
  .dl-tab{{flex:1;padding:10px 8px;border-radius:10px;border:1px solid var(--border);background:var(--panel);color:var(--muted);font-size:.8rem;font-weight:600;cursor:pointer;text-align:center;transition:all .2s;font-family:'Syne',sans-serif;}}
  .dl-tab.active{{border-color:var(--a1);background:rgba(59,158,255,0.12);color:var(--a1);}}
  @keyframes pulse-glow{{0%,100%{{box-shadow:0 0 12px rgba(59,158,255,0.3);}}50%{{box-shadow:0 0 22px rgba(59,158,255,0.55);}}}}
  .stats-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}}
  .inputs-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:18px;}}
  .controls-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px;}}
  .options-grid{{display:grid;grid-template-columns:2fr 1fr;gap:12px;margin-bottom:24px;}}
  .multi-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:18px;}}
  .footer-grid{{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:40px;padding-bottom:44px;border-bottom:1px solid var(--border);}}
  @media(max-width:768px){{
    .nav-desktop{{display:none!important;}}
    .nav-mobile-btn{{display:flex!important;align-items:center;justify-content:center;background:none;border:none;color:var(--muted);font-size:1.25rem;cursor:pointer;}}
    .nav-mobile-menu.active{{display:flex!important;flex-direction:column;gap:6px;background:var(--bg);border-top:1px solid var(--border);padding:14px 24px;position:absolute;top:60px;left:0;right:0;z-index:100;box-shadow:0 10px 15px -3px rgba(0,0,0,0.05);}}
    .nav-mobile-menu .nav-btn{{display:block;padding:10px 14px;text-align:left;border-radius:9px;width:100%;box-sizing:border-box;}}
    .footer-grid{{grid-template-columns:1fr 1fr;gap:28px;}}
    .stats-grid{{grid-template-columns:1fr;gap:10px;}}
  }}
  @media(max-width:640px){{
    .controls-grid{{grid-template-columns:1fr;gap:10px;}}
    .inputs-grid, .multi-grid, .options-grid{{grid-template-columns:1fr;gap:12px;}}
    .glass{{padding:20px!important;}}
  }}
  @media(max-width:480px){{
    .glass{{border-radius:16px;padding:16px!important;}}
    .footer-grid{{grid-template-columns:1fr;gap:20px;}}
    .btn-primary{{padding:13px 18px;font-size:.92rem;}}
  }}
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
      <a href="/terms.html" class="nav-btn"><i class="fa-solid fa-file-contract" style="margin-right:5px;"></i>Terms</a>
      <a href="/tts/" class="nav-btn nav-active">All Languages TTS</a>
      <button onclick="toggleTheme()" class="nav-btn" id="theme-btn" style="display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:10px;padding:0;cursor:pointer;" aria-label="Toggle theme">
        <i class="fa-solid fa-moon"></i>
      </button>
      <button id="pwa-install-btn" onclick="triggerPWAInstall()" style="display:none;align-items:center;gap:6px;padding:7px 14px;border-radius:10px;background:linear-gradient(135deg,var(--a1),var(--a2));border:none;color:#fff;cursor:pointer;font-size:.8rem;font-weight:700;font-family:'Syne',sans-serif;white-space:nowrap;box-shadow:0 0 12px rgba(59,158,255,0.3);animation:pulse-glow 2s infinite;" aria-label="Install App">
        <i class="fa-solid fa-mobile-screen-button"></i> Install App
      </button>
    </div>
    <button class="nav-mobile-btn" onclick="toggleMobileMenu()" style="background:none;border:none;color:var(--muted);font-size:1.2rem;">
      <i class="fa-solid fa-bars"></i>
    </button>
  </div>
  <div id="mobile-menu" class="nav-mobile-menu">
    <a href="/" class="nav-btn"><i class="fa-solid fa-house" style="margin-right:8px;"></i>Home</a>
    <a href="/about.html" class="nav-btn"><i class="fa-solid fa-circle-info" style="margin-right:8px;"></i>About</a>
    <a href="/contact.html" class="nav-btn"><i class="fa-solid fa-headset" style="margin-right:8px;"></i>Contact</a>
    <a href="/privacy.html" class="nav-btn"><i class="fa-solid fa-shield-halved" style="margin-right:8px;"></i>Privacy Policy</a>
    <a href="/terms.html" class="nav-btn"><i class="fa-solid fa-file-contract" style="margin-right:8px;"></i>Terms of Service</a>
    <a href="/tts/" class="nav-btn nav-active">All Languages TTS</a>
    <button onclick="toggleTheme();toggleMobileMenu()" class="nav-btn" id="theme-btn-mob" style="text-align:left;display:flex;align-items:center;gap:8px;cursor:pointer;width:100%;box-sizing:border-box;">
      <i class="fa-solid fa-moon"></i>Toggle Theme
    </button>
    <button id="pwa-install-btn-mob" onclick="triggerPWAInstall();toggleMobileMenu()" class="nav-btn" style="display:none;text-align:left;align-items:center;gap:8px;cursor:pointer;width:100%;box-sizing:border-box;background:linear-gradient(135deg,rgba(59,158,255,0.15),rgba(147,51,234,0.15));color:#3dd68c;font-weight:700;border:1px solid rgba(61,214,140,0.3);margin-top:6px;border-radius:10px;">
      <i class="fa-solid fa-mobile-screen-button" style="color:#3dd68c;"></i> Install VoicePro App
    </button>
  </div>
</nav>

<!-- ANNOUNCEMENT MARQUEE BAR -->
<div style="margin-top:60px;background:linear-gradient(90deg,#1d4ed8,#6d28d9,#db2777);color:#fff;font-family:'Syne',sans-serif;font-size:0.86rem;font-weight:700;padding:10px 0;box-shadow:0 4px 14px rgba(0,0,0,0.12);position:relative;z-index:40;">
  <div style="max-width:1400px;margin:0 auto;display:flex;align-items:center;padding:0 16px;">
    <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(0,0,0,0.32);padding:4px 12px;border-radius:99px;margin-right:12px;white-space:nowrap;flex-shrink:0;font-size:0.73rem;letter-spacing:1px;text-transform:uppercase;">
      <i class="fa-solid fa-bullhorn" style="color:#ffd700;"></i> {lang_upper} TTS
    </div>
    <marquee behavior="scroll" direction="left" scrollamount="7" onmouseover="this.stop();" onmouseout="this.start();" style="cursor:pointer;flex:1;padding-top:2px;">
      FREE {lang_name} TEXT TO SPEECH 2026 &nbsp;&#8226;&nbsp; {voice_count}+ Neural Voices for {lang_name} ({country}) &nbsp;&#8226;&nbsp; Instant MP3 &amp; WAV Download Free &nbsp;&#8226;&nbsp; Multi-Voice Dialogue Generator &nbsp;&#8226;&nbsp; Zero Login &nbsp;&#8226;&nbsp; 104 Languages Supported
    </marquee>
  </div>
</div>

<!-- HERO -->
<section style="padding:48px 20px 28px;max-width:1100px;margin:0 auto;text-align:center;">
  <nav style="font-size:.8rem;color:var(--muted);margin-bottom:18px;" aria-label="Breadcrumb">
    <a href="/" style="color:var(--a1);text-decoration:none;">Home</a>
    <span style="margin:0 6px;">&#8250;</span>
    <a href="/tts/" style="color:var(--a1);text-decoration:none;">All Languages</a>
    <span style="margin:0 6px;">&#8250;</span>
    <span style="color:var(--txt);">{lang_name} ({country})</span>
  </nav>
  <div class="badge-pill" style="margin-bottom:18px;">&#10022; FREE {lang_upper} TEXT TO SPEECH STUDIO 2026 &#10022;</div>
  <h1 style="font-size:clamp(2rem,5vw,3.4rem);font-weight:800;margin-bottom:16px;">
    <span class="tg">{lang_name} Text to Speech</span>
  </h1>
  <p style="color:var(--txt2);font-size:1.02rem;max-width:640px;margin:0 auto 24px;line-height:1.88;">
    {country} &nbsp;&#183;&nbsp; Neural AI Voice Generator &nbsp;&#183;&nbsp; No Login Required
  </p>
  <p style="color:var(--muted);font-size:.92rem;max-width:640px;margin:0 auto 28px;line-height:1.7;">
    Convert {lang_name} text to natural speech free online. {voice_count}+ neural AI voices for {country}. Instant MP3/WAV download. Best free {lang_name} TTS tool 2026.
  </p>
  <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:0;">
    <span style="background:rgba(61,214,140,0.1);border:1px solid rgba(61,214,140,0.2);color:var(--ok);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-check" style="margin-right:5px;"></i>100% Free</span>
    <span style="background:rgba(59,158,255,0.1);border:1px solid rgba(59,158,255,0.2);color:var(--a1);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-bolt" style="margin-right:5px;"></i>Instant MP3</span>
    <span style="background:rgba(124,95,230,0.1);border:1px solid rgba(124,95,230,0.2);color:var(--a2);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-robot" style="margin-right:5px;"></i>{voice_count}+ Neural Voices</span>
    <span style="background:rgba(233,79,163,0.1);border:1px solid rgba(233,79,163,0.2);color:var(--a3);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-user-slash" style="margin-right:5px;"></i>No Login</span>
  </div>
</section>

<!-- STAT CARDS -->
<section style="max-width:860px;margin:0 auto 32px;padding:0 18px;">
  <div class="stats-grid">
    <div class="statc">
      <div style="font-size:1.6rem;margin-bottom:6px;">&#127908;</div>
      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.6rem;color:var(--a1);">{voice_count}+</div>
      <div style="font-size:.76rem;color:var(--muted);font-weight:500;margin-top:2px;">{lang_name} Voices</div>
    </div>
    <div class="statc">
      <div style="font-size:1.6rem;margin-bottom:6px;">&#127758;</div>
      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.6rem;color:var(--a2);">104</div>
      <div style="font-size:.76rem;color:var(--muted);font-weight:500;margin-top:2px;">Languages</div>
    </div>
    <div class="statc">
      <div style="font-size:1.6rem;margin-bottom:6px;">&#9889;</div>
      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.6rem;color:var(--ok);">5K</div>
      <div style="font-size:.76rem;color:var(--muted);font-weight:500;margin-top:2px;">Chars Free</div>
    </div>
  </div>
</section>

<!-- TTS STUDIO WIDGET -->
<section style="max-width:860px;margin:0 auto;padding:0 18px 56px;">
  <div class="glass" style="padding:30px;">
    <h2 style="font-size:1.15rem;font-weight:700;margin-bottom:18px;display:flex;align-items:center;gap:9px;">
      <i class="fa-solid fa-sliders" style="color:var(--a1);"></i>
      {lang_name} Voice Generator &mdash; Advanced Studio
    </h2>

    <!-- MODE TABS -->
    <div style="display:flex;gap:8px;margin-bottom:22px;background:var(--panel);border-radius:14px;padding:5px;border:1px solid var(--border);">
      <button class="tab-btn active" id="tab-single" onclick="switchTab('single')" style="flex:1;">
        <i class="fa-solid fa-microphone" style="margin-right:6px;"></i>Single Voice
      </button>
      <button class="tab-btn" id="tab-multi" onclick="switchTab('multi')" style="flex:1;">
        <i class="fa-solid fa-users" style="margin-right:6px;"></i>Multi-Voice Dialogue
      </button>
    </div>

    <!-- SINGLE VOICE PANEL -->
    <div id="panel-single">
      <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
        <button onclick="loadSample()" style="background:rgba(59,158,255,0.1);border:1px solid rgba(59,158,255,0.2);color:var(--a1);border-radius:9px;padding:7px 14px;font-size:.8rem;font-weight:600;cursor:pointer;font-family:'DM Sans',sans-serif;">
          <i class="fa-solid fa-magic-wand-sparkles" style="margin-right:5px;"></i>Load Sample {lang_name} Text
        </button>
        <span style="font-size:.78rem;color:var(--muted);">or type your own below</span>
      </div>

      <div style="margin-bottom:18px;">
        <span class="slbl"><i class="fa-solid fa-align-left" style="margin-right:5px;"></i>Your {lang_name} Text</span>
        <textarea id="txt" rows="5" placeholder="Type or paste {lang_name} text here... (up to 5000 characters)" oninput="onTxt(this)" onchange="onTxt(this)" onkeyup="onTxt(this)" onpaste="setTimeout(()=>onTxt(this), 50)"></textarea>
        <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:.76rem;color:var(--muted);">
          <span><span id="cc">0</span> / 5000 chars</span>
          <span>~<span id="te">0</span> sec audio</span>
        </div>
      </div>

      <div class="inputs-grid">
        <div>
          <span class="slbl"><i class="fa-solid fa-language" style="margin-right:5px;color:var(--a1);"></i>Language</span>
          <select id="sel-lang" onchange="redirectToLang(this.value)">
            {all_languages_options}
          </select>
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span class="slbl" style="margin:0;"><i class="fa-solid fa-robot" style="margin-right:5px;color:var(--a2);"></i>Voice Character</span>
            <button type="button" onclick="doPreviewVoice()" style="background:none;border:none;color:var(--a1);font-size:.76rem;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:4px;"><i class="fa-solid fa-circle-play"></i>Preview</button>
          </div>
          <select id="sel-voice">
            <optgroup label="General Voices">
              <option value="female-1">Female 1 - Natural</option>
              <option value="female-2">Female 2 - Soft</option>
              <option value="female-3">Female 3 - Pro</option>
              <option value="male-1">Male 1 - Deep</option>
              <option value="male-2">Male 2 - Friendly</option>
              <option value="male-3">Male 3 - Authority</option>
            </optgroup>
            <optgroup label="Kids (age 7-14)">
              <option value="kid-f1">Lily (Age 7) - Kid Female</option>
              <option value="kid-f2">Chloe (Age 10) - Kid Female</option>
              <option value="kid-m1">Mason (Age 8) - Kid Male</option>
              <option value="kid-m2">Logan (Age 12) - Kid Male</option>
            </optgroup>
            <optgroup label="Teens (age 15-20)">
              <option value="teen-f1">Sophia (Age 17) - Teen Female</option>
              <option value="teen-f2">Emma (Age 19) - Teen Female</option>
              <option value="teen-m1">Ethan (Age 16) - Teen Male</option>
              <option value="teen-m2">Noah (Age 18) - Teen Male</option>
            </optgroup>
            <optgroup label="Young Adults (20-40)">
              <option value="young-f1">Aria (Age 25) - Female Natural</option>
              <option value="young-f2">Jenny (Age 28) - Female Friendly</option>
              <option value="young-f3">Sara (Age 32) - Female Pro</option>
              <option value="young-m1">Guy (Age 26) - Male Natural</option>
              <option value="young-m2">Roger (Age 30) - Male Pro</option>
              <option value="young-m3">Ryan (Age 34) - Male Deep</option>
            </optgroup>
            <optgroup label="Middle-Aged (40-60)">
              <option value="mid-f1">Michelle (Age 45) - Female Exec</option>
              <option value="mid-f2">Helen (Age 52) - Female Warm</option>
              <option value="mid-m1">Steffan (Age 48) - Male Presenter</option>
              <option value="mid-m2">Brian (Age 55) - Male Narrator</option>
            </optgroup>
            <optgroup label="Seniors (60-90)">
              <option value="senior-f1">Abigail (Age 68) - Senior Female</option>
              <option value="senior-f2">Esther (Age 75) - Senior Female</option>
              <option value="senior-m1">Arthur (Age 70) - Senior Male</option>
              <option value="senior-m2">Thomas (Age 82) - Senior Male</option>
            </optgroup>
          </select>
        </div>
      </div>

      <div class="controls-grid">
        <div class="ctrl">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:9px;">
            <span style="font-size:.78rem;font-weight:600;color:var(--muted);"><i class="fa-solid fa-gauge-high" style="color:var(--ok);margin-right:4px;"></i>Speed</span>
            <span id="badge-rate" class="mono" style="font-size:.76rem;background:rgba(61,214,140,0.1);color:var(--ok);padding:2px 8px;border-radius:20px;">1.0x</span>
          </div>
          <input type="range" id="sl-rate" min="0.5" max="2.0" step="0.1" value="1.0" oninput="document.getElementById('badge-rate').textContent=parseFloat(this.value).toFixed(1)+'x'">
          <div style="display:flex;justify-content:space-between;font-size:.68rem;color:var(--muted);margin-top:3px;"><span>Slow</span><span>Fast</span></div>
        </div>
        <div class="ctrl">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:9px;">
            <span style="font-size:.78rem;font-weight:600;color:var(--muted);"><i class="fa-solid fa-music" style="color:var(--a2);margin-right:4px;"></i>Pitch</span>
            <span id="badge-pitch" class="mono" style="font-size:.76rem;background:rgba(124,95,230,0.1);color:var(--a2);padding:2px 8px;border-radius:20px;">+0</span>
          </div>
          <input type="range" id="sl-pitch" min="-10" max="10" step="1" value="0" oninput="document.getElementById('badge-pitch').textContent=(this.value>=0?'+':'')+this.value">
          <div style="display:flex;justify-content:space-between;font-size:.68rem;color:var(--muted);margin-top:3px;"><span>Low</span><span>High</span></div>
        </div>
        <div class="ctrl">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:9px;">
            <span style="font-size:.78rem;font-weight:600;color:var(--muted);"><i class="fa-solid fa-volume-high" style="color:var(--a1);margin-right:4px;"></i>Volume</span>
            <span id="badge-vol" class="mono" style="font-size:.76rem;background:rgba(59,158,255,0.1);color:var(--a1);padding:2px 8px;border-radius:20px;">100%</span>
          </div>
          <input type="range" id="sl-vol" min="0" max="100" step="5" value="100" oninput="document.getElementById('badge-vol').textContent=this.value+'%'">
          <div style="display:flex;justify-content:space-between;font-size:.68rem;color:var(--muted);margin-top:3px;"><span>Mute</span><span>Max</span></div>
        </div>
      </div>

      <div class="options-grid">
        <div>
          <span class="slbl"><i class="fa-solid fa-palette" style="color:#f472b6;margin-right:5px;"></i>Speaking Style</span>
          <select id="sel-style">
            <option value="general">General</option>
            <option value="cheerful">Cheerful</option>
            <option value="newscast-formal">Newscast Formal</option>
            <option value="narration-professional">Narration Professional</option>
            <option value="friendly">Friendly</option>
            <option value="poetry-reading">Poetry Reading</option>
            <option value="documentary-narration">Documentary</option>
            <option value="customerservice">Customer Service</option>
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

      <!-- Natural Mode Toggle -->
      <div style="display:flex;align-items:center;justify-content:space-between;background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:14px 18px;margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:10px;">
          <i class="fa-solid fa-wand-magic-sparkles" style="color:var(--a2);font-size:1.1rem;"></i>
          <div>
            <div style="font-size:.88rem;font-weight:700;color:var(--txt);font-family:'Syne',sans-serif;">Natural Voice Mode</div>
            <div style="font-size:.72rem;color:var(--muted);margin-top:2px;line-height:1.3;">Smart prosody &mdash; questions rise &uarr;, exclamations get energy &#9889;, natural pauses at commas &amp; full stops</div>
          </div>
        </div>
        <label style="position:relative;display:inline-block;width:48px;height:26px;flex-shrink:0;margin-left:12px;cursor:pointer;">
          <input type="checkbox" id="natural-mode-toggle" checked style="opacity:0;width:0;height:0;">
          <span style="position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;background:var(--border);transition:.3s;border-radius:26px;"></span>
          <span id="natural-toggle-knob" style="position:absolute;content:'';height:20px;width:20px;left:3px;bottom:3px;background:#fff;transition:.3s;border-radius:50%;box-shadow:0 1px 4px rgba(0,0,0,0.2);"></span>
        </label>
      </div>
      <style>
        #natural-mode-toggle:checked + span {{ background: linear-gradient(135deg, var(--a1), var(--a2)) !important; box-shadow: 0 0 12px rgba(59,158,255,0.4); }}
        #natural-mode-toggle:checked + span + span {{ transform: translateX(22px); }}
      </style>

      <button id="gen-btn" class="btn-primary" onclick="doGenerate()">
        <span id="gen-lbl"><i class="fa-solid fa-wand-magic-sparkles" style="margin-right:8px;"></i>Generate {lang_name} Voice &mdash; Free</span>
      </button>

      <div id="result-area" class="hidden" style="margin-top:20px;">
        <div style="background:rgba(255,255,255,0.015);border:1px solid var(--border);border-radius:16px;padding:18px 20px;margin-bottom:18px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <div style="display:flex;align-items:center;gap:10px;">
              <i class="fa-solid fa-square-check" style="color:var(--ok);font-size:1.25rem;"></i>
              <div>
                <div style="font-weight:700;color:var(--ok);font-size:.9rem;font-family:'Syne',sans-serif;">Audio Ready!</div>
                <div id="gen-info" style="font-size:.74rem;color:var(--muted);margin-top:1px;">Neural TTS &middot; {lang_name}</div>
              </div>
            </div>
            <div id="custom-player-badge" class="badge-pill" style="margin:0;font-size:.7rem;">Natural</div>
          </div>
          <div style="display:flex;align-items:center;gap:12px;background:var(--panel);border-radius:12px;padding:10px 14px;border:1px solid var(--border);">
            <button id="play-pause-btn" onclick="togglePlayPause()" style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--a1),var(--a2));border:none;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:.85rem;box-shadow:0 0 10px rgba(59,158,255,0.25);transition:transform .15s;" onmouseover="this.style.transform='scale(1.08)'" onmouseout="this.style.transform='none'">
              <i class="fa-solid fa-play" id="play-pause-icon"></i>
            </button>
            <span id="player-time-current" class="mono" style="font-size:.72rem;color:var(--txt2);min-width:32px;">0:00</span>
            <div id="player-timeline" onclick="seekAudio(event)" style="flex:1;height:32px;position:relative;cursor:pointer;display:flex;align-items:center;background:var(--bg);border-radius:6px;overflow:hidden;border:1px solid var(--border);">
              <div id="player-progress" style="width:0%;height:100%;background:linear-gradient(90deg,rgba(59,158,255,0.15),rgba(124,95,230,0.15));border-right:2px solid var(--a3);transition:width 0.15s linear;"></div>
            </div>
            <span id="player-time-duration" class="mono" style="font-size:.72rem;color:var(--txt2);min-width:32px;text-align:right;">0:00</span>
          </div>
        </div>
        <audio id="player" style="display:none;"></audio>
        <div style="display:flex;gap:8px;margin-bottom:12px;">
          <button onclick="doDownload('mp3')" class="dl-tab active"><i class="fa-solid fa-download" style="margin-right:5px;"></i>Download MP3</button>
          <button onclick="doDownload('wav')" class="dl-tab"><i class="fa-solid fa-download" style="margin-right:5px;"></i>Download WAV</button>
          <button onclick="copyAudioLink()" class="dl-tab"><i class="fa-solid fa-link" style="margin-right:5px;"></i>Copy Link</button>
        </div>
        <button onclick="doGenerate()" style="width:100%;background:rgba(59,158,255,0.08);border:1px solid rgba(59,158,255,0.2);color:var(--a1);border-radius:12px;padding:11px;font-weight:600;cursor:pointer;font-family:'Syne',sans-serif;font-size:.88rem;">
          <i class="fa-solid fa-rotate-right" style="margin-right:6px;"></i>Regenerate
        </button>
      </div>
    </div>

    <!-- MULTI VOICE PANEL -->
    <div id="panel-multi" class="hidden">
      <div style="background:rgba(59,158,255,0.05);border:1px solid rgba(59,158,255,0.15);border-radius:14px;padding:16px;margin-bottom:18px;font-size:.85rem;color:var(--txt2);">
        <i class="fa-solid fa-circle-info" style="color:var(--a1);margin-right:6px;"></i>
        <strong>Multi-Voice Dialogue:</strong> Create scripts with different {lang_name} voice characters talking in turn. Paste your full script to auto-generate lines.
      </div>

      <!-- Script Import Collapsible Panel -->
      <div id="script-import-area" class="hidden" style="background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:18px;">
        <span class="slbl" style="margin-bottom:6px;display:block;"><i class="fa-solid fa-quote-left" style="margin-right:5px;color:var(--a1);"></i>Paste {lang_name} Script below</span>
        <textarea id="import-script-text" rows="6" style="width:100%;font-family:'DM Sans',sans-serif;font-size:.85rem;padding:10px 14px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--txt);outline:none;resize:vertical;line-height:1.4;" placeholder="Example:&#13;Speaker 1: Hello! Welcome to {lang_name} dialogue generator.&#13;Speaker 2: Thank you! This voice quality is amazing.&#13;Speaker 1: Generate unlimited audio for free!"></textarea>
        <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:12px;">
          <button onclick="toggleImportArea(false)" style="background:transparent;border:none;color:var(--muted);font-weight:600;cursor:pointer;font-size:.8rem;font-family:'Syne',sans-serif;">Cancel</button>
          <button onclick="parseAndImportScript()" style="background:linear-gradient(135deg,var(--a1),var(--a2));border:none;color:#fff;border-radius:8px;padding:8px 16px;font-weight:700;cursor:pointer;font-size:.8rem;font-family:'Syne',sans-serif;">Parse & Load Dialogue</button>
        </div>
      </div>

      <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px;">
        <button onclick="toggleImportArea(true)" style="flex:1;min-width:140px;background:rgba(59,158,255,0.08);border:1px solid rgba(59,158,255,0.2);color:var(--a1);border-radius:12px;padding:12px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;font-size:.82rem;transition:all .2s;white-space:nowrap;"><i class="fa-solid fa-file-import" style="margin-right:6px;"></i>Import Full Script</button>
        <button onclick="addDialogueLine()" style="flex:1;min-width:140px;background:var(--panel);border:1px solid var(--border);color:var(--txt);border-radius:12px;padding:12px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;font-size:.82rem;transition:all .2s;white-space:nowrap;"><i class="fa-solid fa-plus" style="margin-right:6px;"></i>Add Line Manually</button>
      </div>

      <div id="dialogue-lines" style="display:flex;flex-direction:column;gap:14px;margin-bottom:18px;"></div>

      <button id="multi-gen-btn" class="btn-primary" onclick="doMultiGenerate()">
        <span id="multi-gen-lbl"><i class="fa-solid fa-users" style="margin-right:8px;"></i>Generate Multi-Voice Dialogue</span>
      </button>

      <div id="multi-result" class="hidden" style="margin-top:20px;border-top:1px solid var(--border);padding-top:20px;">
        <div style="background:var(--panel);border:1px solid var(--border);border-radius:16px;padding:18px 20px;margin-bottom:18px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <div style="display:flex;align-items:center;gap:10px;">
              <i class="fa-solid fa-square-check" style="color:var(--ok);font-size:1.25rem;"></i>
              <div>
                <div style="font-weight:700;color:var(--ok);font-size:.9rem;font-family:'Syne',sans-serif;">Audio Ready!</div>
                <div id="multi-gen-info" style="font-size:.74rem;color:var(--muted);margin-top:1px;">Neural TTS &middot; {lang_name} Dialogue</div>
              </div>
            </div>
            <div class="badge-pill" style="margin:0;font-size:.7rem;background:rgba(59,158,255,0.1);color:var(--a1);border:1px solid rgba(59,158,255,0.15);">👥 Dialogue</div>
          </div>
          <audio id="multi-player" controls autoplay style="width:100%;margin-bottom:14px;"></audio>
          <div style="display:flex;gap:10px;">
            <button onclick="doDownload('wav')" style="flex:1;background:rgba(61,214,140,0.12);border:1px solid rgba(61,214,140,0.28);color:var(--ok);border-radius:12px;padding:12px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;font-size:.88rem;"><i class="fa-solid fa-download" style="margin-right:6px;"></i>Download Dialogue WAV</button>
            <button onclick="doDownload('mp3')" style="flex:1;background:rgba(59,158,255,0.12);border:1px solid rgba(59,158,255,0.28);color:var(--a1);border-radius:12px;padding:12px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;font-size:.88rem;"><i class="fa-solid fa-download" style="margin-right:6px;"></i>Download Dialogue MP3</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

{voices_table_html}

<!-- SEO CONTENT WRAP -->
<div style="background:rgba(255,255,255,0.015);border-top:1px solid var(--border);">
  <div style="max-width:1100px;margin:0 auto;padding:56px 24px;">

    <div class="section-divider"><span class="section-label">&#10022; {lang_name} TTS Use Cases</span></div>
    <div style="text-align:center;margin-bottom:40px;">
      <h2 style="font-size:clamp(1.5rem,3vw,2.2rem);font-weight:800;margin-bottom:10px;">Who Uses <span class="tg">{lang_name} Text to Speech</span>?</h2>
      <p style="color:var(--muted);font-size:.92rem;">Popular applications for {lang_name} voice generation in {country}</p>
    </div>
    <div style="text-align:center;margin-bottom:56px;">{use_case_tags}</div>

    <div class="section-divider"><span class="section-label">&#10022; Why VoicePro</span></div>
    <div style="text-align:center;margin-bottom:30px;">
      <h2 style="font-size:clamp(1.5rem,3vw,2.2rem);font-weight:800;">Why VoicePro for <span class="tg">{lang_name}</span>?</h2>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px;margin-bottom:56px;">
      <div class="feature-card"><div class="feature-icon" style="background:rgba(59,158,255,0.12);">&#129504;</div><h3 style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">{lang_name}-Native Neural Voices</h3><p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Voices trained specifically on {lang_name} ({country}) native speaker data &mdash; correct pronunciation, natural intonation, authentic regional accent.</p></div>
      <div class="feature-card"><div class="feature-icon" style="background:rgba(61,214,140,0.12);">&#128229;</div><h3 style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">Instant MP3 / WAV Download</h3><p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">No queues, no waiting. Generate up to 5,000 characters in seconds. Download MP3 for web or WAV for studio-quality production.</p></div>
      <div class="feature-card"><div class="feature-icon" style="background:rgba(124,95,230,0.12);">&#127931;</div><h3 style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">Full Voice Customization</h3><p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Adjust speed (0.5x&ndash;2x), pitch (&minus;10 to +10), volume, and speaking style. {voice_count}+ unique voice characters across all ages.</p></div>
      <div class="feature-card"><div class="feature-icon" style="background:rgba(233,79,163,0.12);">&#128101;</div><h3 style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">Multi-Voice Dialogue</h3><p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Create {lang_name} conversations with 2 distinct voices. Perfect for podcasts, YouTube, education, and audiobooks.</p></div>
      <div class="feature-card"><div class="feature-icon" style="background:rgba(251,191,36,0.12);">&#128274;</div><h3 style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">No Login, 100% Private</h3><p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">No account required. Your {lang_name} text is processed on-demand, never stored, never shared. Complete privacy guaranteed.</p></div>
      <div class="feature-card"><div class="feature-icon" style="background:rgba(59,158,255,0.12);">&#128241;</div><h3 style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">Works on Any Device</h3><p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Fully responsive on mobile, tablet, and desktop. No app download &mdash; works in any browser on iOS, Android, and PC.</p></div>
    </div>

    <div class="section-divider"><span class="section-label">&#10022; {lang_name} FAQ</span></div>
    <div style="text-align:center;margin-bottom:28px;">
      <h2 style="font-size:clamp(1.5rem,3vw,2.2rem);font-weight:800;">Frequently Asked <span class="tg">Questions</span></h2>
      <p style="color:var(--muted);font-size:.92rem;margin-top:8px;">About {lang_name} Text to Speech</p>
    </div>
    <div style="max-width:780px;margin:0 auto 56px;">{faq_html}</div>

    <div class="section-divider"><span class="section-label">&#10022; More Languages</span></div>
    <div style="text-align:center;margin-bottom:10px;">
      <h2 style="font-size:1.4rem;font-weight:800;">Explore Other <span class="tg">Languages</span></h2>
    </div>
    <div style="text-align:center;max-width:960px;margin:0 auto;">{related_links}</div>
  </div>
</div>

<!-- FOOTER -->
<footer class="pro-footer">
  <div class="footer-grid">
    <div>
      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.2rem;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
        <div style="width:32px;height:32px;background:linear-gradient(135deg,var(--a1),var(--a2));border-radius:9px;display:flex;align-items:center;justify-content:center;"><i class="fa-solid fa-microphone-lines" style="color:#fff;font-size:.8rem;"></i></div>
        Voice<span style="color:var(--a1);">Pro</span>
      </div>
      <p style="color:var(--muted);font-size:.875rem;line-height:1.75;">Free {lang_name} Text-to-Speech online. 104 languages, 100+ neural voices, instant MP3 download. No login &mdash; ever.</p>
    </div>
    <div>
      <p class="footer-heading">Product</p>
      <a href="/" class="footer-link">Home Studio</a>
      <a href="/tts/" class="footer-link">All Languages</a>
      <a href="/blog.html" class="footer-link">Blog</a>
    </div>
    <div>
      <p class="footer-heading">Company</p>
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
    <p style="color:var(--muted);font-size:.8rem;">&copy; 2026 VoicePro TTS Studio &middot; Free {lang_name} Text to Speech &middot; {country}</p>
    <p style="color:var(--muted);font-size:.78rem;"><span style="color:var(--a1);font-weight:600;">texttoaudiomp3.site</span></p>
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
  const LANG_SLUG_MAP = {lang_slug_map_json};
  let lastAudio = null, lastFile = null;

  let deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', e => {{
    e.preventDefault(); deferredPrompt = e;
    ['pwa-install-btn','pwa-install-btn-mob'].forEach(id => {{
      const b = document.getElementById(id); if(b) b.style.display='flex';
    }});
  }});
  function triggerPWAInstall() {{
    if (deferredPrompt) {{ deferredPrompt.prompt(); deferredPrompt.userChoice.then(()=>{{deferredPrompt=null;}}); }}
  }}

  function redirectToLang(code) {{
    if (code === LANG_CODE) return;
    const s = LANG_SLUG_MAP[code];
    if (s) window.location.href = '/tts/' + s;
  }}

  let dialogueLineCount = 0;
  function switchTab(tab) {{
    const single = document.getElementById('panel-single');
    const multi  = document.getElementById('panel-multi');
    const btnS   = document.getElementById('tab-single');
    const btnM   = document.getElementById('tab-multi');
    if (tab === 'single') {{
      single.classList.remove('hidden'); multi.classList.add('hidden');
      btnS.classList.add('active');      btnM.classList.remove('active');
    }} else {{
      single.classList.add('hidden'); multi.classList.remove('hidden');
      btnS.classList.remove('active'); btnM.classList.add('active');
      if (document.getElementById('dialogue-lines').children.length === 0) {{
        const firstVoice = document.querySelector('#sel-voice option') ? document.querySelector('#sel-voice option').value : 'female-1';
        const secondVoice = document.querySelectorAll('#sel-voice option')[1] ? document.querySelectorAll('#sel-voice option')[1].value : 'male-1';
        addDialogueLine('Hello! Welcome to our multi-voice dialogue generator for ' + LANG_NAME + '.', firstVoice);
        addDialogueLine('Thanks! Now we can generate realistic conversations in seconds.', secondVoice);
      }}
    }}
  }}

  function addDialogueLine(initialText = '', initialVoice = '', speakerName = '') {{
    const id = 'dl-' + (++dialogueLineCount);
    const container = document.getElementById('dialogue-lines');
    if (!container) return;
    const selVoiceEl = document.getElementById('sel-voice');
    let optionsHtml = selVoiceEl ? selVoiceEl.innerHTML : '';
    if (initialVoice) {{
      optionsHtml = optionsHtml.replace(new RegExp('value="' + initialVoice + '"'), 'value="' + initialVoice + '" selected');
    }}
    const row = document.createElement('div');
    row.id = id;
    row.style.cssText = "background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:16px;position:relative;display:flex;flex-direction:column;gap:12px;";
    row.innerHTML = `
      <button onclick="removeDialogueLine('${{id}}')" style="position:absolute;right:12px;top:12px;width:28px;height:28px;border-radius:6px;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.15);color:#ef4444;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;" title="Remove line"><i class="fa-solid fa-xmark" style="font-size:.85rem;"></i></button>
      <div style="padding-right:24px;">
        <span class="slbl" style="margin-bottom:6px;font-size:.74rem;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px;line-height:1.3;">
          <span><i class="fa-solid fa-robot" style="margin-right:5px;color:var(--a2);"></i>Character Voice ${{speakerName ? `(${{speakerName}})` : ''}}</span>
          ${{speakerName ? `<span style="font-size:.68rem;background:rgba(59,158,255,0.08);color:var(--a1);padding:1px 6px;border-radius:4px;font-weight:700;white-space:nowrap;">Script Name: ${{speakerName}}</span>` : ''}}
        </span>
        <select class="dl-voice-select" style="width:100%;max-width:100%;font-size:.82rem;padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--txt);outline:none;box-sizing:border-box;">
          ${{optionsHtml}}
        </select>
      </div>
      <div>
        <span class="slbl" style="margin-bottom:6px;font-size:.74rem;"><i class="fa-solid fa-quote-left" style="margin-right:5px;color:var(--muted);"></i>Dialogue Speech</span>
        <textarea class="dl-text-area" rows="2" style="width:100%;max-width:100%;font-family:'DM Sans',sans-serif;font-size:.85rem;padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--txt);outline:none;resize:vertical;box-sizing:border-box;" placeholder="Type what this character says…">${{initialText}}</textarea>
      </div>
    `;
    container.appendChild(row);
  }}

  function removeDialogueLine(id) {{
    const el = document.getElementById(id);
    if (el) el.remove();
  }}

  function toggleImportArea(show) {{
    const area = document.getElementById('script-import-area');
    if (area) {{
      if (show) area.classList.remove('hidden');
      else area.classList.add('hidden');
    }}
  }}

  function parseAndImportScript() {{
    const txt = document.getElementById('import-script-text').value.trim();
    if (!txt) {{ showToast('Please paste a script first!', 'err'); return; }}
    const rawLines = txt.split('\n');
    const parsedLines = [];
    const lineRegex = /^(?:\d+[\.\)\-\s]*)?\s*([^:\-\n]+?)\s*[:\-]\s*(.*)$/;
    for (let rawLine of rawLines) {{
      rawLine = rawLine.trim();
      if (!rawLine) continue;
      const match = rawLine.match(lineRegex);
      if (match) {{
        parsedLines.push({{ speaker: match[1].trim(), text: match[2].trim() }});
      }} else {{
        parsedLines.push({{ speaker: '', text: rawLine }});
      }}
    }}
    if (parsedLines.length === 0) {{
      showToast('Could not parse script lines.', 'err');
      return;
    }}
    const selVoiceEl = document.getElementById('sel-voice');
    const allVoiceValues = Array.from(selVoiceEl.querySelectorAll('option')).map(o => o.value);
    const speakerVoiceMap = {{}};
    let voiceIndex = 0;
    document.getElementById('dialogue-lines').innerHTML = '';
    let lastSpeakerVoice = allVoiceValues[0] || 'female-1';
    for (const line of parsedLines) {{
      if (line.speaker) {{
        const normSpeaker = line.speaker.toLowerCase();
        if (!speakerVoiceMap[normSpeaker]) {{
          speakerVoiceMap[normSpeaker] = allVoiceValues[voiceIndex % allVoiceValues.length] || 'female-1';
          voiceIndex++;
        }}
        lastSpeakerVoice = speakerVoiceMap[normSpeaker];
        addDialogueLine(line.text, lastSpeakerVoice, line.speaker);
      }} else {{
        addDialogueLine(line.text, lastSpeakerVoice, 'Narrator');
      }}
    }}
    toggleImportArea(false);
    showToast(`Imported ${{parsedLines.length}} script lines! 🎉`);
  }}

  function bufferToWav(buffer) {{
    let numOfChan = buffer.numberOfChannels,
        length = buffer.length * numOfChan * 2 + 44,
        bufferArr = new ArrayBuffer(length),
        view = new DataView(bufferArr),
        channels = [], i, sample,
        offset = 0,
        pos = 0;

    function setUint16(data) {{ view.setUint16(pos, data, true); pos += 2; }}
    function setUint32(data) {{ view.setUint32(pos, data, true); pos += 4; }}

    setUint32(0x46464952); // "RIFF"
    setUint32(length - 8);
    setUint32(0x45564157); // "WAVE"
    setUint32(0x20746d66); // "fmt "
    setUint32(16);
    setUint16(1); // PCM
    setUint16(numOfChan);
    setUint32(buffer.sampleRate);
    setUint32(buffer.sampleRate * 2 * numOfChan);
    setUint16(numOfChan * 2);
    setUint16(16);
    setUint32(0x61746164); // "data"
    setUint32(length - pos - 4);

    for (i = 0; i < buffer.numberOfChannels; i++) channels.push(buffer.getChannelData(i));

    while (pos < length) {{
      for (i = 0; i < numOfChan; i++) {{
        sample = Math.max(-1, Math.min(1, channels[i][offset]));
        sample = (sample < 0 ? sample * 0x8000 : sample * 0x7FFF);
        view.setInt16(pos, sample, true);
        pos += 2;
      }}
      offset++;
    }}
    return new Blob([bufferArr], {{ type: "audio/wav" }});
  }}

  function loadSample() {{
    const t = document.getElementById('txt');
    t.value = SAMPLE_TEXT; onTxt(t);
    showToast('Sample ' + LANG_NAME + ' text loaded!');
  }}

  function onTxt(el) {{
    let c = el.value.length;
    if (c > 5000) {{ el.value = el.value.substring(0, 5000); c = 5000; }}
    document.getElementById('cc').textContent = c;
    document.getElementById('te').textContent = Math.ceil(c / 15);
    el.style.height = 'auto'; el.style.height = el.scrollHeight + 'px';
  }}

  function showToast(msg, type='ok') {{
    const e=document.getElementById('toast'), ic=document.getElementById('toast-icon'), tx=document.getElementById('toast-msg');
    ic.className = type==='ok' ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-exclamation';
    ic.style.color = type==='ok' ? 'var(--ok)' : '#f87171';
    tx.textContent = msg; e.classList.add('on');
    setTimeout(()=>e.classList.remove('on'), 3500);
  }}

  async function doPreviewVoice() {{
    const vtype = document.getElementById('sel-voice').value;
    const rate = parseFloat(document.getElementById('sl-rate').value).toFixed(2);
    const pitch = document.getElementById('sl-pitch').value;
    const style = document.getElementById('sel-style').value;
    showToast('Loading ' + LANG_NAME + ' preview...');
    try {{
      const r = await fetch('/preview-voice', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ language: LANG_CODE, voice_type: vtype, rate: parseFloat(rate), pitch: parseInt(pitch), style: style }})
      }});
      const d = await r.json();
      if (d.success) {{
        const audio = new Audio(d.audio_data);
        audio.play();
        showToast('▶ Playing preview');
      }} else {{
        showToast(d.error || 'Preview unavailable', 'err');
      }}
    }} catch(e) {{
      showToast('Network error — preview failed', 'err');
    }}
  }}

  async function doGenerate() {{
    const text = document.getElementById('txt').value.trim();
    if (!text) {{ showToast('Please enter ' + LANG_NAME + ' text first!', 'err'); return; }}
    const btn = document.getElementById('gen-btn'), lbl = document.getElementById('gen-lbl');
    btn.disabled = true;
    lbl.innerHTML = '<span class="spinner"></span><span style="margin-left:9px;">Generating ' + LANG_NAME + ' audio...</span>';
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
    fd.append('natural_mode', 'true');
    try {{
      const r = await fetch('/generate', {{method:'POST', body:fd}});
      const d = await r.json();
      if (d.success) {{
        lastAudio = d.audio_data; lastFile = d.filename;
        const playerEl = document.getElementById('player');
        playerEl.src = d.audio_data;
        playerEl.play().catch(e => console.log('Autoplay blocked:', e));
        const selVal = document.getElementById('sel-voice').value;
        const selOpt = document.querySelector('#sel-voice option[value="' + selVal + '"]');
        const voiceName = selOpt ? selOpt.textContent.replace(/^[^-]+-\s*/, '').trim() : selVal;
        const genInfo = document.getElementById('gen-info');
        if (genInfo) genInfo.textContent = (d.method || 'Neural TTS') + ' \xb7 ' + voiceName + ' \xb7 ' + LANG_NAME;
        let badge = 'Natural';
        if (selVal.includes('kid')) badge = 'Kid';
        else if (selVal.includes('teen')) badge = 'Teen';
        else if (selVal.includes('young')) badge = 'Young Adult';
        else if (selVal.includes('mid')) badge = 'Mid-Age';
        else if (selVal.includes('senior')) badge = 'Senior';
        else if (selVal.includes('female')) badge = 'Female';
        else if (selVal.includes('male')) badge = 'Male';
        const badgeEl = document.getElementById('custom-player-badge');
        if (badgeEl) badgeEl.textContent = badge;
        document.getElementById('result-area').classList.remove('hidden');
        showToast(LANG_NAME + ' audio ready! 🎉');
      }} else {{ showToast(d.error || 'Generation failed', 'err'); }}
    }} catch(e) {{ showToast('Network error — please retry', 'err'); }}
    finally {{
      btn.disabled = false;
      lbl.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles" style="margin-right:8px;"></i>Generate ' + LANG_NAME + ' Voice \u2014 Free';
    }}
  }}

  async function doMultiGenerate() {{
    const lines = document.querySelectorAll('#dialogue-lines > div');
    if (lines.length === 0) {{ showToast('Please add at least one dialogue line!', 'err'); return; }}
    const script = [];
    for (const line of lines) {{
      const select = line.querySelector('.dl-voice-select');
      const textarea = line.querySelector('.dl-text-area');
      const val = textarea.value.trim();
      if (!val) {{ showToast('Please fill all dialogue boxes!', 'err'); textarea.focus(); return; }}
      script.push({{ voice: select.value, text: val }});
    }}
    const btn = document.getElementById('multi-gen-btn'), lbl = document.getElementById('multi-gen-lbl'), res = document.getElementById('multi-result');
    btn.disabled = true; res.classList.add('hidden');
    try {{
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const decodedBuffers = [];
      for (let i = 0; i < script.length; i++) {{
        lbl.innerHTML = `<span class="spinner"></span><span style="margin-left:9px;">Generating Line ${{i+1}}/${{script.length}}…</span>`;
        const line = script[i];
        const fd = new FormData();
        fd.append('text', line.text);
        fd.append('language', LANG_CODE);
        fd.append('voice_type', line.voice);
        fd.append('rate', '1.00');
        fd.append('pitch', '0');
        fd.append('volume', '100');
        fd.append('style', 'general');
        fd.append('format', 'mp3');
        fd.append('response_type', 'base64');
        fd.append('natural_mode', 'true');

        const r = await fetch('/generate', {{ method: 'POST', body: fd }});
        const d = await r.json();
        if (!d.success) throw new Error(d.error || `Error at line ${{i+1}}`);

        const base64Data = d.audio_data.split(',')[1];
        const binaryStr = window.atob(base64Data);
        const bytes = new Uint8Array(binaryStr.length);
        for (let j = 0; j < binaryStr.length; j++) bytes[j] = binaryStr.charCodeAt(j);

        const decodedBuffer = await new Promise((resolve, reject) => {{
          audioCtx.decodeAudioData(bytes.buffer, resolve, reject);
        }});
        decodedBuffers.push(decodedBuffer);
      }}

      lbl.innerHTML = `<span class="spinner"></span><span style="margin-left:9px;">Merging dialogue lines…</span>`;
      const totalLength = decodedBuffers.reduce((sum, b) => sum + b.length, 0);
      const sampleRate = decodedBuffers[0].sampleRate;
      const combinedBuffer = audioCtx.createBuffer(1, totalLength, sampleRate);
      let offset = 0;
      for (const b of decodedBuffers) {{
        combinedBuffer.copyToChannel(b.getChannelData(0), 0, offset);
        offset += b.length;
      }}

      const wavBlob = bufferToWav(combinedBuffer);
      const wavUrl = URL.createObjectURL(wavBlob);
      lastAudio = wavUrl;
      lastFile = `dialogue_${{LANG_CODE}}_${{Date.now()}}.wav`;
      const playerEl = document.getElementById('multi-player');
      playerEl.src = wavUrl;
      playerEl.play().catch(e => console.log('Autoplay blocked:', e));

      const infoEl = document.getElementById('multi-gen-info');
      if (infoEl) infoEl.textContent = `Dialogue · ${{script.length}} Parts · ${{LANG_NAME}}`;
      res.classList.remove('hidden');
      showToast('Multi-Voice Dialogue generated! 🎉');
    }} catch (e) {{
      showToast(e.message || 'Dialogue generation failed. Try again.', 'err');
      console.error(e);
    }} finally {{
      btn.disabled = false;
      lbl.innerHTML = '<i class="fa-solid fa-users" style="margin-right:8px;"></i>Generate Multi-Voice Dialogue';
    }}
  }}

  function doDownload(type) {{
    if (!lastAudio) {{ showToast('Generate audio first!', 'err'); return; }}
    const ext = type === 'wav' ? 'wav' : 'mp3';
    const fn  = (lastFile || 'voicepro_' + LANG_CODE + '_' + Date.now()).replace(/\.[^.]+$/, '') + '.' + ext;
    const a   = document.createElement('a');
    a.href = lastAudio; a.download = fn;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    showToast('Downloading ' + ext.toUpperCase() + '...');
  }}

  function copyAudioLink() {{
    navigator.clipboard.writeText(window.location.href)
      .then(() => showToast('Page link copied!'))
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
    const target  = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', target);
    localStorage.setItem('theme', target);
    updateThemeIcons();
  }}

  function updateThemeIcons() {{
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    const iconClass = theme === 'light' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
    ['theme-btn', 'theme-btn-mob'].forEach(id => {{
      const b = document.getElementById(id);
      if (b) b.querySelector('i') && (b.querySelector('i').className = iconClass);
    }});
  }}

  function togglePlayPause() {{
    const audio = document.getElementById('player'); if (!audio) return;
    if (audio.paused) audio.play(); else audio.pause();
  }}

  function toggleMultiPlayPause() {{
    const audio = document.getElementById('multi-player'); if (!audio) return;
    if (audio.paused) audio.play(); else audio.pause();
  }}

  function seekAudio(e) {{
    const audio = document.getElementById('player'); if (!audio || !audio.duration) return;
    const rect  = document.getElementById('player-timeline').getBoundingClientRect();
    audio.currentTime = ((e.clientX - rect.left) / rect.width) * audio.duration;
  }}

  function seekMultiAudio(e) {{
    const audio = document.getElementById('multi-player'); if (!audio || !audio.duration) return;
    const rect  = document.getElementById('multi-player-timeline').getBoundingClientRect();
    audio.currentTime = ((e.clientX - rect.left) / rect.width) * audio.duration;
  }}

  function formatTime(secs) {{
    const m = Math.floor(secs / 60), s = Math.floor(secs % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }}

  function initCustomPlayer() {{
    [['player','play-pause-icon','player-progress','player-time-current','player-time-duration'],
     ['multi-player','multi-play-pause-icon','multi-player-progress','multi-player-time-current','multi-player-time-duration']].forEach(([pid, icid, prgid, curid, durid]) => {{
      const audio = document.getElementById(pid); if (!audio) return;
      audio.addEventListener('play',  () => {{ const ic = document.getElementById(icid); if(ic) ic.className='fa-solid fa-pause'; }});
      audio.addEventListener('pause', () => {{ const ic = document.getElementById(icid); if(ic) ic.className='fa-solid fa-play'; }});
      audio.addEventListener('timeupdate', () => {{
        const cur = audio.currentTime, dur = audio.duration || 0, pct = dur > 0 ? (cur/dur)*100 : 0;
        const prog = document.getElementById(prgid);   if(prog) prog.style.width = pct + '%';
        const curT = document.getElementById(curid); if(curT) curT.textContent = formatTime(cur);
        const durT = document.getElementById(durid); if(durT && dur) durT.textContent = formatTime(dur);
      }});
      audio.addEventListener('ended', () => {{
        const ic   = document.getElementById(icid);     if(ic) ic.className='fa-solid fa-play';
        const prog = document.getElementById(prgid);     if(prog) prog.style.width='0%';
        const curT = document.getElementById(curid); if(curT) curT.textContent='0:00';
      }});
    }});
  }}

  function toggleMobileMenu() {{
    const menu = document.getElementById('mobile-menu');
    if(menu) menu.classList.toggle('active');
  }}

  document.addEventListener('DOMContentLoaded', () => {{
    updateThemeIcons();
    initCustomPlayer();
    const txtEl = document.getElementById('txt');
    if (txtEl && txtEl.value) onTxt(txtEl);
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
        f'<a href="/tts/{slug(e[0])}" class="lang-badge">{e[1]} ({e[2]})</a>'
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

    # Build all-languages dropdown options (for language switcher)
    all_languages_options = "\n".join(
        f'<option value="{e[0]}"{" selected" if e[0] == code else ""}>{e[1]} ({e[2]})</option>'
        for e in LANGUAGES
    )

    # Build lang->slug map for JS redirect
    lang_slug_map = {e[0]: slug(e[0]) for e in LANGUAGES}
    lang_slug_map_json = json.dumps(lang_slug_map, ensure_ascii=False)

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
        all_languages_options=all_languages_options,
        lang_slug_map_json=lang_slug_map_json,
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

    # Generate comprehensive sitemap.xml with priorities and lastmod
    sitemap_path = os.path.join("templates", "sitemap.xml")
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        
        # Core pages
        core_pages = [
            ("/", "1.0", "daily"),
            ("/about.html", "0.8", "monthly"),
            ("/blog.html", "0.9", "weekly"),
            ("/tts/", "0.9", "weekly"),
            ("/contact.html", "0.6", "monthly"),
            ("/privacy.html", "0.5", "yearly"),
            ("/terms.html", "0.5", "yearly"),
        ]
        for url_path, priority, freq in core_pages:
            f.write(f"  <url>\n    <loc>https://www.texttoaudiomp3.site{url_path}</loc>\n    <lastmod>{today_str}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n  </url>\n")
            
        # Blog guides
        blog_guides = [
            "/blog/what-is-ai-text-to-speech",
            "/blog/convert-text-to-mp3-free",
            "/blog/hindi-text-to-speech-guide",
            "/blog/ai-voiceover-youtube",
            "/blog/voice-customization-guide",
            "/blog/free-vs-paid-tts-tools",
            "/blog/tts-for-accessibility",
            "/blog/elearning-audio-workflow",
            "/blog/marathi-text-to-speech-guide",
            "/blog/tts-for-podcasters",
            "/blog/100-languages-and-voices-guide",
        ]
        for guide_slug in blog_guides:
            f.write(f"  <url>\n    <loc>https://www.texttoaudiomp3.site{guide_slug}</loc>\n    <lastmod>{today_str}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n")
            
        # pSEO pages
        for m in manifest:
            f.write(f"  <url>\n    <loc>https://www.texttoaudiomp3.site{m['url']}</loc>\n    <lastmod>{today_str}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n")
            
        f.write('</urlset>\n')
    print(f"Generated comprehensive sitemap -> {sitemap_path}")

    # Write robots.txt
    robots_path = os.path.join("templates", "robots.txt")
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write("User-agent: *\n")
        f.write("Allow: /\n")
        f.write("Sitemap: https://www.texttoaudiomp3.site/sitemap.xml\n")
    print(f"Generated robots.txt -> {robots_path}")

    # Optional Google site verification placeholder (replace with actual token if needed)
    verification_path = os.path.join("templates", "google1234567890abcdef.html")
    with open(verification_path, "w", encoding="utf-8") as f:
        f.write("<meta name=\"google-site-verification\" content=\"YOUR_VERIFICATION_CODE\" />")
    print(f"Generated Google site verification file -> {verification_path}")

    print(f"\nGenerated {len(manifest)} pSEO pages -> templates/tts/")
    print(f"Manifest -> templates/tts_manifest.json")
    return manifest


if __name__ == "__main__":
    main()
