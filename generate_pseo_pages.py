"""
VoicePro TTS – Programmatic SEO Page Generator
Generates one landing page per language+country combination.
Run:  python generate_pseo_pages.py
Output: templates/tts/<slug>.html  (one file per language)
"""

import os, json, re, datetime
from app import VOICE_MAPPING

# ──────────────────────────────────────────────────────────────
#  UNIQUE LANGUAGE FACTS FOR SEO (per-language encyclopedia data)
# ──────────────────────────────────────────────────────────────
LANGUAGE_FACTS = {
    "hi-IN": {"script":"Devanagari","script_type":"Abugida","speakers":"615 million","family":"Indo-Aryan","origin":"Hindi evolved from Sauraseni Prakrit through Shauraseni Apabhraṃśa in the 7th century CE, with modern Standard Hindi crystallizing during the Delhi Sultanate era.","cultural":"Hindi is the lingua franca of Bollywood, the world's largest film industry by number of films produced annually, creating massive demand for Hindi voiceover content.","direction":"ltr","official":"India (alongside English)","digital":"Bollywood dubbing, government e-governance portals, WhatsApp audio messages, and Hindi YouTube channels which collectively receive over 200 billion views annually"},
    "mr-IN": {"script":"Devanagari","script_type":"Abugida","speakers":"83 million","family":"Indo-Aryan","origin":"Marathi traces its literary origins to the 13th-century saint-poet Dnyaneshwar, whose Dnyaneshwari commentary on the Bhagavad Gita established Marathi as a language of scholarly discourse.","cultural":"Marathi has the third-oldest literary tradition among Indian languages, with Lavani and Powada being unique poetic performance traditions that demand expressive vocal delivery.","direction":"ltr","official":"Maharashtra, India","digital":"Marathi news podcasts, Lavani audiobooks, Maharashtra state educational content, and Marathi devotional audio streaming platforms"},
    "gu-IN": {"script":"Gujarati","script_type":"Abugida","speakers":"57 million","family":"Indo-Aryan","origin":"The Gujarati script evolved from the Nāgarī script around the 16th century, dropping the characteristic headline (shirorekha) that distinguishes Devanagari.","cultural":"Gujarati is the native language of Mahatma Gandhi, and the Gujarati business diaspora spanning East Africa, the UK, and North America creates global demand for Gujarati audio content.","direction":"ltr","official":"Gujarat, Dadra and Nagar Haveli, India","digital":"Gujarati garba and folk music narration, diamond trade communications in Surat, NRI community podcasts, and Gujarati audiobook platforms"},
    "ta-IN": {"script":"Tamil","script_type":"Abugida","speakers":"78 million","family":"Dravidian","origin":"Tamil is one of the longest-surviving classical languages in the world, with Sangam literature dating back to 300 BCE, making it over 2,300 years old.","cultural":"Tamil has been declared a classical language of India, and its Sangam poetry tradition is considered one of the greatest literary achievements of the ancient world, rivaling Greek and Latin literature.","direction":"ltr","official":"Tamil Nadu, Puducherry (India), Singapore, Sri Lanka","digital":"Kollywood film dubbing, Tamil devotional content, Carnatic music lyrics, Singapore government multilingual services, and Tamil educational YouTube channels"},
    "te-IN": {"script":"Telugu","script_type":"Abugida","speakers":"82 million","family":"Dravidian","origin":"Telugu inscriptions date back to 575 CE (the Kalamalla inscription), and the language earned the nickname 'Italian of the East' from European linguists for its vowel-ending phonology.","cultural":"Tollywood (Telugu film industry) is India's second-largest by revenue, and Telugu is the fastest-growing language on the Indian internet with a 400% increase in content consumption since 2020.","direction":"ltr","official":"Andhra Pradesh, Telangana, India","digital":"Tollywood trailer narration, Telugu tech tutorial voiceovers, Telangana government digital services, and Telugu podcast platforms that have grown 300% in 3 years"},
    "kn-IN": {"script":"Kannada","script_type":"Abugida","speakers":"44 million","family":"Dravidian","origin":"The Halmidi inscription (450 CE) is the oldest known Kannada inscription, and the language has produced 8 Jnanpith Award winners — the most for any Dravidian language.","cultural":"Kannada is the administrative language of Bengaluru (Bangalore), India's Silicon Valley, creating unique demand for tech-oriented Kannada voice content in India's IT capital.","direction":"ltr","official":"Karnataka, India","digital":"Sandalwood film industry dubbing, Bangalore startup pitch narrations in Kannada, Karnataka state e-learning, and Kannada tech podcast channels"},
    "ml-IN": {"script":"Malayalam","script_type":"Abugida","speakers":"38 million","family":"Dravidian","origin":"Malayalam has one of the most complex scripts among Indian languages with 578 conjunct consonant combinations, derived from the ancient Grantha script used for Sanskrit.","cultural":"Kerala, where Malayalam is spoken, has India's highest literacy rate (96.2%), driving exceptional demand for educational audio content and audiobooks in Malayalam.","direction":"ltr","official":"Kerala, Lakshadweep, India","digital":"Mollywood film narration, Kerala educational audio platforms, Malayalam literary audiobooks, and Gulf NRI community content for the 2+ million Malayalees abroad"},
    "bn-IN": {"script":"Bengali","script_type":"Abugida","speakers":"230 million","family":"Indo-Aryan","origin":"Rabindranath Tagore composed the national anthems of both India (Jana Gana Mana) and Bangladesh (Amar Sonar Bangla) in Bengali, making it the only language with two national anthems.","cultural":"Bengali has a Nobel Prize-winning literary tradition (Tagore, 1913) and Bangla poetry, particularly Nazrul Geeti and Rabindra Sangeet, form an integral part of the cultural identity of 230 million speakers.","direction":"ltr","official":"West Bengal, Tripura (India)","digital":"Rabindra Sangeet audio recordings, Bengali podcast networks, Kolkata cultural festival narrations, and educational content for the 100+ million Bengali internet users"},
    "pa-IN": {"script":"Gurmukhi","script_type":"Abugida","speakers":"113 million","family":"Indo-Aryan","origin":"The Gurmukhi script was standardized by Guru Angad, the second Sikh Guru, in the 16th century specifically to write the Sikh scriptures, making it deeply intertwined with Sikh religious identity.","cultural":"Punjabi is the language of Bhangra music, which has become a global phenomenon, and Punjabi songs consistently dominate Indian music charts and YouTube trending lists worldwide.","direction":"ltr","official":"Punjab, India","digital":"Bhangra and Punjabi pop music production, Gurbani audio streaming, Punjabi comedy content, and agricultural advisory voice services for Punjab's farming community"},
    "or-IN": {"script":"Odia","script_type":"Abugida","speakers":"35 million","family":"Indo-Aryan","origin":"Odia was recognized as India's 6th classical language in 2014, with literary traditions dating back to Sarala Das's 15th-century Odia Mahabharata, the first translation of the epic into any regional language.","cultural":"The Jagannath Temple in Puri and the Konark Sun Temple are UNESCO World Heritage sites in Odisha, generating significant demand for Odia-language tourism and devotional audio guides.","direction":"ltr","official":"Odisha, India","digital":"Jagannath temple devotional audio, Odia literature audiobooks, Odisha state e-governance, and Odia educational content for tribal areas"},
    "bn-BD": {"script":"Bengali","script_type":"Abugida","speakers":"170 million","family":"Indo-Aryan","origin":"The Bengali Language Movement of 1952, where students died protesting for Bengali's recognition, led UNESCO to declare February 21 as International Mother Language Day — the only language to inspire a global holiday.","cultural":"Bangladesh has the world's largest river delta (Sundarbans), and Bengali is central to the country's identity — the 1971 Liberation War was fought partly to preserve Bengali language and culture.","direction":"ltr","official":"Bangladesh (national language)","digital":"Bangladeshi news broadcasting, garment industry training audio, Dhaka University educational content, and Bengali audio platforms serving 170 million speakers"},
    "ur-PK": {"script":"Nastaliq (Perso-Arabic)","script_type":"Abjad","speakers":"70 million","family":"Indo-Aryan","origin":"Urdu developed as a contact language in the military camps (Urdu means 'army' in Turkish) of the Delhi Sultanate, blending Hindi grammar with Persian and Arabic vocabulary into an elegant literary language.","cultural":"Urdu is celebrated for its poetry traditions — Ghazal, Nazm, and Mushaira (poetry recitation gatherings) — and poets like Mirza Ghalib and Faiz Ahmed Faiz are revered across South Asia.","direction":"rtl","official":"Pakistan (national language)","digital":"Urdu news anchoring, Ghazal and Nazm audio recordings, Pakistani drama dubbing, and Urdu literary podcast platforms"},
    "ne-NP": {"script":"Devanagari","script_type":"Abugida","speakers":"16 million","family":"Indo-Aryan","origin":"Nepali was historically called Khas Kura (language of the Khas people) and became Nepal's national language after the unification of Nepal by Prithvi Narayan Shah in 1768.","cultural":"Nepal is the birthplace of Lord Buddha (Lumbini) and home to Mount Everest, driving demand for Nepali-language tourism guides, trekking audio, and Buddhist devotional content.","direction":"ltr","official":"Nepal (national language), Sikkim (India)","digital":"Himalayan trekking audio guides, Nepali FM radio content, Nepal government digital services, and Nepali diaspora community podcasts"},
    "si-LK": {"script":"Sinhala","script_type":"Abugida","speakers":"17 million","family":"Indo-Aryan","origin":"Sinhala has one of the most aesthetically rounded scripts in the world, evolved from Brahmi script. The earliest Sinhala inscriptions date to the 3rd century BCE, found in ancient Sri Lankan cave temples.","cultural":"Sri Lanka's Sinhala literary tradition includes the Mahavamsa (Great Chronicle), a continuous historical record spanning over 2,000 years — one of the longest unbroken historical narratives in any language.","direction":"ltr","official":"Sri Lanka (official language)","digital":"Sri Lankan broadcasting narration, Sinhala educational platforms, Buddhist Pali text readings, and Sri Lankan tourism audio guides for cultural heritage sites"},
    "en-US": {"script":"Latin","script_type":"Alphabet","speakers":"380 million native","family":"Germanic","origin":"American English diverged from British English in the 17th century with colonization, and Noah Webster's 1828 dictionary deliberately simplified spellings (color vs colour, center vs centre) to establish American linguistic independence.","cultural":"American English is the dominant language of global technology, with Silicon Valley, Hollywood, and the US music industry driving worldwide English content consumption exceeding 500 billion hours annually.","direction":"ltr","official":"United States (de facto)","digital":"YouTube content creation, podcast production, corporate training, e-learning courses, audiobook narration, and accessibility tools for 330+ million Americans"},
    "en-GB": {"script":"Latin","script_type":"Alphabet","speakers":"60 million native","family":"Germanic","origin":"British English preserves many older spellings and pronunciations from Middle English, and the Great Vowel Shift (1400-1700) fundamentally changed English pronunciation while spelling remained largely frozen.","cultural":"The BBC's Received Pronunciation (RP) was historically considered 'standard' English, but modern British TTS must handle diverse regional accents from Cockney to Geordie to Scottish English.","direction":"ltr","official":"United Kingdom","digital":"BBC-style narration, British audiobook production, UK e-learning platforms, and British English language training for the 1.5 billion global English learners"},
    "en-AU": {"script":"Latin","script_type":"Alphabet","speakers":"25 million","family":"Germanic","origin":"Australian English developed unique characteristics from the blending of British dialects brought by colonists and convicts, plus Aboriginal language influences, creating distinctive vowel sounds and slang.","cultural":"Australian English is known for its distinctive rising intonation pattern and vocabulary like 'arvo' (afternoon) and 'barbie' (barbecue), reflecting Australia's relaxed cultural identity.","direction":"ltr","official":"Australia (de facto)","digital":"Australian educational content, tourism audio guides for the Great Barrier Reef and Outback, and Australian podcast production which has grown 89% since 2023"},
    "en-IN": {"script":"Latin","script_type":"Alphabet","speakers":"130 million","family":"Germanic","origin":"Indian English developed during British colonial rule and has evolved into a distinct variety with unique vocabulary (prepone, do the needful, lakh, crore) recognized by linguists as a legitimate English dialect.","cultural":"India has the world's second-largest English-speaking population, and Indian English is the language of India's $250 billion IT industry, Bollywood English-language films, and pan-Indian business communication.","direction":"ltr","official":"India (official language alongside Hindi)","digital":"Indian IT training content, IIT/IIM educational lectures, Indian startup pitch videos, call center training, and pan-Indian corporate communications"},
    "en-CA": {"script":"Latin","script_type":"Alphabet","speakers":"27 million","family":"Germanic","origin":"Canadian English uniquely blends British spelling conventions (colour, centre) with American pronunciation patterns, plus French-influenced vocabulary in bilingual regions like Quebec and New Brunswick.","cultural":"Canada's official bilingualism (English-French) means Canadian English TTS must coexist with French content, and Canadian English has distinctive features like 'eh' as a discourse marker and 'aboot' pronunciation.","direction":"ltr","official":"Canada (co-official with French)","digital":"Canadian government bilingual services, Toronto media production, Canadian educational platforms, and content for 38 million Canadians"},
    "en-ZA": {"script":"Latin","script_type":"Alphabet","speakers":"17 million","family":"Germanic","origin":"South African English has been shaped by contact with Afrikaans, Zulu, Xhosa, and other languages, creating unique vocabulary like 'braai' (barbecue), 'robot' (traffic light), and 'bakkie' (pickup truck).","cultural":"South Africa has 11 official languages, and South African English serves as the primary language of business, media, and inter-ethnic communication across the Rainbow Nation's diverse population.","direction":"ltr","official":"South Africa (one of 11 official languages)","digital":"South African broadcasting, rainbow nation educational content, mining and business training materials, and content for SA's growing tech startup ecosystem"},
    "en-NG": {"script":"Latin","script_type":"Alphabet","speakers":"90 million L2","family":"Germanic","origin":"Nigerian English (or Naija) has evolved into a dynamic variety incorporating Yoruba, Igbo, and Hausa linguistic features, with Nigerian Pidgin English serving as a lingua franca for 100+ million speakers.","cultural":"Nollywood (Nigerian film industry) is the world's second-largest by volume, and Nigeria's booming Afrobeats music scene has made Nigerian English globally influential in entertainment.","direction":"ltr","official":"Nigeria (official language)","digital":"Nollywood production narration, Nigerian podcast explosion, Afrobeats music content, and educational audio for Nigeria's 220 million population"},
    "es-ES": {"script":"Latin","script_type":"Alphabet","speakers":"48 million (Spain)","family":"Romance","origin":"Castilian Spanish originated in the Kingdom of Castile and was codified by Alfonso X 'the Wise' in the 13th century, who mandated that official documents be written in Castilian instead of Latin.","cultural":"Spain's Real Academia Española (RAE), founded in 1713, maintains the official standard for the Spanish language, and its motto 'Limpia, fija y da esplendor' (cleans, fixes, and gives splendor) guides linguistic purity.","direction":"ltr","official":"Spain","digital":"Spanish broadcasting, European Spanish e-learning, tourism audio for Spain's 85 million annual visitors, and castellano academic content"},
    "es-MX": {"script":"Latin","script_type":"Alphabet","speakers":"130 million","family":"Romance","origin":"Mexican Spanish absorbed hundreds of Nahuatl (Aztec) words after the Spanish conquest — words like chocolate, tomato, avocado, and coyote entered world languages through Mexican Spanish.","cultural":"Mexico is the world's largest Spanish-speaking country by population, and Mexican telenovelas are broadcast in over 100 countries, making Mexican Spanish accent one of the most widely recognized worldwide.","direction":"ltr","official":"Mexico (de facto)","digital":"Mexican telenovela dubbing, Latin American YouTube content, Mexican podcast production, and educational audio for Mexico's 130 million population"},
    "es-AR": {"script":"Latin","script_type":"Alphabet","speakers":"45 million","family":"Romance","origin":"Argentine Spanish is distinguished by 'voseo' (using 'vos' instead of 'tú') and its Italian-influenced intonation, a legacy of the massive Italian immigration wave of the late 19th century.","cultural":"Argentina's unique Lunfardo slang, born in Buenos Aires tango culture, has enriched Spanish with hundreds of colorful expressions and is inseparable from tango lyrics and Argentine literature.","direction":"ltr","official":"Argentina","digital":"Argentine media production, tango music narration, River Plate football commentary, and South American Spanish educational content"},
    "es-CO": {"script":"Latin","script_type":"Alphabet","speakers":"51 million","family":"Romance","origin":"Colombian Spanish, particularly the Bogotá dialect (Rolo), is widely considered one of the clearest and most neutral Spanish accents, making it highly sought after for international Spanish media and dubbing.","cultural":"Colombia's literary tradition includes Nobel laureate Gabriel García Márquez, whose magical realism in novels like 'One Hundred Years of Solitude' elevated Colombian Spanish to global literary prominence.","direction":"ltr","official":"Colombia","digital":"International Spanish dubbing (Bogotá accent preferred), Colombian podcast production, call center training audio, and Latin American corporate content"},
    "es-US": {"script":"Latin","script_type":"Alphabet","speakers":"42 million native","family":"Romance","origin":"US Spanish is a dynamic blend of Mexican, Caribbean, Central American, and South American varieties, reflecting the diverse origins of the 63 million Hispanic Americans who make the US the world's second-largest Spanish-speaking country.","cultural":"The US Hispanic market represents $2.8 trillion in purchasing power, and bilingual English-Spanish content creation is one of the fastest-growing digital media segments in North America.","direction":"ltr","official":"United States (no official status, widely spoken)","digital":"US Hispanic marketing audio, bilingual educational content, Spanish-language podcast production, and content for 63 million US Hispanics"},
    "fr-FR": {"script":"Latin","script_type":"Alphabet","speakers":"68 million","family":"Romance","origin":"French became Europe's diplomatic lingua franca after the Treaty of Westphalia (1648), and the Académie Française, founded by Cardinal Richelieu in 1635, continues to guard French linguistic purity to this day.","cultural":"French is an official language of 29 countries across 5 continents and remains the working language of international diplomacy, the International Olympic Committee, and numerous UN agencies.","direction":"ltr","official":"France","digital":"French broadcasting, luxury brand marketing narration, French academic content, EU institutional communications, and French podcast production"},
    "fr-CA": {"script":"Latin","script_type":"Alphabet","speakers":"7 million","family":"Romance","origin":"Canadian French (Québécois) preserves many 17th-century French pronunciations lost in European French, as Quebec was colonized before the French Revolution's linguistic reforms standardized Parisian French.","cultural":"Quebec's language laws (Bill 101) make French the sole official language of the province, creating a unique market where all business, signage, and media must be in French — driving enormous demand for French-Canadian voiceover content.","direction":"ltr","official":"Canada (co-official with English), Quebec","digital":"Quebec media production, Canadian bilingual government services, Québécois podcast platforms, and French-Canadian educational content"},
    "de-DE": {"script":"Latin","script_type":"Alphabet","speakers":"95 million","family":"Germanic","origin":"Martin Luther's 1534 Bible translation into German is credited with standardizing the German language, as he deliberately chose a dialect understandable across regions, effectively creating modern High German.","cultural":"Germany is Europe's largest economy and German is the most widely spoken native language in the EU. German compound words (like Donaudampfschifffahrtsgesellschaftskapitän) are famous for their complexity and precision.","direction":"ltr","official":"Germany, Austria, Switzerland, Liechtenstein, Belgium, Luxembourg","digital":"German industrial training content, Bundesliga sports commentary, German engineering documentation, EU institutional content, and DACH region podcast production"},
    "de-AT": {"script":"Latin","script_type":"Alphabet","speakers":"9 million","family":"Germanic","origin":"Austrian German (Österreichisches Deutsch) has official recognition as a distinct variety in the EU, with over 7,000 officially listed vocabulary differences from Standard German, including unique food terminology like Palatschinken (pancakes) and Paradeiser (tomatoes).","cultural":"Austria's musical heritage — from Mozart and Strauss to the Vienna Philharmonic — means Austrian German TTS must handle musical terminology and the distinctive softer Austrian pronunciation.","direction":"ltr","official":"Austria","digital":"Austrian broadcasting, Vienna cultural institution audio guides, Alpine tourism narration, and Austrian educational content"},
    "it-IT": {"script":"Latin","script_type":"Alphabet","speakers":"68 million","family":"Romance","origin":"Modern Italian is based on the Tuscan dialect, largely because of the literary prestige of Dante Alighieri's 'Divine Comedy' (1320), which established Tuscan as Italy's literary standard centuries before political unification.","cultural":"Italian is the language of opera, classical music, culinary arts, and fashion. Musical terms worldwide (piano, forte, crescendo, tempo) are Italian, making Italian TTS essential for music education and cultural content.","direction":"ltr","official":"Italy, San Marino, Vatican City, Switzerland","digital":"Italian opera libretto narration, fashion industry presentations, Italian tourism audio guides for 65 million annual visitors, and Italian culinary content"},
    "pt-BR": {"script":"Latin","script_type":"Alphabet","speakers":"215 million","family":"Romance","origin":"Brazilian Portuguese diverged significantly from European Portuguese after 1822 independence, incorporating thousands of Tupi-Guarani indigenous words and African linguistic influences from the transatlantic slave trade.","cultural":"Brazil is the world's largest Portuguese-speaking country (215 million vs Portugal's 10 million), and Brazilian Portuguese is the dominant variety in global media, music (Bossa Nova, Samba), and digital content.","direction":"ltr","official":"Brazil","digital":"Brazilian YouTube content (5th largest market globally), novela dubbing, Brazilian podcast boom, Samba and MPB music production, and educational audio for Brazil's 215 million citizens"},
    "pt-PT": {"script":"Latin","script_type":"Alphabet","speakers":"10 million","family":"Romance","origin":"Portuguese explorers spread their language across four continents in the 15th-16th centuries, making Portuguese the 6th most spoken language globally and the most spoken language in the Southern Hemisphere.","cultural":"Fado music, UNESCO Intangible Cultural Heritage, is Portugal's soulful musical tradition that demands emotionally expressive vocal delivery — making natural TTS crucial for Portuguese cultural content.","direction":"ltr","official":"Portugal","digital":"European Portuguese broadcasting, Fado music narration, Portuguese tourism audio guides, and content for the 260 million Portuguese speakers worldwide"},
    "nl-NL": {"script":"Latin","script_type":"Alphabet","speakers":"25 million","family":"Germanic","origin":"Dutch is the closest major language relative to English, sharing Germanic roots. The Dutch Golden Age (17th century) made Dutch a language of science, trade, and art, with painters like Rembrandt and Vermeer.","cultural":"The Netherlands has Europe's highest English proficiency among non-native speakers, yet Dutch remains vital for government, education, and media — creating demand for high-quality Dutch TTS.","direction":"ltr","official":"Netherlands, Belgium (Flanders), Suriname","digital":"Dutch broadcasting, Netherlands e-governance, Flemish media content, and educational audio for the Benelux region"},
    "sv-SE": {"script":"Latin","script_type":"Alphabet","speakers":"10 million","family":"Germanic","origin":"Swedish evolved from Old Norse, the language of the Vikings, and modern Swedish retains melodic tonal qualities (word accents) that give it a distinctive sing-song prosody unique among Germanic languages.","cultural":"Sweden is home to Spotify, IKEA, and a disproportionately influential music export industry (ABBA, Max Martin), making Swedish digital content production a cornerstone of the creative economy.","direction":"ltr","official":"Sweden, Finland (co-official)","digital":"Swedish podcast production (Sweden has among the highest podcast listenership per capita globally), IKEA product narration, Swedish educational content, and Nordic media"},
    "nb-NO": {"script":"Latin","script_type":"Alphabet","speakers":"5 million","family":"Germanic","origin":"Norway uniquely has two official written standards — Bokmål (based on Danish-influenced urban speech) and Nynorsk (based on rural dialects) — a linguistic situation called 'language struggle' (målstriden) that continues today.","cultural":"Norwegian is essential for the massive North Sea oil industry, and Norway's sovereign wealth fund (the world's largest at $1.7 trillion) drives demand for professional Norwegian financial content.","direction":"ltr","official":"Norway","digital":"Norwegian oil industry training, Nordic broadcasting, Norwegian educational platforms, and content for Norway's high-GDP digital economy"},
    "da-DK": {"script":"Latin","script_type":"Alphabet","speakers":"6 million","family":"Germanic","origin":"Danish was the administrative language of the entire Nordic region during the Kalmar Union (1397-1523), and modern Danish is notable for its soft consonants and glottal stop (stød) that make it famously difficult to understand for other Scandinavians.","cultural":"Denmark gave the world Hans Christian Andersen's fairy tales, and the concept of 'hygge' (cozy contentment) has become a global cultural phenomenon — both requiring authentic Danish narration.","direction":"ltr","official":"Denmark, Faroe Islands, Greenland","digital":"Danish broadcasting, Scandinavian audiobook production, Danish e-learning platforms, and LEGO corporate content"},
    "fi-FI": {"script":"Latin","script_type":"Alphabet","speakers":"5.5 million","family":"Uralic","origin":"Finnish is a Uralic language completely unrelated to its Scandinavian neighbors, with 15 grammatical cases and extensive agglutination — a single Finnish word can express what requires an entire English sentence.","cultural":"Finland consistently ranks #1 in global education quality (PISA), and the Kalevala epic poem (1835) is the national literary treasure that inspired Tolkien's Elvish languages in Lord of the Rings.","direction":"ltr","official":"Finland (co-official with Swedish)","digital":"Finnish educational content (supporting Finland's world-leading education system), Nokia corporate communications, Finnish sauna culture audio guides, and Nordic media production"},
    "pl-PL": {"script":"Latin","script_type":"Alphabet","speakers":"45 million","family":"Slavic","origin":"Polish uses a modified Latin alphabet with unique diacritical marks (ą, ę, ó, ś, ź, ż, ć, ń, ł) and has seven grammatical cases, making it one of the most complex Slavic languages for pronunciation engines.","cultural":"Poland has produced literary Nobel laureates (Henryk Sienkiewicz, Wisława Szymborska, Olga Tokarczuk) and has a thriving game development industry (CD Projekt RED, creators of The Witcher and Cyberpunk 2077).","direction":"ltr","official":"Poland, EU","digital":"Polish gaming industry voiceover, Polish educational content, Eastern European media production, and corporate training for Poland's rapidly growing tech sector"},
    "cs-CZ": {"script":"Latin","script_type":"Alphabet","speakers":"10.7 million","family":"Slavic","origin":"Czech linguist Jan Hus invented the háček (ˇ) diacritical mark in the 15th century, which was later adopted by Slovak, Slovenian, Croatian, and other languages — a Czech contribution to global linguistics.","cultural":"Prague is a global center of animated film production, and the Czech language's complex morphology (7 cases, intricate verb aspects) makes natural-sounding Czech TTS a significant technical achievement.","direction":"ltr","official":"Czech Republic, EU","digital":"Czech animation dubbing, Prague tourism audio guides, Czech Republic e-learning, and Central European corporate content"},
    "sk-SK": {"script":"Latin","script_type":"Alphabet","speakers":"5.2 million","family":"Slavic","origin":"Slovak and Czech are mutually intelligible sister languages, yet Slovak has preserved older Slavic features — Ľudovít Štúr codified literary Slovak in 1843 based on Central Slovak dialects rather than the closely related Czech.","cultural":"Slovakia has a rich tradition of folk music and storytelling, and the High Tatras mountains drive significant tourism demand for Slovak-language audio guides and cultural content.","direction":"ltr","official":"Slovakia, EU","digital":"Slovak broadcasting, Tatra mountains tourism narration, Slovak educational platforms, and cross-border Czech-Slovak media content"},
    "hu-HU": {"script":"Latin","script_type":"Alphabet","speakers":"13 million","family":"Uralic","origin":"Hungarian is a Uralic language linguistic island in Central Europe, completely unrelated to any neighboring language. With 18 grammatical cases and vowel harmony, it is considered one of the hardest European languages to master.","cultural":"Hungary has produced more Nobel laureates per capita than almost any country, and Hungarian mathematical and scientific terminology has contributed words like 'hologram' and concepts to global science.","direction":"ltr","official":"Hungary, EU","digital":"Hungarian broadcasting, Budapest tourism audio guides, Hungarian educational content, and corporate training for Hungary's growing services sector"},
    "ro-RO": {"script":"Latin","script_type":"Alphabet","speakers":"26 million","family":"Romance","origin":"Romanian is the only Romance language that preserved the Latin grammatical case system and definite article suffixation (unlike French, Spanish, Italian), making it the closest living language to Latin grammar.","cultural":"Romania's Transylvania region is famous worldwide through Bram Stoker's Dracula, and Romanian folk traditions, particularly the Merry Cemetery of Săpânța, create unique cultural content needs.","direction":"ltr","official":"Romania, Moldova, EU","digital":"Romanian broadcasting, Transylvania tourism narration, Romanian IT industry content (Romania is a top European tech hub), and educational audio"},
    "bg-BG": {"script":"Cyrillic","script_type":"Alphabet","speakers":"8 million","family":"Slavic","origin":"Bulgaria created the Cyrillic alphabet in the 9th century CE — Saints Cyril and Methodius (and their students) developed it in the First Bulgarian Empire, and it spread to Russia, Serbia, Ukraine, and other Slavic nations.","cultural":"Bulgaria is the birthplace of the Cyrillic alphabet used by 250+ million people today, and Bulgarian folk music's asymmetric rhythms (like 7/8 and 11/8 time signatures) are mathematically unique in world music.","direction":"ltr","official":"Bulgaria, EU","digital":"Bulgarian broadcasting, Cyrillic heritage content, Bulgarian educational platforms, and tourism audio for Bulgaria's Black Sea and mountain resorts"},
    "hr-HR": {"script":"Latin","script_type":"Alphabet","speakers":"5.5 million","family":"Slavic","origin":"Croatian uses the Latin alphabet while its close relative Serbian uses Cyrillic — despite the languages being mutually intelligible. Croatian standardization was championed by Ljudevit Gaj in the 19th century.","cultural":"Croatia's stunning Adriatic coastline (1,244 islands) makes it a top European tourist destination, with Dubrovnik serving as the filming location for King's Landing in Game of Thrones.","direction":"ltr","official":"Croatia, EU","digital":"Croatian tourism narration for Adriatic coast, Croatian broadcasting, Dalmatian cultural content, and EU institutional translations"},
    "uk-UA": {"script":"Cyrillic","script_type":"Alphabet","speakers":"45 million","family":"Slavic","origin":"Ukrainian has a distinctive melodic quality, earning it the nickname 'singing language.' The language was suppressed under Russian imperial and Soviet rule, making its preservation a powerful act of national identity.","cultural":"Ukrainian culture includes unique traditions like vyshyvanka embroidery, pysanky decorated eggs, and a rich literary tradition from Taras Shevchenko to modern authors, all demanding authentic Ukrainian voice content.","direction":"ltr","official":"Ukraine","digital":"Ukrainian broadcasting and news, educational content for Ukrainian diaspora, cultural preservation audio projects, and Ukrainian government digital services"},
    "ru-RU": {"script":"Cyrillic","script_type":"Alphabet","speakers":"258 million","family":"Slavic","origin":"Peter the Great reformed the Cyrillic alphabet in 1708, simplifying it from Church Slavonic to create the modern Russian 'civil script' (grazhdanskiy shrift) used today.","cultural":"Russian literature (Tolstoy, Dostoevsky, Chekhov, Pushkin) is considered one of the world's greatest literary traditions, and Russian remains a lingua franca across the 15 former Soviet republics.","direction":"ltr","official":"Russia, Belarus, Kazakhstan, Kyrgyzstan","digital":"Russian audiobook production, CIS region broadcasting, Russian educational platforms, Russian-language YouTube (one of the largest language segments), and tech documentation"},
    "el-GR": {"script":"Greek","script_type":"Alphabet","speakers":"13 million","family":"Hellenic","origin":"Greek has the longest documented history of any living language, spanning 3,400 years of continuous written records. The Greek alphabet, adapted from Phoenician around 800 BCE, became the ancestor of Latin and Cyrillic scripts.","cultural":"Greek contributed more words to the English language than any other language except Latin, with scientific and philosophical terms (philosophy, democracy, biology, physics) being Greek in origin.","direction":"ltr","official":"Greece, Cyprus, EU","digital":"Greek broadcasting, ancient heritage tourism narration, Greek educational content, Orthodox religious audio, and Greek diaspora community platforms"},
    "tr-TR": {"script":"Latin","script_type":"Alphabet","speakers":"80 million","family":"Turkic","origin":"Turkey switched from Arabic to Latin script in 1928 under Atatürk's language revolution, one of the most dramatic linguistic reforms in history, achieving near-universal literacy within a generation.","cultural":"Turkish is the gateway to the Turkic language family spanning from Turkey to Central Asia, and Turkish TV dramas (dizi) are exported to over 150 countries, creating global demand for Turkish voice content.","direction":"ltr","official":"Turkey, Northern Cyprus","digital":"Turkish drama (dizi) dubbing for 150+ country exports, Turkish broadcasting, Istanbul tourism narration, and Turkish educational content for 80 million speakers"},
    "ja-JP": {"script":"Kanji + Hiragana + Katakana","script_type":"Logographic + Syllabary","speakers":"125 million","family":"Japonic","origin":"Japanese uses three simultaneous writing systems — Kanji (Chinese characters), Hiragana (native syllabary), and Katakana (for foreign words) — making it one of the most complex writing systems in active use.","cultural":"Japan's anime, manga, and gaming industries generate $30+ billion annually and are consumed globally, creating massive demand for Japanese voice acting (seiyū) and voice synthesis technology.","direction":"ltr","official":"Japan","digital":"Anime and game voiceover production, Japanese podcast platforms, Japan tourism audio guides, J-Pop music content, and Japanese corporate training materials"},
    "zh-CN": {"script":"Simplified Chinese","script_type":"Logographic","speakers":"920 million","family":"Sino-Tibetan","origin":"Chinese is the world's oldest continuously used writing system, with oracle bone inscriptions dating to 1250 BCE. Simplified Chinese characters were introduced in the 1950s-60s to increase literacy rates.","cultural":"Mandarin Chinese is spoken by more native speakers than any other language. China's digital economy (WeChat, Douyin/TikTok, Alibaba) has created the world's largest digital content ecosystem.","direction":"ltr","official":"China (PRC), Singapore","digital":"Chinese social media content (Douyin, Bilibili), e-commerce product narration, Chinese educational platforms, corporate training for China's 1.4 billion market, and Mandarin language learning audio"},
    "zh-TW": {"script":"Traditional Chinese","script_type":"Logographic","speakers":"23 million","family":"Sino-Tibetan","origin":"Taiwan preserves Traditional Chinese characters (繁體字) with their full complexity, as opposed to mainland China's simplified versions. Traditional characters maintain visual connections to their ancient pictographic origins spanning 3,000+ years.","cultural":"Taiwan's semiconductor industry (TSMC) drives the global tech economy, and Taiwanese Mandarin has a distinctive softer pronunciation and unique vocabulary influenced by Hokkien and Japanese.","direction":"ltr","official":"Taiwan (ROC)","digital":"Taiwanese tech industry content, Traditional Chinese audiobooks, Taiwan tourism narration, and content for the global Traditional Chinese reading community"},
    "zh-HK": {"script":"Traditional Chinese","script_type":"Logographic","speakers":"7.5 million","family":"Sino-Tibetan","origin":"Cantonese preserves many features of ancient Chinese that Mandarin has lost, including the entering tone (入聲) and distinctions between initial consonants. Linguists consider Cantonese closer to Tang Dynasty Chinese pronunciation.","cultural":"Hong Kong's film industry and Cantopop music scene have made Cantonese one of the most culturally influential Chinese varieties globally, with Bruce Lee and Jackie Chan films popularizing Cantonese worldwide.","direction":"ltr","official":"Hong Kong SAR (co-official with English)","digital":"Cantonese broadcasting, Hong Kong film industry dubbing, Cantopop music production, and content for the 80+ million Cantonese speakers worldwide"},
    "ko-KR": {"script":"Hangul","script_type":"Featural alphabet","speakers":"77 million","family":"Koreanic","origin":"Hangul was scientifically designed by King Sejong the Great in 1443, with each consonant shape reflecting the position of the tongue and mouth during pronunciation — making it the only major alphabet created by a known inventor with documented design principles.","cultural":"The Korean Wave (Hallyu) — K-Pop, K-Drama, Korean cinema (Parasite won the Oscar) — has made Korean one of the most studied languages globally, with BTS and Blackpink driving unprecedented interest.","direction":"ltr","official":"South Korea, North Korea","digital":"K-Drama dubbing and subtitling, K-Pop lyric narration, Korean webtoon audio, Korean gaming voiceover, and Korean language learning content for millions of global Hallyu fans"},
    "vi-VN": {"script":"Latin (Quốc Ngữ)","script_type":"Alphabet","speakers":"85 million","family":"Austroasiatic","origin":"Vietnamese is a tonal language with 6 tones, and its Latin-based script (Quốc Ngữ) was developed by Portuguese Jesuit missionaries in the 17th century — making Vietnamese the only major Southeast Asian language using Latin letters.","cultural":"Vietnamese cuisine (phở, bánh mì) has become globally popular, and Vietnam's rapidly growing digital economy makes Vietnamese one of the fastest-growing languages for digital content creation in Southeast Asia.","direction":"ltr","official":"Vietnam","digital":"Vietnamese e-commerce narration, Vietnam tourism audio guides, Vietnamese educational platforms, and content for Vietnam's booming digital economy with 78 million internet users"},
    "th-TH": {"script":"Thai","script_type":"Abugida","speakers":"69 million","family":"Kra-Dai","origin":"The Thai script was created by King Ramkhamhaeng the Great in 1283, adapted from Khmer script. Thai is written without spaces between words, making text segmentation a unique challenge for Thai TTS systems.","cultural":"Thailand's tourism industry (40 million visitors annually) and its global culinary influence (Thai cuisine ranked among the world's best) create enormous demand for Thai-language audio guides and content.","direction":"ltr","official":"Thailand","digital":"Thai tourism narration for 40M annual visitors, Thai broadcasting, Thai educational content, Thai e-commerce platforms, and Buddhist temple audio guides"},
    "id-ID": {"script":"Latin","script_type":"Alphabet","speakers":"200 million","family":"Austronesian","origin":"Indonesian (Bahasa Indonesia) was deliberately chosen as the national language over Javanese (which had more speakers) during independence to unite 700+ ethnic groups, based on Malay — a trade lingua franca for centuries.","cultural":"Indonesia is the world's 4th most populous nation with 270 million people across 17,000 islands speaking 700+ local languages, making Indonesian TTS crucial for national communication and education.","direction":"ltr","official":"Indonesia","digital":"Indonesian social media content (4th largest Facebook user base globally), e-commerce narration, Indonesian educational platforms, and government communication for 270 million citizens"},
    "ms-MY": {"script":"Latin","script_type":"Alphabet","speakers":"33 million","family":"Austronesian","origin":"Malay is one of the oldest documented Austronesian languages, with 7th-century inscriptions found in Sumatra. It served as the lingua franca of Southeast Asian maritime trade for over a millennium.","cultural":"Malaysia's multilingual society (Malay, Chinese, Tamil, English) makes Malay TTS essential for government services, education, and national media in a country that celebrates linguistic diversity.","direction":"ltr","official":"Malaysia, Brunei, Singapore","digital":"Malaysian broadcasting, Kuala Lumpur tourism narration, Malaysian educational content, and ASEAN regional communication"},
    "fil-PH": {"script":"Latin","script_type":"Alphabet","speakers":"28 million native, 80 million total","family":"Austronesian","origin":"Filipino is based on Tagalog but incorporates elements from other Philippine languages plus heavy Spanish and English influence — reflecting 333 years of Spanish and 48 years of American colonization.","cultural":"The Philippines has the highest social media usage per capita globally (an average of 4+ hours daily), and Filipino content creation on YouTube, TikTok, and Facebook drives massive demand for Filipino voiceover.","direction":"ltr","official":"Philippines (co-official with English)","digital":"Filipino social media content production, OFW (Overseas Filipino Workers) communication content, Philippine educational audio, and Filipino vlog narration"},
    "ar-SA": {"script":"Arabic","script_type":"Abjad","speakers":"35 million (Saudi)","family":"Semitic","origin":"Arabic is the language of the Quran, and Classical Arabic has remained remarkably stable for 1,400+ years. Saudi Arabia's Najdi dialect forms the basis of Gulf Arabic, distinct from Egyptian or Levantine varieties.","cultural":"Saudi Arabia's Vision 2030 modernization program is driving massive digital content creation, and Arabic calligraphy is recognized by UNESCO as an Intangible Cultural Heritage of Humanity.","direction":"rtl","official":"Saudi Arabia (25+ Arab League nations)","digital":"Islamic educational content, Saudi Vision 2030 corporate communications, Arabic podcast platforms, and Gulf region e-commerce narration"},
    "ar-EG": {"script":"Arabic","script_type":"Abjad","speakers":"100 million","family":"Semitic","origin":"Egyptian Arabic is the most widely understood Arabic dialect globally, largely due to Egypt's dominant film, television, and music industries that have broadcast Egyptian Arabic across the Arab world since the 1930s.","cultural":"Egypt's entertainment industry makes Egyptian Arabic the 'Hollywood of the Arab world,' and Egyptian voice actors are the most sought-after for Arabic dubbing of international films and TV shows.","direction":"rtl","official":"Egypt","digital":"Egyptian film and TV dubbing, Arabic broadcasting (Egypt leads the Arab media industry), Egyptian educational content, and pan-Arab entertainment narration"},
    "fa-IR": {"script":"Perso-Arabic","script_type":"Abjad","speakers":"110 million","family":"Indo-Iranian","origin":"Persian (Farsi) is the language of Rumi, Hafez, and Ferdowsi, whose Shahnameh (Book of Kings) at 50,000 couplets is the longest epic poem written by a single author in human history.","cultural":"Persian calligraphy and poetry are considered the highest art forms in Iranian culture, and Persian has influenced Turkish, Urdu, and numerous Central Asian languages with its rich literary vocabulary.","direction":"rtl","official":"Iran, Afghanistan (as Dari), Tajikistan (as Tajik)","digital":"Persian literary audiobooks, Iranian broadcasting, Nowruz cultural content, and content for the 110 million Persian speakers across Iran, Afghanistan, and Tajikistan"},
    "he-IL": {"script":"Hebrew","script_type":"Abjad","speakers":"9 million","family":"Semitic","origin":"Hebrew is the only successfully revived dead language in human history. Eliezer Ben-Yehuda led the revival of Hebrew as a spoken language in the late 19th century after it had been used only for religious texts for nearly 2,000 years.","cultural":"Modern Hebrew had to coin thousands of new words for concepts that didn't exist in Biblical Hebrew (telephone, electricity, ice cream), making it a fascinating case study in language engineering.","direction":"rtl","official":"Israel","digital":"Israeli tech startup content, Hebrew educational platforms, Jewish religious audio, Israeli broadcasting, and Hebrew language learning content"},
    "ka-GE": {"script":"Georgian (Mkhedruli)","script_type":"Alphabet","speakers":"3.7 million","family":"Kartvelian","origin":"Georgian has one of only 14 unique alphabets in the world. The Georgian script (Mkhedruli) evolved from the older Asomtavruli script, and Georgian manuscripts from the 5th century CE are among the earliest in the Caucasus region.","cultural":"Georgia's polyphonic singing tradition is recognized by UNESCO as a Masterpiece of Intangible Heritage, and Georgian wine-making tradition spanning 8,000 years is the oldest in the world.","direction":"ltr","official":"Georgia","digital":"Georgian broadcasting, Caucasus tourism narration, Georgian wine culture content, and Georgian educational platforms"},
    "sw-KE": {"script":"Latin","script_type":"Alphabet","speakers":"100 million L2","family":"Bantu","origin":"Swahili is Africa's most widely spoken language, serving as a lingua franca across East Africa. It uniquely blends Bantu grammar with extensive Arabic vocabulary — 'Swahili' itself comes from the Arabic 'sahil' meaning 'coast.'","cultural":"Swahili is an official language of the African Union and has become the most taught African language globally, with increasing representation in international media and Disney's 'The Lion King' popularizing Swahili words like 'simba' (lion) and 'hakuna matata.'","direction":"ltr","official":"Kenya, Tanzania, Uganda, DRC, African Union","digital":"East African broadcasting, safari tourism narration, Pan-African educational content, and Swahili digital platforms for 100+ million speakers"},
    "am-ET": {"script":"Ge'ez (Ethiopic)","script_type":"Abugida","speakers":"32 million","family":"Semitic","origin":"Amharic uses the ancient Ge'ez script (Fidel), one of the oldest alphabets in continuous use, with 231 characters representing consonant-vowel combinations. Ethiopia is the only African country never colonized by a European power.","cultural":"Ethiopia has its own unique calendar (13 months), time system, and the Ge'ez script connects modern Amharic speakers to 2,000+ years of Ethiopian literary and religious tradition.","direction":"ltr","official":"Ethiopia (federal working language)","digital":"Ethiopian broadcasting, Amharic educational content, Ethiopian Orthodox religious audio, and content for Ethiopia's 120 million population"},
    "zu-ZA": {"script":"Latin","script_type":"Alphabet","speakers":"12 million","family":"Bantu","origin":"Zulu is famous for its click consonants (borrowed from Khoisan languages) — three distinct click types (dental, palatal, lateral) that make Zulu pronunciation uniquely challenging for TTS systems.","cultural":"The Zulu kingdom under Shaka Zulu was one of the most powerful African states, and Zulu cultural traditions (including the Reed Dance ceremony and Zulu beadwork) remain vibrant in modern South Africa.","direction":"ltr","official":"South Africa (one of 11 official languages)","digital":"South African broadcasting, Zulu educational content, KwaZulu-Natal tourism narration, and multilingual South African government services"},
    "af-ZA": {"script":"Latin","script_type":"Alphabet","speakers":"7 million","family":"Germanic","origin":"Afrikaans evolved from 17th-century Dutch dialects spoken by Cape Colony settlers, making it the youngest Germanic language. It simplified Dutch grammar dramatically — dropping gender, most conjugations, and the case system.","cultural":"Afrikaans literature and music (particularly 'Afrikaans rock') have experienced a cultural renaissance in post-apartheid South Africa, and Afrikaans remains important in South African business, agriculture, and media.","direction":"ltr","official":"South Africa (one of 11 official languages)","digital":"South African broadcasting, Afrikaans educational content, Western Cape tourism narration, and South African agricultural training audio"},
    "lv-LV": {"script":"Latin","script_type":"Alphabet","speakers":"1.75 million","family":"Baltic","origin":"Latvian is one of only two surviving Baltic languages (with Lithuanian), preserving ancient Indo-European features that have been lost in most other European languages, making it invaluable for historical linguistics.","cultural":"Latvia's Song and Dance Festival (Dziesmu svētki), a UNESCO Masterpiece, brings together 40,000+ singers, demonstrating the central role of language and song in Latvian national identity.","direction":"ltr","official":"Latvia, EU","digital":"Latvian broadcasting, Baltic educational content, Riga tourism narration, and EU institutional translations"},
    "lt-LT": {"script":"Latin","script_type":"Alphabet","speakers":"3 million","family":"Baltic","origin":"Lithuanian is considered the most archaic living Indo-European language, preserving features from Proto-Indo-European that disappeared from Latin, Greek, and Sanskrit thousands of years ago. Sanskrit scholars can recognize Lithuanian words.","cultural":"Lithuania was the last European country to adopt Christianity (1387), and Lithuanian folk songs (dainos) preserve pre-Christian Baltic mythology, making them a unique European cultural treasure.","direction":"ltr","official":"Lithuania, EU","digital":"Lithuanian broadcasting, Baltic cultural content, Vilnius tourism narration, and Lithuanian educational platforms"},
    "et-EE": {"script":"Latin","script_type":"Alphabet","speakers":"1.1 million","family":"Uralic","origin":"Estonian is closely related to Finnish (both Uralic languages) but unrelated to neighboring Latvian, Russian, or Swedish. Estonian has 14 grammatical cases and no grammatical gender or future tense.","cultural":"Estonia is the world's most digitally advanced society — e-Residency, digital voting, and 99% of government services online — making Estonian digital content and TTS crucial for this digital-first nation.","direction":"ltr","official":"Estonia, EU","digital":"Estonian e-governance content, digital Estonia platform narration, Estonian educational content, and Baltic region tech communication"},
    "az-AZ": {"script":"Latin","script_type":"Alphabet","speakers":"23 million","family":"Turkic","origin":"Azerbaijan switched from Arabic to Latin script in 1929 (before Turkey), then to Cyrillic under Soviet rule, and back to Latin after independence in 1991 — making Azerbaijanis who lived through the Soviet era trilingual in scripts.","cultural":"Azerbaijan sits at the crossroads of Europe and Asia, and its mugham musical tradition (UNESCO heritage) blends Persian, Turkish, and Caucasian elements into a unique art form requiring expressive vocal delivery.","direction":"ltr","official":"Azerbaijan","digital":"Azerbaijani broadcasting, Caspian region tourism narration, Baku cultural content, and content for Azerbaijan's growing oil-funded digital economy"},
    "kk-KZ": {"script":"Latin (transitioning from Cyrillic)","script_type":"Alphabet","speakers":"13 million","family":"Turkic","origin":"Kazakhstan is currently transitioning from Cyrillic to Latin script (target completion: 2031), one of the most ambitious script reforms in the 21st century affecting all government, education, and media content.","cultural":"Kazakhstan is the world's largest landlocked country and the birthplace of apples (the word 'Almaty' means 'full of apples'), with a rich nomadic cultural heritage driving demand for Kazakh-language cultural content.","direction":"ltr","official":"Kazakhstan (co-official with Russian)","digital":"Kazakh government digital transition content, Central Asian broadcasting, Kazakh educational platforms, and content for Kazakhstan's Cyrillic-to-Latin script reform"},
    "uz-UZ": {"script":"Latin","script_type":"Alphabet","speakers":"34 million","family":"Turkic","origin":"Uzbek was written in Arabic script until 1927, Latin until 1940, Cyrillic until 1993, and has now officially returned to Latin — giving Uzbekistan the distinction of using four different scripts within a century.","cultural":"Uzbekistan's Silk Road cities (Samarkand, Bukhara, Khiva) are UNESCO World Heritage sites, and Uzbek is the most widely spoken Turkic language in Central Asia.","direction":"ltr","official":"Uzbekistan","digital":"Uzbek educational content, Silk Road tourism narration, Uzbek broadcasting, and Central Asian cultural preservation audio"},
    "sq-AL": {"script":"Latin","script_type":"Alphabet","speakers":"7.5 million","family":"Albanian (isolate branch)","origin":"Albanian is the sole surviving member of its own branch of Indo-European languages, having no close relatives. Its origins remain debated — possibly descended from ancient Illyrian or Thracian languages.","cultural":"Albania's unique Besa code of honor (meaning 'to keep the promise') led Albanians to shelter and save nearly all Jewish refugees during World War II, the only European country where the Jewish population increased during the Holocaust.","direction":"ltr","official":"Albania, Kosovo, North Macedonia","digital":"Albanian broadcasting, Adriatic tourism narration, Albanian educational content, and Kosovo diaspora community platforms"},
    "mk-MK": {"script":"Cyrillic","script_type":"Alphabet","speakers":"2 million","family":"Slavic","origin":"Macedonian was standardized as a literary language only in 1945, making it one of Europe's youngest standard languages. It is the only Slavic language that has completely abandoned the case system.","cultural":"North Macedonia is home to Lake Ohrid, one of Europe's oldest and deepest lakes, and the Ohrid literary school where Saints Clement and Naum developed early Slavic literacy in the 9th century.","direction":"ltr","official":"North Macedonia","digital":"Macedonian broadcasting, Ohrid tourism narration, Macedonian educational content, and Balkan regional media"},
    "bs-BA": {"script":"Latin","script_type":"Alphabet","speakers":"2.5 million","family":"Slavic","origin":"Bosnian, Croatian, and Serbian were historically considered one language (Serbo-Croatian) but have been recognized as separate standard languages since Bosnia's independence in 1992, with Bosnian uniquely incorporating more Turkish and Arabic loanwords.","cultural":"Bosnia's cultural heritage reflects centuries of Ottoman influence, and Sarajevo's nickname 'Jerusalem of Europe' reflects its unique coexistence of mosques, churches, synagogues, and Orthodox cathedrals.","direction":"ltr","official":"Bosnia and Herzegovina","digital":"Bosnian broadcasting, Sarajevo tourism narration, Bosnian educational content, and Balkan diaspora community platforms"},
    "sr-RS": {"script":"Cyrillic + Latin","script_type":"Alphabet","speakers":"12 million","family":"Slavic","origin":"Serbian is the only European language that officially uses two scripts simultaneously — Cyrillic and Latin — and Serbian speakers routinely switch between them, a phenomenon called 'digraphia.'","cultural":"Serbia's EXIT music festival is one of Europe's largest, and Serbian culture bridges Western and Eastern European traditions, with the medieval Serbian monastery frescoes recognized as masterpieces of European art.","direction":"ltr","official":"Serbia, Bosnia and Herzegovina","digital":"Serbian broadcasting, Belgrade tourism narration, Serbian educational platforms, and Balkan media production"},
    "sl-SI": {"script":"Latin","script_type":"Alphabet","speakers":"2.5 million","family":"Slavic","origin":"Slovenian has the most complex grammatical number system of any Slavic language — preserving the rare dual number (for exactly two items) in addition to singular and plural, a feature lost in most other languages.","cultural":"Despite only 2 million speakers, Slovenian literature punches above its weight — Slovenia has the most bookshops and libraries per capita in the world, and Slovenian was the first written Slavic language (Freising manuscripts, 1000 CE).","direction":"ltr","official":"Slovenia, EU","digital":"Slovenian broadcasting, Ljubljana and Lake Bled tourism narration, Slovenian educational content, and Alpine region cultural audio"},
    "mt-MT": {"script":"Latin","script_type":"Alphabet","speakers":"520,000","family":"Semitic","origin":"Maltese is the only Semitic language written in Latin script and the only Semitic language that is an official EU language. It evolved from Siculo-Arabic (the Arabic dialect of medieval Sicily) with heavy Italian and English influence.","cultural":"Malta's 7,000-year history includes the world's oldest freestanding structures (Ġgantija temples, older than the Pyramids), and Maltese seamlessly blends Arabic roots with Romance vocabulary.","direction":"ltr","official":"Malta, EU","digital":"Maltese broadcasting, Malta tourism narration for 3+ million annual visitors, Maltese educational content, and EU institutional translations"},
    "cy-GB": {"script":"Latin","script_type":"Alphabet","speakers":"880,000","family":"Celtic","origin":"Welsh is the most widely spoken Celtic language and has been spoken continuously in Britain since before the Roman invasion. The Welsh language law of 1993 gave Welsh equal status with English in Wales.","cultural":"The Eisteddfod festival, dating back to 1176, is Europe's largest cultural festival celebrating Welsh poetry, music, and literature — entirely conducted in Welsh, a vibrant demonstration of Celtic language survival.","direction":"ltr","official":"Wales (UK), co-official with English","digital":"Welsh broadcasting (S4C Welsh-language TV channel), Welsh educational content, Snowdonia tourism narration, and Welsh government bilingual services"},
    "ga-IE": {"script":"Latin","script_type":"Alphabet","speakers":"1.7 million (170,000 daily)","family":"Celtic","origin":"Irish (Gaeilge) is the oldest vernacular literature in Western Europe, with Ogham inscriptions dating to the 4th century. Irish had its own unique script (Gaelic type/Cló Gaelach) until the mid-20th century.","cultural":"Ireland's Gaeltacht regions are Irish-speaking communities where the language is the daily medium of life, and Irish language revitalization is a major government priority with Irish now mandatory in schools.","direction":"ltr","official":"Ireland (first official language), EU","digital":"Irish language learning content, TG4 (Irish-language TV) production, Gaeltacht tourism narration, and Irish government bilingual services"},
    "ca-ES": {"script":"Latin","script_type":"Alphabet","speakers":"10 million","family":"Romance","origin":"Catalan is not a dialect of Spanish but an independent Romance language descended from Vulgar Latin, with its earliest known document (Forum Iudicum) dating to the 12th century. Catalan literature flourished during the medieval Crown of Aragon.","cultural":"Barcelona and Catalonia's strong cultural identity drives significant demand for Catalan-language content, and Catalan is the language of FC Barcelona's motto 'Més que un club' (More than a club).","direction":"ltr","official":"Catalonia, Balearic Islands, Valencia (Spain), Andorra","digital":"Catalan broadcasting (TV3), Barcelona tourism narration, Catalan educational content, and Andorra's sole official language content"},
    "is-IS": {"script":"Latin","script_type":"Alphabet","speakers":"370,000","family":"Germanic","origin":"Icelandic has changed so little over 1,000 years that modern Icelanders can read the medieval Viking sagas in their original Old Norse. Rather than borrowing foreign words, Icelandic creates new compounds from native roots (e.g., 'tölva' for computer = number + prophetess).","cultural":"Iceland's literary tradition (Sagas, Eddas) is a UNESCO Memory of the World treasure, and Icelanders read more books per capita than any other nation, driving demand for Icelandic audiobooks and narration.","direction":"ltr","official":"Iceland","digital":"Icelandic literary audiobooks, Iceland tourism narration (3x more tourists than residents annually), Icelandic educational content, and Viking saga audio productions"},
    "mn-MN": {"script":"Cyrillic","script_type":"Alphabet","speakers":"5.2 million","family":"Mongolic","origin":"Mongolian was historically written in the unique vertical Mongolian script (written top-to-bottom, left-to-right), and Mongolia now uses Cyrillic while Inner Mongolia (China) still uses the traditional vertical script.","cultural":"Mongolia's vast steppes and nomadic heritage (Genghis Khan's empire was history's largest contiguous land empire) create unique content needs for Mongolian-language cultural preservation and tourism.","direction":"ltr","official":"Mongolia","digital":"Mongolian broadcasting, Gobi Desert tourism narration, Mongolian educational content, and nomadic cultural heritage audio preservation"},
    "km-KH": {"script":"Khmer","script_type":"Abugida","speakers":"16 million","family":"Austroasiatic","origin":"Khmer has the largest alphabet of any language in the world (74 letters according to Guinness World Records), and the Khmer script is the ancestor of Thai and Lao writing systems.","cultural":"Cambodia's Angkor Wat is the world's largest religious monument and the heart of Khmer cultural identity. Khmer classical dance (Apsara) is a UNESCO Intangible Cultural Heritage requiring precise vocal accompaniment.","direction":"ltr","official":"Cambodia","digital":"Cambodian broadcasting, Angkor Wat tourism narration, Khmer educational content, and Cambodian cultural preservation audio"},
    "lo-LA": {"script":"Lao","script_type":"Abugida","speakers":"7 million","family":"Kra-Dai","origin":"Lao and Thai scripts share a common ancestor (Khmer), and the two languages are mutually intelligible to a significant degree. Lao script has fewer consonant classes than Thai, reflecting historical simplification.","cultural":"Laos is known as the 'Land of a Million Elephants,' and Lao culture centers on Theravada Buddhism — with 4,900+ temples (wats) creating demand for Lao-language Buddhist audio content.","direction":"ltr","official":"Laos","digital":"Lao broadcasting, Luang Prabang tourism narration, Lao Buddhist educational content, and Mekong region cultural audio"},
    "my-MM": {"script":"Myanmar (Burmese)","script_type":"Abugida","speakers":"33 million","family":"Sino-Tibetan","origin":"The circular shapes of the Myanmar script evolved because scribes wrote on palm leaves — straight lines would tear the leaves, so every letter became round. This gives Burmese one of the most visually distinctive scripts in the world.","cultural":"Myanmar's 2,000+ year Buddhist heritage includes Bagan's 4,000+ temples, and Burmese puppetry (Yoke thé) and classical music require expressive vocal narration in the tonal Burmese language.","direction":"ltr","official":"Myanmar (Burma)","digital":"Myanmar broadcasting, Bagan temple tourism narration, Buddhist educational audio, and Myanmar cultural preservation content"},
    "ps-AF": {"script":"Perso-Arabic","script_type":"Abjad","speakers":"40-60 million","family":"Indo-Iranian","origin":"Pashto has a rich oral poetry tradition spanning centuries, with the Pashtunwali code of honor and Landay (two-line folk poems, often composed by women) representing one of the world's oldest living oral literary traditions.","cultural":"Pashto is spoken across the Afghanistan-Pakistan border region by the Pashtun people, the world's largest tribal society (estimated 50+ million), with a strong tradition of oral storytelling and poetry.","direction":"rtl","official":"Afghanistan (co-official with Dari)","digital":"Pashto broadcasting, Afghan educational content, Pashtun cultural audio preservation, and diaspora community platforms"},
    "yo-NG": {"script":"Latin","script_type":"Alphabet","speakers":"47 million","family":"Niger-Congo","origin":"Yoruba is a tonal language with three tones (high, mid, low) marked by diacritics. The Yoruba people created one of Africa's most sophisticated pre-colonial civilizations centered around Ife, considered the spiritual homeland of the Yoruba.","cultural":"Yoruba religious traditions (Ifá divination system, UNESCO heritage) spread globally through the African diaspora, becoming Candomblé in Brazil, Santería in Cuba, and Vodou in Haiti.","direction":"ltr","official":"Nigeria (one of 3 major national languages)","digital":"Nollywood Yoruba film narration, Yoruba educational content, Ifá cultural preservation audio, and Nigerian broadcasting"},
    "ha-NG": {"script":"Latin (Boko)","script_type":"Alphabet","speakers":"80 million","family":"Afroasiatic (Chadic)","origin":"Hausa is the most widely spoken Chadic language and serves as a lingua franca across West Africa. Historically written in Arabic script (Ajami), modern Hausa uses the Latin-based Boko alphabet standardized by the British in the early 20th century.","cultural":"Hausa is the language of Kannywood (Kano-based film industry), Northern Nigeria's answer to Nollywood, producing hundreds of films annually and creating significant demand for Hausa voiceover content.","direction":"ltr","official":"Nigeria (one of 3 major national languages)","digital":"Kannywood film narration, Hausa broadcasting (BBC Hausa, VOA Hausa), Northern Nigerian educational content, and West African trade communication"},
    "so-SO": {"script":"Latin","script_type":"Alphabet","speakers":"16 million","family":"Afroasiatic (Cushitic)","origin":"Somali was an unwritten language until 1972, when Somalia officially adopted a Latin-based orthography. Before that, Somali oral poetry was the primary literary form, with poets holding the highest social status.","cultural":"Somali poetry is UNESCO-recognized as one of the world's great oral traditions, and the Somali people are sometimes called 'a nation of poets' — making expressive TTS particularly meaningful for Somali content.","direction":"ltr","official":"Somalia, Somaliland, Djibouti","digital":"Somali broadcasting, Somali diaspora community content, Somali educational platforms, and oral poetry preservation audio"},
    "jv-ID": {"script":"Latin","script_type":"Alphabet","speakers":"82 million","family":"Austronesian","origin":"Javanese has the largest number of speakers of any language without official national status. It historically used the Javanese script (Aksara Jawa), derived from Brahmi, and has a complex system of speech levels (ngoko, madya, krama) reflecting social hierarchy.","cultural":"Java's Borobudur temple (world's largest Buddhist monument) and Prambanan temple complex (Hindu) reflect the island's rich cultural heritage, and Javanese wayang (shadow puppetry) is a UNESCO Intangible Cultural Heritage.","direction":"ltr","official":"Java, Indonesia (regional)","digital":"Javanese cultural content, wayang puppet show narration, Javanese educational platforms, and content for the 82 million Javanese speakers on the world's most populated island"},
    "gl-ES": {"script":"Latin","script_type":"Alphabet","speakers":"2.4 million","family":"Romance","origin":"Galician and Portuguese were originally the same language (Galician-Portuguese) until the 14th century, and Galician-Portuguese was the language of medieval Iberian lyric poetry (cantigas), considered among the finest in European literary history.","cultural":"Galicia's Santiago de Compostela is the endpoint of the famous Camino de Santiago pilgrimage route walked by 400,000+ pilgrims annually, creating demand for Galician-language pilgrimage audio guides.","direction":"ltr","official":"Galicia, Spain (co-official with Spanish)","digital":"Galician broadcasting (TVG), Santiago pilgrimage narration, Galician cultural content, and Galician language preservation platforms"},
    "eu-ES": {"script":"Latin","script_type":"Alphabet","speakers":"750,000","family":"Language isolate","origin":"Basque (Euskara) is Europe's only surviving pre-Indo-European language, completely unrelated to any other known language on Earth. Its origins predate the arrival of Indo-European languages by thousands of years, making it a linguistic mystery.","cultural":"Basque culture includes unique traditions like stone-lifting competitions (harrijasotzaile), pelota sports, and the Basque Gastronomic Society tradition — Basque cuisine has the highest concentration of Michelin stars per capita globally.","direction":"ltr","official":"Basque Country, Navarre (Spain); French Basque Country","digital":"Basque broadcasting (ETB), Basque gastronomy content, Basque language education (ikastola), and Basque cultural preservation audio"},
    "hy-AM": {"script":"Armenian","script_type":"Alphabet","speakers":"6 million","family":"Armenian (Indo-European)","origin":"The Armenian alphabet was created by Mesrop Mashtots in 405 CE specifically to translate the Bible into Armenian. It is unique among alphabets — linguists believe Mashtots designed each letter based on his deep understanding of Armenian phonology.","cultural":"Armenia was the first nation to adopt Christianity as a state religion (301 CE), and Armenian illuminated manuscripts and stone cross carvings (khachkars) are UNESCO-recognized cultural treasures.","direction":"ltr","official":"Armenia","digital":"Armenian broadcasting, Armenian diaspora content (8+ million Armenian diaspora worldwide), Armenian educational platforms, and cultural heritage narration"},
    "tk-TM": {"script":"Latin","script_type":"Alphabet","speakers":"7 million","family":"Turkic","origin":"Turkmen switched from Arabic to Latin script (1929), then Cyrillic (1940), and back to a modified Latin alphabet after independence (1993). Turkmen is closely related to Azerbaijani and Turkish.","cultural":"Turkmenistan is home to the Akhal-Teke horse breed, considered the most beautiful horse in the world, and the Darvaza gas crater ('Door to Hell') draws adventurous tourists requiring Turkmen-language content.","direction":"ltr","official":"Turkmenistan","digital":"Turkmen broadcasting, Central Asian tourism narration, Turkmen educational content, and cultural preservation audio"},
    "ky-KG": {"script":"Cyrillic","script_type":"Alphabet","speakers":"4.5 million","family":"Turkic","origin":"The Epic of Manas is the Kyrgyz national epic poem — at 500,000+ lines, it is the longest epic poem in the world (20 times longer than the Iliad and Odyssey combined) and is traditionally recited entirely from memory by master storytellers.","cultural":"Kyrgyzstan's nomadic heritage centers around the yurt (boz üy), and the World Nomad Games held in Kyrgyzstan celebrate Central Asian nomadic sports and culture, creating unique content needs.","direction":"ltr","official":"Kyrgyzstan (co-official with Russian)","digital":"Kyrgyz broadcasting, Central Asian nomadic culture content, Kyrgyz educational platforms, and Epic of Manas audio preservation"},
    "nl-BE": {"script":"Latin","script_type":"Alphabet","speakers":"6.5 million","family":"Germanic","origin":"Belgian Dutch (Flemish) has notable pronunciation and vocabulary differences from Netherlands Dutch, though both use the same standard written form. The Flemish Movement for linguistic rights shaped modern Belgium's federal structure.","cultural":"Flanders has a world-renowned art heritage (Van Eyck, Rubens, Bruegel) and Belgian chocolate, beer, and waffle culture creates unique content needs for Flemish-language food and culture narration.","direction":"ltr","official":"Belgium (Flanders region)","digital":"Flemish broadcasting (VRT), Belgian tourism narration, Flemish educational content, and Belgium's bilingual government services"},
    "fr-BE": {"script":"Latin","script_type":"Alphabet","speakers":"4.5 million","family":"Romance","origin":"Belgian French differs from Parisian French in its use of 'septante' (70), 'nonante' (90), and 'octante/huitante' (80), which are actually more logical than France's vigesimal system (soixante-dix, quatre-vingts, quatre-vingt-dix).","cultural":"Brussels, where Belgian French is primarily spoken, is the de facto capital of the European Union, making Belgian French crucial for EU institutional communication and multilingual European content.","direction":"ltr","official":"Belgium (Wallonia, Brussels)","digital":"EU institutional content, Belgian broadcasting (RTBF), Brussels tourism narration, and Belgian educational content"},
    "de-CH": {"script":"Latin","script_type":"Alphabet","speakers":"5.4 million","family":"Germanic","origin":"Swiss German (Schweizerdeutsch) dialects differ so significantly from Standard German that they are often mutually unintelligible — Standard German is learned as almost a foreign language in Swiss schools, creating a unique 'diglossia' situation.","cultural":"Switzerland's multilingualism (German, French, Italian, Romansh) in a small country is a model of linguistic coexistence, and Swiss German is the everyday spoken language while Standard German is used for writing and formal situations.","direction":"ltr","official":"Switzerland (co-official with French, Italian, Romansh)","digital":"Swiss broadcasting (SRF), Swiss tourism narration for Alps and luxury destinations, Swiss financial services content, and Swiss educational platforms"},
    "fr-CH": {"script":"Latin","script_type":"Alphabet","speakers":"2 million","family":"Romance","origin":"Swiss French (Romand) shares Belgian French's logical number system (septante, huitante, nonante) and has unique Swiss vocabulary. Geneva's role as home to UN, WHO, Red Cross, and WTO makes Swiss French important for international diplomacy.","cultural":"Switzerland's French-speaking region (Romandie) hosts the Montreux Jazz Festival, CERN particle physics laboratory, and the International Olympic Committee, creating diverse content needs in Swiss French.","direction":"ltr","official":"Switzerland (co-official with German, Italian, Romansh)","digital":"International organization content (UN Geneva), Swiss French broadcasting (RTS), Montreux tourism narration, and Swiss French educational content"},
    "ar-AE": {"script":"Arabic","script_type":"Abjad","speakers":"10 million","family":"Semitic","origin":"UAE Arabic (Gulf/Khaleeji dialect) reflects the country's transformation from pearl-diving Bedouin communities to a global hub — modern UAE Arabic has absorbed English, Hindi, and Urdu vocabulary reflecting Dubai and Abu Dhabi's cosmopolitan population.","cultural":"The UAE's ambitious cultural projects (Louvre Abu Dhabi, planned Guggenheim) and the world's largest concentration of luxury hospitality drive massive demand for Arabic-language tourism and business content.","direction":"rtl","official":"United Arab Emirates","digital":"UAE corporate communications, Dubai/Abu Dhabi luxury tourism narration, Middle Eastern broadcasting, and Arabic e-commerce content for the Gulf market"},
    "ar-MA": {"script":"Arabic","script_type":"Abjad","speakers":"37 million","family":"Semitic","origin":"Moroccan Arabic (Darija) is the most divergent Arabic dialect from Modern Standard Arabic, incorporating substantial Berber (Amazigh), French, and Spanish vocabulary — making it often incomprehensible to speakers of Eastern Arabic dialects.","cultural":"Morocco's imperial cities (Marrakech, Fez, Meknes, Rabat) and Saharan landscapes draw 13+ million tourists annually, and Moroccan Arabic's unique blend of Arabic, Amazigh, and French reflects the country's rich multicultural heritage.","direction":"rtl","official":"Morocco (co-official with Amazigh)","digital":"Moroccan broadcasting, Sahara and Atlas tourism narration, Moroccan French-Arabic bilingual content, and North African cultural audio"},
}


def generate_rich_seo_content(lang_name, country, native_name, code, voice_count):
    """Generate 500+ word truly unique SEO article for each language page."""
    facts = LANGUAGE_FACTS.get(code, {})
    if not facts:
        # Fallback for any language not in LANGUAGE_FACTS
        return f"""
        <h3>About {lang_name} Text to Speech</h3>
        <p>{lang_name}, known natively as {native_name}, is spoken primarily in {country}. VoicePro provides advanced neural AI voices for {lang_name}, enabling high-quality text-to-speech conversion for content creators, educators, and businesses. Our {lang_name} TTS technology captures the natural pronunciation, rhythm, and intonation patterns specific to {country}, delivering professional-grade audio output.</p>
        <h3>Why Use {lang_name} TTS for Content Creation?</h3>
        <p>With growing digital content consumption in {country}, {lang_name} voiceover content is in higher demand than ever. VoicePro's neural voices support instant MP3 and WAV downloads, allowing creators to produce {lang_name} audio for YouTube videos, podcasts, e-learning modules, audiobooks, and social media content without expensive voice actors or studio equipment.</p>
        """

    script = facts.get("script", "")
    script_type = facts.get("script_type", "")
    speakers = facts.get("speakers", "millions of")
    family = facts.get("family", "")
    origin = facts.get("origin", "")
    cultural = facts.get("cultural", "")
    direction = facts.get("direction", "ltr")
    official = facts.get("official", country)
    digital = facts.get("digital", f"{lang_name} content creation")

    # Use code hash to pick different template orderings
    seed = sum(ord(c) for c in code) % 6

    para_history = f"{lang_name}, known natively as <strong>{native_name}</strong>, belongs to the <em>{family}</em> language family and is written in the <strong>{script}</strong> script — a {script_type.lower()} writing system that {'reads from right to left' if direction == 'rtl' else 'reads from left to right'}. With approximately <strong>{speakers} speakers</strong>, {lang_name} serves as an official language of <strong>{official}</strong>. {origin}"

    para_culture = f"{cultural} This rich cultural and linguistic heritage makes authentic {lang_name} voice synthesis not just a technical achievement, but a meaningful tool for cultural preservation and digital accessibility."

    para_tts = f"VoicePro's {lang_name} text-to-speech engine leverages Microsoft's advanced neural TTS technology, specifically optimized for the phonological patterns of {lang_name} as spoken in {country}. Unlike generic TTS tools that produce robotic output, our AI models are trained on native {lang_name} speaker data to capture authentic pronunciation, natural intonation contours, regional prosody, and the subtle rhythmic patterns that distinguish fluent {lang_name} speech. The result is audio that sounds genuinely human — indistinguishable from a professional {lang_name} voice actor in many contexts."

    para_digital = f"The demand for high-quality {lang_name} audio content continues to accelerate across multiple industries. Key use cases include: <strong>{digital}</strong>. Whether you are a solo content creator producing YouTube videos, a corporate training department building multilingual e-learning modules, or a media company localizing content for {country}'s market, VoicePro provides the professional {lang_name} voice generation you need — completely free, with no login required."

    para_tech = f"Our {lang_name} TTS studio offers comprehensive voice customization: adjust speaking speed from 0.5x to 2x, modify pitch from -10 to +10 semitones, select from {voice_count}+ neural voice characters (male, female, young, mature, professional), and generate both MP3 (compressed, ideal for web and podcasts) and WAV (uncompressed, ideal for professional production) audio formats. The multi-voice dialogue generator enables you to create realistic {lang_name} conversations with distinct speakers — perfect for podcast production, educational dialogues, and dramatic narration."

    para_why = f"What sets VoicePro apart for {lang_name} TTS? Three key advantages: <strong>Zero cost</strong> — no subscription, no credit limits, no hidden fees. <strong>Zero registration</strong> — no account creation, no email verification, no data collection. <strong>Maximum quality</strong> — the same Microsoft Azure Neural engine used by enterprise applications, available to every {lang_name} speaker for free. Your text is processed on-demand and never stored, ensuring complete privacy for sensitive content."

    # Rotate paragraph order based on language code to make each page structurally different
    orders = [
        [para_history, para_culture, para_tts, para_digital, para_tech, para_why],
        [para_tts, para_history, para_digital, para_culture, para_why, para_tech],
        [para_culture, para_tts, para_history, para_why, para_digital, para_tech],
        [para_digital, para_history, para_tech, para_tts, para_culture, para_why],
        [para_history, para_tts, para_culture, para_tech, para_why, para_digital],
        [para_tech, para_culture, para_digital, para_history, para_why, para_tts],
    ]

    titles = [
        [f"The {lang_name} Language — History & Heritage", f"{lang_name} in Culture & Society", f"Neural {lang_name} Voice Technology", f"{lang_name} Digital Content Landscape", f"Voice Customization for {lang_name}", f"Why Choose VoicePro for {lang_name}?"],
        [f"Advanced {lang_name} Neural TTS", f"Origins of {lang_name}", f"Growing Demand for {lang_name} Audio", f"Cultural Significance of {lang_name}", f"Free {lang_name} TTS — No Strings Attached", f"Professional {lang_name} Voice Controls"],
        [f"{lang_name} — A Cultural Treasure", f"Neural Voice Synthesis for {lang_name}", f"History of the {lang_name} Language", f"VoicePro's Free Promise", f"{lang_name} Audio in the Digital Age", f"Studio-Grade {lang_name} Controls"],
        [f"The {lang_name} Content Opportunity", f"Where {lang_name} Comes From", f"Fine-Tune Your {lang_name} Voice", f"How VoicePro's {lang_name} AI Works", f"{lang_name} Beyond Language", f"Truly Free {lang_name} TTS"],
        [f"Understanding {lang_name}", f"State-of-the-Art {lang_name} TTS", f"The Soul of {lang_name}", f"Customize Every Detail", f"No Cost, No Compromise", f"Creating {lang_name} Audio Content"],
        [f"Professional {lang_name} Voice Studio", f"The World of {lang_name}", f"Who Needs {lang_name} Audio?", f"Roots of {lang_name}", f"Why Free Matters", f"From Text to {lang_name} Speech"],
    ]

    selected_paras = orders[seed]
    selected_titles = titles[seed]

    html_parts = []
    for i, (title, para) in enumerate(zip(selected_titles, selected_paras)):
        top_margin = "28px" if i > 0 else "0"
        html_parts.append(f'<h3 style="font-family:Syne,sans-serif;font-weight:700;font-size:1.1rem;margin:{top_margin} 0 12px;color:var(--txt);">{title}</h3>')
        html_parts.append(f'<p style="color:var(--txt2);font-size:.92rem;line-height:1.85;margin-bottom:8px;">{para}</p>')

    return "\n      ".join(html_parts)


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

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  :root{{--bg:#d8dee9;--card:#ffffff;--border:rgba(15,23,42,0.12);--borderH:rgba(59,158,255,0.4);--a1:#1d4ed8;--a2:#6d28d9;--a3:#db2777;--txt:#0f172a;--txt2:#334155;--muted:#64748b;--panel:#edf2f7;--ok:#10b981;--grid-line:rgba(0,0,0,0.02);--shadow:0 10px 30px -5px rgba(0,0,0,0.04),0 8px 16px -6px rgba(0,0,0,0.04);--nav-bg:#ffffff;}}
  [data-theme="dark"]{{--bg:#070b12;--card:rgba(255,255,255,0.032);--border:rgba(255,255,255,0.07);--borderH:rgba(59,158,255,0.38);--a1:#3b9eff;--a2:#7c5fe6;--a3:#e94fa3;--txt:#dde4f0;--txt2:#b8c4d8;--muted:#6e7e98;--panel:#0c1220;--ok:#3dd68c;--grid-line:rgba(255,255,255,0.012);--shadow:none;--nav-bg:#070b12;}}
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
  html{{scroll-behavior:smooth;}}
  body{{background:var(--bg);color:var(--txt);font-family:'DM Sans',sans-serif;min-height:100vh;display:flex;flex-direction:column;-webkit-font-smoothing:antialiased;overflow-x:hidden;width:100%;max-width:100vw;}}
  body::before{{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse 80% 50% at 20% 10%,rgba(59,158,255,0.055) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 80% 80%,rgba(124,95,230,0.045) 0%,transparent 60%),repeating-linear-gradient(0deg,transparent,transparent 63px,var(--grid-line) 64px),repeating-linear-gradient(90deg,transparent,transparent 63px,var(--grid-line) 64px);}}
  body>*{{position:relative;z-index:1;}}
  h1,h2,h3,h4,h5{{font-family:'Syne',sans-serif;letter-spacing:-0.02em;line-height:1.15;}}
  .tg{{background:linear-gradient(130deg,var(--a1) 0%,var(--a2) 50%,var(--a3) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
  .mono{{font-family:'Space Mono',monospace;}}
  .glass-nav{{background:var(--nav-bg);backdrop-filter:blur(24px);border-bottom:1px solid var(--border);opacity:0.96;}}
  .nav-btn{{padding:7px 14px;border-radius:10px;font-size:.85rem;font-weight:500;transition:all .18s;color:var(--muted);border:none;background:transparent;cursor:pointer;font-family:'DM Sans',sans-serif;text-decoration:none;display:inline-block;}}
  .nav-btn:hover,.nav-active{{color:var(--a1);background:rgba(59,158,255,0.09);}}
  .glass{{background:var(--card);backdrop-filter:blur(16px);border:1px solid var(--border);border-radius:22px;box-shadow:var(--shadow);width:100%;max-width:100%;box-sizing:border-box;}}
  .gcard{{background:var(--card);border:1px solid var(--border);border-radius:16px;box-shadow:var(--shadow);transition:border-color .25s,box-shadow .25s,transform .2s;}}
  .gcard:hover{{border-color:var(--borderH);box-shadow:0 0 28px rgba(59,158,255,0.08);transform:translateY(-1px);}}
  .ctrl{{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:14px 16px;width:100%;box-sizing:border-box;}}
  .btn-primary{{background:linear-gradient(135deg,var(--a1),var(--a2),var(--a3));background-size:220%;border:none;border-radius:14px;color:#fff;font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;letter-spacing:0.02em;padding:15px 28px;cursor:pointer;width:100%;transition:background-position .45s,transform .15s,box-shadow .3s;box-shadow:0 4px 28px rgba(59,158,255,0.24);}}
  .btn-primary:hover{{background-position:right;box-shadow:0 6px 36px rgba(59,158,255,0.4);}}
  .btn-primary:active{{transform:scale(.976);}}
  .btn-primary:disabled{{opacity:.5;cursor:not-allowed;transform:none;}}
  textarea{{background:var(--panel);border:1.5px solid var(--border);border-radius:14px;color:var(--txt);font-family:'DM Sans',sans-serif;font-size:.96rem;line-height:1.65;padding:14px 18px 24px;width:100%;max-width:100%;outline:none;resize:none;transition:border-color .2s,box-shadow .2s;min-height:120px;max-height:400px;overflow-y:auto;box-sizing:border-box;}}
  textarea:focus{{border-color:var(--a1);box-shadow:0 0 0 3px rgba(59,158,255,0.13);}}
  textarea::placeholder{{color:var(--muted);}}
  select{{appearance:none;background:var(--panel);border:1px solid var(--border);border-radius:12px;color:var(--txt);font-family:'DM Sans',sans-serif;font-size:.9rem;padding:11px 36px 11px 14px;outline:none;cursor:pointer;width:100%;max-width:100%;text-overflow:ellipsis;white-space:nowrap;overflow:hidden;box-sizing:border-box;transition:border-color .2s;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='11' height='11' viewBox='0 0 12 12'%3E%3Cpath fill='%236e7e98' d='M6 8L1 3h10z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;}}
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
  .feature-card{{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:26px;transition:border-color .25s,box-shadow .25s,transform .2s;width:100%;box-sizing:border-box;}}
  .feature-card:hover{{border-color:var(--borderH);box-shadow:0 0 24px rgba(59,158,255,0.07);transform:translateY(-2px);}}
  .feature-icon{{width:46px;height:46px;border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:1.25rem;margin-bottom:16px;}}
  .lang-badge{{display:inline-block;background:rgba(59,158,255,0.09);border:1px solid rgba(59,158,255,0.18);border-radius:100px;padding:5px 14px;font-size:.8rem;color:var(--a1);margin:4px;font-weight:600;text-decoration:none;transition:all .2s;}}
  .lang-badge:hover{{background:rgba(59,158,255,0.18);transform:translateY(-1px);box-shadow:0 2px 10px rgba(59,158,255,0.15);}}
  .section-divider{{display:flex;align-items:center;gap:16px;margin-bottom:48px;}}
  .section-divider::before,.section-divider::after{{content:'';flex:1;height:1px;background:linear-gradient(90deg,transparent,var(--border),transparent);}}
  .section-label{{font-family:'Syne',sans-serif;font-size:.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);white-space:nowrap;}}
  .pro-footer{{background:rgba(5,8,14,0.97);border-top:1px solid var(--border);padding:52px 24px 0;margin-top:auto;width:100%;box-sizing:border-box;}}
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
  .stats-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;width:100%;box-sizing:border-box;}}
  .inputs-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:18px;width:100%;box-sizing:border-box;}}
  .controls-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px;width:100%;box-sizing:border-box;}}
  .options-grid{{display:grid;grid-template-columns:2fr 1fr;gap:12px;margin-bottom:24px;width:100%;box-sizing:border-box;}}
  .multi-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-bottom:18px;width:100%;box-sizing:border-box;}}
  .footer-grid{{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:40px;padding-bottom:44px;border-bottom:1px solid var(--border);width:100%;box-sizing:border-box;}}
  
  /* ═══ GLOBAL RESPONSIVE HELPERS ═══ */
  section,div,.glass,.gcard,.ctrl{{overflow-wrap:break-word;word-wrap:break-word;}}
  img,video,iframe{{max-width:100%;}}
  .resp-table-wrap{{display:block;overflow-x:auto;-webkit-overflow-scrolling:touch;width:100%;box-sizing:border-box;border-radius:18px;}}
  .resp-table-wrap table{{min-width:600px;max-width:none;width:100%;}}
  .resp-table-wrap td,.resp-table-wrap th{{padding:10px 14px;font-size:.82rem;white-space:nowrap;}}

  /* ═══ RESPONSIVENESS FIXES ═══ */
  @media(max-width:900px){{
    .options-grid{{grid-template-columns:1fr 1fr;}}
  }}
  @media(max-width:768px){{
    .nav-desktop{{display:none!important;}}
    .nav-mobile-btn{{display:flex!important;align-items:center;justify-content:center;background:none;border:none;color:var(--muted);font-size:1.25rem;cursor:pointer;}}
    .nav-mobile-menu.active{{display:flex!important;flex-direction:column;gap:6px;background:var(--bg);border-top:1px solid var(--border);padding:14px 24px;position:absolute;top:60px;left:0;right:0;z-index:100;box-shadow:0 10px 15px -3px rgba(0,0,0,0.05);}}
    .nav-mobile-menu .nav-btn{{display:block;padding:10px 14px;text-align:left;border-radius:9px;width:100%;box-sizing:border-box;}}
    .footer-grid{{grid-template-columns:1fr 1fr;gap:28px;}}
    .stats-grid{{grid-template-columns:1fr;gap:10px;}}
    .controls-grid{{grid-template-columns:repeat(2,1fr);gap:10px;}}
    .options-grid{{grid-template-columns:1fr;gap:12px;}}
    .inputs-grid, .multi-grid{{grid-template-columns:1fr;gap:12px;}}
    h1{{font-size:1.6rem!important;}}
    h2{{font-size:1.2rem!important;}}
    h3{{font-size:1.05rem!important;}}
    .badge-pill{{font-size:.65rem!important;padding:4px 10px!important;}}
  }}
  @media(max-width:640px){{
    .controls-grid{{grid-template-columns:1fr;gap:10px;}}
    .inputs-grid, .multi-grid, .options-grid{{grid-template-columns:1fr;gap:12px;}}
    .glass{{padding:18px!important;border-radius:16px;}}
    .pro-footer{{padding:32px 14px 0!important;}}
    .faq-q{{padding:14px 16px;font-size:.88rem;}}
    .faq-item.open .faq-a{{padding:0 16px 16px;}}
    .feature-card{{padding:18px;border-radius:14px;}}
  }}
  @media(max-width:480px){{
    .glass{{border-radius:14px;padding:14px!important;}}
    .footer-grid{{grid-template-columns:1fr;gap:20px;}}
    .btn-primary{{padding:12px 14px;font-size:.88rem;border-radius:12px;}}
    .tab-btn{{padding:8px 10px;font-size:.78rem;}}
    .dl-tab{{padding:8px 6px;font-size:.72rem;}}
    .ctrl{{padding:10px 12px;border-radius:10px;}}
    .slbl{{font-size:.62rem;letter-spacing:1px;}}
    .nav-mobile-menu.active{{padding:10px 16px;}}
    .statc{{padding:12px;border-radius:12px;}}
    .toast{{bottom:12px;right:12px;left:12px;max-width:none;font-size:.8rem;padding:10px 14px;}}
    select{{font-size:.82rem;padding:9px 30px 9px 10px;}}
    textarea{{font-size:.88rem;padding:10px 12px 18px;min-height:100px;}}
  }}
  @media(max-width:360px){{
    .glass{{padding:10px!important;border-radius:12px;}}
    h1{{font-size:1.35rem!important;}}
    h2{{font-size:1.05rem!important;}}
    .btn-primary{{padding:11px 10px;font-size:.82rem;}}
    .badge-pill{{font-size:.6rem!important;padding:3px 8px!important;letter-spacing:.3px;}}
    .feature-card{{padding:14px;}}
    .feature-icon{{width:38px;height:38px;font-size:1rem;}}
    .pro-footer{{padding:24px 10px 0!important;}}
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
      <a href="/about" class="nav-btn"><i class="fa-solid fa-circle-info" style="margin-right:5px;"></i>About</a>
      <a href="/blog" class="nav-btn"><i class="fa-solid fa-newspaper" style="margin-right:5px;"></i>Blog</a>
      <a href="/tts/" class="nav-btn nav-active"><i class="fa-solid fa-globe" style="margin-right:5px;"></i>Languages</a>
      <a href="/contact" class="nav-btn"><i class="fa-solid fa-headset" style="margin-right:5px;"></i>Contact</a>
      <a href="/privacy" class="nav-btn"><i class="fa-solid fa-shield-halved" style="margin-right:5px;"></i>Privacy</a>
      <a href="/terms" class="nav-btn"><i class="fa-solid fa-file-contract" style="margin-right:5px;"></i>Terms</a>
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
    <a href="/about" class="nav-btn"><i class="fa-solid fa-circle-info" style="margin-right:8px;"></i>About</a>
    <a href="/blog" class="nav-btn"><i class="fa-solid fa-newspaper" style="margin-right:8px;"></i>Blog</a>
    <a href="/tts/" class="nav-btn nav-active"><i class="fa-solid fa-globe" style="margin-right:8px;"></i>All Languages TTS</a>
    <a href="/contact" class="nav-btn"><i class="fa-solid fa-headset" style="margin-right:8px;"></i>Contact</a>
    <a href="/privacy" class="nav-btn"><i class="fa-solid fa-shield-halved" style="margin-right:8px;"></i>Privacy Policy</a>
    <a href="/terms" class="nav-btn"><i class="fa-solid fa-file-contract" style="margin-right:8px;"></i>Terms of Service</a>
    <a href="/disclaimer" class="nav-btn"><i class="fa-solid fa-triangle-exclamation" style="margin-right:8px;"></i>Disclaimer</a>
    <a href="/cookies" class="nav-btn"><i class="fa-solid fa-cookie-bite" style="margin-right:8px;"></i>Cookie Policy</a>
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
      FREE {lang_name} TEXT TO SPEECH 2026 &nbsp;&#8226;&nbsp; 30+ Neural Voices for {lang_name} ({country}) &nbsp;&#8226;&nbsp; Instant MP3 &amp; WAV Download Free &nbsp;&#8226;&nbsp; Multi-Voice Dialogue Generator &nbsp;&#8226;&nbsp; Zero Login &nbsp;&#8226;&nbsp; 104 Languages Supported
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
    Convert {lang_name} text to natural speech free online. 30+ neural AI voices for {country}. Instant MP3/WAV download. Best free {lang_name} TTS tool 2026.
  </p>
  <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:0;">
    <span style="background:rgba(61,214,140,0.1);border:1px solid rgba(61,214,140,0.2);color:var(--ok);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-check" style="margin-right:5px;"></i>100% Free</span>
    <span style="background:rgba(59,158,255,0.1);border:1px solid rgba(59,158,255,0.2);color:var(--a1);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-bolt" style="margin-right:5px;"></i>Instant MP3</span>
    <span style="background:rgba(124,95,230,0.1);border:1px solid rgba(124,95,230,0.2);color:var(--a2);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-robot" style="margin-right:5px;"></i>30+ Neural Voices</span>
    <span style="background:rgba(233,79,163,0.1);border:1px solid rgba(233,79,163,0.2);color:var(--a3);border-radius:100px;padding:5px 16px;font-size:.8rem;font-weight:600;"><i class="fa-solid fa-user-slash" style="margin-right:5px;"></i>No Login</span>
  </div>
</section>

{regional_seo_html}

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
              <option value="female-4">Female 4 - Warm</option>
              <option value="female-5">Female 5 - Crisp</option>
              <option value="male-1">Male 1 - Deep</option>
              <option value="male-2">Male 2 - Friendly</option>
              <option value="male-3">Male 3 - Authority</option>
              <option value="male-4">Male 4 - Warm</option>
              <option value="male-5">Male 5 - Crisp</option>
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
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));gap:18px;margin-bottom:56px;">
      <div class="feature-card"><div class="feature-icon" style="background:rgba(59,158,255,0.12);">&#129504;</div><h3 style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">{lang_name}-Native Neural Voices</h3><p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Voices trained specifically on {lang_name} ({country}) native speaker data &mdash; correct pronunciation, natural intonation, authentic regional accent.</p></div>
      <div class="feature-card"><div class="feature-icon" style="background:rgba(61,214,140,0.12);">&#128229;</div><h3 style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">Instant MP3 / WAV Download</h3><p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">No queues, no waiting. Generate up to 5,000 characters in seconds. Download MP3 for web or WAV for studio-quality production.</p></div>
      <div class="feature-card"><div class="feature-icon" style="background:rgba(124,95,230,0.12);">&#127931;</div><h3 style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">Full Voice Customization</h3><p style="color:var(--txt2);font-size:.88rem;line-height:1.78;">Adjust speed (0.5x&ndash;2x), pitch (&minus;10 to +10), volume, and speaking style. 30+ unique voice characters across all ages.</p></div>
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

{deep_seo_html}
{cross_links_html}

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
      <a href="/about" class="footer-link">About Us</a>
      <a href="/blog" class="footer-link">Blog</a>
      <a href="/tts/" class="footer-link">All Languages</a>
    </div>
    <div>
      <p class="footer-heading">Support</p>
      <a href="/contact" class="footer-link">Contact Support</a>
      <a href="/disclaimer" class="footer-link">AI Disclaimer</a>
      <a href="/cookies" class="footer-link">Cookie Policy</a>
    </div>
    <div>
      <p class="footer-heading">Legal</p>
      <a href="/privacy" class="footer-link">Privacy Policy</a>
      <a href="/terms" class="footer-link">Terms of Service</a>
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
<!-- Cookie Consent Banner -->
<div id="cookie-consent" style="display:none;position:fixed;bottom:0;left:0;right:0;z-index:10000;background:rgba(7,11,18,0.97);backdrop-filter:blur(12px);border-top:1px solid rgba(59,158,255,0.15);padding:18px 24px;">
  <div style="max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;">
    <p style="color:#dde4f0;font-size:.85rem;line-height:1.6;margin:0;flex:1;min-width:280px;font-family:'DM Sans',sans-serif;">🍪 We use cookies for analytics and personalized advertising (Google AdSense). By continuing to use this site, you consent to our use of cookies. <a href="/privacy.html" style="color:#3b9eff;text-decoration:underline;">Learn more</a></p>
    <div style="display:flex;gap:10px;flex-shrink:0;">
      <button onclick="acceptCookies()" style="padding:9px 22px;background:linear-gradient(135deg,#1d4ed8,#6d28d9);color:#fff;border:none;border-radius:10px;font-family:'Syne',sans-serif;font-weight:700;font-size:.82rem;cursor:pointer;transition:all .2s;">Accept All</button>
      <button onclick="rejectCookies()" style="padding:9px 22px;background:transparent;color:#b8c4d8;border:1px solid rgba(255,255,255,0.15);border-radius:10px;font-family:'Syne',sans-serif;font-weight:600;font-size:.82rem;cursor:pointer;transition:all .2s;">Reject Non-Essential</button>
    </div>
  </div>
</div>
<script>
function acceptCookies(){{localStorage.setItem('cookie_consent','accepted');document.getElementById('cookie-consent').style.display='none';}}
function rejectCookies(){{localStorage.setItem('cookie_consent','rejected');document.getElementById('cookie-consent').style.display='none';}}
(function(){{if(!localStorage.getItem('cookie_consent')){{document.getElementById('cookie-consent').style.display='block';}}}}());
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
    meta_desc  = (f"Convert {lang_name} text to speech free online. 30+ neural AI voices for {country}. "
                  f"Instant MP3/WAV download, no login. Best {lang_name} TTS tool 2026.")
    meta_kw    = (f"{lang_name.lower()} text to speech, {lang_name.lower()} text to voice, {lang_name.lower()} tts, {lang_name.lower()} voice generator, "
                  f"free {lang_name.lower()} tts {country.lower()}, {lang_name.lower()} ai voice, "
                  f"{native_name} text to speech, {code} tts, free tts {country.lower()}, text to voice, text to speech")
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
<section style="max-width:920px;margin:0 auto 56px;padding:0 18px;overflow:hidden;width:100%;box-sizing:border-box;">
  <h2 style="font-size:clamp(1.4rem,3vw,1.9rem);font-weight:800;margin-bottom:8px;text-align:center;">
    Available <span class="tg">{lang_name} Voice Profiles</span>
  </h2>
  <p style="text-align:center;color:var(--muted);font-size:.9rem;margin-bottom:24px;">Explore the full list of neural voice models available for {lang_name} ({country}) speech generation.</p>
  
  <div style="width:100%;max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:10px;">
    <div style="background:var(--card);border:1px solid var(--border);border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,0.02);min-width:600px;">
      <table style="width:100%;border-collapse:collapse;text-align:left;font-size:.88rem;color:var(--txt);">
        <thead>
          <tr style="border-bottom:1px solid var(--border);background:rgba(255,255,255,0.015);">
            <th style="padding:14px 18px;font-weight:700;color:var(--muted);font-family:'Syne',sans-serif;white-space:nowrap;">Voice Character</th>
            <th style="padding:14px 18px;font-weight:700;color:var(--muted);font-family:'Syne',sans-serif;white-space:nowrap;">Gender / Age</th>
            <th style="padding:14px 18px;font-weight:700;color:var(--muted);font-family:'Syne',sans-serif;white-space:nowrap;">Neural Model ID</th>
            <th style="padding:14px 18px;font-weight:700;color:var(--muted);font-family:'Syne',sans-serif;white-space:nowrap;">Mapping Type</th>
          </tr>
        </thead>
        <tbody>
          {voices_rows_html}
        </tbody>
      </table>
    </div>
  </div>
</section>"""

    # Build all-languages dropdown options (for language switcher)
    all_languages_options = "\n".join(
        f'<option value="{e[0]}"{" selected" if e[0] == code else ""}>{e[1]} ({e[2]})</option>'
        for e in LANGUAGES
    )

    STATE_MAP = {
        "mr-IN": "Maharashtra",
        "gu-IN": "Gujarat",
        "ta-IN": "Tamil Nadu",
        "te-IN": "Andhra Pradesh and Telangana",
        "kn-IN": "Karnataka",
        "ml-IN": "Kerala",
        "bn-IN": "West Bengal",
        "pa-IN": "Punjab",
        "or-IN": "Odisha",
        "hi-IN": "Northern and Central India",
        "ur-PK": "Punjab and Sindh",
        "zh-CN": "Mainland China",
        "zh-TW": "Taiwan",
        "zh-HK": "Hong Kong",
    }
    state_region = STATE_MAP.get(code, "")
    region_display = f"{state_region}, {country}" if state_region else country

    regional_seo_html = f"""
<!-- REGIONAL SEO BLOCK -->
<section style="max-width:860px;margin:0 auto 32px;padding:0 18px;">
  <div style="background:linear-gradient(145deg, rgba(59,158,255,0.03), rgba(124,95,230,0.03));border:1px solid rgba(124,95,230,0.15);border-radius:18px;padding:28px 24px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.01);">
    <h3 style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.3rem;color:var(--txt);margin-bottom:12px;">
      <i class="fa-solid fa-earth-asia" style="color:var(--a1);margin-right:8px;"></i>
      Optimized for {lang_name} Speakers in {region_display}
    </h3>
    <p style="color:var(--txt2);font-size:.95rem;line-height:1.7;max-width:700px;margin:0 auto;">
      Experience authentic pronunciation and natural intonation tailored for <strong>{lang_name}</strong> as spoken natively in <strong>{region_display}</strong>. Perfect for localized marketing, regional content creation, and professional e-learning modules. VoicePro's advanced neural AI guarantees maximum local engagement and professional audio quality.
    </p>
  </div>
</section>
"""

    # Generate rich unique SEO content (500+ words per language)
    rich_seo_content = generate_rich_seo_content(lang_name, country, native_name, code, voice_count)

    deep_seo_html = f"""
<!-- DEEP SEO CONTENT - UNIQUE PER LANGUAGE -->
<section style="max-width:860px;margin:0 auto 40px;padding:0 18px;">
  <div style="background:var(--panel);border:1px solid var(--border);border-radius:18px;padding:32px 28px;">
    <h2 style="font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(1.3rem,2.5vw,1.7rem);color:var(--txt);margin-bottom:24px;display:flex;align-items:center;gap:10px;">
      <i class="fa-solid fa-book-open" style="color:var(--a2);"></i>
      About {lang_name} ({native_name}) Text to Speech
    </h2>
    <div style="color:var(--txt2);font-size:.92rem;line-height:1.85;">
      {rich_seo_content}
    </div>
  </div>
</section>
"""

    # Build lang->slug map for JS redirect
    lang_slug_map = {e[0]: slug(e[0]) for e in LANGUAGES}
    lang_slug_map_json = json.dumps(lang_slug_map, ensure_ascii=False)

    # ── Cross-Links: Same Country + Popular Global Languages ──────
    # Group languages by country
    same_country = [e for e in LANGUAGES if e[2] == country and e[0] != code]
    
    # Popular global languages (always show these as fallback)
    popular_codes = [
        "hi-IN", "en-US", "es-ES", "fr-FR", "de-DE", "ja-JP",
        "zh-CN", "ko-KR", "ar-SA", "pt-BR", "ru-RU", "it-IT",
        "tr-TR", "vi-VN", "th-TH", "id-ID", "nl-NL", "pl-PL",
        "sv-SE", "uk-UA"
    ]
    popular = [e for e in LANGUAGES if e[0] in popular_codes and e[0] != code]
    
    # Remove duplicates (if same-country lang is also in popular list)
    same_country_codes = {e[0] for e in same_country}
    popular_unique = [e for e in popular if e[0] not in same_country_codes]
    
    # Build cross-links HTML
    pill_style = 'padding:6px 14px;background:var(--panel);border:1px solid var(--border);border-radius:20px;font-size:.82rem;color:var(--txt2);text-decoration:none;transition:all .2s;white-space:nowrap;'
    
    cross_parts = []
    
    if same_country:
        cross_parts.append(f'<h4 style="font-family:\'Syne\',sans-serif;font-weight:700;font-size:.95rem;color:var(--a1);margin:0 0 12px;">🏠 More Languages in {country}</h4>')
        cross_parts.append('<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px;">')
        for e in same_country:
            s = slug(e[0])
            cross_parts.append(f'<a href="/tts/{s}" style="{pill_style}">{e[3]} {e[1]} ({e[2]})</a>')
        cross_parts.append('</div>')
    
    cross_parts.append('<h4 style="font-family:\'Syne\',sans-serif;font-weight:700;font-size:.95rem;color:var(--a2);margin:0 0 12px;">🌍 Popular Languages Worldwide</h4>')
    cross_parts.append('<div style="display:flex;flex-wrap:wrap;gap:8px;">')
    for e in popular_unique[:15]:
        s = slug(e[0])
        cross_parts.append(f'<a href="/tts/{s}" style="{pill_style}">{e[3]} {e[1]} ({e[2]})</a>')
    cross_parts.append('</div>')
    
    cross_links_inner = '\n      '.join(cross_parts)
    
    cross_links_html = f"""
<!-- CROSS-LINKS: RELATED LANGUAGES -->
<section style="max-width:860px;margin:0 auto 40px;padding:0 18px;">
  <div style="background:var(--card);border:1px solid var(--border);border-radius:18px;padding:28px 24px;">
    <h3 style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;color:var(--txt);margin-bottom:20px;display:flex;align-items:center;gap:10px;">
      <i class="fa-solid fa-language" style="color:var(--a1);"></i>
      Explore More Languages
    </h3>
    <div>
      {cross_links_inner}
    </div>
    <div style="text-align:center;margin-top:20px;">
      <a href="/tts/" style="display:inline-flex;align-items:center;gap:8px;padding:10px 24px;background:linear-gradient(135deg,var(--a1),var(--a2));color:#fff;border-radius:12px;font-family:'Syne',sans-serif;font-weight:700;font-size:.88rem;text-decoration:none;transition:all .2s;">
        <i class="fa-solid fa-globe"></i> View All 104 Languages
      </a>
    </div>
  </div>
</section>
"""

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
        regional_seo_html=regional_seo_html,
        deep_seo_html=deep_seo_html,
        cross_links_html=cross_links_html,
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
