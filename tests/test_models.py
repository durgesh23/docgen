"""
Tests for document models.
"""

import pytest

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


class TestTextSpan:
    """Tests for TextSpan class."""
    
    def test_basic_text_span(self):
        """Test basic text span creation."""
        span = TextSpan(text="Hello")
        
        assert span.text == "Hello"
        assert not span.bold
        assert not span.italic
        assert not span.code
        assert span.link is None
    
    def test_formatted_text_span(self):
        """Test formatted text span."""
        span = TextSpan(text="Bold", bold=True)
        
        assert span.text == "Bold"
        assert span.bold
        assert not span.italic
    
    def test_str_representation(self):
        """Test string representation."""
        span = TextSpan(text="Test")
        
        assert str(span) == "Test"


class TestTableCell:
    """Tests for TableCell class."""
    
    def test_basic_cell(self):
        """Test basic cell creation."""
        cell = TableCell(content="Value")
        
        assert cell.content == "Value"
        assert cell.colspan == 1
        assert cell.rowspan == 1
        assert cell.alignment == "left"
        assert not cell.is_header
    
    def test_header_cell(self):
        """Test header cell."""
        cell = TableCell(content="Header", is_header=True)
        
        assert cell.is_header
    
    def test_get_text_string(self):
        """Test get_text with string content."""
        cell = TableCell(content="Value")
        
        assert cell.get_text() == "Value"
    
    def test_get_text_spans(self):
        """Test get_text with TextSpan content."""
        cell = TableCell(content=[
            TextSpan(text="Hello "),
            TextSpan(text="World")
        ])
        
        assert cell.get_text() == "Hello World"


class TestTable:
    """Tests for Table class."""
    
    def test_basic_table(self):
        """Test basic table creation."""
        table = Table(rows=[
            TableRow(cells=[TableCell(content="A")], is_header=True),
            TableRow(cells=[TableCell(content="B")]),
        ])
        
        assert len(table.rows) == 2
    
    def test_header_rows(self):
        """Test getting header rows."""
        table = Table(rows=[
            TableRow(cells=[TableCell(content="H1")], is_header=True),
            TableRow(cells=[TableCell(content="H2")], is_header=True),
            TableRow(cells=[TableCell(content="D1")]),
        ])
        
        headers = table.header_rows
        assert len(headers) == 2
    
    def test_body_rows(self):
        """Test getting body rows."""
        table = Table(rows=[
            TableRow(cells=[TableCell(content="H1")], is_header=True),
            TableRow(cells=[TableCell(content="D1")]),
            TableRow(cells=[TableCell(content="D2")]),
        ])
        
        body = table.body_rows
        assert len(body) == 2
    
    def test_num_columns(self):
        """Test getting number of columns."""
        table = Table(rows=[
            TableRow(cells=[
                TableCell(content="A"),
                TableCell(content="B"),
                TableCell(content="C"),
            ]),
        ])
        
        assert table.num_columns == 3


class TestListItem:
    """Tests for ListItem class."""
    
    def test_basic_list_item(self):
        """Test basic list item."""
        item = ListItem(content="Item text")
        
        assert item.get_text() == "Item text"
        assert len(item.children) == 0
    
    def test_list_item_with_children(self):
        """Test list item with nested children."""
        item = ListItem(
            content="Parent",
            children=[
                ListItem(content="Child 1"),
                ListItem(content="Child 2"),
            ]
        )
        
        assert len(item.children) == 2


class TestDocumentElement:
    """Tests for DocumentElement class."""
    
    def test_basic_element(self):
        """Test basic element creation."""
        element = DocumentElement(
            element_type=ElementType.PARAGRAPH,
            content="Test content"
        )
        
        assert element.element_type == ElementType.PARAGRAPH
        assert element.content == "Test content"
    
    def test_get_text_string(self):
        """Test get_text with string content."""
        element = DocumentElement(
            element_type=ElementType.PARAGRAPH,
            content="Test"
        )
        
        assert element.get_text() == "Test"
    
    def test_get_text_spans(self):
        """Test get_text with TextSpan list."""
        element = DocumentElement(
            element_type=ElementType.PARAGRAPH,
            content=[
                TextSpan(text="Hello "),
                TextSpan(text="World")
            ]
        )
        
        assert element.get_text() == "Hello World"
    
    def test_heading_level(self):
        """Test heading level property."""
        h1 = DocumentElement(element_type=ElementType.HEADING1, content="H1")
        h2 = DocumentElement(element_type=ElementType.HEADING2, content="H2")
        p = DocumentElement(element_type=ElementType.PARAGRAPH, content="P")
        
        assert h1.level == 1
        assert h2.level == 2
        assert p.level is None


class TestDocumentMetadata:
    """Tests for DocumentMetadata class."""
    
    def test_basic_metadata(self):
        """Test basic metadata creation."""
        meta = DocumentMetadata(
            title="Test",
            version="1.0",
            author="Author"
        )
        
        assert meta.title == "Test"
        assert meta.version == "1.0"
        assert meta.author == "Author"
    
    def test_get_method(self):
        """Test get method."""
        meta = DocumentMetadata(title="Test")
        
        assert meta.get("title") == "Test"
        assert meta.get("nonexistent", "default") == "default"
    
    def test_custom_fields(self):
        """Test custom metadata fields."""
        meta = DocumentMetadata(
            title="Test",
            custom={"custom_field": "custom_value"}
        )
        
        assert meta.get("custom_field") == "custom_value"
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        meta = DocumentMetadata(
            title="Test",
            version="1.0",
            custom={"extra": "value"}
        )
        
        d = meta.to_dict()
        
        assert d["title"] == "Test"
        assert d["version"] == "1.0"
        assert d["extra"] == "value"
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "title": "Test",
            "version": "1.0",
            "custom_field": "custom_value"
        }
        
        meta = DocumentMetadata.from_dict(data)
        
        assert meta.title == "Test"
        assert meta.version == "1.0"
        assert meta.get("custom_field") == "custom_value"


class TestDocument:
    """Tests for Document class."""
    
    @pytest.fixture
    def sample_document(self):
        """Create a sample document."""
        metadata = DocumentMetadata(title="Test Document")
        elements = [
            DocumentElement(
                element_type=ElementType.HEADING1,
                content="Section 1",
                attributes={"id": "section-1"}
            ),
            DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content="Paragraph 1"
            ),
            DocumentElement(
                element_type=ElementType.HEADING2,
                content="Subsection 1.1",
                attributes={"id": "subsection-1-1"}
            ),
            DocumentElement(
                element_type=ElementType.PARAGRAPH,
                content="Paragraph 2"
            ),
        ]
        return Document(metadata=metadata, elements=elements)
    
    def test_basic_document(self, sample_document):
        """Test basic document creation."""
        assert sample_document.metadata.title == "Test Document"
        assert len(sample_document.elements) == 4
    
    def test_get_headings(self, sample_document):
        """Test getting headings."""
        headings = sample_document.get_headings()
        
        assert len(headings) == 2
        assert headings[0].element_type == ElementType.HEADING1
        assert headings[1].element_type == ElementType.HEADING2
    
    def test_get_headings_with_max_level(self, sample_document):
        """Test getting headings with max level filter."""
        headings = sample_document.get_headings(max_level=1)
        
        assert len(headings) == 1
        assert headings[0].element_type == ElementType.HEADING1
    
    def test_get_toc_entries(self, sample_document):
        """Test getting TOC entries."""
        toc = sample_document.get_toc_entries(max_depth=2)
        
        assert len(toc) == 2
        assert toc[0] == (1, "Section 1", "section-1")
        assert toc[1] == (2, "Subsection 1.1", "subsection-1-1")
