# DocGen Project - Development Context

**Last Updated:** February 17, 2026  
**Branch:** `explore/adoc`  
**Status:** Active Development

## Project Overview

DocGen is a Python-based PDF document generator that converts Markdown and AsciiDoc documents into professionally styled PDFs. The tool is designed to generate Ford-style release notes and technical documentation.

## Architecture

```
docgen/
├── src/docgen/
│   ├── __init__.py
│   ├── cli.py              # Click-based CLI
│   ├── generator.py        # Main document generator
│   ├── models.py           # Document data models
│   ├── parsers/
│   │   ├── base.py         # Base parser interface
│   │   ├── markdown_parser.py
│   │   └── asciidoc_parser.py
│   ├── renderers/
│   │   ├── pdf_renderer.py # ReportLab PDF rendering
│   │   └── styles.py       # Style management
│   └── utils/
│       └── helpers.py      # Utility functions
├── templates/
│   ├── ford_release_notes/ # Ford ECG2 VECU style
│   │   ├── template.yaml
│   │   ├── styles.yaml
│   │   └── header_footer.yaml
│   └── generic/
│       ├── template.yaml
│       ├── styles.yaml
│       └── header_footer.yaml
└── tests/                  # 115 tests
```

## Features Implemented

### Core Features
- [x] Markdown parsing with YAML front matter
- [x] AsciiDoc parsing support
- [x] PDF generation using ReportLab
- [x] Template-based styling (YAML configuration)
- [x] Headers and footers with page numbers
- [x] Tables with styling
- [x] Ordered and unordered lists (nested)
- [x] Code blocks with syntax highlighting
- [x] Blockquotes
- [x] Horizontal rules

### Advanced Features
- [x] **Image rendering** - Inline and block images with sizing
- [x] **Table of Contents (TOC)** - Auto-generated with configurable depth
- [x] **Watch mode** - Auto-regenerate on file changes (`--watch`)
- [x] **Batch processing** - Process multiple files (`--batch`)
- [x] **Admonitions** - NOTE, WARNING, TIP, IMPORTANT, CAUTION blocks
- [x] **Title page** - Professional title page matching Ford ECG2 VECU style

### Title Page Features
- Verification Continuum™ branding (top-left)
- Document title (left-aligned)
- Version number (bottom-right)
- Date (bottom-right)
- No header/footer on title page
- Absolute positioning matching sample PDF coordinates

## CLI Usage

```bash
# Basic usage
docgen input.md -o output.pdf

# With template
docgen input.md -o output.pdf -t ford_release_notes

# With metadata override
docgen input.md -o output.pdf --meta 'title=My Doc' --meta 'version=1.0'

# Watch mode
docgen input.md -o output.pdf --watch

# Batch processing
docgen input_dir/ --batch --output-dir output_dir/
```

## Templates

### ford_release_notes
- Matches Ford ECG2 VECU Release Notes style
- Letter size (8.5" x 11")
- 1-inch margins
- Navy blue headings
- Professional header/footer with:
  - Document title and version
  - "Ford Confidential" notice
  - Page numbers (Page X of Y)
  - Date

### generic
- Clean, minimal style
- Suitable for general documentation

## Metadata (YAML Front Matter)

```yaml
---
title: "Ford ECG2 VECU Release Notes"
version: "R2.8.1"
date: "February 2026"
author: "Engineering Team"
confidentiality: "Ford Confidential"
document_number: "VECU-RN-001"
revision: "A"
---
```

## Test Coverage

- **115 tests** across all modules
- Tests located in `tests/` directory
- Run with: `pytest tests/ -q`

## Git History (Recent Commits)

| Commit | Description |
|--------|-------------|
| 8b48e2d | Update example to match Ford ECG2 VECU Release Notes format |
| f164d42 | Update title page positioning to match sample PDF exactly |
| ab91c30 | Add title page support with branding, title, version, and date |
| ec22b63 | Add project configuration and build files |
| 18bd4ab | Add example documents and generated output |
| 7988e05 | Add comprehensive test suite (115 tests) |
| 1afc9b7 | Add PDF templates: ford_release_notes and generic |
| b0ae530 | Add utility helpers and package metadata |
| e152f47 | Add PDF renderer with ReportLab |
| cb6df6a | Add Markdown and AsciiDoc parsers |
| 82f681b | Add core docgen module with models, generator, and CLI |

## Dependencies

- **reportlab** - PDF generation
- **pyyaml** - YAML parsing
- **click** - CLI framework
- **watchdog** - File watching (for --watch mode)
- **pypdf** - PDF reading (for testing)

## Sample Output

Title page renders as:
```
Verification Continuum™
Ford ECG2 VECU Release Notes
                                        Version R2.8.1
                                        February 2026
```

Content pages include header/footer:
```
┌────────────────────────────────────────────────────────┐
│ Ford ECG2 VECU Release Notes        Version: R2.8.1   │
│ ────────────────────────────────────────────────────── │
│                                                        │
│                      [Content]                         │
│                                                        │
│ ────────────────────────────────────────────────────── │
│ Ford Confidential              Page 2 of 5  Feb 2026  │
└────────────────────────────────────────────────────────┘
```

## Next Steps / TODO

- [ ] Add logo/image support on title page
- [ ] Support custom fonts (TTF/OTF)
- [ ] Add watermark support
- [ ] Export to additional formats (HTML, DOCX)
- [ ] Add section numbering option
- [ ] Improve TOC styling with dot leaders

## Files Modified in Session

1. `src/docgen/renderers/pdf_renderer.py` - Added TitlePageFlowable, absolute positioning
2. `src/docgen/renderers/styles.py` - Added get_title_page_config(), get_structure_config()
3. `templates/ford_release_notes/template.yaml` - Added title_page configuration
4. `templates/ford_release_notes/styles.yaml` - Added title_page_* styles
5. `examples/sample_release_notes.md` - Updated front matter to match sample
