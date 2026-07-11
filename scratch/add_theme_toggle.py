import os

THEME_SCRIPT = """
<script>
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const target = current === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', target);
  localStorage.setItem('theme', target);
  updateThemeIcons();
}

function updateThemeIcons() {
  const theme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', theme);
  const btn = document.getElementById('theme-btn');
  const btnMob = document.getElementById('theme-btn-mob');
  const iconClass = theme === 'light' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
  if (btn) btn.innerHTML = '<i class="' + iconClass + '"></i>';
  if (btnMob) btnMob.innerHTML = '<i class="' + iconClass + '"></i>Toggle Theme';
}

document.addEventListener('DOMContentLoaded', () => {
  updateThemeIcons();
});
</script>
</body>
"""

def add_theme_script_to_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check if toggleTheme is already defined in the file
    if "function toggleTheme" in content:
        print(f"Skipping (already has toggleTheme): {filepath}")
        return False
        
    if "</body>" in content:
        # Replace the last occurrence of </body>
        updated = content.replace("</body>", THEME_SCRIPT)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"Added theme toggle to: {filepath}")
        return True
    else:
        print(f"No </body> tag found in: {filepath}")
        return False

def main():
    templates_dir = r"c:\Users\Rupesh\OneDrive\Desktop\python 12-02-2026\new _add page url\git\git\voice-app\templates"
    
    # We want to update all static HTML templates except index.html and files in subfolders (like tts/)
    for filename in os.listdir(templates_dir):
        if filename.endswith(".html") and filename != "index.html" and filename != "tts_index.html":
            filepath = os.path.join(templates_dir, filename)
            add_theme_script_to_file(filepath)

if __name__ == "__main__":
    main()
