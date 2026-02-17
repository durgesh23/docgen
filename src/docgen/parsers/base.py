"""
Base parser class for document parsing.

This module defines the abstract base class that all parsers must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

from docgen.models import Document


class BaseParser(ABC):
    """
    Abstract base class for document parsers.
    
    All format-specific parsers (Markdown, AsciiDoc, etc.) must
    inherit from this class and implement the required methods.
    """
    
    def __init__(self):
        """Initialize the parser."""
        self._supported_extensions: list = []
    
    @property
    def supported_extensions(self) -> list:
        """Get list of file extensions this parser supports."""
        return self._supported_extensions
    
    def can_parse(self, file_path: str) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            True if this parser can handle the file.
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions
    
    @abstractmethod
    def parse(
        self, 
        content: str, 
        metadata_override: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Parse content string into a Document.
        
        Args:
            content: The raw content string to parse.
            metadata_override: Optional metadata to merge/override.
            
        Returns:
            A Document object representing the parsed content.
        """
        pass
    
    def parse_file(
        self, 
        file_path: str, 
        metadata_override: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Parse a file into a Document.
        
        Args:
            file_path: Path to the file to parse.
            metadata_override: Optional metadata to merge/override.
            
        Returns:
            A Document object representing the parsed content.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = path.read_text(encoding="utf-8")
        document = self.parse(content, metadata_override)
        document.source_path = str(path.absolute())
        
        return document
    
    @abstractmethod
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from content without full parsing.
        
        Args:
            content: The raw content string.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        pass
