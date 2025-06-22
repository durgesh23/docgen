import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# docgen/main.py

def setup_logger(log_level=logging.INFO, log_file=None):
    """Configure and return logger."""

    # Create a logger
    logger = logging.getLogger('docgen')
    logger.setLevel(log_level)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

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
    -v --verbose: Enable verbose logging.
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
        default='docs',
        help='Output doc name'
    )
    parser.add_argument(
        '-v', '--verbose',
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
            logging.info(f"Created output directory: {args.output}")
        except OSError as e:
            logging.error(f"Failed to create output directory: {e}")
            sys.exit(1)
    else:
        logging.info(f"Output directory already exists: {args.output}")
    # Validate format
    if args.format not in ['html', 'pdf', 'docx']:
        logging.error(f"Invalid format specified: {args.format}. Choose from 'html', 'pdf', or 'docx'.")
        sys.exit(1)
    # Validate language
    if args.language not in ['en', 'fr', 'es', 'de']:
        logging.error(f"Invalid language specified: {args.language}. Choose from 'en', 'fr', 'es', or 'de'.")
        sys.exit(1)
    # Validate config file
    if args.config and not os.path.isfile(args.config):
        logging.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    logging.debug(f"Parsed arguments: {args}")
    
    return parser


def main(args=None):
    """
    Main function to run the documentation generation process.
    """
    # Parse command line arguments
    parser = parse_arguments()
    print("Parsing command line arguments...")
    print(parser)
    try:
        args = parser.parse_args(args)
    except argparse.ArgumentError as e:
        parser.print_help()
        sys.exit(2)
    
    # Setup logger
    logger = setup_logger(args.verbose and logging.DEBUG or logging.INFO,
                          log_file=os.path.join(args.output, 'docgen.log'))
    
    # Set logger level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.info("Starting documentation generation process...")


    



if __name__ == "__main__":
    main()