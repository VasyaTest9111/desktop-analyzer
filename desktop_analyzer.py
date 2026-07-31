import os
import datetime

TARGET_PATHS = [
    r'C:\Users\vasya',
    r'C:\Users\vasya\Desktop',
    r'C:\Users\vasya\Documents'
]

OUTPUT_FILE = r'C:\Users\vasya\desktop_snapshot.md'

IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', '.obsidian', '.vscode',
    'AppData', 'Local Settings', 'Cookies', 'Recent', 'SendTo', 'Start Menu',
    'NetHood', 'PrintHood', 'Templates', 'Application Data', 'My Documents'
}

MAX_DEPTH = 3
MAX_FILES_PER_DIR = 15
RELEVANT_EXTENSIONS = ('.md', '.py', '.json', '.html', '.txt', '.js')
JOHNNY_DECIMAL_RANGE = range(10, 100)
PARA_KEYWORDS = ["PROJECTS", "AREAS", "RESOURCES", "ARCHIVES"]


def validate_johnny_decimal(folder_name):
    """Check if folder name matches Johnny Decimal pattern (10-99)."""
    return any(folder_name.startswith(f"{i}") for i in JOHNNY_DECIMAL_RANGE)


def validate_para(folder_name):
    """Check if folder name matches PARA methodology keywords."""
    return any(keyword in folder_name.upper() for keyword in PARA_KEYWORDS)


def get_folder_status(folder_name):
    """Return status emoji based on folder naming validation."""
    if validate_johnny_decimal(folder_name) or validate_para(folder_name):
        return "✅"
    return "⚠️"


def should_ignore_dir(dir_name, ignore_dirs=None):
    """Check if directory should be ignored."""
    if ignore_dirs is None:
        ignore_dirs = IGNORE_DIRS
    return dir_name in ignore_dirs or dir_name.startswith('.')


def filter_ignored_dirs(dirs, ignore_dirs=None):
    """Filter out ignored directories in-place."""
    if ignore_dirs is None:
        ignore_dirs = IGNORE_DIRS
    dirs[:] = [d for d in dirs if not should_ignore_dir(d, ignore_dirs)]


def filter_relevant_files(files, extensions=None):
    """Filter files by relevant extensions."""
    if extensions is None:
        extensions = RELEVANT_EXTENSIONS
    return [f for f in files if f.endswith(extensions)][:MAX_FILES_PER_DIR]


def analyze():
    snapshot = [f"# OMEGA SYSTEM SNAPSHOT | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    snapshot.append("> [!] Звіт містить аналіз кореневої директорії та проектних папок.\n")

    seen_paths = set()

    for path in TARGET_PATHS:
        if not os.path.exists(path):
            continue

        snapshot.append(f"## 📂 SCANNING: {path}")

        for root, dirs, files in os.walk(path):
            filter_ignored_dirs(dirs)

            if root in seen_paths:
                continue
            seen_paths.add(root)

            level = root.replace(path, '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root) or root

            status = get_folder_status(folder_name)

            if level < MAX_DEPTH:
                snapshot.append(f"{indent}- {status} **[{folder_name}]**")

                relevant_files = filter_relevant_files(files)
                for f in relevant_files:
                    snapshot.append(f"{indent}  - 📄 {f}")

        snapshot.append("\n" + "---" + "\n")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(snapshot))
    print(f"\n[SUCCESS] Звіт OMEGA-ENTITY збережено: {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze()