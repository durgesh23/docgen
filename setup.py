#!/usr/bin/env python3
"""Setup script for PDF Document Generator."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="docgen",
    version="1.0.0",
    author="Document Generator Team",
    author_email="docgen@example.com",
    description="A flexible PDF document generator from Markdown/AsciiDoc with template support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/docgen",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.10",
    install_requires=[
        "reportlab>=4.0.0",
        "markdown>=3.5.0",
        "PyYAML>=6.0.1",
        "Jinja2>=3.1.2",
        "click>=8.1.7",
        "python-dateutil>=2.8.2",
        "Pillow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "docgen=docgen.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "docgen": [
            "templates/**/*.yaml",
            "config/*.yaml",
        ],
    },
)
