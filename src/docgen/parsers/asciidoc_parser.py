"""
AsciiDoc parser implementation.

This module provides parsing capabilities for AsciiDoc documents.
It uses a pure Python parser for basic AsciiDoc syntax.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from docgen.parsers.base import BaseParser
from docgen.models import (
    Document,
    DocumentElement,
    DocumentMetadata,
    ElementType,
    TextSpan,
    Table,
    TableRow,
    TableCell,
    ListItem,
)


class AsciiDocParser(BaseParser):
    """
    Parser for AsciiDoc documents.
    
    Supports:
    - Document attributes for metadata
    - Section headers (=, ==, etc.)
    - Paragraphs with inline formatting
    - Tables (AsciiDoc table syntax)
    - Ordered and unordered lists
    - Code blocks (delimited)
    - Admonitions (NOTE, TIP, WARNING, etc.)
    """
    
    def __init__(self):
        """Initialize the AsciiDoc parser."""
        super().__init__()
        self._supported_extensions = [".adoc", ".asciidoc", ".asc"]
        
        # Regex patterns
        self._title_pattern = re.compile(r'^=\s+(.+)$')
        self._heading_pattern = re.compile(r'^(={2,6})\s+(.+)$', re.MULTILINE)
        self._attribute_pattern = re.compile(r'^:(\w+):\s*(.*)$')
        self._code_block_start = re.compile(r'^----$|^\[source,?(\w*)\]$')
        self._code_block_end = re.compile(r'^----$')
        self._table_delimiter = re.compile(r'^\|===\s*$')
        self._table_cell_pattern = re.compile(r'^\|(.*)$')
        self._unordered_list_pattern = re.compile(r'^(\*+)\s+(.+)$')
        self._ordered_list_pattern = re.compile(r'^(\.+)\s+(.+)$')
        self._admonition_pattern = re.compile(
            r'^(NOTE|TIP|IMPORTANT|WARNING|CAUTION):\s*(.*)$'
        )
        
        # Inline patterns
        self._bold_pattern = re.compile(r'\*(.+?)\*')
        self._italic_pattern = re.compile(r'_(.+?)_')
        self._mono_pattern = re.compile(r'\+(.+?)\+|`(.+?)`')
        self._link_pattern = re.compile(r'link:([^\[]+)\[([^\]]*)\]')
        self._xref_pattern = re.compile(r'<<([^,>]+)(?:,([^>]+))?>>') 
    
    def parse(
        self,
        content: str,
        metadata_override: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Parse AsciiDoc content into a Document.
        
        Args:
            content: AsciiDoc content string.
            metadata_override: Optional metadata to merge/override.
            
        Returns:
            Parsed Document object.
        """
        # Extract metadata from attributes
        metadata_dict = self.extract_metadata(content)
        
        # Apply overrides
        if metadata_override:
            metadata_dict.update(metadata_override)
        
        metadata = DocumentMetadata.from_dict(metadata_dict)
        
        # Parse content into elements
        elements = self._parse_content(content)
        
        return Document(
            metadata=metadata,
            elements=elements,
            source_format="asciidoc"
        )
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract document attributes as metadata.
        
        Args:
            content: AsciiDoc content.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        metadata = {}
        lines = content.split('\n')
        
        for line in lines:
            # Check for document title
            title_match = self._title_pattern.match(line)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
                continue
            
            # Check for attributes
            attr_match = self._attribute_pattern.match(line)
            if attr_match:
                key = attr_match.group(1)
                value = attr_match.group(2).strip()
                metadata[key] = value
                continue
            
            # Stop at first non-attribute, non-blank, non-title line
            if line.strip() and not line.startswith(':') and not line.startswith('='):
                # Allow blank lines in header
                if not self._title_pattern.match(line):
                    break
        
        return metadata
    
    def _parse_content(self, content: str) -> List[DocumentElement]:
        """Parse content into document elements."""
        elements = []
        lines = content.split('\n')
        i = 0
        
        # Skip document header (title and attributes)
        while i < len(lines):
            line = lines[i]
            if (self._title_pattern.match(line) or 
                self._attribute_pattern.match(line) or
                not line.strip()):
                i += 1
            else:
                break
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            
            # Check for section headers
            heading_match = self._heading_pattern.match(line)
            if heading_match:
                level = len(heading_match.group(1)) - 1  # == is h1
                level = min(level, 6)
                text = heading_match.group(2).strip()
                element_type = getattr(ElementType, f"HEADING{level}")
                elements.append(DocumentElement(
                    element_type=element_type,
                    content=self._parse_inline(text),
                    attributes={"id": self._generate_anchor(text)}
                ))
                i += 1
                continue
            
            # Check for source block annotation
            source_match = re.match(r'^\[source,?(\w*)\]$', line)
            if source_match:
                language = source_match.group(1)
                # Next should be ---- delimited block
                if i + 1 < len(lines) and lines[i + 1].strip() == '----':
                    element, consumed = self._parse_code_block(lines, i + 1, language)
                    if element:
                        elements.append(element)
                    i += consumed + 1
                    continue
                i += 1
                continue
            
            # Check for code block (---- delimiter)
            if line.strip() == '----':
                element, consumed = self._parse_code_block(lines, i)
                if element:
                    elements.append(element)
                i += consumed
                continue
            
            # Check for table
            if self._table_delimiter.match(line):
                element, consumed = self._parse_table(lines, i)
                if element:
                    elements.append(element)
                i += consumed
                continue
            
            # Check for unordered list
            if self._unordered_list_pattern.match(line):
                element, consumed = self._parse_list(lines, i, ordered=False)
                if element:
                    elements.append(element)
                i += consumed
                continue
            
            # Check for ordered list
            if self._ordered_list_pattern.match(line):
                element, consumed = self._parse_list(lines, i, ordered=True)
                if element:
                    elements.append(element)
                i += consumed
                continue
            
            # Check for admonition
            admon_match = self._admonition_pattern.match(line)
            if admon_match:
                elements.append(DocumentElement(
                    element_type=ElementType.ADMONITION,
                    content=self._parse_inline(admon_match.group(2)),
                    attributes={"type": admon_match.group(1)}
                ))
                i += 1
                continue
            
            # Default: paragraph
            element, consumed = self._parse_paragraph(lines, i)
            if element:
                elements.append(element)
            i += consumed
        
        return elements
    
    def _parse_inline(self, text: str) -> List[TextSpan]:
        """Parse inline formatting."""
        spans = []
        
        # Handle monospace/code first
        parts = []
        last_end = 0
        for match in self._mono_pattern.finditer(text):
            if match.start() > last_end:
                parts.append(('text', text[last_end:match.start()]))
            mono_text = match.group(1) or match.group(2)
            parts.append(('code', mono_text))
            last_end = match.end()
        if last_end < len(text):
            parts.append(('text', text[last_end:]))
        
        for part_type, part_text in parts:
            if part_type == 'code':
                spans.append(TextSpan(text=part_text, code=True))
            else:
                spans.extend(self._parse_bold_italic(part_text))
        
        if not spans:
            spans.append(TextSpan(text=text))
        
        return spans
    
    def _parse_bold_italic(self, text: str) -> List[TextSpan]:
        """Parse bold and italic in AsciiDoc style."""
        spans = []
        
        # Process bold (*text*)
        parts = []
        last_end = 0
        for match in self._bold_pattern.finditer(text):
            if match.start() > last_end:
                parts.append(('plain', text[last_end:match.start()]))
            parts.append(('bold', match.group(1)))
            last_end = match.end()
        if last_end < len(text):
            parts.append(('plain', text[last_end:]))
        
        if not parts:
            parts = [('plain', text)]
        
        for part_type, part_text in parts:
            if part_type == 'bold':
                # Check for italic within
                for span in self._parse_italic_only(part_text):
                    span.bold = True
                    spans.append(span)
            else:
                spans.extend(self._parse_italic_only(part_text))
        
        return spans if spans else [TextSpan(text=text)]
    
    def _parse_italic_only(self, text: str) -> List[TextSpan]:
        """Parse italic only (_text_)."""
        spans = []
        last_end = 0
        
        for match in self._italic_pattern.finditer(text):
            if match.start() > last_end:
                plain = text[last_end:match.start()]
                if plain:
                    spans.append(TextSpan(text=plain))
            spans.append(TextSpan(text=match.group(1), italic=True))
            last_end = match.end()
        
        if last_end < len(text):
            remaining = text[last_end:]
            if remaining:
                spans.append(TextSpan(text=remaining))
        
        return spans if spans else [TextSpan(text=text)]
    
    def _generate_anchor(self, text: str) -> str:
        """Generate anchor ID from heading text."""
        anchor = re.sub(r'[^\w\s-]', '', text.lower())
        anchor = re.sub(r'\s+', '-', anchor.strip())
        return f"_{anchor}"
    
    def _parse_code_block(
        self, 
        lines: List[str], 
        start: int,
        language: str = ""
    ) -> Tuple[Optional[DocumentElement], int]:
        """Parse a delimited code block."""
        code_lines = []
        i = start + 1  # Skip opening ----
        
        while i < len(lines):
            if lines[i].strip() == '----':
                i += 1
                break
            code_lines.append(lines[i])
            i += 1
        
        code = '\n'.join(code_lines)
        element = DocumentElement(
            element_type=ElementType.CODE_BLOCK,
            content=code,
            attributes={"language": language}
        )
        
        return element, i - start
    
    def _parse_table(
        self, 
        lines: List[str], 
        start: int
    ) -> Tuple[Optional[DocumentElement], int]:
        """Parse an AsciiDoc table."""
        rows = []
        i = start + 1  # Skip opening |===
        current_row_cells = []
        is_first_row = True
        
        # Check for cols attribute before table
        # For now, simple parsing
        
        while i < len(lines):
            line = lines[i]
            
            # End of table
            if self._table_delimiter.match(line):
                # Save current row if any
                if current_row_cells:
                    rows.append(TableRow(
                        cells=[TableCell(content=c, is_header=is_first_row) 
                               for c in current_row_cells],
                        is_header=is_first_row
                    ))
                i += 1
                break
            
            # Empty line may separate rows
            if not line.strip():
                if current_row_cells:
                    rows.append(TableRow(
                        cells=[TableCell(content=c, is_header=is_first_row) 
                               for c in current_row_cells],
                        is_header=is_first_row
                    ))
                    current_row_cells = []
                    is_first_row = False
                i += 1
                continue
            
            # Parse cells from line
            if line.startswith('|'):
                # Split by | but handle first empty element
                cells = line.split('|')[1:]  # Skip first empty
                cells = [c.strip() for c in cells if c.strip() or cells.index(c) < len(cells) - 1]
                
                if not current_row_cells:
                    current_row_cells = cells
                else:
                    # Continuation or new row
                    # In AsciiDoc, each cell can be on its own line
                    if len(cells) == 1:
                        current_row_cells.append(cells[0])
                    else:
                        # Multiple cells, probably new row
                        if current_row_cells:
                            rows.append(TableRow(
                                cells=[TableCell(content=c, is_header=is_first_row) 
                                       for c in current_row_cells],
                                is_header=is_first_row
                            ))
                            is_first_row = False
                        current_row_cells = cells
            
            i += 1
        
        if not rows:
            return None, i - start
        
        table = Table(rows=rows)
        element = DocumentElement(
            element_type=ElementType.TABLE,
            content=table
        )
        
        return element, i - start
    
    def _parse_list(
        self, 
        lines: List[str], 
        start: int, 
        ordered: bool = False
    ) -> Tuple[Optional[DocumentElement], int]:
        """Parse a list."""
        items = []
        i = start
        pattern = self._ordered_list_pattern if ordered else self._unordered_list_pattern
        base_level = None
        
        while i < len(lines):
            line = lines[i]
            
            if not line.strip():
                i += 1
                continue
            
            match = pattern.match(line)
            if match:
                level = len(match.group(1))
                text = match.group(2)
                
                if base_level is None:
                    base_level = level
                
                if level == base_level:
                    items.append(ListItem(content=self._parse_inline(text)))
                    i += 1
                elif level > base_level:
                    # Nested list
                    nested, consumed = self._parse_list(lines, i, ordered)
                    if items and nested:
                        items[-1].children.extend(nested.content)
                    i += consumed
                else:
                    break
            else:
                # Check for other list type
                other = self._unordered_list_pattern if ordered else self._ordered_list_pattern
                if other.match(line):
                    break
                # Non-list content
                if line.startswith(' ') or line.startswith('\t'):
                    # Continuation
                    if items:
                        prev = items[-1].get_text()
                        items[-1].content = self._parse_inline(prev + ' ' + line.strip())
                    i += 1
                else:
                    break
        
        element_type = ElementType.ORDERED_LIST if ordered else ElementType.UNORDERED_LIST
        element = DocumentElement(
            element_type=element_type,
            content=items
        )
        
        return element, i - start
    
    def _parse_paragraph(
        self, 
        lines: List[str], 
        start: int
    ) -> Tuple[Optional[DocumentElement], int]:
        """Parse a paragraph."""
        para_lines = []
        i = start
        
        while i < len(lines):
            line = lines[i]
            
            if not line.strip():
                break
            
            # Check for block elements
            if (self._heading_pattern.match(line) or
                line.strip() == '----' or
                line.strip() == '|===' or
                self._unordered_list_pattern.match(line) or
                self._ordered_list_pattern.match(line) or
                re.match(r'^\[source', line)):
                break
            
            para_lines.append(line)
            i += 1
        
        if not para_lines:
            return None, 1
        
        text = ' '.join(para_lines)
        element = DocumentElement(
            element_type=ElementType.PARAGRAPH,
            content=self._parse_inline(text)
        )
        
        return element, i - start
