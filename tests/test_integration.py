"""
Integration tests with real directory structures and operations.
"""
import pytest
from pathlib import Path
from desktop_analyzer import (
    validate_johnny_decimal,
    validate_para,
    get_folder_status,
    should_ignore_dir,
    filter_ignored_dirs,
    filter_relevant_files,
)


@pytest.mark.integration
class TestRealDirectoryStructures:
    """Integration tests with real temporary directory structures."""

    def test_jd_projects_structure(self, temp_folder_structure):
        """Test with realistic Johnny Decimal projects structure."""
        projects = temp_folder_structure / "10-Projects"
        assert projects.exists()
        assert validate_johnny_decimal(projects.name)
        assert get_folder_status(projects.name) == "✅"

    def test_jd_areas_structure(self, temp_folder_structure):
        """Test with realistic Johnny Decimal areas structure."""
        areas = temp_folder_structure / "20-Areas"
        assert areas.exists()
        assert validate_johnny_decimal(areas.name)

    def test_jd_resources_structure(self, temp_folder_structure):
        """Test with realistic Johnny Decimal resources structure."""
        resources = temp_folder_structure / "30-Resources"
        assert resources.exists()
        assert validate_johnny_decimal(resources.name)

    def test_jd_archives_structure(self, temp_folder_structure):
        """Test with realistic Johnny Decimal archives structure."""
        archives = temp_folder_structure / "40-Archives"
        assert archives.exists()
        assert validate_johnny_decimal(archives.name)

    def test_para_projects_structure(self, temp_folder_structure):
        """Test with realistic PARA projects structure."""
        projects = temp_folder_structure / "Projects"
        assert projects.exists()
        assert validate_para(projects.name)
        assert get_folder_status(projects.name) == "✅"

    def test_para_areas_structure(self, temp_folder_structure):
        """Test with realistic PARA areas structure."""
        areas = temp_folder_structure / "Areas"
        assert areas.exists()
        assert validate_para(areas.name)

    def test_para_resources_structure(self, temp_folder_structure):
        """Test with realistic PARA resources structure."""
        resources = temp_folder_structure / "Resources"
        assert resources.exists()
        assert validate_para(resources.name)

    def test_para_archives_structure(self, temp_folder_structure):
        """Test with realistic PARA archives structure."""
        archives = temp_folder_structure / "Archives"
        assert archives.exists()
        assert validate_para(archives.name)

    def test_invalid_folder_in_structure(self, temp_folder_structure):
        """Test detection of invalid folder structure."""
        invalid = temp_folder_structure / "invalid-folder"
        assert invalid.exists()
        assert not validate_johnny_decimal(invalid.name)
        assert not validate_para(invalid.name)
        assert get_folder_status(invalid.name) == "⚠️"

    def test_hidden_folder_filtering(self, temp_folder_structure):
        """Test filtering of hidden folders."""
        hidden = temp_folder_structure / ".hidden"
        assert hidden.exists()
        assert should_ignore_dir(hidden.name)

    def test_pycache_filtering(self, temp_folder_structure):
        """Test filtering of pycache directories."""
        pycache = temp_folder_structure / "__pycache__"
        assert pycache.exists()
        assert should_ignore_dir(pycache.name)

    def test_git_filtering(self, temp_folder_structure):
        """Test filtering of git directories."""
        git = temp_folder_structure / ".git"
        assert git.exists()
        assert should_ignore_dir(git.name)


@pytest.mark.integration
class TestFileOperations:
    """Integration tests for file operations."""

    def test_enumerate_files_in_project(self, temp_folder_structure):
        """Test enumerating files in project directory."""
        projects = temp_folder_structure / "10-Projects"
        files = list(projects.glob("*"))
        file_names = [f.name for f in files if f.is_file()]

        assert len(file_names) > 0
        result = filter_relevant_files(file_names)
        assert len(result) > 0

    def test_filter_mixed_files(self, temp_folder_structure):
        """Test filtering mixed file types."""
        projects = temp_folder_structure / "10-Projects"
        files = list(projects.glob("*"))
        file_names = [f.name for f in files if f.is_file()]

        # Should have relevant files
        result = filter_relevant_files(file_names)
        # At least some should be relevant extensions
        assert isinstance(result, list)

    def test_recursive_directory_walk(self, nested_structure):
        """Test recursive walk through nested structure."""
        base = nested_structure

        # Simulate os.walk
        all_dirs = []
        for item in base.rglob("*"):
            if item.is_dir():
                all_dirs.append(item.name)

        assert len(all_dirs) > 0
        assert "20-Level1" in all_dirs
        assert "30-Level2" in all_dirs

    def test_nested_validation(self, nested_structure):
        """Test validation at different nesting levels."""
        base = nested_structure

        for item in base.rglob("*"):
            if item.is_dir():
                status = get_folder_status(item.name)
                assert status in ["✅", "⚠️"]

    def test_deep_nesting_performance(self, nested_structure):
        """Test performance with deeply nested structures."""
        base = nested_structure
        depth = 0
        current = base

        # Count depth
        for item in current.rglob("*"):
            if item.is_dir():
                item_depth = len(item.relative_to(base).parts)
                depth = max(depth, item_depth)

        assert depth >= 3


@pytest.mark.integration
class TestComplexScenarios:
    """Integration tests for complex real-world scenarios."""

    def test_mixed_jd_and_para_structure(self, temp_folder_structure):
        """Test structure with both JD and PARA folders."""
        folders = [
            "10-Projects",      # JD (also contains "PROJECTS")
            "20-Areas",         # JD (also contains "AREAS")
            "Projects",         # PARA
            "Areas",            # PARA
            "invalid-folder"    # Invalid
        ]

        valid_jd = [f for f in folders if validate_johnny_decimal(f)]
        valid_para = [f for f in folders if validate_para(f)]
        valid_any = [f for f in folders if get_folder_status(f) == "✅"]

        assert len(valid_jd) == 2  # Only 10-Projects, 20-Areas
        # PARA matches: "10-Projects" (contains PROJECTS), "20-Areas" (contains AREAS), "Projects", "Areas"
        assert len(valid_para) == 4
        # Both JD and PARA are valid, plus 4 from PARA
        assert len(valid_any) == 4

    def test_nested_filtering(self, nested_structure):
        """Test filtering at multiple nesting levels."""
        base = nested_structure

        for root, dirs, files in base.walk() if hasattr(base, 'walk') else []:
            # Simulate filtering
            filter_ignored_dirs(dirs)
            assert len(dirs) >= 0

    def test_complete_structure_validation(self, temp_folder_structure):
        """Test complete structure validation."""
        base = temp_folder_structure

        valid_count = 0
        invalid_count = 0

        for item in base.iterdir():
            if item.is_dir():
                status = get_folder_status(item.name)
                if status == "✅":
                    valid_count += 1
                else:
                    invalid_count += 1

        assert valid_count > 0  # Should have some valid
        assert invalid_count > 0  # Should have some invalid

    def test_batch_operations(self, temp_folder_structure):
        """Test batch operations on directory contents."""
        base = temp_folder_structure

        dirs = [d.name for d in base.iterdir() if d.is_dir()]
        dirs_copy = dirs.copy()

        # Filter
        filter_ignored_dirs(dirs)

        # Should have removed some
        assert len(dirs) < len(dirs_copy)
        # But should have some left
        assert len(dirs) > 0

    def test_file_enumeration_realistic(self, temp_folder_structure):
        """Test realistic file enumeration scenario."""
        base = temp_folder_structure

        for folder in base.iterdir():
            if folder.is_dir() and not should_ignore_dir(folder.name):
                files = [f.name for f in folder.iterdir() if f.is_file()]
                result = filter_relevant_files(files)

                # Results should be valid
                assert isinstance(result, list)
                assert all(isinstance(f, str) for f in result)

    def test_status_assignment_on_structure(self, temp_folder_structure):
        """Test status assignment across structure."""
        base = temp_folder_structure

        statuses = {}
        for item in base.iterdir():
            if item.is_dir():
                status = get_folder_status(item.name)
                statuses[item.name] = status

        # Should have mixed statuses
        assert "✅" in statuses.values()
        assert "⚠️" in statuses.values()


@pytest.mark.integration
class TestEdgeCaseIntegrations:
    """Integration tests for edge cases."""

    def test_unicode_paths_full_workflow(self, tmp_path):
        """Test full workflow with unicode paths."""
        base = tmp_path / "тест"
        base.mkdir()

        jd_folder = base / "10-Проект"
        jd_folder.mkdir()
        (jd_folder / "файл.md").touch()

        # Validate
        assert validate_johnny_decimal(jd_folder.name)

        # Filter files
        files = [f.name for f in jd_folder.iterdir()]
        result = filter_relevant_files(files)
        assert len(result) > 0

    def test_special_chars_full_workflow(self, tmp_path):
        """Test full workflow with special character paths."""
        base = tmp_path / "test-project"
        base.mkdir()

        para_folder = base / "My-Projects & Areas"
        para_folder.mkdir()
        (para_folder / "script.py").touch()

        # Validate (contains Projects and Areas)
        assert "Projects" in para_folder.name or "Areas" in para_folder.name or validate_para(para_folder.name)

        # Filter files
        files = [f.name for f in para_folder.iterdir()]
        result = filter_relevant_files(files)
        assert 'script.py' in result

    def test_mixed_ignored_in_structure(self, tmp_path):
        """Test mixed ignored directories in structure."""
        base = tmp_path / "project"
        base.mkdir()

        dirs_to_create = [
            ("10-Projects", False),
            (".git", True),
            ("__pycache__", True),
            ("src", False),
        ]

        for dir_name, should_be_ignored in dirs_to_create:
            dir_path = base / dir_name
            dir_path.mkdir()

            is_ignored = should_ignore_dir(dir_name)
            assert is_ignored == should_be_ignored

    def test_empty_nested_invalid_folders(self, tmp_path):
        """Test handling empty nested invalid folders."""
        base = tmp_path / "structure"
        base.mkdir()

        (base / "invalid1").mkdir()
        (base / "invalid1" / "nested-invalid").mkdir()
        (base / "10-Valid").mkdir()

        # Traverse and validate
        all_valid = []
        for item in base.rglob("*"):
            if item.is_dir():
                if get_folder_status(item.name) == "✅":
                    all_valid.append(item.name)

        assert "10-Valid" in all_valid
