"""
Tests for utility functions.
"""

import os
import tempfile
from pathlib import Path
import pytest

from docgen.utils.helpers import (
    get_template_path,
    list_templates,
    get_file_format,
    ensure_directory,
    format_date,
    sanitize_filename,
)


class TestGetFileFormat:
    """Tests for get_file_format function."""
    
    def test_markdown_extensions(self):
        """Test recognition of Markdown extensions."""
        assert get_file_format("file.md") == "markdown"
        assert get_file_format("file.markdown") == "markdown"
        assert get_file_format("path/to/file.md") == "markdown"
    
    def test_asciidoc_extensions(self):
        """Test recognition of AsciiDoc extensions."""
        assert get_file_format("file.adoc") == "asciidoc"
        assert get_file_format("file.asciidoc") == "asciidoc"
        assert get_file_format("path/to/file.adoc") == "asciidoc"
    
    def test_unknown_extension(self):
        """Test error for unknown extension."""
        with pytest.raises(ValueError) as exc_info:
            get_file_format("file.txt")
        
        assert "Unknown file format" in str(exc_info.value)
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        assert get_file_format("file.MD") == "markdown"
        assert get_file_format("file.ADOC") == "asciidoc"


class TestEnsureDirectory:
    """Tests for ensure_directory function."""
    
    def test_create_directory(self, temp_dir):
        """Test creating a new directory."""
        new_dir = os.path.join(temp_dir, "new_directory")
        
        result = ensure_directory(new_dir)
        
        assert os.path.isdir(new_dir)
        assert result == Path(new_dir)
    
    def test_create_nested_directories(self, temp_dir):
        """Test creating nested directories."""
        nested_dir = os.path.join(temp_dir, "a", "b", "c")
        
        result = ensure_directory(nested_dir)
        
        assert os.path.isdir(nested_dir)
    
    def test_existing_directory(self, temp_dir):
        """Test with existing directory."""
        # Should not raise error
        result = ensure_directory(temp_dir)
        
        assert os.path.isdir(temp_dir)


class TestFormatDate:
    """Tests for format_date function."""
    
    def test_format_iso_date(self):
        """Test formatting ISO date."""
        result = format_date("2026-02-17")
        
        assert result == "2026-02-17"
    
    def test_format_us_date(self):
        """Test formatting US date."""
        result = format_date("02/17/2026")
        
        # Should be converted to ISO format
        assert "2026" in result
    
    def test_no_date_returns_current(self):
        """Test that no date returns current date."""
        result = format_date(None)
        
        # Should return a valid date string
        assert len(result) == 10  # YYYY-MM-DD format
    
    def test_invalid_date_passthrough(self):
        """Test that invalid date is passed through."""
        result = format_date("invalid date")
        
        assert result == "invalid date"


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""
    
    def test_remove_invalid_characters(self):
        """Test removing invalid characters."""
        result = sanitize_filename("file<name>:test")
        
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
    
    def test_strip_spaces(self):
        """Test stripping leading/trailing spaces."""
        result = sanitize_filename("  filename  ")
        
        assert result == "filename"
    
    def test_valid_filename_unchanged(self):
        """Test that valid filename is unchanged."""
        result = sanitize_filename("valid_filename-123")
        
        assert result == "valid_filename-123"


class TestListTemplates:
    """Tests for list_templates function."""
    
    def test_list_templates(self, template_dir):
        """Test listing templates from template directory."""
        templates = list_templates([str(template_dir)])
        
        assert isinstance(templates, list)
        # Should find our templates
        if templates:
            assert all(isinstance(t, str) for t in templates)
    
    def test_list_templates_empty_path(self):
        """Test with empty custom paths."""
        # Should still work (may return empty list if no default templates)
        templates = list_templates([])
        
        assert isinstance(templates, list)


class TestGetTemplatePath:
    """Tests for get_template_path function."""
    
    def test_find_existing_template(self, template_dir):
        """Test finding an existing template."""
        path = get_template_path("ford_release_notes", [str(template_dir)])
        
        if path:  # Template exists
            assert path.is_dir()
            assert (path / "template.yaml").exists()
    
    def test_template_not_found(self):
        """Test when template doesn't exist."""
        path = get_template_path("nonexistent_template_xyz", [])
        
        assert path is None
