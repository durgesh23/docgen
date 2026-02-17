"""
Command-line interface for PDF Document Generator.
"""

import sys
from pathlib import Path
from typing import Optional, Tuple
import click

from docgen.generator import PDFGenerator
from docgen.utils import list_templates


def parse_metadata(ctx, param, value) -> dict:
    """Parse metadata key=value pairs."""
    metadata = {}
    for item in value:
        if '=' in item:
            key, val = item.split('=', 1)
            metadata[key.strip()] = val.strip()
        else:
            click.echo(f"Warning: Invalid metadata format '{item}', expected 'key=value'", err=True)
    return metadata


@click.command()
@click.argument('input_file', type=click.Path(exists=True), required=False)
@click.option(
    '-o', '--output',
    type=click.Path(),
    help='Output PDF file path. Defaults to input filename with .pdf extension.'
)
@click.option(
    '-t', '--template',
    default='ford_release_notes',
    help='Template to use for PDF generation.'
)
@click.option(
    '--meta',
    multiple=True,
    callback=parse_metadata,
    help='Metadata in key=value format (can be used multiple times).'
)
@click.option(
    '--list-templates',
    'show_templates',
    is_flag=True,
    help='List available templates and exit.'
)
@click.option(
    '--template-info',
    'template_info',
    is_flag=True,
    help='Show information about the selected template.'
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Path to configuration file.'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug output.'
)
@click.option(
    '--watch', '-w',
    is_flag=True,
    help='Watch input file for changes and auto-regenerate PDF.'
)
@click.option(
    '--batch',
    'batch_dir',
    type=click.Path(exists=True),
    help='Process all .md/.adoc files in directory.'
)
@click.option(
    '--output-dir',
    'output_dir',
    type=click.Path(),
    help='Output directory for batch processing.'
)
@click.version_option(version='1.0.0', prog_name='docgen')
def main(
    input_file: Optional[str],
    output: Optional[str],
    template: str,
    meta: dict,
    show_templates: bool,
    template_info: bool,
    config: Optional[str],
    debug: bool,
    watch: bool,
    batch_dir: Optional[str],
    output_dir: Optional[str]
):
    """
    PDF Document Generator - Convert Markdown/AsciiDoc to PDF.
    
    Generate professional PDF documents from Markdown (.md) or AsciiDoc (.adoc)
    files using customizable templates.
    
    \b
    Examples:
        docgen input.md -o output.pdf
        docgen input.md --template ford_release_notes
        docgen input.adoc -o docs/output.pdf --meta title="My Document"
        docgen --list-templates
        docgen input.md --watch
        docgen --batch ./docs --output-dir ./pdfs
    """
    # Enable debug logging if requested
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # List templates if requested
    if show_templates:
        templates = list_templates()
        if templates:
            click.echo("Available templates:")
            for t in templates:
                marker = " (default)" if t == "ford_release_notes" else ""
                click.echo(f"  - {t}{marker}")
        else:
            click.echo("No templates found.")
        return
    
    # Show template info if requested
    if template_info:
        try:
            generator = PDFGenerator(template=template, config_path=config)
            info = generator.get_template_info()
            
            click.echo(f"Template: {info.get('name', template)}")
            click.echo(f"Version: {info.get('version', 'N/A')}")
            click.echo(f"Description: {info.get('description', 'N/A')}")
            
            page = info.get('page', {})
            click.echo(f"Page size: {page.get('size', 'LETTER')}")
            click.echo(f"Orientation: {page.get('orientation', 'portrait')}")
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        return
    
    # Batch processing mode
    if batch_dir:
        try:
            generator = PDFGenerator(template=template, config_path=config)
            batch_path = Path(batch_dir)
            
            # Find all markdown and asciidoc files
            input_files = list(batch_path.glob('*.md')) + list(batch_path.glob('*.adoc'))
            
            if not input_files:
                click.echo(f"No .md or .adoc files found in {batch_dir}", err=True)
                sys.exit(1)
            
            click.echo(f"Batch processing {len(input_files)} files with template: {template}")
            
            # Determine output directory
            out_path = Path(output_dir) if output_dir else batch_path
            out_path.mkdir(parents=True, exist_ok=True)
            
            success_count = 0
            for input_path in input_files:
                output_file = out_path / input_path.with_suffix('.pdf').name
                try:
                    generator.generate(str(input_path), str(output_file), metadata=meta)
                    click.echo(f"  ✓ {input_path.name} -> {output_file.name}")
                    success_count += 1
                except Exception as e:
                    click.echo(f"  ✗ {input_path.name}: {e}", err=True)
            
            click.echo(f"Completed: {success_count}/{len(input_files)} files generated")
            
        except Exception as e:
            if debug:
                raise
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        return
    
    # Input file is required for standard generation or watch mode
    if not input_file and not batch_dir:
        click.echo("Error: INPUT_FILE is required for PDF generation.", err=True)
        click.echo("Use --help for usage information.", err=True)
        sys.exit(1)
    
    # Determine output file
    if not output:
        input_path = Path(input_file)
        output = str(input_path.with_suffix('.pdf'))
    
    # Watch mode
    if watch:
        try:
            import time
            generator = PDFGenerator(template=template, config_path=config)
            input_path = Path(input_file)
            last_mtime = 0
            
            click.echo(f"Watching {input_file} for changes (Ctrl+C to stop)...")
            click.echo(f"Template: {template}")
            click.echo(f"Output: {output}")
            
            while True:
                try:
                    current_mtime = input_path.stat().st_mtime
                    if current_mtime != last_mtime:
                        if last_mtime != 0:
                            click.echo(f"\n[{time.strftime('%H:%M:%S')}] File changed, regenerating...")
                        else:
                            click.echo(f"[{time.strftime('%H:%M:%S')}] Initial generation...")
                        
                        try:
                            generator.generate(input_file, output, metadata=meta)
                            click.echo(f"[{time.strftime('%H:%M:%S')}] Generated: {output}")
                        except Exception as e:
                            click.echo(f"[{time.strftime('%H:%M:%S')}] Error: {e}", err=True)
                        
                        last_mtime = current_mtime
                    
                    time.sleep(1)
                except FileNotFoundError:
                    click.echo(f"Warning: File {input_file} not found, waiting...", err=True)
                    time.sleep(2)
                    
        except KeyboardInterrupt:
            click.echo("\nStopped watching.")
            return
        except Exception as e:
            if debug:
                raise
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        return
    
    # Standard PDF generation
    try:
        generator = PDFGenerator(template=template, config_path=config)
        
        click.echo(f"Generating PDF using template: {template}")
        click.echo(f"Input: {input_file}")
        click.echo(f"Output: {output}")
        
        result = generator.generate(input_file, output, metadata=meta)
        
        click.echo(f"Successfully generated: {result}")
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if debug:
            raise
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
