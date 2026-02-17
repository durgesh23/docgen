"""
Tests for the main PDFGenerator class.
"""

import os
import tempfile
from pathlib import Path
import pytest

from docgen.generator import PDFGenerator
from docgen.models import Document


class TestPDFGenerator:
    """Tests for PDFGenerator class."""
    
    @pytest.fixture
    def generator(self, template_dir):
        """Create a PDFGenerator for testing."""
        return PDFGenerator(
            template="ford_release_notes",
            template_paths=[str(template_dir)]
        )
    
    def test_init_with_valid_template(self, template_dir):
        """Test initialization with a valid template."""
        gen = PDFGenerator(
            template="ford_release_notes",
            template_paths=[str(template_dir)]
        )
        
        assert gen.current_template == "ford_release_notes"
    
    def test_init_with_invalid_template(self, template_dir):
        """Test initialization with an invalid template."""
        with pytest.raises(ValueError) as exc_info:
            PDFGenerator(
                template="nonexistent_template",
                template_paths=[str(template_dir)]
            )
        
        assert "not found" in str(exc_info.value)
    
    def test_list_templates(self, generator):
        """Test listing available templates."""
        templates = generator.list_templates()
        
        assert isinstance(templates, list)
        assert "ford_release_notes" in templates
    
    def test_get_template_info(self, generator):
        """Test getting template information."""
        info = generator.get_template_info()
        
        assert isinstance(info, dict)
        assert "name" in info
        assert "version" in info
    
    def test_supported_formats(self, generator):
        """Test getting supported formats."""
        formats = generator.supported_formats
        
        assert "markdown" in formats
        assert "asciidoc" in formats
    
    def test_set_template(self, generator, template_dir):
        """Test switching templates."""
        generator.set_template("generic")
        
        assert generator.current_template == "generic"
    
    def test_generate_from_markdown_file(self, generator, sample_markdown, temp_dir):
        """Test generating PDF from Markdown file."""
        # Write sample markdown to file
        input_path = os.path.join(temp_dir, "input.md")
        with open(input_path, 'w') as f:
            f.write(sample_markdown)
        
        output_path = os.path.join(temp_dir, "output.pdf")
        
        result = generator.generate(input_path, output_path)
        
        assert os.path.exists(result)
        assert result == output_path
        
        # Verify it's a PDF
        with open(result, 'rb') as f:
            header = f.read(4)
            assert header == b'%PDF'
    
    def test_generate_from_asciidoc_file(self, generator, sample_asciidoc, temp_dir):
        """Test generating PDF from AsciiDoc file."""
        # Write sample asciidoc to file
        input_path = os.path.join(temp_dir, "input.adoc")
        with open(input_path, 'w') as f:
            f.write(sample_asciidoc)
        
        output_path = os.path.join(temp_dir, "output.pdf")
        
        result = generator.generate(input_path, output_path)
        
        assert os.path.exists(result)
    
    def test_generate_with_metadata_override(self, generator, sample_markdown, temp_dir):
        """Test generating PDF with metadata override."""
        input_path = os.path.join(temp_dir, "input.md")
        with open(input_path, 'w') as f:
            f.write(sample_markdown)
        
        output_path = os.path.join(temp_dir, "output.pdf")
        
        result = generator.generate(
            input_path,
            output_path,
            metadata={"title": "Overridden Title", "custom_field": "Custom Value"}
        )
        
        assert os.path.exists(result)
    
    def test_generate_from_string(self, generator, temp_dir):
        """Test generating PDF from string content."""
        content = """# Test Document

This is a test document generated from a string.

## Features

- Feature 1
- Feature 2
"""
        output_path = os.path.join(temp_dir, "from_string.pdf")
        
        result = generator.generate_from_string(
            content,
            output_path,
            input_format="markdown",
            metadata={"title": "String Document"}
        )
        
        assert os.path.exists(result)
    
    def test_generate_file_not_found(self, generator, temp_dir):
        """Test error handling for missing input file."""
        with pytest.raises(FileNotFoundError):
            generator.generate(
                "/nonexistent/path/file.md",
                os.path.join(temp_dir, "output.pdf")
            )
    
    def test_generate_unsupported_format(self, generator, temp_dir):
        """Test error handling for unsupported format."""
        # Create a file with unsupported extension
        input_path = os.path.join(temp_dir, "input.xyz")
        with open(input_path, 'w') as f:
            f.write("Some content")
        
        with pytest.raises(ValueError) as exc_info:
            generator.generate(input_path, os.path.join(temp_dir, "output.pdf"))
        
        assert "Unknown file format" in str(exc_info.value)
    
    def test_generate_creates_output_directory(self, generator, sample_markdown, temp_dir):
        """Test that generate creates output directory if needed."""
        input_path = os.path.join(temp_dir, "input.md")
        with open(input_path, 'w') as f:
            f.write(sample_markdown)
        
        output_dir = os.path.join(temp_dir, "nested", "output", "dir")
        output_path = os.path.join(output_dir, "output.pdf")
        
        result = generator.generate(input_path, output_path)
        
        assert os.path.exists(result)
        assert os.path.isdir(output_dir)


class TestPDFGeneratorIntegration:
    """Integration tests for PDFGenerator."""
    
    @pytest.fixture
    def generator(self, template_dir):
        """Create a PDFGenerator for testing."""
        return PDFGenerator(
            template="ford_release_notes",
            template_paths=[str(template_dir)]
        )
    
    def test_full_workflow_markdown(self, generator, temp_dir):
        """Test full workflow from Markdown to PDF."""
        # Create a comprehensive Markdown document
        markdown_content = """---
title: "Integration Test Document"
version: "1.0.0"
date: "2026-02-17"
author: "Test Suite"
confidentiality: "Internal Use Only"
---

# Integration Test

## Overview

This document tests the full integration of the PDF generator.
It includes **bold**, *italic*, and `code` formatting.

## Table Example

| Column A | Column B | Column C |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |

## List Example

### Unordered List

- First item
- Second item
- Third item

### Ordered List

1. Step one
2. Step two
3. Step three

## Code Block

```python
def example():
    return "Hello, World!"
```

## Conclusion

This concludes the integration test document.
"""
        
        input_path = os.path.join(temp_dir, "integration.md")
        with open(input_path, 'w') as f:
            f.write(markdown_content)
        
        output_path = os.path.join(temp_dir, "integration.pdf")
        
        result = generator.generate(input_path, output_path)
        
        assert os.path.exists(result)
        
        # Check file size is reasonable (not empty, not too small)
        file_size = os.path.getsize(result)
        assert file_size > 1000  # At least 1KB
    
    def test_template_switching(self, template_dir, temp_dir):
        """Test generating same content with different templates."""
        content = """# Test Document

This is a simple test document.

## Section

Some content here.
"""
        
        input_path = os.path.join(temp_dir, "test.md")
        with open(input_path, 'w') as f:
            f.write(content)
        
        # Generate with Ford template
        gen1 = PDFGenerator(
            template="ford_release_notes",
            template_paths=[str(template_dir)]
        )
        output1 = os.path.join(temp_dir, "ford_output.pdf")
        gen1.generate(input_path, output1)
        
        # Generate with generic template
        gen2 = PDFGenerator(
            template="generic",
            template_paths=[str(template_dir)]
        )
        output2 = os.path.join(temp_dir, "generic_output.pdf")
        gen2.generate(input_path, output2)
        
        # Both should exist and be different
        assert os.path.exists(output1)
        assert os.path.exists(output2)
        
        # File sizes should be different (different styling)
        size1 = os.path.getsize(output1)
        size2 = os.path.getsize(output2)
        
        # Both should be valid PDFs
        with open(output1, 'rb') as f:
            assert f.read(4) == b'%PDF'
        with open(output2, 'rb') as f:
            assert f.read(4) == b'%PDF'
