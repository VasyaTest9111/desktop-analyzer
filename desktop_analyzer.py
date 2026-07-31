import os
import json
import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Set, Dict, Optional, Tuple
from pathlib import Path

# Default constants
DEFAULT_IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', '.obsidian', '.vscode',
    'AppData', 'Local Settings', 'Cookies', 'Recent', 'SendTo', 'Start Menu',
    'NetHood', 'PrintHood', 'Templates', 'Application Data', 'My Documents'
}

DEFAULT_EXTENSIONS = ('.md', '.py', '.json', '.html', '.txt', '.js')
JOHNNY_DECIMAL_RANGE = range(10, 100)
PARA_KEYWORDS = ["PROJECTS", "AREAS", "RESOURCES", "ARCHIVES"]

# Backward compatibility aliases
IGNORE_DIRS = DEFAULT_IGNORE_DIRS
RELEVANT_EXTENSIONS = DEFAULT_EXTENSIONS
MAX_DEPTH = 3
MAX_FILES_PER_DIR = 15


@dataclass
class AnalyzerConfig:
    """Configuration for DesktopAnalyzer."""
    target_paths: List[str]
    output_file: Optional[str] = None
    ignore_dirs: Set[str] = field(default_factory=lambda: DEFAULT_IGNORE_DIRS.copy())
    max_depth: int = 3
    max_files_per_dir: int = 15
    extensions: Tuple[str, ...] = DEFAULT_EXTENSIONS
    output_format: str = "markdown"  # markdown, json, dict


@dataclass
class FileInfo:
    """Information about a file."""
    name: str
    extension: str


@dataclass
class FolderInfo:
    """Information about a folder."""
    path: str
    name: str
    status: str
    is_valid_jd: bool
    is_valid_para: bool
    level: int
    files: List[FileInfo] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Result of directory analysis."""
    folders: List[FolderInfo] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    scanned_paths: List[str] = field(default_factory=list)
    total_folders: int = 0
    total_files: int = 0
    valid_folders: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        data = self.to_dict()
        return json.dumps(data, indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        lines = [
            f"# OMEGA SYSTEM SNAPSHOT | {self.timestamp}\n",
            "> [!] Звіт містить аналіз кореневої директорії та проектних папок.\n"
        ]

        for path in self.scanned_paths:
            lines.append(f"## 📂 SCANNING: {path}")

            for folder in self.folders:
                if folder.path.startswith(path):
                    indent = '  ' * folder.level
                    lines.append(f"{indent}- {folder.status} **[{folder.name}]**")

                    for file in folder.files:
                        lines.append(f"{indent}  - 📄 {file.name}")

            lines.append("\n---\n")

        return '\n'.join(lines)


class DesktopAnalyzer:
    """Analyze desktop directory structure for OMEGA agent."""

    def __init__(self, config: AnalyzerConfig):
        """Initialize analyzer with configuration."""
        self.config = config
        self.result = AnalysisResult()

    def analyze(self) -> AnalysisResult:
        """Analyze target directories and return structured result."""
        self.result = AnalysisResult(scanned_paths=self.config.target_paths)
        seen_paths: Set[str] = set()

        for path in self.config.target_paths:
            if not os.path.exists(path):
                continue

            for root, dirs, files in os.walk(path):
                self._filter_ignored_dirs(dirs)

                if root in seen_paths:
                    continue
                seen_paths.add(root)

                level = root.replace(path, '').count(os.sep)

                # Limit depth by clearing dirs for os.walk to avoid going deeper
                if level >= self.config.max_depth - 1:
                    dirs[:] = []

                folder_name = os.path.basename(root) or root
                status = self._get_folder_status(folder_name)
                is_valid_jd = self._validate_johnny_decimal(folder_name)
                is_valid_para = self._validate_para(folder_name)

                folder_info = FolderInfo(
                    path=root,
                    name=folder_name,
                    status=status,
                    is_valid_jd=is_valid_jd,
                    is_valid_para=is_valid_para,
                    level=level
                )

                # Add files
                relevant_files = self._filter_relevant_files(files)
                for file in relevant_files:
                    _, ext = os.path.splitext(file)
                    folder_info.files.append(FileInfo(name=file, extension=ext))
                    self.result.total_files += 1

                self.result.folders.append(folder_info)
                self.result.total_folders += 1
                if status == "✅":
                    self.result.valid_folders += 1

        return self.result

    def save(self, output_file: Optional[str] = None) -> str:
        """Save analysis result to file."""
        output_file = output_file or self.config.output_file
        if not output_file:
            raise ValueError("output_file must be provided in config or as parameter")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.config.output_format == "json":
            content = self.result.to_json()
        elif self.config.output_format == "markdown":
            content = self.result.to_markdown()
        else:
            raise ValueError(f"Unknown output format: {self.config.output_format}")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_file

    def _validate_johnny_decimal(self, folder_name: str) -> bool:
        """Check if folder name matches Johnny Decimal pattern."""
        return any(folder_name.startswith(f"{i}") for i in JOHNNY_DECIMAL_RANGE)

    def _validate_para(self, folder_name: str) -> bool:
        """Check if folder name matches PARA methodology keywords."""
        return any(keyword in folder_name.upper() for keyword in PARA_KEYWORDS)

    def _get_folder_status(self, folder_name: str) -> str:
        """Return status emoji based on folder naming validation."""
        if self._validate_johnny_decimal(folder_name) or self._validate_para(folder_name):
            return "✅"
        return "⚠️"

    def _should_ignore_dir(self, dir_name: str) -> bool:
        """Check if directory should be ignored."""
        return dir_name in self.config.ignore_dirs or dir_name.startswith('.')

    def _filter_ignored_dirs(self, dirs: List[str]) -> None:
        """Filter out ignored directories in-place."""
        dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]

    def _filter_relevant_files(self, files: List[str]) -> List[str]:
        """Filter files by relevant extensions."""
        return [f for f in files if f.endswith(self.config.extensions)][:self.config.max_files_per_dir]


# Backward compatibility: module-level functions
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
        ignore_dirs = DEFAULT_IGNORE_DIRS
    return dir_name in ignore_dirs or dir_name.startswith('.')


def filter_ignored_dirs(dirs, ignore_dirs=None):
    """Filter out ignored directories in-place."""
    if ignore_dirs is None:
        ignore_dirs = DEFAULT_IGNORE_DIRS
    dirs[:] = [d for d in dirs if not should_ignore_dir(d, ignore_dirs)]


def filter_relevant_files(files, extensions=None):
    """Filter files by relevant extensions."""
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS
    return [f for f in files if f.endswith(extensions)][:15]


def analyze():
    """Backward compatible analyze function."""
    config = AnalyzerConfig(
        target_paths=[
            r'C:\Users\vasya',
            r'C:\Users\vasya\Desktop',
            r'C:\Users\vasya\Documents'
        ],
        output_file=r'C:\Users\vasya\desktop_snapshot.md',
        output_format='markdown'
    )
    analyzer = DesktopAnalyzer(config)
    analyzer.analyze()
    output_file = analyzer.save()
    print(f"\n[SUCCESS] Звіт OMEGA-ENTITY збережено: {output_file}")


if __name__ == "__main__":
    analyze()