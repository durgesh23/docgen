# PDF Document Generator (docgen)

A flexible, template-based PDF document generator that converts Markdown (`.md`) and AsciiDoc (`.adoc`) files into professionally formatted PDF documents.

## Features

- **Multi-format Input**: Support for Markdown and AsciiDoc source files
- **Template System**: Multiple templates for different document styles
- **Professional Output**: High-quality PDF generation matching corporate standards
- **Customizable Styling**: Configurable fonts, colors, margins, headers, and footers
- **Table Support**: Full table rendering with styling options
- **Metadata Support**: Extract and use document metadata (title, version, date, etc.)
- **CLI & API**: Use via command line or integrate into Python applications
- **Watch Mode**: Auto-regenerate PDF when source files change
- **Batch Processing**: Convert multiple files at once
- **Image Support**: Embed images with automatic scaling
- **Table of Contents**: Generate automatic TOC from document headings
- **Admonitions**: Styled NOTE, TIP, WARNING, CAUTION, and IMPORTANT blocks

## Installation

### From Source

```bash
# Clone the repository
cd docgen

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Quick Install

```bash
pip install -e .
```

## Quick Start

### Command Line Usage

```bash
# Basic conversion
docgen input.md -o output.pdf

# Using a specific template
docgen input.md -o output.pdf --template ford_release_notes

# With custom metadata
docgen input.md -o output.pdf --template ford_release_notes \
    --meta title="My Document" \
    --meta version="1.0.0" \
    --meta date="2026-02-17"

# List available templates
docgen --list-templates

# Watch mode - auto-regenerate on file changes
docgen input.md -o output.pdf --watch

# Batch processing - convert all files in a directory
docgen --batch ./docs --output-dir ./pdfs

# Show help
docgen --help
```

### Python API Usage

```python
from docgen import PDFGenerator

# Create generator with template
generator = PDFGenerator(template="ford_release_notes")

# Generate PDF from Markdown
generator.generate(
    input_file="release_notes.md",
    output_file="release_notes.pdf",
    metadata={
        "title": "ECG2 VECU Release Notes",
        "version": "1.0.0",
        "date": "2026-02-17",
        "confidentiality": "Ford Confidential"
    }
)

# Generate from string content
generator.generate_from_string(
    content="# Hello World\n\nThis is a test document.",
    output_file="test.pdf",
    input_format="markdown"
)
```

## Input File Format

### Markdown with YAML Front Matter

```markdown
---
title: "ECG2 VECU Release Notes"
version: "1.0.0"
date: "2026-02-17"
author: "Engineering Team"
confidentiality: "Ford Confidential"
---

# Document Title

## Section 1: Overview

This is the overview section with **bold** and *italic* text.

## Section 2: Change Log

| Version | Date       | Description          |
|---------|------------|----------------------|
| 1.0.0   | 2026-02-17 | Initial release      |
| 0.9.0   | 2026-01-15 | Beta release         |

## Section 3: Details

- Bullet point 1
- Bullet point 2
  - Nested bullet
- Bullet point 3

1. Numbered item 1
2. Numbered item 2
3. Numbered item 3
```

### AsciiDoc Format

```asciidoc
= ECG2 VECU Release Notes
:version: 1.0.0
:date: 2026-02-17
:author: Engineering Team
:confidentiality: Ford Confidential

== Overview

This is the overview section with *bold* and _italic_ text.

== Change Log

[cols="1,2,4", options="header"]
|===
|Version |Date |Description
|1.0.0 |2026-02-17 |Initial release
|0.9.0 |2026-01-15 |Beta release
|===

== Details

* Bullet point 1
* Bullet point 2
** Nested bullet
* Bullet point 3

== Important Notes

NOTE: This is an informational note.

WARNING: This is a warning message.

TIP: This is a helpful tip.
```

### Admonitions (AsciiDoc)

AsciiDoc supports special callout blocks for important information:

```asciidoc
NOTE: Informational message for users.

TIP: Helpful hints and best practices.

IMPORTANT: Critical information that must not be missed.

WARNING: Indicates potential issues or caveats.

CAUTION: Warns about dangerous or destructive actions.
```

These render as color-coded boxes in the PDF output.

## Templates

### Available Templates

| Template | Description |
|----------|-------------|
| `ford_release_notes` | Professional release notes format matching Ford ECG2 VECU style |
| `generic` | Clean, general-purpose document template |

### Template Structure

Each template consists of:

```
templates/
└── template_name/
    ├── template.yaml      # Main template configuration
    ├── styles.yaml        # Typography and color definitions
    └── header_footer.yaml # Header and footer settings
```

### Creating Custom Templates

1. Copy an existing template folder
2. Modify the YAML configuration files
3. Place in the `templates/` directory

#### template.yaml

```yaml
name: "My Custom Template"
version: "1.0"
description: "Custom template for my documents"

page:
  size: "LETTER"        # LETTER, A4, LEGAL, etc.
  orientation: "portrait"  # portrait or landscape
  margins:
    top: 72             # in points (72 points = 1 inch)
    bottom: 72
    left: 72
    right: 72
```

#### styles.yaml

```yaml
fonts:
  default:
    family: "Helvetica"
    size: 10
    color: "#000000"
  
  heading1:
    family: "Helvetica-Bold"
    size: 18
    color: "#000080"
    space_before: 18
    space_after: 12
  
  heading2:
    family: "Helvetica-Bold"
    size: 14
    color: "#000080"
    space_before: 14
    space_after: 8

  table_header:
    family: "Helvetica-Bold"
    size: 10
    background: "#D0D0D0"
    color: "#000000"

  table_cell:
    family: "Helvetica"
    size: 9
    padding: 6

colors:
  primary: "#000080"
  secondary: "#333333"
  border: "#000000"
  alt_row: "#F5F5F5"
```

#### header_footer.yaml

```yaml
header:
  enabled: true
  height: 50
  first_page: false    # Show header on first page?
  
  elements:
    - type: "text"
      content: "{title}"
      position: "left"
      style: "header_text"
    
    - type: "line"
      position: "bottom"
      color: "#000080"
      width: 1

footer:
  enabled: true
  height: 40
  first_page: true
  
  elements:
    - type: "text"
      content: "{confidentiality}"
      position: "left"
      style: "footer_text"
    
    - type: "text"
      content: "Page {page_number} of {total_pages}"
      position: "center"
      style: "footer_text"
    
    - type: "text"
      content: "{date}"
      position: "right"
      style: "footer_text"
    
    - type: "line"
      position: "top"
      color: "#000080"
      width: 1
```

## CLI Reference

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output PDF file path |
| `--template` | `-t` | Template to use (default: ford_release_notes) |
| `--meta` | | Metadata key=value pairs (repeatable) |
| `--list-templates` | | List available templates |
| `--template-info` | | Show template details |
| `--config` | | Path to configuration file |
| `--debug` | | Enable debug output |
| `--watch` | `-w` | Watch file for changes and auto-regenerate |
| `--batch` | | Process all .md/.adoc files in directory |
| `--output-dir` | | Output directory for batch processing |
| `--version` | | Show version number |
| `--help` | | Show help message |

### Examples

```bash
# Watch mode - auto-regenerate on save
docgen release_notes.md -o output.pdf --watch

# Batch convert entire directory
docgen --batch ./docs --output-dir ./pdfs --template generic

# Override multiple metadata fields
docgen input.md -o out.pdf \
    --meta title="Custom Title" \
    --meta version="2.0" \
    --meta author="John Doe"

# Use debug mode for troubleshooting
docgen input.md -o output.pdf --debug
```

## Configuration

### Global Configuration

Create a `config.yaml` file to set defaults:

```yaml
default_template: "ford_release_notes"
output_directory: "./output"

defaults:
  confidentiality: "Confidential"
  author: "Engineering Team"

logging:
  level: "INFO"
  file: "docgen.log"
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DOCGEN_TEMPLATE_DIR` | Custom template directory path |
| `DOCGEN_CONFIG` | Path to configuration file |
| `DOCGEN_OUTPUT_DIR` | Default output directory |

## API Reference

### PDFGenerator Class

```python
class PDFGenerator:
    def __init__(
        self,
        template: str = "generic",
        config_path: Optional[str] = None
    ):
        """
        Initialize PDF generator.
        
        Args:
            template: Template name to use
            config_path: Path to custom configuration file
        """
    
    def generate(
        self,
        input_file: str,
        output_file: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate PDF from input file.
        
        Args:
            input_file: Path to .md or .adoc file
            output_file: Output PDF path
            metadata: Optional metadata overrides
            
        Returns:
            Path to generated PDF
        """
    
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
            content: Document content as string
            output_file: Output PDF path
            input_format: "markdown" or "asciidoc"
            metadata: Optional metadata
            
        Returns:
            Path to generated PDF
        """
    
    def list_templates(self) -> List[str]:
        """Return list of available template names."""
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Return template configuration details."""
```

### Document Model

```python
@dataclass
class Document:
    """Represents a parsed document."""
    metadata: Dict[str, Any]
    content: List[DocumentElement]
    
@dataclass
class DocumentElement:
    """Base class for document elements."""
    element_type: str  # heading, paragraph, table, list, etc.
    content: Any
    attributes: Dict[str, Any]
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=docgen --cov-report=html

# Run specific test file
pytest tests/test_generator.py

# Run with verbose output
pytest -v
```

### Code Style

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Project Structure

```
docgen/
├── README.md
├── requirements.txt
├── setup.py
├── config/
│   └── default_config.yaml
├── templates/
│   ├── ford_release_notes/
│   │   ├── template.yaml
│   │   ├── styles.yaml
│   │   └── header_footer.yaml
│   └── generic/
│       ├── template.yaml
│       ├── styles.yaml
│       └── header_footer.yaml
├── src/
│   └── docgen/
│       ├── __init__.py
│       ├── cli.py
│       ├── generator.py
│       ├── models.py
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── markdown_parser.py
│       │   └── asciidoc_parser.py
│       ├── renderers/
│       │   ├── __init__.py
│       │   ├── pdf_renderer.py
│       │   └── styles.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_generator.py
│   ├── test_parsers.py
│   ├── test_renderers.py
│   └── test_cli.py
├── examples/
│   ├── sample_release_notes.md
│   ├── sample_document.adoc
│   └── output/
└── sample/
    └── Ford_ECG2_VECU_ReleaseNotes.pdf
```

## Troubleshooting

### Common Issues

**Q: PDF generation fails with font error**
A: Ensure you have the required fonts installed, or use built-in fonts (Helvetica, Times-Roman, Courier).

**Q: Tables are not rendering correctly**
A: Check that your Markdown tables follow the standard format with proper column separators.

**Q: AsciiDoc parsing fails**
A: Ensure `asciidoctor` is installed: `gem install asciidoctor`

**Q: Watch mode isn't detecting changes**
A: The watch mode polls every 1 second. Ensure the file is being saved and not just modified in a buffer.

**Q: Images aren't appearing in the PDF**
A: Check that image paths are relative to the input document or use absolute paths. Supported formats: PNG, JPEG, GIF.

### Logging

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or via CLI:

```bash
docgen input.md -o output.pdf --debug
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Changelog

### v1.1.0 (2026-02-17)
- **Watch Mode**: Auto-regenerate PDF when source files change (`--watch` / `-w`)
- **Batch Processing**: Convert multiple files at once (`--batch` / `--output-dir`)
- **Image Support**: Embed images with automatic scaling and captions
- **Table of Contents**: Generate automatic TOC from document headings
- **Admonitions**: Styled NOTE, TIP, WARNING, CAUTION, and IMPORTANT blocks
- Added TOC configuration to templates
- Added admonition color styling to templates
- New tests for all new features (115 total tests)

### v1.0.0 (2026-02-15)
- Initial release
- Markdown and AsciiDoc support
- Ford Release Notes template
- Generic template
- CLI and Python API
