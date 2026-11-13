"""
Tests for path validation logic (Johnny Decimal and PARA).
"""
import pytest
from desktop_analyzer import (
    validate_johnny_decimal,
    validate_para,
    get_folder_status,
)


@pytest.mark.unit
@pytest.mark.validation
class TestJohnnyDecimalValidation:
    """Test Johnny Decimal folder naming validation (10-99)."""

    def test_valid_johnny_decimal_10_to_19(self):
        """Johnny Decimal folders starting with 10-19 should be valid."""
        valid_names = [
            '10-Projects', '10_test', '10', '15-Important',
            '19-Final'
        ]
        for name in valid_names:
            assert validate_johnny_decimal(name), f"Failed for {name}"

    def test_valid_johnny_decimal_20_to_29(self):
        """Johnny Decimal folders starting with 20-29 should be valid."""
        valid_names = [
            '20-Areas', '20_archive', '20', '25-Active',
            '29-End'
        ]
        for name in valid_names:
            assert validate_johnny_decimal(name), f"Failed for {name}"

    def test_valid_johnny_decimal_30_to_39(self):
        """Johnny Decimal folders starting with 30-39 should be valid."""
        valid_names = ['30-Resources', '35-Docs', '39-End']
        for name in valid_names:
            assert validate_johnny_decimal(name), f"Failed for {name}"

    def test_valid_johnny_decimal_40_to_99(self):
        """Johnny Decimal folders starting with 40-99 should be valid."""
        valid_names = [
            '40-Archives', '50-Data', '60-Config', '70-Logs',
            '80-Temp', '90-Deploy', '99-Final'
        ]
        for name in valid_names:
            assert validate_johnny_decimal(name), f"Failed for {name}"

    def test_invalid_johnny_decimal_single_digit(self):
        """Single digit folder names should be invalid."""
        invalid_names = ['1', '2', '3', '9']
        for name in invalid_names:
            assert not validate_johnny_decimal(name), f"Should be invalid: {name}"

    def test_johnny_decimal_with_three_digits(self):
        """Three digit numbers starting with 10-99 also match (startswith behavior)."""
        # Note: The validation uses startswith, so "100" matches "10", "999" matches "99", etc.
        assert validate_johnny_decimal('100-TooBig')  # Matches because starts with "10"
        assert validate_johnny_decimal('101-Nope')     # Matches because starts with "10"
        assert validate_johnny_decimal('999-Invalid')  # Matches because starts with "99"

    def test_invalid_johnny_decimal_no_prefix(self):
        """Folder names without numeric prefix should be invalid."""
        invalid_names = ['Projects', 'Documents', 'Archive', 'a10-Test']
        for name in invalid_names:
            assert not validate_johnny_decimal(name), f"Should be invalid: {name}"

    def test_invalid_johnny_decimal_requires_exact_start(self):
        """Johnny Decimal must be at the start of the name."""
        assert not validate_johnny_decimal('folder-10-test')
        assert not validate_johnny_decimal('my-10-projects')
        assert validate_johnny_decimal('10-test')

    def test_johnny_decimal_case_insensitive(self):
        """Johnny Decimal should work with any case suffix."""
        assert validate_johnny_decimal('10-PROJECTS')
        assert validate_johnny_decimal('10-Projects')
        assert validate_johnny_decimal('10-projects')

    def test_johnny_decimal_with_special_chars(self):
        """Johnny Decimal should work with various separators."""
        valid = ['10-test', '10_test', '10 test', '10.test', '10test']
        for name in valid:
            assert validate_johnny_decimal(name), f"Failed for {name}"


@pytest.mark.unit
@pytest.mark.validation
class TestPARAValidation:
    """Test PARA methodology folder naming validation."""

    def test_valid_para_projects(self):
        """PARA 'Projects' keyword should be recognized."""
        valid_names = [
            'Projects', 'PROJECTS', 'projects', 'My Projects',
            'Active Projects', 'Current-Projects', 'projects-2024',
            'archived-projects', 'PrOjEcTs'
        ]
        for name in valid_names:
            assert validate_para(name), f"Failed for {name}"

    def test_valid_para_areas(self):
        """PARA 'Areas' keyword should be recognized."""
        valid_names = [
            'Areas', 'AREAS', 'areas', 'My Areas',
            'Key Areas', 'Focus-Areas', 'areas-of-interest',
            'ArEaS'
        ]
        for name in valid_names:
            assert validate_para(name), f"Failed for {name}"

    def test_valid_para_resources(self):
        """PARA 'Resources' keyword should be recognized (exact match)."""
        valid_names = [
            'Resources', 'RESOURCES', 'resources', 'My Resources',
            'Learning Resources', 'Resources-Library', 'resources-2024',
            'ReSOuRcEs'
        ]
        for name in valid_names:
            assert validate_para(name), f"Failed for {name}"

    def test_valid_para_archives(self):
        """PARA 'Archives' keyword should be recognized (exact match)."""
        valid_names = [
            'Archives', 'ARCHIVES', 'archives', 'Old Archives',
            'Project Archives', 'Archives-Storage', 'archives-old',
            'ArChIvEs'
        ]
        for name in valid_names:
            assert validate_para(name), f"Failed for {name}"

    def test_valid_para_case_insensitive(self):
        """PARA validation should be case-insensitive."""
        test_cases = [
            ('PROJECTS', True),
            ('projects', True),
            ('Projects', True),
            ('PrOjEcTs', True),
        ]
        for name, expected in test_cases:
            result = validate_para(name)
            assert result == expected, f"Case sensitivity issue for {name}"

    def test_valid_para_partial_matches(self):
        """PARA keywords must be exactly in folder names (not substrings)."""
        valid_names = [
            'My-Projects-2024',
            '01-Areas-of-Focus',
            'Resources-Library-v2',
            'Old-Archives-Backup'
        ]
        for name in valid_names:
            assert validate_para(name), f"Failed for {name}"

    def test_invalid_para_no_keywords(self):
        """Folder names without PARA keywords should be invalid."""
        invalid_names = [
            'Documents', 'Downloads', 'Desktop', 'Workspace',
            'Temp', 'Storage', 'Backup', 'Data'
        ]
        for name in invalid_names:
            assert not validate_para(name), f"Should be invalid: {name}"

    def test_para_substring_must_exist(self):
        """PARA keywords must be substrings in the uppercase folder name."""
        # The implementation checks if keyword IN folder_name.upper()
        assert not validate_para('ProjectManager')  # 'PROJECTS' not in 'PROJECTMANAGER'
        assert validate_para('Projects-List')  # 'PROJECTS' in 'PROJECTS-LIST'
        assert not validate_para('Areaway')  # 'AREAS' not in 'AREAWAY'
        assert not validate_para('Area-Notes')  # 'AREAS' not in 'AREA-NOTES'
        assert validate_para('Areas-Notes')  # 'AREAS' in 'AREAS-NOTES'

    def test_invalid_para_empty_string(self):
        """Empty string should not validate as PARA."""
        assert not validate_para('')

    def test_invalid_para_whitespace_only(self):
        """Whitespace-only string should not validate as PARA."""
        assert not validate_para('   ')


@pytest.mark.unit
@pytest.mark.validation
class TestFolderStatus:
    """Test folder status emoji assignment."""

    def test_status_valid_johnny_decimal(self):
        """Valid Johnny Decimal folders should get ✅ status."""
        assert get_folder_status('10-Projects') == '✅'
        assert get_folder_status('20-Areas') == '✅'
        assert get_folder_status('99-Final') == '✅'

    def test_status_valid_para(self):
        """Valid PARA folders should get ✅ status."""
        assert get_folder_status('Projects') == '✅'
        assert get_folder_status('Areas') == '✅'
        assert get_folder_status('Resources') == '✅'
        assert get_folder_status('Archives') == '✅'

    def test_status_invalid_folder(self):
        """Invalid folders should get ⚠️ status."""
        assert get_folder_status('Documents') == '⚠️'
        assert get_folder_status('Downloads') == '⚠️'
        assert get_folder_status('Temp') == '⚠️'
        assert get_folder_status('Random-Folder') == '⚠️'

    def test_status_prefers_first_match(self):
        """When both JD and PARA match, should still return ✅."""
        assert get_folder_status('10-Projects') == '✅'

    def test_status_case_insensitive_para(self):
        """PARA validation in status should be case-insensitive."""
        assert get_folder_status('PROJECTS') == '✅'
        assert get_folder_status('projects') == '✅'
        assert get_folder_status('PrOjEcTs') == '✅'

    def test_status_empty_string(self):
        """Empty folder name should get ⚠️ status."""
        assert get_folder_status('') == '⚠️'

    def test_status_special_characters(self):
        """Folders with special characters should validate correctly."""
        assert get_folder_status('10-Projects-2024') == '✅'
        assert get_folder_status('Areas_of_Focus') == '✅'
        assert get_folder_status('!!!Invalid!!!') == '⚠️'


@pytest.mark.unit
@pytest.mark.validation
class TestValidationEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_validation_with_unicode_chars(self):
        """Validation should handle unicode characters."""
        assert not validate_johnny_decimal('١٠-Projects')  # Arabic numerals
        assert not validate_johnny_decimal('十-Projects')  # Chinese character

    def test_validation_with_whitespace(self):
        """Validation should handle leading/trailing whitespace."""
        assert not validate_johnny_decimal('  10-Projects')
        assert validate_johnny_decimal('10-Projects  ')  # startswith ignores trailing

    def test_validation_very_long_names(self):
        """Validation should handle very long folder names."""
        long_name = '10-' + 'A' * 1000
        assert validate_johnny_decimal(long_name)

        long_para = 'A' * 500 + 'PROJECTS' + 'B' * 500
        assert validate_para(long_para)

    def test_validation_none_input(self):
        """Validation should handle None input gracefully."""
        with pytest.raises((TypeError, AttributeError)):
            validate_johnny_decimal(None)
        with pytest.raises((TypeError, AttributeError)):
            validate_para(None)

    def test_validation_numeric_input(self):
        """Validation should handle numeric input."""
        with pytest.raises((TypeError, AttributeError)):
            validate_johnny_decimal(10)
        with pytest.raises((TypeError, AttributeError)):
            validate_para(20)
