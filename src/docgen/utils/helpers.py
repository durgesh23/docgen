"""
Utility functions for the PDF Document Generator.
"""

import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime


def get_package_root() -> Path:
    """Get the package root directory."""
    return Path(__file__).parent.parent.parent.parent


def get_template_path(template_name: str, custom_paths: Optional[List[str]] = None) -> Optional[Path]:
    """
    Find the path to a template directory.
    
    Args:
        template_name: Name of the template to find.
        custom_paths: Additional paths to search for templates.
        
    Returns:
        Path to template directory or None if not found.
    """
    search_paths = []
    
    # Add custom paths first
    if custom_paths:
        search_paths.extend(custom_paths)
    
    # Add default paths
    package_root = get_package_root()
    search_paths.extend([
        package_root / "templates",
        Path.cwd() / "templates",
        Path.home() / ".docgen" / "templates",
    ])
    
    # Check environment variable
    env_path = os.environ.get("DOCGEN_TEMPLATE_DIR")
    if env_path:
        search_paths.insert(0, Path(env_path))
    
    # Search for template
    for base_path in search_paths:
        template_path = Path(base_path) / template_name
        if template_path.is_dir() and (template_path / "template.yaml").exists():
            return template_path
    
    return None


def list_templates(custom_paths: Optional[List[str]] = None) -> List[str]:
    """
    List all available templates.
    
    Args:
        custom_paths: Additional paths to search for templates.
        
    Returns:
        List of template names.
    """
    templates = set()
    search_paths = []
    
    # Add custom paths
    if custom_paths:
        search_paths.extend(custom_paths)
    
    # Add default paths
    package_root = get_package_root()
    search_paths.extend([
        package_root / "templates",
        Path.cwd() / "templates",
        Path.home() / ".docgen" / "templates",
    ])
    
    # Check environment variable
    env_path = os.environ.get("DOCGEN_TEMPLATE_DIR")
    if env_path:
        search_paths.append(Path(env_path))
    
    # Find templates
    for base_path in search_paths:
        base_path = Path(base_path)
        if base_path.is_dir():
            for item in base_path.iterdir():
                if item.is_dir() and (item / "template.yaml").exists():
                    templates.add(item.name)
    
    return sorted(templates)


def get_file_format(file_path: str) -> str:
    """
    Determine the input format from file extension.
    
    Args:
        file_path: Path to the input file.
        
    Returns:
        Format string ('markdown' or 'asciidoc').
        
    Raises:
        ValueError: If format cannot be determined.
    """
    ext = Path(file_path).suffix.lower()
    
    markdown_extensions = {'.md', '.markdown', '.mdown', '.mkd'}
    asciidoc_extensions = {'.adoc', '.asciidoc', '.asc'}
    
    if ext in markdown_extensions:
        return 'markdown'
    elif ext in asciidoc_extensions:
        return 'asciidoc'
    else:
        raise ValueError(f"Unknown file format: {ext}")


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory.
        
    Returns:
        Path object for the directory.
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def format_date(date_str: Optional[str] = None, format_string: str = "%Y-%m-%d") -> str:
    """
    Format a date string or return current date.
    
    Args:
        date_str: Optional date string to format.
        format_string: Output format string.
        
    Returns:
        Formatted date string.
    """
    if date_str:
        # Try to parse various formats
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]:
            try:
                date = datetime.strptime(date_str, fmt)
                return date.strftime(format_string)
            except ValueError:
                continue
        return date_str
    
    return datetime.now().strftime(format_string)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename.
        
    Returns:
        Sanitized filename.
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    return filename
