echo #!/bin/bash
echo "## Generating PDF documentation for FORD ECG2 VDK User Guide"
echo "Cleaning pervious generated files..."
rm -f FORD_ECG2_UserGuide.pdf
echo "## Making PDF documentation"
title="FORD ECG2 VDK User Guide"
toc="Table of Contents"
author="Synopsys"
pandoc FORD_ECG2_UserGuide.md -o FORD_ECG2_UserGuide.pdf \
    --template=generic_template.tex \
    --pdf-engine=xelatex \
    --number-sections \
    --listings \
    -V title="$title" \
    -V author="$author" \
    -V date="June 16, 2025"
echo "## DONE"
