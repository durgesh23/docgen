"""
Markdown parser implementation.

This module provides parsing capabilities for Markdown documents,
including support for YAML front matter, tables, and various
Markdown extensions.
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


class MarkdownParser(BaseParser):
    """
    Parser for Markdown documents.
    
    Supports:
    - YAML front matter for metadata
    - Headers (h1-h6)
    - Paragraphs with inline formatting (bold, italic, code)
    - Tables (GitHub-flavored Markdown)
    - Ordered and unordered lists (including nested)
    - Code blocks
    - Blockquotes
    - Horizontal rules
    - Links and images
    """
    
    def __init__(self):
        """Initialize the Markdown parser."""
        super().__init__()
        self._supported_extensions = [".md", ".markdown"]
        
        # Regex patterns
        self._front_matter_pattern = re.compile(
            r'^---\s*\n(.*?)\n---\s*\n',
            re.DOTALL
        )
        self._heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self._table_row_pattern = re.compile(r'^\|(.+)\|$')
        self._table_separator_pattern = re.compile(r'^\|[\s\-:|]+\|$')
        self._code_block_pattern = re.compile(
            r'^```(\w*)\n(.*?)\n```',
            re.MULTILINE | re.DOTALL
        )
        self._blockquote_pattern = re.compile(r'^>\s*(.*)$', re.MULTILINE)
        self._hr_pattern = re.compile(r'^(\*{3,}|-{3,}|_{3,})$', re.MULTILINE)
        self._unordered_list_pattern = re.compile(r'^(\s*)[-*+]\s+(.+)$')
        self._ordered_list_pattern = re.compile(r'^(\s*)\d+\.\s+(.+)$')
        
        # Inline patterns
        self._bold_pattern = re.compile(r'\*\*(.+?)\*\*|__(.+?)__')
        self._italic_pattern = re.compile(r'\*(.+?)\*|_(.+?)_')
        self._code_inline_pattern = re.compile(r'`([^`]+)`')
        self._link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self._image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    
    def parse(
        self,
        content: str,
        metadata_override: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Parse Markdown content into a Document.
        
        Args:
            content: Markdown content string.
            metadata_override: Optional metadata to merge/override.
            
        Returns:
            Parsed Document object.
        """
        # Extract metadata from front matter
        metadata_dict = self.extract_metadata(content)
        
        # Apply overrides
        if metadata_override:
            metadata_dict.update(metadata_override)
        
        metadata = DocumentMetadata.from_dict(metadata_dict)
        
        # Remove front matter from content
        content = self._remove_front_matter(content)
        
        # Parse content into elements
        elements = self._parse_content(content)
        
        return Document(
            metadata=metadata,
            elements=elements,
            source_format="markdown"
        )
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract YAML front matter metadata.
        
        Args:
            content: Markdown content with optional front matter.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        import yaml
        
        match = self._front_matter_pattern.match(content)
        if not match:
            return {}
        
        try:
            front_matter = match.group(1)
            metadata = yaml.safe_load(front_matter)
            return metadata if isinstance(metadata, dict) else {}
        except yaml.YAMLError:
            return {}
    
    def _remove_front_matter(self, content: str) -> str:
        """Remove YAML front matter from content."""
        return self._front_matter_pattern.sub('', content).strip()
    
    def _parse_content(self, content: str) -> List[DocumentElement]:
        """Parse content into document elements."""
        elements = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            
            # Check for code blocks (multi-line)
            if line.strip().startswith('```'):
                element, consumed = self._parse_code_block(lines, i)
                if element:
                    elements.append(element)
                i += consumed
                continue
            
            # Check for headings
            heading_match = self._heading_pattern.match(line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                element_type = getattr(ElementType, f"HEADING{level}")
                elements.append(DocumentElement(
                    element_type=element_type,
                    content=self._parse_inline(text),
                    attributes={"id": self._generate_anchor(text)}
                ))
                i += 1
                continue
            
            # Check for horizontal rule
            if self._hr_pattern.match(line.strip()):
                elements.append(DocumentElement(
                    element_type=ElementType.HORIZONTAL_RULE,
                    content=None
                ))
                i += 1
                continue
            
            # Check for table
            if self._is_table_start(lines, i):
                element, consumed = self._parse_table(lines, i)
                if element:
                    elements.append(element)
                i += consumed
                continue
            
            # Check for blockquote
            if line.strip().startswith('>'):
                element, consumed = self._parse_blockquote(lines, i)
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
            
            # Default: paragraph
            element, consumed = self._parse_paragraph(lines, i)
            if element:
                elements.append(element)
            i += consumed
        
        return elements
    
    def _parse_inline(self, text: str) -> List[TextSpan]:
        """
        Parse inline formatting into TextSpan objects.
        
        Handles bold, italic, code, and links.
        """
        spans = []
        
        # Simple approach: parse text sequentially
        # For production, use a proper inline parser
        
        # First, handle code spans (they shouldn't be processed further)
        parts = []
        last_end = 0
        for match in self._code_inline_pattern.finditer(text):
            if match.start() > last_end:
                parts.append(('text', text[last_end:match.start()]))
            parts.append(('code', match.group(1)))
            last_end = match.end()
        if last_end < len(text):
            parts.append(('text', text[last_end:]))
        
        for part_type, part_text in parts:
            if part_type == 'code':
                spans.append(TextSpan(text=part_text, code=True))
            else:
                # Process bold and italic in remaining text
                spans.extend(self._parse_bold_italic(part_text))
        
        # If no spans created, create single plain text span
        if not spans:
            spans.append(TextSpan(text=text))
        
        return spans
    
    def _parse_bold_italic(self, text: str) -> List[TextSpan]:
        """Parse bold and italic formatting."""
        spans = []
        
        # Handle bold
        parts = []
        last_end = 0
        for match in self._bold_pattern.finditer(text):
            if match.start() > last_end:
                parts.append(('plain', text[last_end:match.start()]))
            bold_text = match.group(1) or match.group(2)
            parts.append(('bold', bold_text))
            last_end = match.end()
        if last_end < len(text):
            parts.append(('plain', text[last_end:]))
        
        if not parts:
            parts = [('plain', text)]
        
        for part_type, part_text in parts:
            if part_type == 'bold':
                # Check for italic within bold
                italic_spans = self._parse_italic_only(part_text)
                for span in italic_spans:
                    span.bold = True
                spans.extend(italic_spans)
            else:
                # Check for italic in plain text
                spans.extend(self._parse_italic_only(part_text))
        
        return spans if spans else [TextSpan(text=text)]
    
    def _parse_italic_only(self, text: str) -> List[TextSpan]:
        """Parse only italic formatting."""
        spans = []
        last_end = 0
        
        # Use a simpler pattern for italic (single * or _)
        pattern = re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)')
        
        for match in pattern.finditer(text):
            if match.start() > last_end:
                plain = text[last_end:match.start()]
                if plain:
                    spans.append(TextSpan(text=plain))
            italic_text = match.group(1) or match.group(2)
            spans.append(TextSpan(text=italic_text, italic=True))
            last_end = match.end()
        
        if last_end < len(text):
            remaining = text[last_end:]
            if remaining:
                spans.append(TextSpan(text=remaining))
        
        return spans if spans else [TextSpan(text=text)]
    
    def _generate_anchor(self, text: str) -> str:
        """Generate anchor ID from heading text."""
        # Remove formatting and convert to lowercase
        anchor = re.sub(r'[^\w\s-]', '', text.lower())
        anchor = re.sub(r'\s+', '-', anchor)
        return anchor
    
    def _is_table_start(self, lines: List[str], start: int) -> bool:
        """Check if a table starts at the given line."""
        if start >= len(lines):
            return False
        
        line = lines[start].strip()
        if not self._table_row_pattern.match(line):
            return False
        
        # Check for separator line
        if start + 1 < len(lines):
            next_line = lines[start + 1].strip()
            if self._table_separator_pattern.match(next_line):
                return True
        
        return False
    
    def _parse_table(
        self, 
        lines: List[str], 
        start: int
    ) -> Tuple[Optional[DocumentElement], int]:
        """Parse a Markdown table."""
        rows = []
        alignments = []
        i = start
        
        # Parse header row
        header_line = lines[i].strip()
        header_cells = self._parse_table_row(header_line)
        rows.append(TableRow(
            cells=[TableCell(content=cell, is_header=True) for cell in header_cells],
            is_header=True
        ))
        i += 1
        
        # Parse separator row (get alignments)
        if i < len(lines):
            sep_line = lines[i].strip()
            alignments = self._parse_table_alignments(sep_line)
            i += 1
        
        # Parse body rows
        while i < len(lines):
            line = lines[i].strip()
            if not self._table_row_pattern.match(line):
                break
            
            cells = self._parse_table_row(line)
            row_cells = []
            for j, cell in enumerate(cells):
                alignment = alignments[j] if j < len(alignments) else "left"
                row_cells.append(TableCell(
                    content=cell,
                    alignment=alignment,
                    is_header=False
                ))
            rows.append(TableRow(cells=row_cells, is_header=False))
            i += 1
        
        table = Table(rows=rows)
        element = DocumentElement(
            element_type=ElementType.TABLE,
            content=table
        )
        
        return element, i - start
    
    def _parse_table_row(self, line: str) -> List[str]:
        """Parse cells from a table row."""
        # Remove leading/trailing pipes and split
        line = line.strip('|')
        cells = [cell.strip() for cell in line.split('|')]
        return cells
    
    def _parse_table_alignments(self, sep_line: str) -> List[str]:
        """Parse column alignments from separator line."""
        sep_line = sep_line.strip('|')
        cells = sep_line.split('|')
        alignments = []
        
        for cell in cells:
            cell = cell.strip()
            if cell.startswith(':') and cell.endswith(':'):
                alignments.append('center')
            elif cell.endswith(':'):
                alignments.append('right')
            else:
                alignments.append('left')
        
        return alignments
    
    def _parse_code_block(
        self, 
        lines: List[str], 
        start: int
    ) -> Tuple[Optional[DocumentElement], int]:
        """Parse a fenced code block."""
        line = lines[start].strip()
        
        # Get language
        language = ""
        if line.startswith('```'):
            language = line[3:].strip()
        
        # Find closing fence
        code_lines = []
        i = start + 1
        while i < len(lines):
            if lines[i].strip() == '```':
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
    
    def _parse_blockquote(
        self, 
        lines: List[str], 
        start: int
    ) -> Tuple[Optional[DocumentElement], int]:
        """Parse a blockquote."""
        quote_lines = []
        i = start
        
        while i < len(lines):
            line = lines[i]
            match = self._blockquote_pattern.match(line)
            if match:
                quote_lines.append(match.group(1))
                i += 1
            elif line.strip() == '':
                # Check if next non-empty line is still a quote
                j = i + 1
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                if j < len(lines) and lines[j].strip().startswith('>'):
                    quote_lines.append('')
                    i += 1
                else:
                    break
            else:
                break
        
        content = '\n'.join(quote_lines)
        element = DocumentElement(
            element_type=ElementType.BLOCKQUOTE,
            content=self._parse_inline(content)
        )
        
        return element, i - start
    
    def _parse_list(
        self, 
        lines: List[str], 
        start: int, 
        ordered: bool = False
    ) -> Tuple[Optional[DocumentElement], int]:
        """Parse an ordered or unordered list."""
        items = []
        i = start
        base_indent = self._get_indent(lines[start])
        pattern = self._ordered_list_pattern if ordered else self._unordered_list_pattern
        
        while i < len(lines):
            line = lines[i]
            
            # Empty line might end list or be part of multi-para item
            if not line.strip():
                i += 1
                continue
            
            match = pattern.match(line)
            if match:
                indent = len(match.group(1))
                if indent == base_indent:
                    # Same level item
                    text = match.group(2)
                    items.append(ListItem(content=self._parse_inline(text)))
                    i += 1
                elif indent > base_indent:
                    # Nested list - parse recursively
                    nested_element, consumed = self._parse_list(lines, i, ordered)
                    if items and nested_element:
                        # Add as children of last item
                        items[-1].children.append(
                            ListItem(content=nested_element.content)
                        )
                    i += consumed
                else:
                    # Lower indent, end this list
                    break
            else:
                # Check other list type
                other_pattern = self._unordered_list_pattern if ordered else self._ordered_list_pattern
                other_match = other_pattern.match(line)
                if other_match:
                    # Different list type, end this list
                    break
                elif self._get_indent(line) > base_indent:
                    # Continuation of last item
                    if items:
                        # Append to last item content
                        prev_content = items[-1].get_text()
                        items[-1].content = self._parse_inline(
                            prev_content + ' ' + line.strip()
                        )
                    i += 1
                else:
                    # Non-list line at same/lower indent
                    break
        
        element_type = ElementType.ORDERED_LIST if ordered else ElementType.UNORDERED_LIST
        element = DocumentElement(
            element_type=element_type,
            content=items
        )
        
        return element, i - start
    
    def _get_indent(self, line: str) -> int:
        """Get indentation level of a line."""
        return len(line) - len(line.lstrip())
    
    def _parse_paragraph(
        self, 
        lines: List[str], 
        start: int
    ) -> Tuple[Optional[DocumentElement], int]:
        """Parse a paragraph (multiple lines until blank line)."""
        para_lines = []
        i = start
        
        while i < len(lines):
            line = lines[i]
            
            # End on blank line
            if not line.strip():
                break
            
            # End on special elements
            if (self._heading_pattern.match(line) or
                line.strip().startswith('```') or
                line.strip().startswith('>') or
                self._hr_pattern.match(line.strip()) or
                self._unordered_list_pattern.match(line) or
                self._ordered_list_pattern.match(line) or
                self._is_table_start(lines, i)):
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
