# OMEGA Desktop Analyzer - Документація

## 📋 Зміст
1. [Огляд](#огляд)
2. [Встановлення](#встановлення)
3. [Швидкий старт](#швидкий-старт)
4. [API Довідник](#api-довідник)
5. [CLI Довідник](#cli-довідник)
6. [OMEGA Інтеграція](#omega-інтеграція)
7. [Приклади](#приклади)

---

## Огляд

**OMEGA Desktop Analyzer** - інтелектуальний інструмент для аналізу структури директорій. Він:

- ✅ Аналізує директорії за методологіями **Johnny Decimal** (10-99) і **PARA** (Projects/Areas/Resources/Archives)
- ✅ Фільтрує системний шум (`.git`, `__pycache__`, тощо)
- ✅ Генерує звіти у форматах **Markdown**, **JSON**, **Python dict**
- ✅ Інтегрується з OMEGA агентом для розуміння робочого простору
- ✅ 182 тести з 55% покриттям

### Можливості
- 🔍 Рекурсивний аналіз директорій
- 📊 Структурована класифікація папок
- 📄 Фільтрація файлів за розширеннями
- 🎯 Розпізнавання валідних проектів
- 🔧 Гнучка конфігурація
- 🚀 Ready для production

---

## Встановлення

### Вимоги
- Python 3.9+
- pytest (для тестів)

### Setup
```bash
# Клонування репозиторію
git clone https://github.com/VasyaTest9111/desktop-analyzer.git
cd desktop-analyzer

# Встановлення dev залежностей
pip install -r requirements-dev.txt

# Запуск тестів
pytest tests/ -v
```

---

## Швидкий старт

### 1️⃣ Базовий аналіз (Python)

```python
from desktop_analyzer import DesktopAnalyzer, AnalyzerConfig

# Створіть конфіг
config = AnalyzerConfig(
    target_paths=["/path/to/workspace"],
    output_format="markdown"
)

# Запустіть аналіз
analyzer = DesktopAnalyzer(config)
result = analyzer.analyze()

# Отримайте результат
print(result.to_markdown())
```

### 2️⃣ CLI аналіз

```bash
# Базовий аналіз
python desktop_analyzer_cli.py /workspace

# З JSON виходом
python desktop_analyzer_cli.py /workspace --format json --output report.json

# З кастомними параметрами
python desktop_analyzer_cli.py /workspace \
  --depth 5 \
  --max-files 20 \
  --extensions .py .json .md \
  --verbose
```

### 3️⃣ OMEGA інтеграція

```python
from omega_integration_example import OmegaWorkspaceAnalyzer

analyzer = OmegaWorkspaceAnalyzer(["/workspace"])
context = analyzer.analyze_workspace()

# Контекст для агента
agent_context = analyzer.get_agent_context()
json_context = analyzer.get_json_context()
```

---

## API Довідник

### AnalyzerConfig (Dataclass)

Конфігурація для аналізатора.

```python
from desktop_analyzer import AnalyzerConfig

config = AnalyzerConfig(
    target_paths: List[str],           # Які папки аналізувати
    output_file: Optional[str] = None, # Де зберігати звіт
    ignore_dirs: Set[str] = ...,       # Папки для ігнорування
    max_depth: int = 3,                # Максимальна глибина
    max_files_per_dir: int = 15,       # Макс файлів на папку
    extensions: Tuple[str, ...] = ..., # Розширення для фільтрації
    output_format: str = "markdown"    # "markdown", "json", або "dict"
)
```

### DesktopAnalyzer (Клас)

Основний аналізатор.

```python
analyzer = DesktopAnalyzer(config)

# Методи
result = analyzer.analyze()              # Аналізувати
output_file = analyzer.save()            # Зберегти результат

# Приватні методи для кастомізації
analyzer._validate_johnny_decimal(name)  # Перевірити JD
analyzer._validate_para(name)            # Перевірити PARA
analyzer._get_folder_status(name)        # Отримати статус
```

### AnalysisResult (Dataclass)

Результат аналізу.

```python
result = analyzer.analyze()

# Властивості
result.folders               # List[FolderInfo] - папки
result.timestamp            # str - час аналізу
result.scanned_paths        # List[str] - проаналізовані шляхи
result.total_folders        # int - всього папок
result.total_files          # int - всього файлів
result.valid_folders        # int - валідних папок

# Методи
result.to_dict()           # → Dict
result.to_json()           # → JSON string
result.to_markdown()       # → Markdown string
```

### FolderInfo (Dataclass)

Інформація про папку.

```python
folder: FolderInfo
folder.path          # str - повний шлях
folder.name          # str - ім'я папки
folder.status        # str - "✅" або "⚠️"
folder.is_valid_jd   # bool - валідна JD?
folder.is_valid_para # bool - валідна PARA?
folder.level         # int - глибина
folder.files         # List[FileInfo] - файли
```

### FileInfo (Dataclass)

Інформація про файл.

```python
file: FileInfo
file.name           # str - ім'я файлу
file.extension      # str - розширення
```

---

## CLI Довідник

### Синтаксис
```bash
python desktop_analyzer_cli.py <paths...> [options]
```

### Параметри

| Параметр | Скорочено | За замовчуванням | Опис |
|----------|-----------|------------------|------|
| `--format` | `-f` | markdown | Формат виходу: markdown, json, dict |
| `--output` | `-o` | (stdout) | Файл для збереження |
| `--depth` | `-d` | 3 | Максимальна глибина |
| `--max-files` | — | 15 | Файлів на папку |
| `--extensions` | `-e` | .md .py .json... | Розширення |
| `--ignore` | — | — | Додатково ігнорувати папки |
| `--verbose` | `-v` | false | Деталізований вивід |

### Приклади

```bash
# Аналіз поточної папки
python desktop_analyzer_cli.py .

# JSON на файл
python desktop_analyzer_cli.py /workspace -f json -o report.json

# Глибокий аналіз з кастомом
python desktop_analyzer_cli.py /workspace \
  --depth 10 \
  --max-files 50 \
  --extensions .py .js .ts \
  --output deep_report.md \
  --verbose

# Ігнорування додатків папок
python desktop_analyzer_cli.py /workspace \
  --ignore node_modules venv dist \
  --format json

# Кілька шляхів
python desktop_analyzer_cli.py /path1 /path2 /path3
```

---

## OMEGA Інтеграція

### OmegaWorkspaceAnalyzer (Клас)

Інтеграція для OMEGA агента.

```python
from omega_integration_example import OmegaWorkspaceAnalyzer

# Ініціалізація
analyzer = OmegaWorkspaceAnalyzer(
    workspace_paths=["/workspace", "/projects"]
)

# Методи
context = analyzer.analyze_workspace()      # Повна структурована інформація
projects = analyzer._extract_projects()     # Валідні проекти
structure = analyzer._extract_structure()   # Структура по рівнях
file_types = analyzer._extract_file_types() # Статистика файлів

# Для агента
agent_context = analyzer.get_agent_context()  # Читальний формат
json_context = analyzer.get_json_context()    # JSON для API
```

### Вихід для OMEGA

```python
{
  "timestamp": "2026-07-31 11:39:00",
  "workspace_summary": {
    "total_folders": 15,
    "valid_folders": 8,
    "total_files": 120,
    "valid_percentage": 53.3
  },
  "structure": {
    "by_level": {
      "0": [...],  # Кореневі папки
      "1": [...],  # Рівень 1
      "2": [...]   # Рівень 2
    }
  },
  "projects": [
    {
      "name": "10-Projects",
      "path": "/workspace/10-Projects",
      "type": "johnny_decimal",
      "files": [...]
    }
  ],
  "file_types": {
    ".py": 45,
    ".md": 20,
    ".json": 15
  }
}
```

---

## Приклади

### Приклад 1: Аналіз робочого простору

```python
from desktop_analyzer import DesktopAnalyzer, AnalyzerConfig

config = AnalyzerConfig(
    target_paths=["/home/user/projects"],
    output_format="markdown",
    output_file="/tmp/workspace_report.md",
    max_depth=4
)

analyzer = DesktopAnalyzer(config)
result = analyzer.analyze()
analyzer.save()

print(f"Знайдено {result.total_folders} папок")
print(f"Валідних: {result.valid_folders}")
print(f"Файлів: {result.total_files}")
```

### Приклад 2: JSON API

```python
from desktop_analyzer import DesktopAnalyzer, AnalyzerConfig
import json

config = AnalyzerConfig(
    target_paths=["/workspace"],
    output_format="json"
)

analyzer = DesktopAnalyzer(config)
result = analyzer.analyze()

# Отримати JSON
json_data = result.to_json()

# Або як dict
dict_data = result.to_dict()
print(json.dumps(dict_data, indent=2))
```

### Приклад 3: OMEGA агент

```python
from omega_integration_example import OmegaWorkspaceAnalyzer

# Ініціалізація
analyzer = OmegaWorkspaceAnalyzer(["/workspace"])

# Отримати контекст
context = analyzer.analyze_workspace()

# Для AI агента
print("=" * 60)
print("OMEGA WORKSPACE ANALYSIS")
print("=" * 60)
print(analyzer.get_agent_context())

# Для API
api_data = analyzer.get_json_context()
```

### Приклад 4: CLI

```bash
# Базовий аналіз
python desktop_analyzer_cli.py /workspace

# Детальний аналіз з JSON
python desktop_analyzer_cli.py /workspace \
  --format json \
  --output analysis.json \
  --depth 5 \
  --verbose

# Аналіз кількох папок
python desktop_analyzer_cli.py /workspace /projects /data \
  --format markdown \
  --output combined_report.md
```

---

## Тестування

### Запуск всіх тестів
```bash
pytest tests/ -v
```

### Запуск специфічної категорії
```bash
# Тільки path validation тести
pytest tests/test_path_validation.py -v

# Тільки integration тести
pytest tests/test_integration.py -v

# З coverage
pytest tests/ --cov=desktop_analyzer --cov-report=html
```

### Тестова статистика
- **182 тести** - 100% passing
- **55% code coverage**
- **6 категорій** - Path Validation, Directory Filtering, File Enumeration, Report Generation, Error Handling, Integration

---

## FAQ

**Q: Як додати свої розширення?**
```python
config = AnalyzerConfig(
    target_paths=["/workspace"],
    extensions=('.py', '.js', '.java', '.go')
)
```

**Q: Як ігнорувати додаткові папки?**
```python
from desktop_analyzer import DEFAULT_IGNORE_DIRS

custom_ignore = DEFAULT_IGNORE_DIRS.copy()
custom_ignore.update({'node_modules', 'dist', 'build'})

config = AnalyzerConfig(
    target_paths=["/workspace"],
    ignore_dirs=custom_ignore
)
```

**Q: Як отримати контекст для OMEGA?**
```python
from omega_integration_example import OmegaWorkspaceAnalyzer

analyzer = OmegaWorkspaceAnalyzer(["/workspace"])
context = analyzer.analyze_workspace()  # Для JSON API
text = analyzer.get_agent_context()     # Для агента
```

---

## Ліцензія

MIT License - Vasya Core Architecture

## Автор

Василь Мисінов (Vasya Core Architecture)

---

**Версія**: 2.0
**Оновлено**: 2026-07-31
**Статус**: Production Ready ✅
