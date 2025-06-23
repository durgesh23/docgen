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
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
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
    -o --output: Specify the output directory for the generated documentation.
    -d --debug: Enable verbose logging.
    -l --language: Specify the language for the documentation (default is English).
    -c --config: Path to a configuration file for doc details. If no arguments are provided, default values will be used.
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
        '-o', '--output',
        type=str,
        default='bin',
        help='Output doc name'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '-l', '--language',
        type=str,
        default='en',
        help='Language for the documentation (default: en)'
    )
    parser.add_argument(   
        '-c', '--config',
        type=str,
        default=None,
        help='Path to a configuration file for doc parameters (default: None, no config file used)'
    )
    # parser.add_argument(
    #     '-h', '--help',
    #     action='help',
    #     help='Show this help message and exit'
    # )

    args = parser.parse_args()
    # Validate output directory
    if not os.path.exists(args.output):
        try:
            os.makedirs(args.output)
            logger.info(f"Created output directory: {args.output}")
        except OSError as e:
            logger.error(f"Failed to create output directory: {e}")
            sys.exit(1)
    else:
        logger.info(f"Output directory already exists: {args.output}")
    # Validate format
    if args.format not in ['html', 'pdf', 'docx']:
        logger.error(f"Invalid format specified: {args.format}. Choose from 'html', 'pdf', or 'docx'.")
        sys.exit(1)
    # Validate language
    if args.language not in ['en', 'fr', 'es', 'de']:
        logger.error(f"Invalid language specified: {args.language}. Choose from 'en', 'fr', 'es', or 'de'.")
        sys.exit(1)
    # Validate config file
    if args.config and not os.path.isfile(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    # logging.debug(f"Parsed arguments: {args}")
    
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
    logger = setup_logger(args.debug and logging.DEBUG or logging.INFO,
                          log_file=Path(args.output) / 'docgen.log' if args.output else Path('.') / 'docgen.log')
    
    # Set logger level based on verbosity
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.info("Starting documentation generation process...")

    # Log the parsed arguments
    logger.debug(f"Arguments:")
    logger.debug(f"Input file: {args.input}")
    logger.debug(f"Output format: {args.format}")
    logger.debug(f"Output directory: {args.output}")
    logger.debug(f"Language: {args.language}")
    logger.debug(f"Configuration file: {args.config}")  
    logger.debug(f"cwd: {cwd}")
    
    # Create DocGen instance
    docgen = DocGen(
        input_file=args.input,
        out_file_name=args.output,
        output_format=args.format,
        output_dir=cwd,
        language=args.language,
        config_file=args.config
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