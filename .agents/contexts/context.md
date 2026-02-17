# DocGen Project - Development Context

**Last Updated:** February 17, 2026  
**Branch:** `explore/adoc`  
**Status:** Active Development

## Project Overview

DocGen is a Python-based PDF document generator that converts Markdown and AsciiDoc documents into professionally styled PDFs. The tool is designed to generate Synopsys-style release notes and technical documentation.

## Architecture

```
docgen/
├── src/docgen/
│   ├── cli.py              # Click-based CLI
│   ├── generator.py        # Main document generator
│   ├── models.py           # Document data models
│   ├── parsers/            # Markdown & AsciiDoc parsers
│   └── renderers/
│       ├── pdf_renderer.py # ReportLab PDF rendering
│       └── styles.py       # Style management
├── templates/
│   ├── ford_release_notes/ # Ford ECG2 VECU style
│   ├── generic/            # Basic style
│   ├── copyright/          # Copyright page content
│   │   └── copyright.md
│   └── logos/
│       └── snps_logo.png   # Synopsys logo (642x146)
└── tests/                  # 115 tests
```

## Features Implemented

### Title Page
- **Logo**: Synopsys logo at top-right (150x34 display)
- **Branding**: "Verification Continuum™" - 16pt, purple (#5a428c)
- **Title**: Document title - 24pt, black
- **Horizontal line**: After title, purple accent color
- **Version/Date**: Bottom-right, 11pt

### Document Structure
- **Copyright page**: Auto-generated from `templates/copyright/copyright.md`
- **Table of Contents**: Auto-generated with styled title
- **Chapters**: H1 starts on new page with top spacing
- **Headers/Footers**: Title, version, page numbers, date

### Page Settings (Current)
- **Size**: LETTER (612x792 points)
- **Margins**: 57pt all sides (~0.79 inch, matches sample PDF)

### Accent Color
- **Synopsys Purple**: `#5a428c` (extracted from logo)

## CLI Usage

```bash
docgen input.md -o output.pdf -t ford_release_notes
docgen input.adoc -o output.pdf -t ford_release_notes --watch
```

## Configuration Files

### template.yaml - Key Settings
```yaml
page:
  margins: {top: 57, bottom: 57, left: 57, right: 57}

title_page:
  enabled: true
  elements:
    - type: image (logo, top-right)
    - type: text (branding, title)
    - type: line (horizontal separator)
    - type: text (version, date)

copyright:
  enabled: true

chapter:
  start_new_page: true
  top_spacing: 72
```

### styles.yaml - Key Font Styles
```yaml
title_page_branding: {size: 16, color: "#5a428c"}
title_page_title: {size: 24, color: "#000000"}
heading1: {size: 14, color: "#5a428c", border_bottom: true}
```

## Sample PDF Reference

From `sample/Ford_ECG2_VECU_ReleaseNotes.pdf`:
- Title page text positions: y=596.8 (branding), y=567 (title), y=157.8 (version), y=144.2 (date)
- Left margin: x=56.7 (~57pt)
- Logo: 642x146 pixels

## Test Commands

```bash
pytest tests/ -q                    # Run all 115 tests
docgen examples/sample_release_notes.md -o examples/output/sample_release_notes.pdf -t ford_release_notes
```

## Recent Session Changes

1. Fixed title page overflow - relative positioning system
2. Added logo support with `_draw_image_element()`
3. Added horizontal line support with `_draw_line_element()`
4. Added copyright page from `templates/copyright/copyright.md`
5. Added TOC page with styled title
6. Added chapter styling (page breaks, top spacing)
7. Updated accent color to Synopsys purple (#5a428c)
8. Reduced margins from 72pt to 57pt to match sample

## Key Files Modified

- `src/docgen/renderers/pdf_renderer.py` - TitlePageFlowable with image/line support
- `src/docgen/renderers/styles.py` - get_copyright_config(), get_chapter_config()
- `templates/ford_release_notes/template.yaml` - Title page, margins, structure
- `templates/ford_release_notes/styles.yaml` - Purple accent colors
- `templates/copyright/copyright.md` - Copyright template (new)

## TODO

- [ ] Custom fonts (TTF/OTF)
- [ ] Watermarks
- [ ] TOC dot leaders/page numbers
- [ ] Section numbering
