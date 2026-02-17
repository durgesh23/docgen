"""
PDF Document Generator (docgen)

A flexible, template-based PDF document generator that converts
Markdown and AsciiDoc files into professionally formatted PDFs.
"""

__version__ = "1.0.0"
__author__ = "Document Generator Team"

from docgen.generator import PDFGenerator
from docgen.models import Document, DocumentElement, ElementType

__all__ = [
    "PDFGenerator",
    "Document",
    "DocumentElement",
    "ElementType",
    "__version__",
]
