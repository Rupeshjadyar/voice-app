import os
import re

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We want to replace `<a href="/" class="nav-link ">Studio</a>` and `<a href="/" class="nav-link">Studio</a>`
    # with "Home Studio"
    updated = content
    
    # 1. Replace with extra spaces inside class if any
    updated = re.sub(
        r'(<a\s+href="/"\s+class="nav-link\s*"\s*>\s*)Studio(\s*</a>)',
        r'\1Home Studio\2',
        updated
    )
    
    # 2. Let's also do a general replace for case where class="nav-link " has a space
    updated = re.sub(
        r'(<a\s+href="/"\s+class="nav-link\s+"\s*>\s*)Studio(\s*</a>)',
        r'\1Home Studio\2',
        updated
    )

    if updated != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"Updated: {filepath}")
        return True
    return False

def main():
    templates_dir = r"c:\Users\Rupesh\OneDrive\Desktop\python 12-02-2026\new _add page url\git\git\voice-app\templates"
    
    # Update main templates
    for filename in os.listdir(templates_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(templates_dir, filename)
            update_file(filepath)
            
    # Update generator script
    generator_path = r"c:\Users\Rupesh\OneDrive\Desktop\python 12-02-2026\new _add page url\git\git\voice-app\generate_pseo_pages.py"
    update_file(generator_path)

if __name__ == "__main__":
    main()
