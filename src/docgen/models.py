"""
Document models for the PDF generator.

This module defines the data structures used to represent
parsed documents in an intermediate format.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ElementType(Enum):
    """Types of document elements."""
    TITLE = "title"
    HEADING1 = "heading1"
    HEADING2 = "heading2"
    HEADING3 = "heading3"
    HEADING4 = "heading4"
    HEADING5 = "heading5"
    HEADING6 = "heading6"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    LIST_ITEM = "list_item"
    CODE_BLOCK = "code_block"
    BLOCKQUOTE = "blockquote"
    HORIZONTAL_RULE = "horizontal_rule"
    IMAGE = "image"
    RAW_HTML = "raw_html"
    PAGE_BREAK = "page_break"
    TOC = "toc"
    ADMONITION = "admonition"


@dataclass
class TextSpan:
    """Represents a span of formatted text."""
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    link: Optional[str] = None
    
    def __str__(self) -> str:
        return self.text


@dataclass
class TableCell:
    """Represents a cell in a table."""
    content: Union[str, List[TextSpan]]
    colspan: int = 1
    rowspan: int = 1
    alignment: str = "left"  # left, center, right
    is_header: bool = False
    
    def get_text(self) -> str:
        """Get plain text content of the cell."""
        if isinstance(self.content, str):
            return self.content
        return "".join(str(span) for span in self.content)


@dataclass
class TableRow:
    """Represents a row in a table."""
    cells: List[TableCell]
    is_header: bool = False


@dataclass
class Table:
    """Represents a table structure."""
    rows: List[TableRow]
    column_widths: Optional[List[float]] = None  # Proportional widths
    caption: Optional[str] = None
    
    @property
    def header_rows(self) -> List[TableRow]:
        """Get header rows."""
        return [row for row in self.rows if row.is_header]
    
    @property
    def body_rows(self) -> List[TableRow]:
        """Get body rows."""
        return [row for row in self.rows if not row.is_header]
    
    @property
    def num_columns(self) -> int:
        """Get number of columns."""
        if not self.rows:
            return 0
        return max(len(row.cells) for row in self.rows)


@dataclass
class ListItem:
    """Represents a list item."""
    content: Union[str, List[TextSpan]]
    children: List["ListItem"] = field(default_factory=list)
    
    def get_text(self) -> str:
        """Get plain text content."""
        if isinstance(self.content, str):
            return self.content
        return "".join(str(span) for span in self.content)


@dataclass
class DocumentElement:
    """
    Represents a single element in a document.
    
    Attributes:
        element_type: The type of element (heading, paragraph, table, etc.)
        content: The content of the element (varies by type)
        attributes: Additional attributes specific to the element type
        children: Child elements (for nested structures)
    """
    element_type: ElementType
    content: Any  # str, List[TextSpan], Table, List[ListItem], etc.
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List["DocumentElement"] = field(default_factory=list)
    
    def get_text(self) -> str:
        """Get plain text representation of the element."""
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, list):
            if all(isinstance(item, TextSpan) for item in self.content):
                return "".join(str(span) for span in self.content)
            elif all(isinstance(item, ListItem) for item in self.content):
                return "\n".join(item.get_text() for item in self.content)
        elif isinstance(self.content, Table):
            # Return table as text representation
            lines = []
            for row in self.content.rows:
                cells = [cell.get_text() for cell in row.cells]
                lines.append(" | ".join(cells))
            return "\n".join(lines)
        return str(self.content) if self.content else ""
    
    @property
    def level(self) -> Optional[int]:
        """Get heading level if this is a heading element."""
        heading_levels = {
            ElementType.HEADING1: 1,
            ElementType.HEADING2: 2,
            ElementType.HEADING3: 3,
            ElementType.HEADING4: 4,
            ElementType.HEADING5: 5,
            ElementType.HEADING6: 6,
        }
        return heading_levels.get(self.element_type)


@dataclass
class DocumentMetadata:
    """
    Document metadata extracted from front matter.
    
    Attributes:
        title: Document title
        author: Document author
        date: Document date
        version: Document version
        confidentiality: Confidentiality notice
        custom: Additional custom metadata fields
    """
    title: str = ""
    author: str = ""
    date: str = ""
    version: str = ""
    confidentiality: str = ""
    document_number: str = ""
    revision: str = ""
    organization: str = ""
    custom: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = "") -> Any:
        """Get metadata value by key."""
        # Check standard attributes first
        if hasattr(self, key) and key != "custom":
            value = getattr(self, key)
            return value if value else default
        # Check custom fields
        return self.custom.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        result = {
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "version": self.version,
            "confidentiality": self.confidentiality,
            "document_number": self.document_number,
            "revision": self.revision,
            "organization": self.organization,
        }
        result.update(self.custom)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentMetadata":
        """Create metadata from dictionary."""
        known_fields = {
            "title", "author", "date", "version", 
            "confidentiality", "document_number", 
            "revision", "organization"
        }
        
        standard = {k: v for k, v in data.items() if k in known_fields}
        custom = {k: v for k, v in data.items() if k not in known_fields}
        
        return cls(**standard, custom=custom)


@dataclass
class Document:
    """
    Represents a complete parsed document.
    
    Attributes:
        metadata: Document metadata (title, author, etc.)
        elements: List of document elements in order
        source_format: Original format (markdown, asciidoc)
        source_path: Path to source file (if applicable)
    """
    metadata: DocumentMetadata
    elements: List[DocumentElement]
    source_format: str = "markdown"
    source_path: Optional[str] = None
    
    def get_headings(self, max_level: int = 6) -> List[DocumentElement]:
        """Get all headings up to specified level."""
        heading_types = {
            ElementType.HEADING1,
            ElementType.HEADING2,
            ElementType.HEADING3,
            ElementType.HEADING4,
            ElementType.HEADING5,
            ElementType.HEADING6,
        }
        return [
            elem for elem in self.elements
            if elem.element_type in heading_types
            and (elem.level or 0) <= max_level
        ]
    
    def get_toc_entries(self, max_depth: int = 2) -> List[tuple]:
        """
        Get table of contents entries.
        
        Returns list of (level, text, anchor) tuples.
        """
        entries = []
        for elem in self.get_headings(max_depth):
            level = elem.level or 1
            text = elem.get_text()
            anchor = elem.attributes.get("id", text.lower().replace(" ", "-"))
            entries.append((level, text, anchor))
        return entries
