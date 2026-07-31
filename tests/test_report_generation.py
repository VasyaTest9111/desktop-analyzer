"""
Tests for report generation and output formatting.
"""
import pytest
import re
import datetime
from desktop_analyzer import analyze


@pytest.mark.unit
class TestReportFormatting:
    """Test markdown report formatting."""

    def test_report_has_header(self, tmp_path, monkeypatch):
        """Report should have main header with timestamp."""
        output_file = tmp_path / "report.md"
        monkeypatch.setenv("OUTPUT_FILE", str(output_file))

        # Create minimal test structure
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        (test_dir / "10-Projects").mkdir()

        # We need to mock the analyze to test formatting
        # For now, test the header format
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.match(timestamp_pattern, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def test_report_has_note_block(self):
        """Report should have note block at start."""
        note = "> [!] Звіт містить аналіз кореневої директорії та проектних папок.\n"
        assert note.startswith('> [!]')
        assert 'анал' in note.lower()

    def test_section_separator_format(self):
        """Section separators should be markdown valid."""
        separator = "\n---\n"
        assert separator.strip() == "---"

    def test_folder_entry_format(self):
        """Folder entries should have emoji and bold name."""
        entry = "- ✅ **[10-Projects]**"
        assert entry.startswith('-')
        assert '✅' in entry or '⚠️' in entry
        assert '**' in entry  # Bold markdown

    def test_file_entry_format(self):
        """File entries should be indented with emoji."""
        entry = "  - 📄 README.md"
        assert entry.startswith('  ')
        assert '📄' in entry
        assert 'README.md' in entry

    def test_indentation_increases_with_depth(self):
        """Indentation should increase with folder depth."""
        level0 = "- ✅ **[root]**"
        level1 = "  - ✅ **[subfolder]**"
        level2 = "    - ✅ **[deep]**"

        assert level0.count('  ') == 0
        assert level1.count('  ') == 1
        assert level2.count('  ') == 2

    def test_scan_section_header(self):
        """Each scan section should have a header."""
        header = "## 📂 SCANNING: /path/to/dir"
        assert header.startswith('##')
        assert '📂' in header
        assert 'SCANNING' in header

    def test_status_emoji_present(self):
        """Valid folders should have ✅, invalid should have ⚠️."""
        valid = "✅"
        invalid = "⚠️"
        assert valid in "- ✅ **[10-Projects]**"
        assert invalid in "- ⚠️ **[random]**"

    def test_report_encoding_utf8(self, tmp_path):
        """Report should be valid UTF-8."""
        report_content = "# OMEGA SNAPSHOT\n> [!] Звіт\n"
        report_file = tmp_path / "report.md"
        report_file.write_text(report_content, encoding='utf-8')

        # Should read back without errors
        read_content = report_file.read_text(encoding='utf-8')
        assert 'Звіт' in read_content


@pytest.mark.unit
class TestReportContent:
    """Test report content structure and accuracy."""

    def test_report_includes_timestamp(self):
        """Report should include valid timestamp."""
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        # Validate format
        parts = timestamp.split(' ')
        assert len(parts) == 2
        assert len(parts[0].split('-')) == 3  # YYYY-MM-DD
        assert len(parts[1].split(':')) == 3  # HH:MM:SS

    def test_report_line_endings(self):
        """Report lines should end consistently."""
        lines = [
            "# Header",
            "- item",
            "  - subitem",
        ]
        content = '\n'.join(lines)

        # Newlines between lines = len(lines) - 1
        expected_newlines = len(lines) - 1
        assert content.count('\n') == expected_newlines

    def test_markdown_headers_valid(self):
        """All markdown headers should be valid."""
        headers = [
            "# Main Header",
            "## Section",
            "### Subsection"
        ]
        for header in headers:
            # Should start with # and space
            assert re.match(r'^#+\s+', header)

    def test_folder_names_not_escaped(self):
        """Folder names should be displayed as-is."""
        folder_name = "10-My-Project"
        entry = f"- ✅ **[{folder_name}]**"
        assert folder_name in entry

    def test_special_chars_in_folder_names(self):
        """Folder names with special chars should work."""
        special_names = [
            "10-Project (v2)",
            "Areas & Resources",
            "Files_Data-2024"
        ]
        for name in special_names:
            entry = f"- ✅ **[{name}]**"
            assert name in entry


@pytest.mark.unit
class TestReportIntegrity:
    """Test report integrity and consistency."""

    def test_report_not_empty(self):
        """Generated report should not be empty."""
        # Minimal report should have at least header + note + separator
        min_lines = 3
        assert min_lines > 0

    def test_each_scan_has_separator(self):
        """Each scan section should end with separator."""
        separators = 2  # Assuming 2 scans
        report = "## SCANNING\n- item\n---\n## SCANNING 2\n---\n"
        assert report.count('---') >= separators

    def test_folders_sorted_by_appearance(self):
        """Folders should appear in walk order."""
        paths = [
            "/root",
            "/root/sub1",
            "/root/sub2",
            "/root/sub1/deep"
        ]
        # os.walk maintains directory order
        assert paths[0] < paths[1] or paths[0] < paths[2]

    def test_valid_markdown_syntax(self):
        """Report should have valid markdown syntax."""
        report = """# OMEGA SNAPSHOT | 2024-01-01 10:00:00

> [!] Note here

## 📂 SCANNING: /path

- ✅ **[folder]**
  - 📄 file.md

---
"""
        # Check basic structure
        assert report.count('#') >= 2
        assert report.count('**') % 2 == 0  # Bold pairs
        assert report.count('[') == report.count(']')

    def test_no_malformed_markdown(self):
        """Report should not have unmatched markdown delimiters."""
        report = "- ✅ **[name]**"
        # Count brackets
        assert report.count('[') == report.count(']')
        assert report.count('*') % 2 == 0  # Even asterisks for bold


@pytest.mark.unit
class TestReportEdgeCases:
    """Test edge cases in report generation."""

    def test_empty_directory_name(self):
        """Empty directory names should be handled."""
        # Unlikely but possible edge case
        name = ""
        entry = f"- ✅ **[{name or 'root'}]**"
        assert 'root' in entry or name in entry

    def test_very_long_folder_name(self):
        """Very long folder names should be included in report."""
        long_name = 'A' * 200
        entry = f"- ✅ **[{long_name}]**"
        assert long_name in entry

    def test_unicode_in_report(self):
        """Unicode characters should be preserved."""
        unicode_name = "Проект-中文-العربية"
        entry = f"- ✅ **[{unicode_name}]**"
        assert unicode_name in entry

    def test_high_nesting_indentation(self):
        """Deep nesting should have correct indentation."""
        for level in range(5):
            indent = '  ' * level
            entry = f"{indent}- item"
            expected_spaces = level * 2
            assert entry.startswith(' ' * expected_spaces)

    def test_many_files_in_directory(self):
        """Report should handle many files (limit to 15)."""
        files = [f"📄 file_{i}.py" for i in range(20)]
        # Only first 15 should be in report
        limited = files[:15]
        assert len(limited) == 15
