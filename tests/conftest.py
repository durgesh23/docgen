"""
Test configuration and fixtures for docgen tests.
"""

import os
import tempfile
from pathlib import Path
import pytest

from docgen.generator import PDFGenerator
from docgen.models import Document, DocumentMetadata, DocumentElement, ElementType


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_markdown():
    """Sample Markdown content for testing."""
    return """---
title: "Test Document"
version: "1.0.0"
date: "2026-02-17"
author: "Test Author"
confidentiality: "Confidential"
---

# Test Document Title

## Introduction

This is a test document with **bold** and *italic* text.

## Features

- Feature 1
- Feature 2
- Feature 3

## Data Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value A  | Value B  | Value C  |
| Value D  | Value E  | Value F  |

## Code Example

```python
def hello_world():
    print("Hello, World!")
```

## Conclusion

This is the conclusion of the test document.
"""


@pytest.fixture
def sample_asciidoc():
    """Sample AsciiDoc content for testing."""
    return """= Test Document Title
:version: 1.0.0
:date: 2026-02-17
:author: Test Author
:confidentiality: Confidential

== Introduction

This is a test document with *bold* and _italic_ text.

== Features

* Feature 1
* Feature 2
* Feature 3

== Data Table

|===
|Column 1 |Column 2 |Column 3

|Value A
|Value B
|Value C

|Value D
|Value E
|Value F
|===

== Code Example

[source,python]
----
def hello_world():
    print("Hello, World!")
----

== Conclusion

This is the conclusion of the test document.
"""


@pytest.fixture
def sample_document():
    """Create a sample Document object for testing."""
    metadata = DocumentMetadata(
        title="Test Document",
        version="1.0.0",
        date="2026-02-17",
        author="Test Author",
        confidentiality="Confidential"
    )
    
    elements = [
        DocumentElement(
            element_type=ElementType.HEADING1,
            content="Introduction",
            attributes={"id": "introduction"}
        ),
        DocumentElement(
            element_type=ElementType.PARAGRAPH,
            content="This is a test paragraph."
        ),
        DocumentElement(
            element_type=ElementType.HEADING2,
            content="Details",
            attributes={"id": "details"}
        ),
        DocumentElement(
            element_type=ElementType.PARAGRAPH,
            content="More detailed information here."
        ),
    ]
    
    return Document(
        metadata=metadata,
        elements=elements,
        source_format="markdown"
    )


@pytest.fixture
def template_dir():
    """Get path to test template directory."""
    # Use the actual templates from the project
    return Path(__file__).parent.parent / "templates"


@pytest.fixture
def generator(template_dir):
    """Create a PDFGenerator instance for testing."""
    return PDFGenerator(
        template="ford_release_notes",
        template_paths=[str(template_dir)]
    )
