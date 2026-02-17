"""
PDF Renderer using ReportLab.

This module handles the actual PDF generation from Document objects,
applying styles and templates.
"""

from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, A4, LEGAL, letter, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, 
    Spacer, 
    Table as RLTable,
    TableStyle,
    PageBreak,
    ListFlowable,
    ListItem as RLListItem,
    Preformatted,
    KeepTogether,
    HRFlowable,
    Image,
    Flowable,
)
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame, NextPageTemplate
from reportlab.platypus.tableofcontents import TableOfContents

from docgen.models import (
    Document, 
    DocumentElement, 
    ElementType,
    TextSpan,
    Table,
    ListItem,
)
from docgen.renderers.styles import StyleManager


# Page size mapping
PAGE_SIZES = {
    'LETTER': LETTER,
    'A4': A4,
    'LEGAL': LEGAL,
}


class TitlePageFlowable(Flowable):
    """
    Custom flowable for rendering a title page.
    
    Renders title page elements at specified positions matching
    the Ford ECG2 VECU Release Notes style.
    """
    
    def __init__(
        self, 
        width: float, 
        height: float, 
        config: dict, 
        metadata: dict,
        style_manager,
        parse_color
    ):
        """
        Initialize title page flowable.
        
        Args:
            width: Available content width.
            height: Available content height.
            config: Title page configuration from template.
            metadata: Document metadata for variable substitution.
            style_manager: StyleManager instance.
            parse_color: Color parsing function.
        """
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.config = config
        self.metadata = metadata
        self.style_manager = style_manager
        self._parse_color = parse_color
    
    def wrap(self, available_width, available_height):
        """Return the size of this flowable - fit within available space."""
        # Use the smaller of configured size or available space
        actual_width = min(self.width, available_width)
        actual_height = min(self.height, available_height)
        return (actual_width, actual_height)
    
    def draw(self):
        """Draw the title page elements."""
        canvas = self.canv
        
        # Get elements from config
        elements = self.config.get('elements', [])
        
        for element in elements:
            if element.get('type') == 'text':
                self._draw_text_element(canvas, element)
    
    def _draw_text_element(self, canvas, element: dict):
        """Draw a text element on the title page."""
        # Get content and substitute variables
        content = element.get('content', '')
        content = self._substitute_variables(content)
        
        # Get style
        style_name = element.get('style', 'default')
        font_config = self.style_manager.get_font_config(style_name)
        
        # Set font
        font_name = font_config.get('family', 'Helvetica')
        font_size = font_config.get('size', 12)
        font_color = self._parse_color(font_config.get('color', '#000000'))
        
        canvas.setFont(font_name, font_size)
        canvas.setFillColor(font_color)
        
        # Calculate position
        position = element.get('position', 'center')
        y_offset = element.get('y_offset', 0)
        
        # Calculate y position based on position type
        if position == 'top':
            y = self.height - y_offset
        elif position == 'center':
            y = self.height / 2 + y_offset
        elif position == 'bottom':
            y = y_offset
        else:
            y = self.height / 2 + y_offset
        
        # Calculate x position (center text)
        alignment = font_config.get('alignment', 'center')
        if alignment == 'center':
            x = self.width / 2
            canvas.drawCentredString(x, y, content)
        elif alignment == 'left':
            x = 0
            canvas.drawString(x, y, content)
        elif alignment == 'right':
            x = self.width
            canvas.drawRightString(x, y, content)
        else:
            x = self.width / 2
            canvas.drawCentredString(x, y, content)
    
    def _substitute_variables(self, text: str) -> str:
        """Substitute metadata variables in text."""
        for key, value in self.metadata.items():
            placeholder = '{' + key + '}'
            if placeholder in text:
                text = text.replace(placeholder, str(value) if value else '')
        return text


class NumberedCanvas:
    """
    Canvas wrapper that tracks page numbers and renders headers/footers.
    """
    
    def __init__(self, canvas, doc, style_manager: StyleManager, metadata: Dict[str, Any]):
        self._canvas = canvas
        self._doc = doc
        self._style_manager = style_manager
        self._metadata = metadata
        self._page_count = 0
    
    def __getattr__(self, name):
        return getattr(self._canvas, name)


class PDFRenderer:
    """
    Renders Document objects to PDF files.
    
    Uses ReportLab for PDF generation with support for:
    - Custom templates and styles
    - Headers and footers
    - Tables with styling
    - Lists (ordered and unordered)
    - Code blocks
    - Page numbers
    """
    
    def __init__(self, style_manager: StyleManager):
        """
        Initialize PDF renderer.
        
        Args:
            style_manager: StyleManager instance with loaded template styles.
        """
        self.style_manager = style_manager
        self._page_size = self._get_page_size()
        self._metadata: Dict[str, Any] = {}
        self._toc_entries: List[Tuple[int, str, int]] = []
    
    def _get_page_size(self) -> Tuple[float, float]:
        """Get page size from configuration."""
        size_name = self.style_manager.page_size
        orientation = self.style_manager.orientation
        
        size = PAGE_SIZES.get(size_name.upper(), LETTER)
        
        if orientation.lower() == 'landscape':
            size = landscape(size)
        
        return size
    
    def render(
        self, 
        document: Document, 
        output_path: str,
        metadata_override: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render a Document to PDF.
        
        Args:
            document: Document object to render.
            output_path: Path for output PDF file.
            metadata_override: Optional metadata to override document metadata.
            
        Returns:
            Path to the generated PDF file.
        """
        # Merge metadata
        self._metadata = document.metadata.to_dict()
        if metadata_override:
            self._metadata.update(metadata_override)
        
        # Get margins
        margins = self.style_manager.get_margins()
        
        # Create document
        doc = BaseDocTemplate(
            output_path,
            pagesize=self._page_size,
            topMargin=margins[0],
            rightMargin=margins[1],
            bottomMargin=margins[2],
            leftMargin=margins[3],
            title=self._metadata.get('title', ''),
            author=self._metadata.get('author', ''),
        )
        
        # Calculate frame dimensions
        header_config = self.style_manager.get_header_config()
        footer_config = self.style_manager.get_footer_config()
        
        header_height = header_config.get('height', 0) if header_config.get('enabled', False) else 0
        footer_height = footer_config.get('height', 0) if footer_config.get('enabled', False) else 0
        
        frame_width = self._page_size[0] - margins[1] - margins[3]
        frame_height = self._page_size[1] - margins[0] - margins[2] - header_height - footer_height
        
        # Create main content frame (with space for header/footer)
        main_frame = Frame(
            margins[3],  # x
            margins[2] + footer_height,  # y
            frame_width,
            frame_height,
            id='main'
        )
        
        # Create main page template with header/footer
        main_template = PageTemplate(
            id='main',
            frames=[main_frame],
            onPage=lambda canvas, doc: self._draw_header_footer(canvas, doc)
        )
        
        templates = [main_template]
        
        # Check if title page is enabled
        title_page_config = self.style_manager.get_title_page_config()
        if title_page_config.get('enabled', False):
            # Create title page frame (full height, no header/footer space)
            title_frame_height = self._page_size[1] - margins[0] - margins[2]
            title_frame = Frame(
                margins[3],  # x
                margins[2],  # y
                frame_width,
                title_frame_height,
                id='title_frame'
            )
            
            # Create title page template without header/footer
            title_template = PageTemplate(
                id='title_page',
                frames=[title_frame],
                onPage=lambda canvas, doc: None  # No header/footer on title page
            )
            
            # Insert title page template first
            templates.insert(0, title_template)
        
        doc.addPageTemplates(templates)
        
        # Build story (content)
        story = self._build_story(document)
        
        # Generate PDF
        doc.build(story)
        
        return output_path
    
    def _draw_header_footer(self, canvas, doc):
        """Draw header and footer on each page."""
        canvas.saveState()
        
        page_width, page_height = self._page_size
        margins = self.style_manager.get_margins()
        
        # Draw header
        header_config = self.style_manager.get_header_config()
        if header_config.get('enabled', False):
            # Check if should show on first page
            if doc.page > 1 or header_config.get('first_page', True):
                self._draw_header(canvas, doc, page_width, page_height, margins)
        
        # Draw footer
        footer_config = self.style_manager.get_footer_config()
        if footer_config.get('enabled', False):
            if doc.page > 1 or footer_config.get('first_page', True):
                self._draw_footer(canvas, doc, page_width, page_height, margins)
        
        canvas.restoreState()
    
    def _draw_header(self, canvas, doc, page_width: float, page_height: float, margins: Tuple):
        """Draw page header."""
        header_config = self.style_manager.get_header_config()
        header_height = header_config.get('height', 50)
        
        y_pos = page_height - margins[0]
        x_left = margins[3]
        x_right = page_width - margins[1]
        x_center = page_width / 2
        
        # Get header style
        header_style = self.style_manager.get_font_config('header_text')
        font_name = header_style.get('family', 'Helvetica-Bold')
        font_size = header_style.get('size', 9)
        font_color = self._parse_color(header_style.get('color', '#000080'))
        
        canvas.setFont(font_name, font_size)
        canvas.setFillColor(font_color)
        
        # Process header elements
        for element in header_config.get('elements', []):
            if element.get('type') == 'text':
                text = self._substitute_variables(element.get('content', ''))
                position = element.get('position', 'left')
                
                if position == 'left':
                    canvas.drawString(x_left, y_pos - 15, text)
                elif position == 'center':
                    canvas.drawCentredString(x_center, y_pos - 15, text)
                elif position == 'right':
                    canvas.drawRightString(x_right, y_pos - 15, text)
            
            elif element.get('type') == 'line':
                line_y = y_pos - header_height + element.get('margin_top', 5)
                line_color = self._parse_color(element.get('color', '#000080'))
                line_width = element.get('width', 1)
                
                canvas.setStrokeColor(line_color)
                canvas.setLineWidth(line_width)
                canvas.line(x_left, line_y, x_right, line_y)
    
    def _draw_footer(self, canvas, doc, page_width: float, page_height: float, margins: Tuple):
        """Draw page footer."""
        footer_config = self.style_manager.get_footer_config()
        footer_height = footer_config.get('height', 40)
        
        y_pos = margins[2]
        x_left = margins[3]
        x_right = page_width - margins[1]
        x_center = page_width / 2
        
        # Get footer style
        footer_style = self.style_manager.get_font_config('footer_text')
        font_name = footer_style.get('family', 'Helvetica')
        font_size = footer_style.get('size', 8)
        font_color = self._parse_color(footer_style.get('color', '#666666'))
        
        canvas.setFont(font_name, font_size)
        canvas.setFillColor(font_color)
        
        # Process footer elements
        for element in footer_config.get('elements', []):
            if element.get('type') == 'line':
                line_y = y_pos + footer_height - element.get('margin_bottom', 5)
                line_color = self._parse_color(element.get('color', '#000080'))
                line_width = element.get('width', 1)
                
                canvas.setStrokeColor(line_color)
                canvas.setLineWidth(line_width)
                canvas.line(x_left, line_y, x_right, line_y)
            
            elif element.get('type') == 'text':
                text = self._substitute_variables(
                    element.get('content', ''),
                    page_number=doc.page
                )
                position = element.get('position', 'center')
                
                text_y = y_pos + 10
                
                if position == 'left':
                    canvas.drawString(x_left, text_y, text)
                elif position == 'center':
                    canvas.drawCentredString(x_center, text_y, text)
                elif position == 'right':
                    canvas.drawRightString(x_right, text_y, text)
    
    def _substitute_variables(self, text: str, page_number: int = 0) -> str:
        """Substitute template variables in text."""
        # Replace metadata variables
        for key, value in self._metadata.items():
            text = text.replace(f'{{{key}}}', str(value) if value else '')
        
        # Replace page number
        text = text.replace('{page_number}', str(page_number))
        text = text.replace('{total_pages}', str(page_number))  # Will be updated later
        
        return text
    
    def _parse_color(self, color_str: str) -> colors.Color:
        """Parse color string to ReportLab color."""
        if isinstance(color_str, colors.Color):
            return color_str
        
        if color_str.startswith('#'):
            hex_color = color_str[1:]
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                return colors.Color(r, g, b)
        
        return getattr(colors, color_str, colors.black)
    
    def _build_story(self, document: Document) -> List:
        """Build the document story (content flow)."""
        story = []
        
        # Add title page if enabled
        title_page_flowables = self._build_title_page()
        if title_page_flowables:
            story.extend(title_page_flowables)
        
        # Add document title if present (and no title page)
        elif self._metadata.get('title'):
            title_style = self.style_manager.get_style('title')
            story.append(Paragraph(self._metadata['title'], title_style))
            story.append(Spacer(1, 20))
        
        # Process each element
        for element in document.elements:
            flowables = self._render_element(element)
            story.extend(flowables)
        
        return story
    
    def _build_title_page(self) -> List:
        """Build the title page flowables."""
        title_page_config = self.style_manager.get_title_page_config()
        
        if not title_page_config.get('enabled', False):
            return []
        
        flowables = []
        page_width, page_height = self._page_size
        margins = self.style_manager.get_margins()
        
        # Calculate frame dimensions for title page (full height, no header/footer)
        content_width = page_width - margins[1] - margins[3]
        content_height = page_height - margins[0] - margins[2] - 20  # Safety margin
        
        # Create a custom flowable for the title page
        title_page = TitlePageFlowable(
            width=content_width,
            height=content_height,
            config=title_page_config,
            metadata=self._metadata,
            style_manager=self.style_manager,
            parse_color=self._parse_color,
        )
        
        flowables.append(title_page)
        # NextPageTemplate must come before PageBreak to take effect
        flowables.append(NextPageTemplate('main'))
        flowables.append(PageBreak())
        
        return flowables
    
    def _render_element(self, element: DocumentElement) -> List:
        """Render a single document element to flowables."""
        handlers = {
            ElementType.HEADING1: self._render_heading,
            ElementType.HEADING2: self._render_heading,
            ElementType.HEADING3: self._render_heading,
            ElementType.HEADING4: self._render_heading,
            ElementType.HEADING5: self._render_heading,
            ElementType.HEADING6: self._render_heading,
            ElementType.PARAGRAPH: self._render_paragraph,
            ElementType.TABLE: self._render_table,
            ElementType.UNORDERED_LIST: self._render_list,
            ElementType.ORDERED_LIST: self._render_list,
            ElementType.CODE_BLOCK: self._render_code_block,
            ElementType.BLOCKQUOTE: self._render_blockquote,
            ElementType.HORIZONTAL_RULE: self._render_hr,
            ElementType.PAGE_BREAK: lambda e: [PageBreak()],
            ElementType.IMAGE: self._render_image,
            ElementType.TOC: self._render_toc,
            ElementType.ADMONITION: self._render_admonition,
        }
        
        handler = handlers.get(element.element_type, self._render_paragraph)
        return handler(element)
    
    def _render_heading(self, element: DocumentElement) -> List:
        """Render a heading element."""
        level = element.level or 1
        style_name = f'heading{level}'
        style = self.style_manager.get_style(style_name)
        
        text = self._spans_to_html(element.content)
        
        flowables = [
            Paragraph(text, style),
        ]
        
        # Add border below for H1 if configured
        font_config = self.style_manager.get_font_config(style_name)
        if font_config.get('border_bottom'):
            border_color = self._parse_color(font_config.get('border_color', '#000080'))
            flowables.append(HRFlowable(
                width="100%",
                thickness=font_config.get('border_width', 1),
                color=border_color,
                spaceBefore=2,
                spaceAfter=8
            ))
        
        return flowables
    
    def _render_paragraph(self, element: DocumentElement) -> List:
        """Render a paragraph element."""
        style = self.style_manager.get_style('paragraph')
        text = self._spans_to_html(element.content)
        
        return [Paragraph(text, style)]
    
    def _render_table(self, element: DocumentElement) -> List:
        """Render a table element."""
        table: Table = element.content
        
        if not table or not table.rows:
            return []
        
        # Build table data
        data = []
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                cell_text = cell.get_text()
                row_data.append(cell_text)
            data.append(row_data)
        
        if not data:
            return []
        
        # Calculate column widths
        margins = self.style_manager.get_margins()
        available_width = self._page_size[0] - margins[1] - margins[3]
        
        num_cols = max(len(row) for row in data)
        col_width = available_width / num_cols
        col_widths = [col_width] * num_cols
        
        # Create table
        rl_table = RLTable(data, colWidths=col_widths)
        
        # Apply table style
        table_config = self.style_manager.get_table_config()
        header_bg = self._parse_color(
            table_config.get('header_background', '#D0D0D0')
        )
        border_color = self._parse_color(
            table_config.get('border_color', '#000000')
        )
        alt_row_color = self._parse_color(
            table_config.get('alternate_row_color', '#F5F5F5')
        )
        
        # Get font configs
        header_font = self.style_manager.get_font_config('table_header')
        cell_font = self.style_manager.get_font_config('table_cell')
        
        style_commands = [
            # Grid
            ('GRID', (0, 0), (-1, -1), table_config.get('border_width', 0.5), border_color),
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), table_config.get('cell_padding', 6)),
            ('RIGHTPADDING', (0, 0), (-1, -1), table_config.get('cell_padding', 6)),
            ('TOPPADDING', (0, 0), (-1, -1), table_config.get('cell_padding', 6)),
            ('BOTTOMPADDING', (0, 0), (-1, -1), table_config.get('cell_padding', 6)),
            # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Body font
            ('FONTNAME', (0, 0), (-1, -1), cell_font.get('family', 'Helvetica')),
            ('FONTSIZE', (0, 0), (-1, -1), cell_font.get('size', 9)),
        ]
        
        # Header row styling
        if table.header_rows:
            num_header_rows = len(table.header_rows)
            style_commands.extend([
                ('BACKGROUND', (0, 0), (-1, num_header_rows - 1), header_bg),
                ('FONTNAME', (0, 0), (-1, num_header_rows - 1), header_font.get('family', 'Helvetica-Bold')),
                ('FONTSIZE', (0, 0), (-1, num_header_rows - 1), header_font.get('size', 10)),
            ])
        
        # Alternate row colors
        if table_config.get('alternate_rows', True):
            for i in range(len(table.header_rows), len(data)):
                if (i - len(table.header_rows)) % 2 == 1:
                    style_commands.append(
                        ('BACKGROUND', (0, i), (-1, i), alt_row_color)
                    )
        
        rl_table.setStyle(TableStyle(style_commands))
        
        return [rl_table, Spacer(1, 12)]
    
    def _render_list(self, element: DocumentElement) -> List:
        """Render a list element."""
        items: List[ListItem] = element.content
        ordered = element.element_type == ElementType.ORDERED_LIST
        
        list_config = self.style_manager.get_list_config()
        bullet = list_config.get('bullet_character', '•')
        
        style = self.style_manager.get_style('list_item')
        
        list_items = []
        for item in items:
            text = self._spans_to_html(item.content) if isinstance(item.content, list) else str(item.content)
            para = Paragraph(text, style)
            list_items.append(para)
        
        bullet_type = '1' if ordered else 'bullet'
        
        list_flowable = ListFlowable(
            list_items,
            bulletType=bullet_type,
            bulletFontName='Helvetica',
            bulletFontSize=10,
            leftIndent=list_config.get('bullet_indent', 18),
            bulletDedent=list_config.get('bullet_indent', 18),
            spaceBefore=4,
            spaceAfter=4,
        )
        
        return [list_flowable]
    
    def _render_code_block(self, element: DocumentElement) -> List:
        """Render a code block element."""
        code = element.content
        language = element.attributes.get('language', '')
        
        code_style = self.style_manager.get_font_config('code_block')
        
        style = ParagraphStyle(
            name='CodeBlock',
            fontName=code_style.get('family', 'Courier'),
            fontSize=code_style.get('size', 9),
            textColor=self._parse_color(code_style.get('color', '#000000')),
            backColor=self._parse_color(code_style.get('background', '#F5F5F5')),
            leftIndent=code_style.get('padding', 8),
            rightIndent=code_style.get('padding', 8),
            spaceBefore=8,
            spaceAfter=8,
            leading=code_style.get('size', 9) * 1.4,
        )
        
        # Use Preformatted for code
        preformatted = Preformatted(code, style)
        
        return [preformatted]
    
    def _render_blockquote(self, element: DocumentElement) -> List:
        """Render a blockquote element."""
        style = ParagraphStyle(
            name='Blockquote',
            parent=self.style_manager.get_style('paragraph'),
            leftIndent=20,
            rightIndent=20,
            textColor=colors.Color(0.3, 0.3, 0.3),
            borderLeftColor=colors.Color(0.7, 0.7, 0.7),
            borderLeftWidth=3,
            borderLeftPadding=10,
        )
        
        text = self._spans_to_html(element.content)
        return [Paragraph(text, style)]
    
    def _render_hr(self, element: DocumentElement) -> List:
        """Render a horizontal rule."""
        return [HRFlowable(
            width="100%",
            thickness=1,
            color=colors.Color(0.8, 0.8, 0.8),
            spaceBefore=12,
            spaceAfter=12
        )]
    
    def _spans_to_html(self, content) -> str:
        """Convert TextSpan list to HTML-formatted string."""
        if isinstance(content, str):
            return self._escape_html(content)
        
        if not isinstance(content, list):
            return str(content) if content else ''
        
        html_parts = []
        for span in content:
            if isinstance(span, TextSpan):
                text = self._escape_html(span.text)
                
                if span.code:
                    text = f'<font face="Courier" size="9">{text}</font>'
                if span.bold:
                    text = f'<b>{text}</b>'
                if span.italic:
                    text = f'<i>{text}</i>'
                if span.link:
                    text = f'<a href="{span.link}">{text}</a>'
                
                html_parts.append(text)
            else:
                html_parts.append(self._escape_html(str(span)))
        
        return ''.join(html_parts)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))
    
    def _render_image(self, element: DocumentElement) -> List:
        """Render an image element."""
        image_path = element.content
        alt_text = element.attributes.get('alt', '')
        width = element.attributes.get('width')
        height = element.attributes.get('height')
        
        # Check if image exists
        path = Path(image_path)
        if not path.exists():
            # Try relative to document directory
            if hasattr(self, '_document_dir') and self._document_dir:
                path = Path(self._document_dir) / image_path
        
        if not path.exists():
            # Return placeholder text if image not found
            style = self.style_manager.get_style('paragraph')
            return [Paragraph(f'<i>[Image: {alt_text or image_path}]</i>', style)]
        
        # Get available width for scaling
        margins = self.style_manager.get_margins()
        available_width = self._page_size[0] - margins[1] - margins[3]
        
        try:
            img = Image(str(path))
            
            # Scale image to fit within available width
            if width:
                img.drawWidth = float(width)
            elif img.drawWidth > available_width:
                scale = available_width / img.drawWidth
                img.drawWidth = available_width
                img.drawHeight = img.drawHeight * scale
            
            if height:
                img.drawHeight = float(height)
            
            flowables = [Spacer(1, 6), img]
            
            # Add caption if present
            if alt_text:
                caption_style = ParagraphStyle(
                    name='ImageCaption',
                    parent=self.style_manager.get_style('paragraph'),
                    fontSize=9,
                    textColor=colors.Color(0.4, 0.4, 0.4),
                    alignment=TA_CENTER,
                    spaceBefore=4,
                    spaceAfter=8,
                )
                flowables.append(Paragraph(f'<i>{alt_text}</i>', caption_style))
            else:
                flowables.append(Spacer(1, 6))
            
            return flowables
            
        except Exception as e:
            style = self.style_manager.get_style('paragraph')
            return [Paragraph(f'<i>[Error loading image: {image_path}]</i>', style)]
    
    def _render_toc(self, element: DocumentElement) -> List:
        """Render a table of contents element."""
        toc = TableOfContents()
        
        # Configure TOC styles
        toc_config = self.style_manager.get_toc_config()
        
        toc.levelStyles = [
            ParagraphStyle(
                name='TOCHeading1',
                fontName=toc_config.get('font_family', 'Helvetica-Bold'),
                fontSize=toc_config.get('level1_size', 12),
                leftIndent=0,
                spaceBefore=6,
                spaceAfter=3,
            ),
            ParagraphStyle(
                name='TOCHeading2',
                fontName=toc_config.get('font_family', 'Helvetica'),
                fontSize=toc_config.get('level2_size', 11),
                leftIndent=20,
                spaceBefore=3,
                spaceAfter=2,
            ),
            ParagraphStyle(
                name='TOCHeading3',
                fontName=toc_config.get('font_family', 'Helvetica'),
                fontSize=toc_config.get('level3_size', 10),
                leftIndent=40,
                spaceBefore=2,
                spaceAfter=2,
            ),
        ]
        
        return [
            Paragraph('<b>Table of Contents</b>', self.style_manager.get_style('heading1')),
            Spacer(1, 12),
            toc,
            PageBreak(),
        ]
    
    def _render_admonition(self, element: DocumentElement) -> List:
        """Render an admonition element (NOTE, TIP, WARNING, etc.)."""
        admon_type = element.attributes.get('type', 'NOTE')
        
        # Get admonition config from style manager
        admon_config = self.style_manager.get_admonition_config()
        
        # Define default colors for different admonition types
        admon_colors = {
            'NOTE': {'bg': '#E7F3FF', 'border': '#2196F3', 'text': '#1565C0'},
            'TIP': {'bg': '#E8F5E9', 'border': '#4CAF50', 'text': '#2E7D32'},
            'IMPORTANT': {'bg': '#FFF3E0', 'border': '#FF9800', 'text': '#E65100'},
            'WARNING': {'bg': '#FFF8E1', 'border': '#FFC107', 'text': '#F57F17'},
            'CAUTION': {'bg': '#FFEBEE', 'border': '#F44336', 'text': '#C62828'},
        }
        
        # Get colors for this type
        type_colors = admon_colors.get(admon_type, admon_colors['NOTE'])
        
        # Override with config if available
        type_config = admon_config.get(admon_type.lower(), {})
        bg_color = self._parse_color(type_config.get('background', type_colors['bg']))
        border_color = self._parse_color(type_config.get('border', type_colors['border']))
        text_color = self._parse_color(type_config.get('text', type_colors['text']))
        
        # Create styled paragraph for admonition
        style = ParagraphStyle(
            name=f'Admonition{admon_type}',
            parent=self.style_manager.get_style('paragraph'),
            fontName='Helvetica',
            fontSize=10,
            textColor=text_color,
            backColor=bg_color,
            leftIndent=10,
            rightIndent=10,
            spaceBefore=8,
            spaceAfter=8,
            borderPadding=8,
            borderWidth=2,
            borderColor=border_color,
            borderRadius=4,
        )
        
        # Build content with type prefix
        content = self._spans_to_html(element.content)
        text = f'<b>{admon_type}:</b> {content}'
        
        return [Paragraph(text, style)]
