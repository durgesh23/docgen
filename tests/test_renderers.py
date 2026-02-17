"""
Tests for the PDF renderer.
"""

import os
import tempfile
from pathlib import Path
import pytest

from docgen.renderers.styles import StyleManager
from docgen.renderers.pdf_renderer import PDFRenderer
from docgen.models import (
    Document, 
    DocumentMetadata, 
    DocumentElement, 
    ElementType,
    TextSpan,
    Table,
    TableRow,
    TableCell,
    ListItem,
)


class TestStyleManager:
    """Tests for StyleManager class."""
    
    @pytest.fixture
    def style_manager(self, template_dir):
        """Create a StyleManager for testing."""
        ford_template = template_dir / "ford_release_notes"
        return StyleManager(str(ford_template))
    
    def test_load_configs(self, style_manager):
        """Test that configuration files are loaded."""
        assert style_manager.template_name == "Ford Release Notes"
        assert style_manager.page_size in ["LETTER", "A4"]
    
    def test_get_style(self, style_manager):
        """Test getting a paragraph style."""
        style = style_manager.get_style("paragraph")
        
        assert style is not None
        assert style.name == "paragraph"
        assert style.fontSize > 0
    
    def test_get_style_fallback(self, style_manager):
        """Test fallback to default style."""
        style = style_manager.get_style("nonexistent_style")
        
        # Should return default or fallback style
        assert style is not None
    
    def test_get_color(self, style_manager):
        """Test getting a named color."""
        color = style_manager.get_color("primary")
        
        assert color is not None
    
    def test_get_margins(self, style_manager):
        """Test getting page margins."""
        margins = style_manager.get_margins()
        
        assert len(margins) == 4
        assert all(m > 0 for m in margins)
    
    def test_get_table_config(self, style_manager):
        """Test getting table configuration."""
        config = style_manager.get_table_config()
        
        assert isinstance(config, dict)
        assert "border_width" in config or config == {}
    
    def test_get_header_config(self, style_manager):
        """Test getting header configuration."""
        config = style_manager.get_header_config()
        
        assert isinstance(config, dict)


class TestPDFRenderer:
    """Tests for PDFRenderer class."""
    
    @pytest.fixture
    def renderer(self, template_dir):
        """Create a PDFRenderer for testing."""
        ford_template = template_dir / "ford_release_notes"
        style_manager = StyleManager(str(ford_template))
        return PDFRenderer(style_manager)
    
    @pytest.fixture
    def simple_document(self):
        """Create a simple document for testing."""
        metadata = DocumentMetadata(
            title="Test Document",
            version="1.0.0",
            date="2026-02-17",
            author="Test Author",
            confidentiality="Confidential"
        )
        
        elements = [
            DocumentElement(
                element_type=ElementType.HEADING1,
                content=[TextSpan(text="Introduction")],
                attributes={"id": "introduction"}
            ),
            DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content=[TextSpan(text="This is a test paragraph with "),
                        TextSpan(text="bold", bold=True),
                        TextSpan(text=" text.")]
            ),
        ]
        
        return Document(metadata=metadata, elements=elements)
    
    def test_render_creates_pdf(self, renderer, simple_document, temp_dir):
        """Test that render creates a PDF file."""
        output_path = os.path.join(temp_dir, "output.pdf")
        
        result = renderer.render(simple_document, output_path)
        
        assert os.path.exists(result)
        assert result == output_path
        
        # Check file is valid PDF (starts with %PDF)
        with open(result, 'rb') as f:
            header = f.read(4)
            assert header == b'%PDF'
    
    def test_render_with_metadata_override(self, renderer, simple_document, temp_dir):
        """Test rendering with metadata override."""
        output_path = os.path.join(temp_dir, "output.pdf")
        
        result = renderer.render(
            simple_document, 
            output_path,
            metadata_override={"title": "Overridden Title"}
        )
        
        assert os.path.exists(result)
    
    def test_render_table(self, renderer, temp_dir):
        """Test rendering a document with a table."""
        metadata = DocumentMetadata(title="Table Test")
        
        table = Table(rows=[
            TableRow(
                cells=[
                    TableCell(content="Header 1", is_header=True),
                    TableCell(content="Header 2", is_header=True),
                ],
                is_header=True
            ),
            TableRow(cells=[
                TableCell(content="Cell 1"),
                TableCell(content="Cell 2"),
            ]),
        ])
        
        elements = [
            DocumentElement(element_type=ElementType.TABLE, content=table)
        ]
        
        document = Document(metadata=metadata, elements=elements)
        output_path = os.path.join(temp_dir, "table_output.pdf")
        
        result = renderer.render(document, output_path)
        
        assert os.path.exists(result)
    
    def test_render_list(self, renderer, temp_dir):
        """Test rendering a document with a list."""
        metadata = DocumentMetadata(title="List Test")
        
        items = [
            ListItem(content=[TextSpan(text="Item 1")]),
            ListItem(content=[TextSpan(text="Item 2")]),
            ListItem(content=[TextSpan(text="Item 3")]),
        ]
        
        elements = [
            DocumentElement(element_type=ElementType.UNORDERED_LIST, content=items)
        ]
        
        document = Document(metadata=metadata, elements=elements)
        output_path = os.path.join(temp_dir, "list_output.pdf")
        
        result = renderer.render(document, output_path)
        
        assert os.path.exists(result)
    
    def test_render_code_block(self, renderer, temp_dir):
        """Test rendering a document with a code block."""
        metadata = DocumentMetadata(title="Code Test")
        
        elements = [
            DocumentElement(
                element_type=ElementType.CODE_BLOCK,
                content='def hello():\n    print("Hello")',
                attributes={"language": "python"}
            )
        ]
        
        document = Document(metadata=metadata, elements=elements)
        output_path = os.path.join(temp_dir, "code_output.pdf")
        
        result = renderer.render(document, output_path)
        
        assert os.path.exists(result)
    
    def test_render_multiple_headings(self, renderer, temp_dir):
        """Test rendering document with multiple heading levels."""
        metadata = DocumentMetadata(title="Headings Test")
        
        elements = [
            DocumentElement(
                element_type=ElementType.HEADING1,
                content=[TextSpan(text="Heading 1")]
            ),
            DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content=[TextSpan(text="Content under h1.")]
            ),
            DocumentElement(
                element_type=ElementType.HEADING2,
                content=[TextSpan(text="Heading 2")]
            ),
            DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content=[TextSpan(text="Content under h2.")]
            ),
            DocumentElement(
                element_type=ElementType.HEADING3,
                content=[TextSpan(text="Heading 3")]
            ),
            DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content=[TextSpan(text="Content under h3.")]
            ),
        ]
        
        document = Document(metadata=metadata, elements=elements)
        output_path = os.path.join(temp_dir, "headings_output.pdf")
        
        result = renderer.render(document, output_path)
        
        assert os.path.exists(result)
    
    def test_spans_to_html(self, renderer):
        """Test converting TextSpan list to HTML."""
        spans = [
            TextSpan(text="Normal "),
            TextSpan(text="bold", bold=True),
            TextSpan(text=" and "),
            TextSpan(text="italic", italic=True),
            TextSpan(text=" and "),
            TextSpan(text="code", code=True),
        ]
        
        html = renderer._spans_to_html(spans)
        
        assert "<b>bold</b>" in html
        assert "<i>italic</i>" in html
        assert "code" in html
    
    def test_escape_html(self, renderer):
        """Test HTML escaping."""
        text = "a < b > c & d"
        escaped = renderer._escape_html(text)
        
        assert "&lt;" in escaped
        assert "&gt;" in escaped
        assert "&amp;" in escaped
    
    def test_render_admonition(self, renderer, temp_dir):
        """Test rendering a document with an admonition."""
        metadata = DocumentMetadata(title="Admonition Test")
        
        elements = [
            DocumentElement(
                element_type=ElementType.HEADING1,
                content=[TextSpan(text="Introduction")]
            ),
            DocumentElement(
                element_type=ElementType.ADMONITION,
                content=[TextSpan(text="This is an important note.")],
                attributes={"type": "NOTE"}
            ),
            DocumentElement(
                element_type=ElementType.ADMONITION,
                content=[TextSpan(text="This is a warning message.")],
                attributes={"type": "WARNING"}
            ),
        ]
        
        document = Document(metadata=metadata, elements=elements)
        output_path = os.path.join(temp_dir, "admonition_output.pdf")
        
        result = renderer.render(document, output_path)
        
        assert os.path.exists(result)
    
    def test_render_image_placeholder(self, renderer, temp_dir):
        """Test rendering a document with an image (placeholder for missing image)."""
        metadata = DocumentMetadata(title="Image Test")
        
        elements = [
            DocumentElement(
                element_type=ElementType.HEADING1,
                content=[TextSpan(text="Images")]
            ),
            DocumentElement(
                element_type=ElementType.IMAGE,
                content="nonexistent_image.png",
                attributes={"alt": "Test Image"}
            ),
        ]
        
        document = Document(metadata=metadata, elements=elements)
        output_path = os.path.join(temp_dir, "image_output.pdf")
        
        result = renderer.render(document, output_path)
        
        # Should render a placeholder for missing image
        assert os.path.exists(result)
    
    def test_render_toc(self, renderer, temp_dir):
        """Test rendering a document with table of contents."""
        metadata = DocumentMetadata(title="TOC Test")
        
        elements = [
            DocumentElement(
                element_type=ElementType.TOC,
                content=None
            ),
            DocumentElement(
                element_type=ElementType.HEADING1,
                content=[TextSpan(text="Chapter 1")]
            ),
            DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content=[TextSpan(text="Content for chapter 1.")]
            ),
            DocumentElement(
                element_type=ElementType.HEADING2,
                content=[TextSpan(text="Section 1.1")]
            ),
            DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content=[TextSpan(text="Content for section 1.1.")]
            ),
        ]
        
        document = Document(metadata=metadata, elements=elements)
        output_path = os.path.join(temp_dir, "toc_output.pdf")
        
        result = renderer.render(document, output_path)
        
        assert os.path.exists(result)
