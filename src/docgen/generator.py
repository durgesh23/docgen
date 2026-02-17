"""
Main PDF Generator class.

This module provides the primary interface for generating PDFs
from Markdown and AsciiDoc files.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from docgen.models import Document, DocumentMetadata
from docgen.parsers import MarkdownParser, AsciiDocParser, BaseParser
from docgen.renderers import PDFRenderer, StyleManager
from docgen.utils import get_template_path, list_templates, get_file_format, ensure_directory


class PDFGenerator:
    """
    Main class for generating PDF documents from Markdown or AsciiDoc.
    
    This class provides a high-level interface for:
    - Loading and switching templates
    - Parsing input files
    - Generating PDF output
    
    Example:
        >>> generator = PDFGenerator(template="ford_release_notes")
        >>> generator.generate("input.md", "output.pdf")
    """
    
    def __init__(
        self,
        template: str = "generic",
        config_path: Optional[str] = None,
        template_paths: Optional[List[str]] = None
    ):
        """
        Initialize PDF generator.
        
        Args:
            template: Name of template to use.
            config_path: Optional path to configuration file.
            template_paths: Optional additional template search paths.
        """
        self._template_name = template
        self._config: Dict[str, Any] = {}
        self._template_paths = template_paths or []
        
        # Load configuration
        if config_path:
            self._load_config(config_path)
        
        # Initialize components
        self._parsers: Dict[str, BaseParser] = {
            'markdown': MarkdownParser(),
            'asciidoc': AsciiDocParser(),
        }
        
        # Load template
        self._template_dir: Optional[Path] = None
        self._style_manager: Optional[StyleManager] = None
        self._renderer: Optional[PDFRenderer] = None
        
        self.set_template(template)
    
    def _load_config(self, config_path: str):
        """Load configuration from file."""
        path = Path(config_path)
        if path.exists():
            with open(path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
    
    def set_template(self, template_name: str):
        """
        Set the template to use for PDF generation.
        
        Args:
            template_name: Name of the template.
            
        Raises:
            ValueError: If template is not found.
        """
        template_dir = get_template_path(template_name, self._template_paths)
        
        if not template_dir:
            available = list_templates(self._template_paths)
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available templates: {', '.join(available)}"
            )
        
        self._template_name = template_name
        self._template_dir = template_dir
        self._style_manager = StyleManager(str(template_dir))
        self._renderer = PDFRenderer(self._style_manager)
    
    def generate(
        self,
        input_file: str,
        output_file: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate PDF from an input file.
        
        Args:
            input_file: Path to Markdown or AsciiDoc file.
            output_file: Path for output PDF.
            metadata: Optional metadata to override/add.
            
        Returns:
            Path to generated PDF file.
            
        Raises:
            FileNotFoundError: If input file doesn't exist.
            ValueError: If input format is not supported.
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Determine format
        file_format = get_file_format(input_file)
        
        # Get parser
        parser = self._parsers.get(file_format)
        if not parser:
            raise ValueError(f"No parser for format: {file_format}")
        
        # Parse document
        document = parser.parse_file(input_file, metadata)
        
        # Ensure output directory exists
        output_path = Path(output_file)
        if output_path.parent:
            ensure_directory(str(output_path.parent))
        
        # Render PDF
        return self._renderer.render(document, output_file, metadata)
    
    def generate_from_string(
        self,
        content: str,
        output_file: str,
        input_format: str = "markdown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate PDF from string content.
        
        Args:
            content: Document content string.
            output_file: Path for output PDF.
            input_format: Format of content ('markdown' or 'asciidoc').
            metadata: Optional metadata.
            
        Returns:
            Path to generated PDF file.
        """
        parser = self._parsers.get(input_format)
        if not parser:
            raise ValueError(f"No parser for format: {input_format}")
        
        # Parse document
        document = parser.parse(content, metadata)
        
        # Ensure output directory exists
        output_path = Path(output_file)
        if output_path.parent:
            ensure_directory(str(output_path.parent))
        
        # Render PDF
        return self._renderer.render(document, output_file, metadata)
    
    def list_templates(self) -> List[str]:
        """
        Get list of available templates.
        
        Returns:
            List of template names.
        """
        return list_templates(self._template_paths)
    
    def get_template_info(self, template_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a template.
        
        Args:
            template_name: Template name (uses current if None).
            
        Returns:
            Dictionary with template information.
        """
        name = template_name or self._template_name
        template_dir = get_template_path(name, self._template_paths)
        
        if not template_dir:
            return {}
        
        template_file = template_dir / "template.yaml"
        if template_file.exists():
            with open(template_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        return {}
    
    @property
    def current_template(self) -> str:
        """Get name of current template."""
        return self._template_name
    
    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported input formats."""
        return list(self._parsers.keys())
