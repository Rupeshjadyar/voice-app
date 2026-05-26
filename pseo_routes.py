"""
VoicePro pSEO – Flask Routes + Sitemap
Add these routes to your existing app.py
"""

# ─────────────────────────────────────────────────────────────
#  PASTE THIS BLOCK INTO app.py  (before the  if __name__ == '__main__':  line)
# ─────────────────────────────────────────────────────────────

PSEO_ROUTES_CODE = '''
import json, os
from flask import render_template

# ── Load pSEO manifest once at startup ──────────────────────────────────
_PSEO_MANIFEST = []
_manifest_path = os.path.join(os.path.dirname(__file__), 'templates', 'tts_manifest.json')
if os.path.exists(_manifest_path):
    with open(_manifest_path, encoding='utf-8') as f:
        _PSEO_MANIFEST = json.load(f)
    print(f"✅ pSEO manifest loaded: {len(_PSEO_MANIFEST)} language pages")
else:
    print("⚠️  tts_manifest.json not found — run generate_pseo_pages.py first")


# ── Individual language TTS page ─────────────────────────────────────────
@app.route('/tts/<slug>')
def tts_lang_page(slug):
    """Serve a programmatic SEO page for a specific language."""
    template_path = f'tts/{slug}.html'
    try:
        return render_template(template_path)
    except Exception:
        # 404 fallback
        return render_template('index.html'), 404


# ── All languages index page ─────────────────────────────────────────────
@app.route('/tts/')
@app.route('/tts')
def tts_index():
    """Landing page listing all supported TTS languages."""
    return render_template('tts_index.html', languages=_PSEO_MANIFEST)


# ── Dynamic XML Sitemap (includes pSEO pages) ────────────────────────────
@app.route('/sitemap.xml')
def sitemap_xml():
    from flask import Response
    from datetime import datetime

    base = 'https://www.texttoaudiomp3.site'
    today = datetime.utcnow().strftime('%Y-%m-%d')

    # Static pages
    static_urls = [
        ('/', '1.0', 'daily'),
        ('/about.html', '0.6', 'monthly'),
        ('/blog.html', '0.8', 'weekly'),
        ('/contact.html', '0.5', 'monthly'),
        ('/privacy.html', '0.3', 'yearly'),
        ('/terms.html', '0.3', 'yearly'),
        ('/tts/', '0.9', 'weekly'),
        # Blog posts
        ('/blog/what-is-ai-text-to-speech', '0.7', 'monthly'),
        ('/blog/convert-text-to-mp3-free', '0.7', 'monthly'),
        ('/blog/hindi-text-to-speech-guide', '0.7', 'monthly'),
        ('/blog/ai-voiceover-youtube', '0.7', 'monthly'),
        ('/blog/voice-customization-guide', '0.7', 'monthly'),
        ('/blog/free-vs-paid-tts-tools', '0.7', 'monthly'),
        ('/blog/tts-for-accessibility', '0.7', 'monthly'),
        ('/blog/elearning-audio-workflow', '0.7', 'monthly'),
        ('/blog/marathi-text-to-speech-guide', '0.7', 'monthly'),
        ('/blog/tts-for-podcasters', '0.7', 'monthly'),
    ]

    urls_xml = []
    for path, priority, freq in static_urls:
        urls_xml.append(f"""  <url>
    <loc>{base}{path}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    # pSEO pages
    for entry in _PSEO_MANIFEST:
        urls_xml.append(f"""  <url>
    <loc>{base}{entry['url']}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>""")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n'
    sitemap += '\\n'.join(urls_xml)
    sitemap += '\\n</urlset>'

    return Response(sitemap, mimetype='application/xml')
'''

print(PSEO_ROUTES_CODE)
