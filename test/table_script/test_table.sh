#!/bin/bash

mkdir -p ./build
rm -f ./build/*

pandoc table.md title.txt  -s -o table.tex \
    --pdf-engine=xelatex \
    --template=./../../templates/snps_doc_1.tex \
    --toc \
    --verbose 2> ./build/pandoc_conversion.log \
    --log=./debug.log

xelatex -interaction=nonstopmode -output-directory=./build table.tex


