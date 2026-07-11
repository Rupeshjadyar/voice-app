import os

OLD_TAG_HTML = '    <!-- ✅ MONETAG ADS -->\n    <script src="https://quge5.com/88/tag.min.js" data-zone="258614" async data-cfasync="false"></script>\n'
OLD_TAG_GEN = '<script src="https://quge5.com/88/tag.min.js" data-zone="258614" async data-cfasync="false"></script>'

NEW_TAG_HTML = '    <!-- ✅ MONETAG ADS -->\n    <script>(function(s){s.dataset.zone=\'11271937\',s.src=\'https://nap5k.com/tag.min.js\'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement(\'script\')))</script>\n'
NEW_TAG_GEN = '<script>(function(s){s.dataset.zone=\'11271937\',s.src=\'https://nap5k.com/tag.min.js\'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement(\'script\')))</script>'

def update_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if OLD_TAG_HTML in content:
        content = content.replace(OLD_TAG_HTML, NEW_TAG_HTML)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated HTML file: {filepath}")
        return True
    elif '258614' in content:
        # Fallback if whitespace differs
        content = re.sub(r'<!--\s*✅\s*MONETAG\s*ADS\s*-->\s*<script[^>]*data-zone="258614"[^>]*></script>', NEW_TAG_HTML, content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Regex Updated HTML file: {filepath}")
        return True
    return False

def main():
    templates_dir = r"c:\Users\Rupesh\OneDrive\Desktop\python 12-02-2026\new _add page url\git\git\voice-app\templates"
    
    # 1. Update all static HTML templates
    for filename in os.listdir(templates_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(templates_dir, filename)
            update_html_file(filepath)
            
    # 2. Update generate_pseo_pages.py
    generator_path = r"c:\Users\Rupesh\OneDrive\Desktop\python 12-02-2026\new _add page url\git\git\voice-app\generate_pseo_pages.py"
    with open(generator_path, 'r', encoding='utf-8') as f:
        gen_content = f.read()
        
    if OLD_TAG_GEN in gen_content:
        gen_content = gen_content.replace(OLD_TAG_GEN, NEW_TAG_GEN)
        with open(generator_path, 'w', encoding='utf-8') as f:
            f.write(gen_content)
        print("Updated generate_pseo_pages.py")
    else:
        # Fallback if there was a difference in format
        import re
        gen_content = re.sub(r'<script[^>]*data-zone="258614"[^>]*></script>', NEW_TAG_GEN, gen_content)
        with open(generator_path, 'w', encoding='utf-8') as f:
            f.write(gen_content)
        print("Regex Updated generate_pseo_pages.py")

if __name__ == "__main__":
    main()
