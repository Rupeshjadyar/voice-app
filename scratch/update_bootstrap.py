import os
import re

# Paths
TEMPLATES_DIR = r"c:\Users\Rupesh\OneDrive\Desktop\python 12-02-2026\new _add page url\git\git\voice-app\templates"

# CDN Links
BOOTSTRAP_CSS = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">'
BOOTSTRAP_JS = '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>'

# Responsive Bootstrap Navbar Template
def get_navbar(filename, active_page=""):
    studio_active = "active" if active_page == "studio" else ""
    blog_active = "active" if active_page == "blog" else ""
    about_active = "active" if active_page == "about" else ""
    contact_active = "active" if active_page == "contact" else ""
    privacy_active = "active" if active_page == "privacy" else ""
    terms_active = "active" if active_page == "terms" else ""
    
    return f"""<nav class="navbar navbar-expand-lg sticky-top border-bottom" style="background: var(--bg); border-color: var(--border) !important; z-index: 1000; backdrop-filter: blur(20px); opacity: 0.96;">
  <div class="container-fluid" style="max-width: 1100px; padding: 0 24px;">
    <a class="navbar-brand d-flex align-items-center gap-2" href="/" style="font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.05rem; color: var(--txt);">
      <div class="logo-icon d-flex align-items-center justify-content-center" style="width:34px; height:34px; background:linear-gradient(135deg,var(--a1),var(--a2)); border-radius:9px;">
        <i class="fa-solid fa-microphone-lines" style="color:#fff; font-size:.82rem;"></i>
      </div>
      <span>Voice<span style="color: var(--a1);">Pro</span></span>
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation" style="border-color: var(--border); color: var(--muted); padding: 4px 8px;">
      <i class="fa-solid fa-bars" style="color: var(--muted);"></i>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ms-auto align-items-lg-center gap-1 mt-2 mt-lg-0">
        <li class="nav-item"><a href="/" class="nav-link px-3 py-2 rounded {studio_active}" style="font-size: .85rem; color: var(--muted); transition: all 0.18s;">Studio</a></li>
        <li class="nav-item"><a href="/blog.html" class="nav-link px-3 py-2 rounded {blog_active}" style="font-size: .85rem; color: var(--muted); transition: all 0.18s;">Blog</a></li>
        <li class="nav-item"><a href="/about.html" class="nav-link px-3 py-2 rounded {about_active}" style="font-size: .85rem; color: var(--muted); transition: all 0.18s;">About</a></li>
        <li class="nav-item"><a href="/contact.html" class="nav-link px-3 py-2 rounded {contact_active}" style="font-size: .85rem; color: var(--muted); transition: all 0.18s;">Contact</a></li>
        <li class="nav-item"><a href="/privacy.html" class="nav-link px-3 py-2 rounded {privacy_active}" style="font-size: .85rem; color: var(--muted); transition: all 0.18s;">Privacy</a></li>
        <li class="nav-item"><a href="/terms.html" class="nav-link px-3 py-2 rounded {terms_active}" style="font-size: .85rem; color: var(--muted); transition: all 0.18s;">Terms</a></li>
        <li class="nav-item ms-lg-2">
          <button onclick="toggleTheme()" class="nav-link px-0 py-0 rounded d-inline-flex align-items-center justify-content-center" id="theme-btn" style="background:none; border:none; cursor:pointer; width:34px; height:34px; color: var(--muted);" aria-label="Toggle theme">
            <i class="fa-solid fa-moon"></i>
          </button>
        </li>
      </ul>
    </div>
  </div>
</nav>"""

def update_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject Bootstrap CSS in head (before </head>)
    if "bootstrap.min.css" not in content:
        content = content.replace("</head>", f"  {BOOTSTRAP_CSS}\n</head>")

    # 2. Inject Bootstrap JS before body end (before </body>)
    if "bootstrap.bundle.min.js" not in content:
        content = content.replace("</body>", f"{BOOTSTRAP_JS}\n</body>")

    # 3. Prevent Theme FOUC scripts to include data-bs-theme
    fouc_pattern = r"document\.documentElement\.setAttribute\('data-theme',\s*savedTheme\);"
    if re.search(fouc_pattern, content):
        content = re.sub(fouc_pattern, "document.documentElement.setAttribute('data-theme', savedTheme);\n    document.documentElement.setAttribute('data-bs-theme', savedTheme);", content)

    # Theme toggle function
    toggle_pattern = r"document\.documentElement\.setAttribute\('data-theme',\s*target\);"
    if re.search(toggle_pattern, content):
        content = re.sub(toggle_pattern, "document.documentElement.setAttribute('data-theme', target);\n  document.documentElement.setAttribute('data-bs-theme', target);", content)

    # 4. Enhance stylesheet rules for nav-link
    nav_style_pattern = r"\.nav-link:hover,\s*\.nav-link\.active\s*\{"
    if re.search(nav_style_pattern, content):
        content = re.sub(nav_style_pattern, ".nav-link:hover, .nav-link.active, .navbar-nav .nav-link:hover, .navbar-nav .nav-link.active {", content)

    # 5. Replace site-header navbar
    # Look for <header class="site-header"> ... </header>
    header_pattern = r"<header class=\"site-header\">.*?</header>"
    
    # Determine active page
    active_page = ""
    if filename == "about.html":
        active_page = "about"
    elif filename == "contact.html":
        active_page = "contact"
    elif filename == "privacy.html":
        active_page = "privacy"
    elif filename == "terms.html":
        active_page = "terms"
    elif filename == "blog.html" or "blog-" in filename:
        active_page = "blog"
    elif filename == "tts_index.html":
        active_page = "studio"

    navbar_html = get_navbar(filename, active_page)
    
    content, count = re.subn(header_pattern, navbar_html, content, flags=re.DOTALL)
    if count == 0:
        header_pattern_alt = r"<header class='site-header'>.*?</header>"
        content, count = re.subn(header_pattern_alt, navbar_html, content, flags=re.DOTALL)

    # 6. Make stat-row responsive
    stat_row_pattern = r'<div class="stat-row">(.*?)</div>\s*(?=\n|<!--|\s*<)'
    
    def replace_stat_row(match):
        inner = match.group(1)
        stat_boxes = re.findall(r'<div class="stat-box">.*?</div>\s*(?=<!--|<div|\Z)', inner, flags=re.DOTALL)
        if not stat_boxes:
            stat_boxes = re.findall(r'<div class="stat-box">.*?</div>', inner, flags=re.DOTALL)
            
        bootstrap_boxes = []
        for box in stat_boxes:
            bootstrap_boxes.append(f'  <div class="col-12 col-md-4">\n    {box.strip()}\n  </div>')
        
        return f'<div class="row g-3 my-4">\n' + '\n'.join(bootstrap_boxes) + '\n</div>'

    content = re.sub(stat_row_pattern, replace_stat_row, content, flags=re.DOTALL)

    # 7. Make value-cards grid responsive
    value_cards_pattern = r'<div class="value-cards">(.*?)</div>\s*(?=\n|<!--|\s*<)'
    
    def replace_value_cards(match):
        inner = match.group(1)
        cards = re.findall(r'<div class="value-card">.*?</div>\s*(?=<!--|<div|\Z)', inner, flags=re.DOTALL)
        if not cards:
            cards = re.findall(r'<div class="value-card">.*?</div>', inner, flags=re.DOTALL)
            
        bootstrap_cards = []
        for card in cards:
            bootstrap_cards.append(f'  <div class="col-12 col-sm-6 col-lg-3">\n    {card.strip()}\n  </div>')
            
        return f'<div class="row g-3 my-3">\n' + '\n'.join(bootstrap_cards) + '\n</div>'

    content = re.sub(value_cards_pattern, replace_value_cards, content, flags=re.DOTALL)

    # 8. Make blog-grid grid responsive (for blog.html)
    blog_grid_pattern = r'<div class="blog-grid">(.*?)</div>\s*(?=\n|<!--|\s*<)'
    
    def replace_blog_grid(match):
        inner = match.group(1)
        cards = re.findall(r'<div class="blog-card">.*?</div>\s*(?=<!--|<div|\Z)', inner, flags=re.DOTALL)
        if not cards:
            cards = re.findall(r'<div class="blog-card">.*?</div>', inner, flags=re.DOTALL)
            
        bootstrap_cards = []
        for card in cards:
            bootstrap_cards.append(f'  <div class="col-12 col-md-6 col-lg-4 d-flex">\n    {card.strip()}\n  </div>')
            
        return f'<div class="row g-4 my-3">\n' + '\n'.join(bootstrap_cards) + '\n</div>'

    content = re.sub(blog_grid_pattern, replace_blog_grid, content, flags=re.DOTALL)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {filename}")

def main():
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith(".html") and filename != "google1234567890abcdef.html" and filename != "index.html" and not filename.startswith("tts/"):
            filepath = os.path.join(TEMPLATES_DIR, filename)
            if os.path.isfile(filepath):
                update_file(filepath)

if __name__ == "__main__":
    main()
