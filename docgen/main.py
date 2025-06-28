import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

from src.docgen import DocGen

logger = logging.getLogger("DocGenMain")

# docgen/main.py

def setup_logger(log_level=logging.INFO, log_file=None):
    """Configure and return logger."""
    # Create a logger
    global logger
    # logger = logging.getLogger("DocGenMain")
    logger.setLevel(log_level)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(name)s  %(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Remove any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add handler to logger
    logger.addHandler(ch)

    # Add file handler if log_file is specified
    if log_file:
        #Ensure the directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
                logging.info(f"Created log directory: {log_dir}")
            except OSError as e:
                logging.error(f"Failed to create log directory: {e}")
                sys.exit(1)
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger

def parse_arguments():
    """
    Parse command line arguments.
    valid arguments:
    -i --input: Path to input markdown file.
    -f --format: Specify the output format (e.g., HTML, pdf, docx).
    -m --metadata-file: Path to a metadata file (YAML) for doc details. If no arguments are provided, default values will be used.
    -d --debug: Enable verbose logging.
    
    ## Advanced Usage
    -o --output: Specify the output directory for the generated documentation.
    -p --pandoc-config-file: Path to a Pandoc metadata file (YAML) for full custom generation.
    -t --template: Path to a Pandoc template file (YAML) for custom generation.
    
    -h --help: Show help message and exit.
    """

    parser = argparse.ArgumentParser(description="Generate Doc project.")
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Path to the input markdown file'
    )
    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=['html', 'pdf', 'docx'],
        default='pdf',
        required=True,
        help='Output format for the documentation (default: pdf)'
    )
    parser.add_argument(   
        '-m', '--metadata-file',
        type=str,
        default=None,
        help='Path to a metadata file (YAML) for doc metadata.'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable verbose logging'
    )
    
    # Advanced Usage
    parser.add_argument(
        '-o', '--output',
        type=str,
        default= Path(os.getcwd()),
        help='Output directory for generated document (default: cwd)'
    )
    parser.add_argument(
        '-p', '--pandoc-config-file',
        type=str,
        default=None,
        help='Path to a Pandoc metadata file (YAML) for full custom generation.'
    )
    parser.add_argument(
        '-t', '--template-file',
        type=str,
        default=None,
        help='Path to a Pandoc template file (YAML) for custom generation.'
    )

    # parser.add_argument(
    #     '-h', '--help',
    #     action='help',
    #     help='Show this help message and exit'
    # )

    # args = parser.parse_args()    
    return parser


def main(args=None):
    """
    Main function to run the documentation generation process.
    """
    # Get the directory from which the script is being run
    cwd = os.getcwd()
    
    # Parse command line arguments
    parser = parse_arguments()
    print("Parsing command line arguments...")
    
    try:
        args = parser.parse_args(args)
    except argparse.ArgumentError as e:
        parser.print_help()
        sys.exit(2)
    

    # Setup logger
    logger = setup_logger(args.debug and logging.DEBUG or logging.INFO
                , DE3log_file= args.output / 'logs' / 'docgen.log')
    
    logger.info("Starting documentation generation process...")

    # Create DocGen instance
    docgen = DocGen(input_file=args.input
        , out_file_name=args.output
        , output_format=args.format
        , output_dir=cwd
        , language=args.language
        , metadata_file=args.metadata_file
        , pandoc_metadata_file=args.pandoc_metadata_file
        , template=args.template
    )
    
    docgen.generate()



if __name__ == "__main__":
    # Check if -d is passed as an argument
    if('-d' in sys.argv or '--debug' in sys.argv):
        import debugpy
        debugpy.listen(("localhost", 5678))
        print("Waiting for debugger to attach...")
        debugpy.wait_for_client()

    if("PYTHONBREAKPOINT" not in os.environ):
        breakpoint()
    main()