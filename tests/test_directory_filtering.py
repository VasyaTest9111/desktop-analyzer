"""
Tests for directory filtering logic.
"""
import pytest
from desktop_analyzer import (
    should_ignore_dir,
    filter_ignored_dirs,
    IGNORE_DIRS,
)


@pytest.mark.unit
@pytest.mark.filtering
class TestShouldIgnoreDir:
    """Test individual directory ignore logic."""

    def test_ignore_git_directory(self):
        """Git directories should be ignored."""
        assert should_ignore_dir('.git')

    def test_ignore_pycache_directory(self):
        """Python cache directories should be ignored."""
        assert should_ignore_dir('__pycache__')

    def test_ignore_node_modules_directory(self):
        """Node modules should be ignored."""
        assert should_ignore_dir('node_modules')

    def test_ignore_venv_directory(self):
        """Virtual environment directories should be ignored."""
        assert should_ignore_dir('.venv')

    def test_ignore_obsidian_directory(self):
        """Obsidian config directories should be ignored."""
        assert should_ignore_dir('.obsidian')

    def test_ignore_vscode_directory(self):
        """VS Code config directories should be ignored."""
        assert should_ignore_dir('.vscode')

    def test_ignore_appdata_directory(self):
        """AppData directories should be ignored."""
        assert should_ignore_dir('AppData')

    def test_ignore_local_settings_directory(self):
        """Local Settings directories should be ignored."""
        assert should_ignore_dir('Local Settings')

    def test_ignore_cookies_directory(self):
        """Cookies directories should be ignored."""
        assert should_ignore_dir('Cookies')

    def test_ignore_start_menu_directory(self):
        """Start Menu directories should be ignored."""
        assert should_ignore_dir('Start Menu')

    def test_ignore_hidden_directories_with_dot(self):
        """Directories starting with dot should be ignored."""
        assert should_ignore_dir('.hidden')
        assert should_ignore_dir('.config')
        assert should_ignore_dir('.cache')

    def test_ignore_hidden_subdirectories_with_dot(self):
        """Hidden directories with dot in middle should be ignored if start with dot."""
        assert should_ignore_dir('.dot.config')

    def test_keep_normal_directories(self):
        """Normal directory names should not be ignored."""
        assert not should_ignore_dir('Documents')
        assert not should_ignore_dir('Projects')
        assert not should_ignore_dir('10-Areas')
        assert not should_ignore_dir('MyProject')

    def test_keep_uppercase_directories(self):
        """Uppercase directories should not be ignored (except matching list)."""
        assert not should_ignore_dir('DOCUMENTS')
        assert not should_ignore_dir('PROJECTS')

    def test_keep_mixed_case_directories(self):
        """Mixed case directories should not be ignored."""
        assert not should_ignore_dir('MyDocuments')
        assert not should_ignore_dir('MyProjects')

    def test_ignore_dot_case_sensitive(self):
        """Dot prefix check should be case-sensitive."""
        assert should_ignore_dir('.Config')
        assert should_ignore_dir('.HIDDEN')
        assert not should_ignore_dir('Config')
        assert not should_ignore_dir('HIDDEN')

    def test_ignore_list_case_sensitive(self):
        """Ignore list matching should be case-sensitive."""
        assert should_ignore_dir('AppData')
        assert not should_ignore_dir('appdata')
        assert not should_ignore_dir('APPDATA')

    def test_ignore_special_characters(self):
        """Directories with special characters but not in ignore list."""
        assert not should_ignore_dir('my-project')
        assert not should_ignore_dir('my_project')
        assert not should_ignore_dir('my.project')
        assert not should_ignore_dir('my project')

    def test_should_ignore_with_custom_list(self):
        """should_ignore_dir should work with custom ignore list."""
        custom_ignore = {'foo', 'bar'}
        assert should_ignore_dir('foo', ignore_dirs=custom_ignore)
        assert should_ignore_dir('bar', ignore_dirs=custom_ignore)
        assert not should_ignore_dir('baz', ignore_dirs=custom_ignore)
        # But dotfiles should always be ignored
        assert should_ignore_dir('.hidden', ignore_dirs=custom_ignore)


@pytest.mark.unit
@pytest.mark.filtering
class TestFilterIgnoredDirs:
    """Test batch directory filtering."""

    def test_filter_single_ignored_dir(self):
        """Single ignored directory should be removed."""
        dirs = ['.git', 'Documents']
        filter_ignored_dirs(dirs)
        assert dirs == ['Documents']

    def test_filter_multiple_ignored_dirs(self):
        """Multiple ignored directories should be removed."""
        dirs = ['.git', '__pycache__', 'Documents', '.venv']
        filter_ignored_dirs(dirs)
        assert set(dirs) == {'Documents'}

    def test_filter_no_ignored_dirs(self):
        """If no ignored dirs present, list should be unchanged."""
        dirs = ['Documents', 'Projects', 'Areas']
        original = dirs.copy()
        filter_ignored_dirs(dirs)
        assert dirs == original

    def test_filter_all_ignored_dirs(self):
        """If all dirs are ignored, list should be empty."""
        dirs = ['.git', '__pycache__', '.venv', '.obsidian']
        filter_ignored_dirs(dirs)
        assert dirs == []

    def test_filter_mixed_ignored_dirs(self):
        """Mixed ignored and normal dirs should filter correctly."""
        dirs = ['Documents', '.git', 'Projects', '__pycache__', 'Areas', '.vscode']
        filter_ignored_dirs(dirs)
        assert set(dirs) == {'Documents', 'Projects', 'Areas'}

    def test_filter_modifies_in_place(self):
        """filter_ignored_dirs should modify list in-place."""
        dirs = ['.git', 'Documents']
        original_id = id(dirs)
        filter_ignored_dirs(dirs)
        assert id(dirs) == original_id
        assert dirs == ['Documents']

    def test_filter_preserves_order(self):
        """Filter should preserve the order of remaining directories."""
        dirs = ['A', '.git', 'B', '__pycache__', 'C']
        filter_ignored_dirs(dirs)
        assert dirs == ['A', 'B', 'C']

    def test_filter_with_custom_ignore_list(self):
        """Filter should work with custom ignore list."""
        dirs = ['foo', 'bar', 'baz', 'qux']
        custom_ignore = {'foo', 'baz'}
        filter_ignored_dirs(dirs, ignore_dirs=custom_ignore)
        assert set(dirs) == {'bar', 'qux'}

    def test_filter_empty_list(self):
        """Filter should handle empty directory list."""
        dirs = []
        filter_ignored_dirs(dirs)
        assert dirs == []

    def test_filter_single_dir_ignored(self):
        """Single directory that's ignored should be removed."""
        dirs = ['.git']
        filter_ignored_dirs(dirs)
        assert dirs == []

    def test_filter_single_dir_not_ignored(self):
        """Single directory not in ignore list should remain."""
        dirs = ['Documents']
        filter_ignored_dirs(dirs)
        assert dirs == ['Documents']

    def test_filter_case_sensitivity(self):
        """Filter should be case-sensitive for ignore list."""
        dirs = ['AppData', 'appdata', 'APPDATA', 'Documents']
        filter_ignored_dirs(dirs)
        assert set(dirs) == {'appdata', 'APPDATA', 'Documents'}

    def test_filter_dotfiles_regardless_of_list(self):
        """Directories starting with dot should be ignored."""
        dirs = ['.config', '.hidden', 'Documents', 'Projects']
        filter_ignored_dirs(dirs)
        assert set(dirs) == {'Documents', 'Projects'}

    def test_filter_complex_nested_scenario(self):
        """Complex scenario with many directories."""
        dirs = [
            '10-Projects',
            '.git',
            '20-Areas',
            '__pycache__',
            'Resources',
            '.venv',
            '30-Archives',
            'AppData',
            '.vscode',
        ]
        filter_ignored_dirs(dirs)
        assert set(dirs) == {'10-Projects', '20-Areas', 'Resources', '30-Archives'}

    def test_filter_all_dotfiles(self):
        """List of only dotfiles should become empty."""
        dirs = ['.git', '.venv', '.vscode', '.config']
        filter_ignored_dirs(dirs)
        assert dirs == []

    def test_filter_numeric_names(self):
        """Numeric directory names should not be filtered."""
        dirs = ['10', '20', '30', '.git']
        filter_ignored_dirs(dirs)
        assert set(dirs) == {'10', '20', '30'}


@pytest.mark.unit
@pytest.mark.filtering
class TestFilterIgnoredDirsWithFixtures:
    """Test filtering with real directory structures."""

    def test_filter_realistic_structure(self, sample_ignore_dirs):
        """Test filtering with realistic directory structure."""
        dirs = [
            '10-Projects',
            '.git',
            '20-Areas',
            '__pycache__',
            'node_modules',
            'Resources',
        ]
        filter_ignored_dirs(dirs, ignore_dirs=sample_ignore_dirs)
        expected = {'10-Projects', '20-Areas', 'Resources'}
        assert set(dirs) == expected

    def test_filter_with_temp_structure(self, temp_folder_structure):
        """Test filtering on actual temporary directory structure."""
        dirs = [
            '10-Projects',
            '.git',
            '20-Areas',
            '__pycache__',
            'Projects',
        ]
        filter_ignored_dirs(dirs)
        expected = {'10-Projects', '20-Areas', 'Projects'}
        assert set(dirs) == expected


@pytest.mark.unit
@pytest.mark.filtering
class TestFilterIgnoredDirsEdgeCases:
    """Test edge cases for directory filtering."""

    def test_filter_none_input(self):
        """Filter with None should raise error."""
        with pytest.raises((TypeError, AttributeError)):
            filter_ignored_dirs(None)

    def test_filter_special_characters(self):
        """Directories with special characters should filter correctly."""
        dirs = ['my-project', 'my_project', 'my.project', '.git', 'normal']
        filter_ignored_dirs(dirs)
        assert '.git' not in dirs
        assert 'normal' in dirs

    def test_filter_unicode_directory_names(self):
        """Filter should handle unicode directory names."""
        dirs = ['café', 'naïve', '.git', '文件夹']
        filter_ignored_dirs(dirs)
        assert '.git' not in dirs
        assert 'café' in dirs
        assert '文件夹' in dirs

    def test_filter_whitespace_in_names(self):
        """Directories with whitespace should be handled correctly."""
        # Note: 'My Documents', 'Start Menu', and 'AppData' are in IGNORE_DIRS
        dirs = ['My Documents', 'Start Menu', 'AppData', 'Normal Folder']
        filter_ignored_dirs(dirs)
        assert 'Start Menu' not in dirs
        assert 'AppData' not in dirs
        assert 'My Documents' not in dirs  # This is in IGNORE_DIRS
        assert 'Normal Folder' in dirs

    def test_filter_large_directory_list(self):
        """Filter should handle large directory lists efficiently."""
        dirs = [f'folder_{i}' for i in range(1000)]
        dirs.extend(['.git', '__pycache__', '.venv'])
        original_len = len(dirs)
        filter_ignored_dirs(dirs)
        assert len(dirs) == original_len - 3

    def test_filter_duplicate_directories(self):
        """Filter should handle duplicate directory names."""
        dirs = ['Documents', 'Documents', '.git', '.git', 'Documents']
        filter_ignored_dirs(dirs)
        assert dirs == ['Documents', 'Documents', 'Documents']

    def test_filter_empty_string_directory(self):
        """Empty string directory names should not be filtered."""
        dirs = ['', 'Documents', '.git']
        filter_ignored_dirs(dirs)
        assert '' in dirs
        assert '.git' not in dirs
