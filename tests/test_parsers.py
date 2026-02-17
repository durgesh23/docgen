"""
Tests for the Markdown and AsciiDoc parsers.
"""

import pytest

from docgen.parsers import MarkdownParser, AsciiDocParser
from docgen.models import ElementType, TextSpan


class TestMarkdownParser:
    """Tests for MarkdownParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MarkdownParser()
    
    def test_supported_extensions(self):
        """Test that parser reports correct file extensions."""
        assert ".md" in self.parser.supported_extensions
        assert ".markdown" in self.parser.supported_extensions
    
    def test_can_parse_markdown_file(self):
        """Test can_parse method for Markdown files."""
        assert self.parser.can_parse("test.md")
        assert self.parser.can_parse("document.markdown")
        assert not self.parser.can_parse("test.txt")
        assert not self.parser.can_parse("test.adoc")
    
    def test_extract_metadata_from_front_matter(self):
        """Test extracting metadata from YAML front matter."""
        content = """---
title: "Test Title"
version: "1.0"
author: "Test Author"
---

# Heading
Content here.
"""
        metadata = self.parser.extract_metadata(content)
        
        assert metadata["title"] == "Test Title"
        assert metadata["version"] == "1.0"
        assert metadata["author"] == "Test Author"
    
    def test_extract_metadata_no_front_matter(self):
        """Test extraction when no front matter present."""
        content = "# Just a Heading\n\nSome content."
        metadata = self.parser.extract_metadata(content)
        
        assert metadata == {}
    
    def test_parse_headings(self):
        """Test parsing of heading levels."""
        content = """# Heading 1
## Heading 2
### Heading 3
#### Heading 4
"""
        document = self.parser.parse(content)
        
        assert len(document.elements) == 4
        assert document.elements[0].element_type == ElementType.HEADING1
        assert document.elements[1].element_type == ElementType.HEADING2
        assert document.elements[2].element_type == ElementType.HEADING3
        assert document.elements[3].element_type == ElementType.HEADING4
    
    def test_parse_paragraph(self):
        """Test parsing of paragraphs."""
        content = """This is a simple paragraph.

This is another paragraph.
"""
        document = self.parser.parse(content)
        
        assert len(document.elements) == 2
        assert document.elements[0].element_type == ElementType.PARAGRAPH
        assert document.elements[1].element_type == ElementType.PARAGRAPH
    
    def test_parse_bold_text(self):
        """Test parsing of bold formatting."""
        content = "This has **bold** text."
        document = self.parser.parse(content)
        
        assert len(document.elements) == 1
        spans = document.elements[0].content
        
        # Find the bold span
        bold_spans = [s for s in spans if isinstance(s, TextSpan) and s.bold]
        assert len(bold_spans) == 1
        assert bold_spans[0].text == "bold"
    
    def test_parse_italic_text(self):
        """Test parsing of italic formatting."""
        content = "This has *italic* text."
        document = self.parser.parse(content)
        
        assert len(document.elements) == 1
        spans = document.elements[0].content
        
        # Find the italic span
        italic_spans = [s for s in spans if isinstance(s, TextSpan) and s.italic]
        assert len(italic_spans) == 1
        assert italic_spans[0].text == "italic"
    
    def test_parse_inline_code(self):
        """Test parsing of inline code."""
        content = "Use the `print()` function."
        document = self.parser.parse(content)
        
        assert len(document.elements) == 1
        spans = document.elements[0].content
        
        # Find the code span
        code_spans = [s for s in spans if isinstance(s, TextSpan) and s.code]
        assert len(code_spans) == 1
        assert code_spans[0].text == "print()"
    
    def test_parse_unordered_list(self):
        """Test parsing of unordered lists."""
        content = """- Item 1
- Item 2
- Item 3
"""
        document = self.parser.parse(content)
        
        assert len(document.elements) == 1
        assert document.elements[0].element_type == ElementType.UNORDERED_LIST
        assert len(document.elements[0].content) == 3
    
    def test_parse_ordered_list(self):
        """Test parsing of ordered lists."""
        content = """1. First item
2. Second item
3. Third item
"""
        document = self.parser.parse(content)
        
        assert len(document.elements) == 1
        assert document.elements[0].element_type == ElementType.ORDERED_LIST
        assert len(document.elements[0].content) == 3
    
    def test_parse_table(self):
        """Test parsing of Markdown tables."""
        content = """| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        document = self.parser.parse(content)
        
        assert len(document.elements) == 1
        assert document.elements[0].element_type == ElementType.TABLE
        
        table = document.elements[0].content
        assert len(table.rows) == 3  # Header + 2 body rows
        assert table.rows[0].is_header
    
    def test_parse_code_block(self):
        """Test parsing of fenced code blocks."""
        content = """```python
def hello():
    print("Hello")
```
"""
        document = self.parser.parse(content)
        
        assert len(document.elements) == 1
        assert document.elements[0].element_type == ElementType.CODE_BLOCK
        assert document.elements[0].attributes.get("language") == "python"
        assert "def hello():" in document.elements[0].content
    
    def test_parse_blockquote(self):
        """Test parsing of blockquotes."""
        content = """> This is a quote.
> It spans multiple lines.
"""
        document = self.parser.parse(content)
        
        assert len(document.elements) == 1
        assert document.elements[0].element_type == ElementType.BLOCKQUOTE
    
    def test_parse_horizontal_rule(self):
        """Test parsing of horizontal rules."""
        content = """Some text.

---

More text.
"""
        document = self.parser.parse(content)
        
        hr_elements = [e for e in document.elements if e.element_type == ElementType.HORIZONTAL_RULE]
        assert len(hr_elements) == 1
    
    def test_parse_complete_document(self, sample_markdown):
        """Test parsing a complete Markdown document."""
        document = self.parser.parse(sample_markdown)
        
        # Check metadata
        assert document.metadata.title == "Test Document"
        assert document.metadata.version == "1.0.0"
        assert document.metadata.author == "Test Author"
        
        # Check structure
        assert len(document.elements) > 0
        
        # Check for expected element types
        element_types = [e.element_type for e in document.elements]
        assert ElementType.HEADING1 in element_types
        assert ElementType.HEADING2 in element_types
        assert ElementType.PARAGRAPH in element_types
        assert ElementType.UNORDERED_LIST in element_types
        assert ElementType.TABLE in element_types
        assert ElementType.CODE_BLOCK in element_types


class TestAsciiDocParser:
    """Tests for AsciiDocParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = AsciiDocParser()
    
    def test_supported_extensions(self):
        """Test that parser reports correct file extensions."""
        assert ".adoc" in self.parser.supported_extensions
        assert ".asciidoc" in self.parser.supported_extensions
    
    def test_can_parse_asciidoc_file(self):
        """Test can_parse method for AsciiDoc files."""
        assert self.parser.can_parse("test.adoc")
        assert self.parser.can_parse("document.asciidoc")
        assert not self.parser.can_parse("test.md")
        assert not self.parser.can_parse("test.txt")
    
    def test_extract_metadata_from_attributes(self):
        """Test extracting metadata from AsciiDoc attributes."""
        content = """= Document Title
:version: 1.0
:author: Test Author
:date: 2026-02-17

== Introduction
Content here.
"""
        metadata = self.parser.extract_metadata(content)
        
        assert metadata["title"] == "Document Title"
        assert metadata["version"] == "1.0"
        assert metadata["author"] == "Test Author"
    
    def test_parse_section_headings(self):
        """Test parsing of section headings."""
        content = """= Title

== Section 1

=== Subsection 1.1

== Section 2
"""
        document = self.parser.parse(content)
        
        heading_elements = [e for e in document.elements 
                          if e.element_type in (ElementType.HEADING1, ElementType.HEADING2)]
        assert len(heading_elements) >= 2
    
    def test_parse_unordered_list(self):
        """Test parsing of unordered lists."""
        content = """= Title

* Item 1
* Item 2
* Item 3
"""
        document = self.parser.parse(content)
        
        list_elements = [e for e in document.elements 
                        if e.element_type == ElementType.UNORDERED_LIST]
        assert len(list_elements) == 1
        assert len(list_elements[0].content) == 3
    
    def test_parse_ordered_list(self):
        """Test parsing of ordered lists."""
        content = """= Title

. First
. Second
. Third
"""
        document = self.parser.parse(content)
        
        list_elements = [e for e in document.elements 
                        if e.element_type == ElementType.ORDERED_LIST]
        assert len(list_elements) == 1
        assert len(list_elements[0].content) == 3
    
    def test_parse_table(self):
        """Test parsing of AsciiDoc tables."""
        content = """= Title

|===
|Header 1 |Header 2

|Cell 1 |Cell 2
|Cell 3 |Cell 4
|===
"""
        document = self.parser.parse(content)
        
        table_elements = [e for e in document.elements 
                         if e.element_type == ElementType.TABLE]
        assert len(table_elements) == 1
    
    def test_parse_code_block(self):
        """Test parsing of source code blocks."""
        content = """= Title

[source,python]
----
def hello():
    print("Hello")
----
"""
        document = self.parser.parse(content)
        
        code_elements = [e for e in document.elements 
                        if e.element_type == ElementType.CODE_BLOCK]
        assert len(code_elements) == 1
        assert "def hello():" in code_elements[0].content
    
    def test_parse_complete_document(self, sample_asciidoc):
        """Test parsing a complete AsciiDoc document."""
        document = self.parser.parse(sample_asciidoc)
        
        # Check metadata
        assert document.metadata.version == "1.0.0"
        assert document.metadata.author == "Test Author"
        
        # Check structure
        assert len(document.elements) > 0
        
        # Check for expected element types
        element_types = [e.element_type for e in document.elements]
        assert any(et in element_types for et in 
                   [ElementType.HEADING1, ElementType.HEADING2])
