import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_ignore_dirs():
    """Sample set of directories to ignore."""
    return {
        '.git', '__pycache__', 'node_modules', '.venv', 'AppData'
    }


@pytest.fixture
def temp_folder_structure(temp_dir):
    """Create a realistic temporary folder structure for testing."""
    base = Path(temp_dir)

    folders = [
        '10-Projects',
        '20-Areas',
        '30-Resources',
        '40-Archives',
        'Projects',
        'Areas',
        'Resources',
        'Archives',
        'invalid-folder',
        '.hidden',
        '__pycache__',
        '.git',
    ]

    for folder in folders:
        folder_path = base / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        if folder not in ['.hidden', '__pycache__', '.git']:
            (folder_path / 'README.md').touch()
            (folder_path / 'config.json').touch()
            (folder_path / 'script.py').touch()
            (folder_path / 'styles.css').touch()

    return base


@pytest.fixture
def nested_structure(temp_dir):
    """Create a deeply nested structure to test depth limiting."""
    base = Path(temp_dir)

    level0 = base / '10-Level0'
    level0.mkdir()
    (level0 / 'file0.md').touch()

    level1 = level0 / '20-Level1'
    level1.mkdir()
    (level1 / 'file1.md').touch()

    level2 = level1 / '30-Level2'
    level2.mkdir()
    (level2 / 'file2.md').touch()

    level3 = level2 / '40-Level3'
    level3.mkdir()
    (level3 / 'file3.md').touch()

    return base
