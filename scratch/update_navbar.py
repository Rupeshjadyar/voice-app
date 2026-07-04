import os
import re

TEMPLATES_DIR = r"c:\Users\Rupesh\OneDrive\Desktop\python 12-02-2026\new _add page url\git\git\voice-app\templates"

# Custom mobile navigation CSS to inject in <style>
MOBILE_NAV_CSS = """
  /* --- CUSTOM RESPONSIVE NAV --- */
  .nav-mobile-btn {
    display: none;
  }
  .nav-mobile-menu {
    display: none;
  }
  @media (max-width: 768px) {
    .site-header .nav-links {
      display: none !important;
    }
    .nav-mobile-btn {
      display: flex !important;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      color: var(--muted);
      font-size: 1.25rem;
      cursor: pointer;
    }
    .nav-mobile-menu.active {
      display: flex !important;
      flex-direction: column;
      gap: 6px;
      background: var(--bg);
      border-top: 1px solid var(--border);
      padding: 14px 24px;
      position: absolute;
      top: 60px;
      left: 0;
      right: 0;
      z-index: 100;
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
    }
    .nav-mobile-menu .nav-link {
      display: block;
      padding: 10px 14px;
      text-align: left;
      border-radius: 9px;
      width: 100%;
      box-sizing: border-box;
    }
  }
"""

def get_header_html(filename, active_page=""):
    studio_active = "active" if active_page == "studio" else ""
    blog_active = "active" if active_page == "blog" else ""
    about_active = "active" if active_page == "about" else ""
    contact_active = "active" if active_page == "contact" else ""
    privacy_active = "active" if active_page == "privacy" else ""
    terms_active = "active" if active_page == "terms" else ""

    return f"""<header class="site-header">
  <div class="header-inner">
    <a href="/" class="logo">
      <div class="logo-icon">
        <i class="fa-solid fa-microphone-lines" style="color:#fff;font-size:.82rem;"></i>
      </div>
      Voice<span style="color:var(--a1);">Pro</span>
    </a>
    <nav class="nav-links">
      <a href="/" class="nav-link {studio_active}">Studio</a>
      <a href="/blog.html" class="nav-link {blog_active}">Blog</a>
      <a href="/about.html" class="nav-link {about_active}">About</a>
      <a href="/contact.html" class="nav-link {contact_active}">Contact</a>
      <a href="/privacy.html" class="nav-link {privacy_active}">Privacy</a>
      <a href="/terms.html" class="nav-link {terms_active}">Terms</a>
      <button onclick="toggleTheme()" class="nav-link" id="theme-btn" style="background:none;border:none;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;padding:0;margin-left:5px;" aria-label="Toggle theme">
        <i class="fa-solid fa-moon"></i>
      </button>
    </nav>
    <button class="nav-mobile-btn" onclick="toggleMobileMenu()" aria-label="Toggle navigation">
      <i class="fa-solid fa-bars"></i>
    </button>
  </div>
  <div id="mobile-menu" class="nav-mobile-menu">
    <a href="/" class="nav-link {studio_active}">Studio</a>
    <a href="/blog.html" class="nav-link {blog_active}">Blog</a>
    <a href="/about.html" class="nav-link {about_active}">About</a>
    <a href="/contact.html" class="nav-link {contact_active}">Contact</a>
    <a href="/privacy.html" class="nav-link {privacy_active}">Privacy</a>
    <a href="/terms.html" class="nav-link {terms_active}">Terms</a>
    <button onclick="toggleTheme(); toggleMobileMenu()" class="nav-link" id="theme-btn-mob" style="background:none;border:none;cursor:pointer;display:flex;align-items:center;gap:8px;padding:10px 14px;width:100%;box-sizing:border-box;" aria-label="Toggle theme">
      <i class="fa-solid fa-moon"></i>Toggle Theme
    </button>
  </div>
</header>"""

def update_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove Bootstrap CSS
    content = content.replace('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">', '')
    # 2. Remove Bootstrap JS
    content = content.replace('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>', '')

    # 3. Revert data-bs-theme settings from scripts
    content = content.replace("document.documentElement.setAttribute('data-bs-theme', savedTheme);", "")
    content = content.replace("document.documentElement.setAttribute('data-bs-theme', target);", "")
    content = content.replace("document.documentElement.setAttribute('data-bs-theme', theme);", "")

    # Revert nav-link stylesheet changes if any
    content = content.replace(".nav-link:hover, .nav-link.active, .navbar-nav .nav-link:hover, .navbar-nav .nav-link.active {", ".nav-link:hover,.nav-link.active{")

    # 4. Inject mobile navigation CSS in the style block
    if "/* --- CUSTOM RESPONSIVE NAV --- */" not in content:
        # Find closing </style> tag and insert custom CSS before it
        content = content.replace("</style>", f"{MOBILE_NAV_CSS}\n</style>")

    # 5. Inject toggleMobileMenu JS function
    js_toggle = """
<script>
function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  if (menu) {
    menu.classList.toggle('active');
  }
}
</script>
"""
    if "toggleMobileMenu" not in content:
        content = content.replace("</body>", f"{js_toggle}\n</body>")

    # 6. Replace navbar container
    # Since the previous migration script replaced the navbar with a Bootstrap element starting with <nav class="navbar ...">...</nav>,
    # we want to find and replace that <nav ...> ... </nav> block with our get_header_html().
    bootstrap_nav_pattern = r'<nav class="navbar navbar-expand-lg.*?</nav>'
    
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

    new_header = get_header_html(filename, active_page)
    content, count = re.subn(bootstrap_nav_pattern, new_header, content, flags=re.DOTALL)
    if count == 0:
        # If it was still the old <header> block
        header_pattern = r"<header class=\"site-header\">.*?</header>"
        content, count = re.subn(header_pattern, new_header, content, flags=re.DOTALL)
        if count == 0:
            header_pattern_alt = r"<header class='site-header'>.*?</header>"
            content, count = re.subn(header_pattern_alt, new_header, content, flags=re.DOTALL)

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
