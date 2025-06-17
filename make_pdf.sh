#!/bin/bash

# Check if an output type argument is provided
if [ -z "$1" ]; then
    echo "Error: No output type specified. Use 'pdf' or 'docx'."
    exit 1
fi

output_type=$1

# Validate the output type
if [ "$output_type" != "pdf" ] && [ "$output_type" != "docx" ]; then
    echo "Error: Invalid output type. Use 'pdf' or 'docx'."
    exit 1
fi

# Common variables
out_filename="FORD_ECG2_UserGuide"
title="FORD ECG2 VDK User Guide"
revision="0.1 Draft"
toc="Table of Contents"
author="Synopsys"

# Create a build directory if it doesn't exist
rm -f ./build/*
mkdir -p ./build

# Clean previous generated files
echo "Cleaning previous generated files..."

# Copy necessary files to the build directory
cp $out_filename.md ./build/
cp generic_template.tex ./build/

# Generate intermediate .tex file for debugging
echo "## Generating intermediate .tex file"
# Add the --toc flag to ensure the table of contents is generated
pandoc ./build/$out_filename.md -o ./build/$out_filename.tex \
    --template=./build/generic_template.tex \
    --pdf-engine=xelatex \
    --number-sections \
    --listings \
    --toc \
    --verbose 2> ./build/pandoc_conversion.log \
    -V title="$title" \
    -V revision="$revision" \
    -V toc="$toc" \
    -V toc-depth=3 \
    -V lang="en" \
    -V author="$author" \
    -V date="June 16, 2025"

# Update paths for generated files
out_filename="./build/$out_filename"

# Generate the requested output type
if [ "$output_type" == "pdf" ]; then
    echo "## Generating PDF documentation"
    if [ -f $out_filename.tex ]; then
        xelatex $out_filename.tex
    else
        echo "Error: Intermediate .tex file not found. PDF generation aborted."
        exit 1
    fi
    
    echo "------------------------------------------------------------------------"
    echo ""
    # Check for pending TODOs in the intermediate .tex file and log them
    if [ "$output_type" == "pdf" ] && [ -f $out_filename.tex ]; then
        if grep -q '\\todo{' $out_filename.tex; then
            echo "########################################################"
            echo "## Validating generated PDF file for TODOs"
            echo "########################################################"
            echo "## WARNING: The following TODOs are still pending in the document:"
            echo ""
            grep -n '\\todo{' $out_filename.tex | while IFS=: read -r tex_line_number todo; do
                # Extract the corresponding Markdown line number from the Pandoc log
                md_line_number=$(grep "^$out_filename.md:" ./build/pandoc_conversion.log | grep "line $tex_line_number:" | awk -F 'line ' '{print $2}' | awk '{print $1}')
                if [[ -z "$md_line_number" || ! "$md_line_number" =~ ^[0-9]+$ ]]; then
                    md_line_number="Unknown"
                    markdown_line="(Original Markdown line not found)"
                else
                    markdown_line=$(sed -n "${md_line_number}p" $out_filename.md)
                fi
                # TODO Fix the line number extraction logic
                echo "  - TeX Line $tex_line_number"
                # echo "  - Markdown Line $md_line_number: $markdown_line"
                echo "    TODO: $todo"
            done
            echo ""
            echo "## Please address these TODOs before finalizing the PDF."
        fi
    fi   
elif [ "$output_type" == "docx" ]; then
    echo "## Generating .docx file"
    pandoc FORD_ECG2_UserGuide.md -o FORD_ECG2_UserGuide.docx \
        --template=generic_template.tex \
        --number-sections \
        --listings \
        -V title="$title" \
        -V toc="$toc" \
        -V toc-depth=3 \
        -V lang="en" \
        -V author="$author" \
        -V date="June 16, 2025"
fi

echo "Generated ${out_filename}.${output_type} successfully."
echo "## DONE"
