"""
Style management for PDF rendering.

This module handles loading and applying styles from template
configuration files.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch


class StyleManager:
    """
    Manages styles for PDF generation.
    
    Loads style definitions from YAML configuration and provides
    ReportLab-compatible style objects.
    """
    
    # Alignment mapping
    ALIGNMENTS = {
        'left': TA_LEFT,
        'center': TA_CENTER,
        'right': TA_RIGHT,
        'justify': TA_JUSTIFY,
    }
    
    def __init__(self, template_dir: str):
        """
        Initialize style manager.
        
        Args:
            template_dir: Path to template directory containing styles.yaml
        """
        self.template_dir = Path(template_dir)
        self._styles_config: Dict[str, Any] = {}
        self._template_config: Dict[str, Any] = {}
        self._header_footer_config: Dict[str, Any] = {}
        self._paragraph_styles: Dict[str, ParagraphStyle] = {}
        
        self._load_configs()
        self._build_styles()
    
    def _load_configs(self):
        """Load all configuration files."""
        # Load styles.yaml
        styles_path = self.template_dir / "styles.yaml"
        if styles_path.exists():
            with open(styles_path, 'r') as f:
                self._styles_config = yaml.safe_load(f) or {}
        
        # Load template.yaml
        template_path = self.template_dir / "template.yaml"
        if template_path.exists():
            with open(template_path, 'r') as f:
                self._template_config = yaml.safe_load(f) or {}
        
        # Load header_footer.yaml
        hf_path = self.template_dir / "header_footer.yaml"
        if hf_path.exists():
            with open(hf_path, 'r') as f:
                self._header_footer_config = yaml.safe_load(f) or {}
    
    def _build_styles(self):
        """Build ReportLab paragraph styles from config."""
        base_styles = getSampleStyleSheet()
        fonts_config = self._styles_config.get('fonts', {})
        
        for style_name, style_def in fonts_config.items():
            self._paragraph_styles[style_name] = self._create_paragraph_style(
                style_name, style_def, base_styles
            )
    
    def _create_paragraph_style(
        self, 
        name: str, 
        config: Dict[str, Any],
        base_styles
    ) -> ParagraphStyle:
        """Create a ParagraphStyle from configuration."""
        # Get base style
        parent = base_styles['Normal']
        
        # Parse color
        color = self._parse_color(config.get('color', '#000000'))
        
        # Build style kwargs
        kwargs = {
            'name': name,
            'parent': parent,
            'fontName': config.get('family', 'Helvetica'),
            'fontSize': config.get('size', 10),
            'textColor': color,
            'leading': config.get('leading', config.get('size', 10) * 1.2),
            'spaceBefore': config.get('space_before', 0),
            'spaceAfter': config.get('space_after', 0),
            'alignment': self.ALIGNMENTS.get(
                config.get('alignment', 'left'), TA_LEFT
            ),
        }
        
        # Add optional properties
        if 'first_line_indent' in config:
            kwargs['firstLineIndent'] = config['first_line_indent']
        
        if 'left_indent' in config:
            kwargs['leftIndent'] = config['left_indent']
        
        if 'right_indent' in config:
            kwargs['rightIndent'] = config['right_indent']
        
        return ParagraphStyle(**kwargs)
    
    def _parse_color(self, color_str: str) -> colors.Color:
        """Parse color string to ReportLab color."""
        if isinstance(color_str, colors.Color):
            return color_str
        
        if color_str.startswith('#'):
            # Hex color
            hex_color = color_str[1:]
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                return colors.Color(r, g, b)
        
        # Try named color
        return getattr(colors, color_str, colors.black)
    
    def get_style(self, style_name: str) -> ParagraphStyle:
        """Get a paragraph style by name."""
        if style_name in self._paragraph_styles:
            return self._paragraph_styles[style_name]
        
        # Return default if not found
        if 'default' in self._paragraph_styles:
            return self._paragraph_styles['default']
        
        # Fallback to basic style
        return ParagraphStyle(
            name=style_name,
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.black
        )
    
    def get_font_config(self, style_name: str) -> Dict[str, Any]:
        """Get raw font configuration for a style."""
        fonts = self._styles_config.get('fonts', {})
        return fonts.get(style_name, fonts.get('default', {}))
    
    def get_color(self, color_name: str) -> colors.Color:
        """Get a named color from configuration."""
        colors_config = self._styles_config.get('colors', {})
        color_str = colors_config.get(color_name, '#000000')
        return self._parse_color(color_str)
    
    def get_table_config(self) -> Dict[str, Any]:
        """Get table styling configuration."""
        return self._styles_config.get('tables', {})
    
    def get_list_config(self) -> Dict[str, Any]:
        """Get list styling configuration."""
        return self._styles_config.get('lists', {})
    
    def get_toc_config(self) -> Dict[str, Any]:
        """Get table of contents configuration."""
        return self._styles_config.get('toc', {})
    
    def get_admonition_config(self) -> Dict[str, Any]:
        """Get admonition styling configuration."""
        return self._styles_config.get('admonitions', {})
    
    def get_page_config(self) -> Dict[str, Any]:
        """Get page configuration from template."""
        return self._template_config.get('page', {})
    
    def get_header_config(self) -> Dict[str, Any]:
        """Get header configuration."""
        return self._header_footer_config.get('header', {})
    
    def get_footer_config(self) -> Dict[str, Any]:
        """Get footer configuration."""
        return self._header_footer_config.get('footer', {})
    
    def get_title_page_config(self) -> Dict[str, Any]:
        """Get title page configuration."""
        return self._template_config.get('title_page', {})
    
    def get_copyright_config(self) -> Dict[str, Any]:
        """Get copyright page configuration."""
        return self._template_config.get('copyright', {'enabled': True})
    
    def get_chapter_config(self) -> Dict[str, Any]:
        """Get chapter styling configuration."""
        return self._template_config.get('chapter', {
            'start_new_page': True,
            'show_chapter_number': False,
            'title_style': 'heading1'
        })
    
    def get_structure_config(self) -> Dict[str, Any]:
        """Get document structure configuration."""
        return self._template_config.get('structure', {})
    
    def get_margins(self) -> Tuple[float, float, float, float]:
        """Get page margins (top, right, bottom, left)."""
        page_config = self.get_page_config()
        margins = page_config.get('margins', {})
        
        return (
            margins.get('top', 72),
            margins.get('right', 72),
            margins.get('bottom', 72),
            margins.get('left', 72),
        )
    
    @property
    def template_name(self) -> str:
        """Get template name."""
        return self._template_config.get('name', 'Unknown')
    
    @property
    def page_size(self) -> str:
        """Get page size name."""
        page_config = self.get_page_config()
        return page_config.get('size', 'LETTER')
    
    @property
    def orientation(self) -> str:
        """Get page orientation."""
        page_config = self.get_page_config()
        return page_config.get('orientation', 'portrait')
