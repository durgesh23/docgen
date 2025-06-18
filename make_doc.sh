#!/bin/bash

# Default values
input_file=""
output_type=""
output_file=""
doc_title=""
doc_author=""
doc_revision=""
# Current date in format YYYY-MM-DD
doc_date=$(date +"%B %d, %Y")

# Parse command-line arguments
while getopts "i:t:o:T:A:R:" opt; do
  case $opt in
    i) input_file="$OPTARG" ;;
    t) output_type="$OPTARG" ;;
    o) output_file="$OPTARG" ;;
    T) doc_title="$OPTARG" ;;
    A) doc_author="$OPTARG" ;;
    R) doc_revision="$OPTARG" ;;
    *)
      echo "Usage: $0 -i <input_markdown_file> -t <output_type (pdf|docx)> [-o <output_filename>] [-T <title>] [-A <author>] [-R <revision>]"
      exit 1
      ;;
  esac
done

# Check if the input file exists
if [ ! -f "$input_file" ]; then
  echo "Error: Input file '$input_file' not found."
  exit 1
fi

# Check if output type is valid
if [ "$output_type" != "pdf" ] && [ "$output_type" != "docx" ]; then
  echo "Error: Invalid output type. Use 'pdf' or 'docx'."
  exit 1
fi

# Set output filename
if [ -z "$output_file" ]; then
  # If output_file is not provided, use the input filename without extension
  input_basename=$(basename "$input_file")
  out_filename="${input_basename%.*}"
else
  out_filename="$output_file"
fi

# Set title if not provided
if [ -z "$doc_title" ]; then
  # Use filename as title if not provided
  title="${out_filename//_/ }"
else
  title="$doc_title"
fi

# Set revision if not provided
if [ -z "$doc_revision" ]; then
  revision="0.1.dev"
else
  revision="$doc_revision"
fi

# Set author if not provided
if [ -z "$doc_author" ]; then
  author="Synopsys"
else
  author="$doc_author"
fi

# Set table of contents
toc="Table of Contents"

# Function to run the pandoc command
function run_pandoc() {
  local output_type=$1
  local input_file=$2
  local out_filename=$3
  local title=$4
  local revision=$5
  local toc=$6
  local author=$7
  local date=$8

  if [ "$output_type" == "pdf" ]; then
      pandoc $input_file -o ./build/$out_filename.$output_type \
        --template=./templates/snps_doc.tex \
        --metadata title="$title" \
        --metadata revision="$revision" \
        --metadata toc="$toc" \
        --metadata author="$author" \
        --metadata date="$date" \
        -V datefontsize="\small" \
        -V titlepage=true \
        --pdf-engine=xelatex
  elif [ "$output_type" == "docx" ]; then
      pandoc $input_file -o ./build/$out_filename.$output_type \
        --metadata title="$title" \
        --metadata revision="$revision" \
        --metadata toc="$toc" \
        --metadata author="$author" \
        --metadata date="$date"
  fi
}

# Use current date
date="$doc_date"

# Create a build directory if it doesn't exist
rm -f ./build/* ./bin/*
mkdir -p ./build

# Clean previous generated files
echo "Cleaning previous generated files..."

echo "Generating pdf file..."
# Generate PDF file
if [ "$output_type" == "pdf" ]; then
    run_pandoc "$output_type" "$input_file" "$out_filename" "$title" "$revision" "$toc" "$author" "$date"
    echo "PDF file generated at ./build/$out_filename.$output_type"
# Generate DOCX file
elif [ "$output_type" == "docx" ]; then
    run_pandoc "$output_type" "$input_file" "$out_filename" "$title" "$revision" "$toc" "$author" "$date"
    echo "DOCX file generated at ./build/$out_filename.$output_type"
fi

# Check if the output file was created successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to generate the documentation."
    exit 1
fi

# Ensure the bin directory exists
mkdir -p ./bin
# Move the generated file from build directory to the bin directory
mv ./build/$out_filename.$output_type ./bin/$out_filename.$output_type
echo "Generated ${out_filename}.${output_type} successfully."
echo "## DONE"
