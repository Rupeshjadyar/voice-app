import os
import re

AD_TAG = '\n    <!-- ✅ MONETAG ADS -->\n    <script src="https://quge5.com/88/tag.min.js" data-zone="258614" async data-cfasync="false"></script>\n'

def insert_ad_in_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'data-zone="258614"' in content:
        print(f"Skipping (ad tag already exists): {filepath}")
        return False
        
    # We will insert it right before </head> or after existing meta/script tags
    if '</head>' in content:
        updated = content.replace('</head>', AD_TAG + '</head>')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"Added Ad Tag to: {filepath}")
        return True
    return False

def main():
    templates_dir = r"c:\Users\Rupesh\OneDrive\Desktop\python 12-02-2026\new _add page url\git\git\voice-app\templates"
    
    # 1. Update all static HTML files in templates/
    for filename in os.listdir(templates_dir):
        if filename.endswith(".html") and filename != "google1234567890abcdef.html":
            filepath = os.path.join(templates_dir, filename)
            insert_ad_in_html(filepath)
            
    # 2. Update generate_pseo_pages.py
    generator_path = r"c:\Users\Rupesh\OneDrive\Desktop\python 12-02-2026\new _add page url\git\git\voice-app\generate_pseo_pages.py"
    with open(generator_path, 'r', encoding='utf-8') as f:
        gen_content = f.read()
        
    if 'data-zone="258614"' not in gen_content:
        # Insert the script block into generator page template head
        # We can find the </head> inside PAGE_TEMPLATE or near line 435
        # Let's search for "  </head>" or similar or insert it after the google tag manager / Adsense scripts.
        # PAGE_TEMPLATE's </head> tag is around line 435 in the source
        # Let's look for:
        # <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9707682105347147" crossorigin="anonymous"></script>
        target_str = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9707682105347147" crossorigin="anonymous"></script>'
        replacement_str = target_str + '\n<script src="https://quge5.com/88/tag.min.js" data-zone="258614" async data-cfasync="false"></script>'
        
        updated_gen = gen_content.replace(target_str, replacement_str)
        with open(generator_path, 'w', encoding='utf-8') as f:
            f.write(updated_gen)
        print("Added Ad Tag to generate_pseo_pages.py")
    else:
        print("Skipping generator (ad tag already exists)")

if __name__ == "__main__":
    main()
