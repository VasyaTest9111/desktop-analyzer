"""
Tests for file enumeration and filtering logic.
"""
import pytest
from desktop_analyzer import (
    filter_relevant_files,
    RELEVANT_EXTENSIONS,
    MAX_FILES_PER_DIR,
)


@pytest.mark.unit
class TestFilterRelevantFiles:
    """Test file filtering by extension."""

    def test_filter_markdown_files(self):
        """Markdown files should be included."""
        files = ['README.md', 'NOTES.md', 'other.txt']
        result = filter_relevant_files(files)
        assert 'README.md' in result
        assert 'NOTES.md' in result

    def test_filter_python_files(self):
        """Python files should be included."""
        files = ['script.py', 'main.py', 'test.js']
        result = filter_relevant_files(files)
        assert 'script.py' in result
        assert 'main.py' in result

    def test_filter_json_files(self):
        """JSON files should be included."""
        files = ['config.json', 'package.json', 'data.xml']
        result = filter_relevant_files(files)
        assert 'config.json' in result
        assert 'package.json' in result

    def test_filter_html_files(self):
        """HTML files should be included."""
        files = ['index.html', 'page.html', 'style.css']
        result = filter_relevant_files(files)
        assert 'index.html' in result
        assert 'page.html' in result

    def test_filter_javascript_files(self):
        """JavaScript files should be included."""
        files = ['app.js', 'utils.js', 'script.py']
        result = filter_relevant_files(files)
        assert 'app.js' in result
        assert 'utils.js' in result

    def test_filter_text_files(self):
        """Text files should be included."""
        files = ['notes.txt', 'README.txt', 'config.json']
        result = filter_relevant_files(files)
        assert 'notes.txt' in result
        assert 'README.txt' in result

    def test_exclude_irrelevant_extensions(self):
        """Files with irrelevant extensions should be excluded."""
        files = ['image.png', 'video.mp4', 'archive.zip', 'notes.md']
        result = filter_relevant_files(files)
        assert 'image.png' not in result
        assert 'video.mp4' not in result
        assert 'archive.zip' not in result
        assert 'notes.md' in result

    def test_max_files_limit(self):
        """Only first 15 files should be included."""
        files = [f'file_{i}.py' for i in range(20)]
        result = filter_relevant_files(files)
        assert len(result) == MAX_FILES_PER_DIR

    def test_max_files_less_than_limit(self):
        """If files < limit, all should be included."""
        files = [f'file_{i}.py' for i in range(5)]
        result = filter_relevant_files(files)
        assert len(result) == 5

    def test_mixed_extensions_preserves_order(self):
        """Order of files should be preserved."""
        files = ['a.py', 'b.json', 'c.md', 'd.html', 'e.jpg', 'f.js']
        result = filter_relevant_files(files)
        expected = ['a.py', 'b.json', 'c.md', 'd.html', 'f.js']
        assert result == expected

    def test_custom_extensions(self):
        """Filter should work with custom extensions."""
        files = ['file.py', 'file.java', 'file.txt', 'file.zip']
        custom_ext = ('.py', '.java')
        result = filter_relevant_files(files, extensions=custom_ext)
        assert 'file.py' in result
        assert 'file.java' in result
        assert 'file.txt' not in result

    def test_case_sensitive_extensions(self):
        """Extension matching should be case-sensitive."""
        files = ['README.MD', 'notes.md', 'script.PY']
        result = filter_relevant_files(files)
        # Only lowercase matches
        assert 'notes.md' in result
        assert 'README.MD' not in result
        assert 'script.PY' not in result


@pytest.mark.unit
class TestFileEnumerationEdgeCases:
    """Test edge cases in file enumeration."""

    def test_empty_file_list(self):
        """Empty file list should return empty."""
        result = filter_relevant_files([])
        assert result == []

    def test_no_matching_files(self):
        """If no files match, return empty list."""
        files = ['image.png', 'video.mp4', 'archive.zip']
        result = filter_relevant_files(files)
        assert result == []

    def test_all_matching_files(self):
        """If all files match, return all (up to limit)."""
        files = [f'file_{i}.py' for i in range(10)]
        result = filter_relevant_files(files)
        assert len(result) == 10

    def test_hidden_files_included(self):
        """Hidden files with relevant extensions should be included."""
        files = ['.gitignore', '.env.json', 'README.md']
        result = filter_relevant_files(files)
        assert '.env.json' in result  # .json is relevant
        assert 'README.md' in result

    def test_files_with_multiple_dots(self):
        """Files with multiple dots should match correctly."""
        files = ['archive.tar.gz', 'config.prod.json', 'script.test.py']
        result = filter_relevant_files(files)
        assert 'config.prod.json' in result
        assert 'script.test.py' in result
        assert 'archive.tar.gz' not in result

    def test_files_without_extension(self):
        """Files without extension should be excluded."""
        files = ['Makefile', 'Dockerfile', 'README', 'script.py']
        result = filter_relevant_files(files)
        assert 'Makefile' not in result
        assert 'Dockerfile' not in result
        assert 'README' not in result
        assert 'script.py' in result

    def test_unicode_filenames(self):
        """Unicode filenames should be handled correctly."""
        files = ['тест.py', 'файл.json', 'データ.md', 'image.png']
        result = filter_relevant_files(files)
        assert 'тест.py' in result
        assert 'файл.json' in result
        assert 'データ.md' in result
        assert 'image.png' not in result

    def test_whitespace_in_filenames(self):
        """Filenames with whitespace should work."""
        files = ['my file.py', 'test script.js', 'data.json']
        result = filter_relevant_files(files)
        assert 'my file.py' in result
        assert 'test script.js' in result

    def test_special_characters_in_filenames(self):
        """Special characters in filenames should work."""
        files = ['file-1.py', 'config_prod.json', 'app.v2.js']
        result = filter_relevant_files(files)
        assert 'file-1.py' in result
        assert 'config_prod.json' in result
        assert 'app.v2.js' in result

    def test_very_long_filenames(self):
        """Very long filenames should be handled."""
        long_name = 'a' * 200 + '.py'
        files = [long_name, 'normal.py']
        result = filter_relevant_files(files)
        assert long_name in result
        assert 'normal.py' in result
