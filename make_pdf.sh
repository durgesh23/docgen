#!/bin/bash

# Default values
input_file=""
output_type=""

# Parse command-line arguments
while getopts "i:t:" opt; do
  case $opt in
    i) input_file="$OPTARG" ;;
    t) output_type="$OPTARG" ;;
    *)
      echo "Usage: $0 -i <input_markdown_file> -t <output_type (pdf|docx)>"
      exit 1
      ;;
  esac
done

# Validate input markdown file
if [ -z "$input_file" ]; then
  echo "Error: Input markdown file not specified."
  echo "Usage: $0 -i <input_markdown_file> -t <output_type (pdf|docx)>"
  exit 1
fi

if [ ! -f "$input_file" ]; then
  echo "Error: Input file '$input_file' not found."
  exit 1
fi

# Validate output type
if [ -z "$output_type" ]; then
  echo "Error: Output type not specified."
  echo "Usage: $0 -i <input_markdown_file> -t <output_type (pdf|docx)>"
  exit 1
fi

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

echo "## Generating intermediate .tex file"
# Generate intermediate .tex file for debugging
pandoc $input_file -o ./build/$out_filename.tex \
    --template=generic_template.tex \
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
    -V date="June 17, 2025" \
    -V tables=yes \
    -V table-use-row-colors=true \
    --lua-filter=./fix_real.lua \

# Update paths for generated files
out_filename="./build/$out_filename"

# Generate the requested output type
if [ "$output_type" == "pdf" ]; then
    echo "## Generating PDF documentation"
    if [ -f $out_filename.tex ]; then
        # Direct fix for \real command with sed
        echo "## Preprocessing .tex file to fix table issues..."
        # Fix the \real command first (using proper sed regex with capture groups)
        sed -i 's/\\real{\([0-9.]\+\)}/\1/g' $out_filename.tex
        # Fix the complex table column width expressions
        sed -i 's/(\\columnwidth - 2\\tabcolsep) \* \\real{\([0-9.]\+\)}/\\dimexpr\\columnwidth * \1\\relax/g' $out_filename.tex
        # Extra pattern for the most problematic pattern (line 576)
        sed -i 's/>{\\\(raggedright\\arraybackslash\)}p{(\\columnwidth - 2\\tabcolsep) \* \\real{\([0-9.]\+\)}}@{}/>{\\\1}p{0.\2\\textwidth}@{}/g' $out_filename.tex
        
        # Run xelatex twice to ensure proper resolution of references and table formatting
        echo "Running first pass of xelatex..."
        xelatex -interaction=nonstopmode -output-directory=./build $out_filename.tex
        
        echo "Running second pass of xelatex..."
        xelatex -output-directory=./build $out_filename.tex
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
