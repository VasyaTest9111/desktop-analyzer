import os
import datetime

# НАЛАШТУВАННЯ ДЛЯ ПОВНОГО СКАНУВАННЯ
TARGET_PATHS = [
    r'C:\Users\vasya',
    r'C:\Users\vasya\Desktop',
    r'C:\Users\vasya\Documents'
]

OUTPUT_FILE = r'C:\Users\vasya\desktop_snapshot.md'

# Списки ігнорування (системний шум)
IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', '.obsidian', '.vscode',
    'AppData', 'Local Settings', 'Cookies', 'Recent', 'SendTo', 'Start Menu', 
    'NetHood', 'PrintHood', 'Templates', 'Application Data', 'My Documents'
}

def analyze():
    snapshot = [f"# OMEGA SYSTEM SNAPSHOT | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    snapshot.append("> [!] Звіт містить аналіз кореневої директорії та проектних папок.\n")
    
    seen_paths = set() # Щоб не дублювати папки, якщо вони вкладені

    for path in TARGET_PATHS:
        if not os.path.exists(path):
            continue
            
        snapshot.append(f"## 📂 SCANNING: {path}")
        
        for root, dirs, files in os.walk(path):
            # Модифікуємо dirs на місці для ігнорування сміття
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
            
            if root in seen_paths: continue
            seen_paths.add(root)

            # Визначаємо рівень вкладеності для візуалізації
            level = root.replace(path, '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root) or root
            
            # ПЕРЕВІРКА JOHNNY DECIMAL (10-19, 20-29 і т.д.)
            is_jd = any(folder_name.startswith(f"{i}") for i in range(10, 100))
            # ПЕРЕВІРКА PARA (Projects, Areas, Resources, Archives)
            is_para = any(p in folder_name.upper() for p in ["PROJECTS", "AREAS", "RESOURCES", "ARCHIVES"])
            
            status = "✅" if (is_jd or is_para) else "⚠️"
            
            if level < 3: # Обмежуємо глибину звіту для читабельності
                snapshot.append(f"{indent}- {status} **[{folder_name}]**")
                
                # Додаємо ключові файли (тільки важливі розширення)
                for f in files[:15]:
                    if f.endswith(('.md', '.py', '.json', '.html', '.txt', '.js')):
                        snapshot.append(f"{indent}  - 📄 {f}")
        
        snapshot.append("\n" + "---" + "\n")
                
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(snapshot))
    print(f"\n[SUCCESS] Звіт OMEGA-ENTITY збережено: {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze()