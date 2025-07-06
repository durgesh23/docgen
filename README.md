# DocGen

A powerful tool to create PDF, HTML, and DOCX documentation from Markdown files with advanced formatting and features.

## Features

- Convert Markdown files to PDF, HTML, or DOCX formats
- Enhanced table support with text wrapping and code formatting
- Customizable templates for each output format
- Support for metadata and document properties
- Table of contents generation
- Professional document styling


## Environment Setup

```bash

source setup_env.sh
```


## Usage

`docgen.sh` can be used from any location

```bash
docgen.sh -i <input_file> -m <metadata-file> -f <pdf/docx/html> 

```

### Command Line Arguments

- `-i, --input`: Path to input markdown file
- `-f, --format`: Output format (pdf, html, docx)
- `-o, --output-dir`: Output directory for generated files
- `-m, --metadata-file`: Path to YAML metadata file for document properties
- `-t, --template-file`: Path to custom template file
- `-v, --verbose`: Increase verbosity (can be used multiple times, e.g. -vv for debug level)
- `--log-file`: Specify custom log file path (defaults to output-dir/logs/docgen.log)

### Metadata File

The metadata file is a YAML file that defines document properties:

```yaml
# Document Metadata
title: "Document Title"
author: "Author Name"  # Can be a string or a list
date: "2025-07-06"
subtitle: "Document Subtitle"
abstract: "A brief summary of the document"
keywords: ["keyword1", "keyword2"]

# Additional Properties
version: "1.0.0"
revision: "A"
copyright: "© 2025 Your Organization"
```

### Template Customization

DocGen includes enhanced templates with special support for:

- Advanced table formatting (see [Table Formatting Guide](docgen/docs/table_formatting.md))
- Code block styling and line wrapping
- Title pages and document structure
- Headers and footers
