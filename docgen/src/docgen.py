import os
import sys
import logging
import pandoc
# Importing pandoc types for type annotations
from pandoc.types import *

# Configure logging
logger = logging.getLogger(__name__)


# DocGen: A simple documentation generator using Pandoc
class DocGen:
    def __init__(self, input_file, out_file_name, output_format, output_dir, language='en', config_file=None):
        self.input_file = input_file
        self.out_file_name = out_file_name
        self.output_format = output_format
        self.output_dir = output_dir
        self.language = language
        self.config_file = config_file

        # Validate input parameters
        if not os.path.isfile(self.input_file):
            logger.error(f"Input file does not exist: {self.input_file}")
            sys.exit(1)
        if self.output_format not in ['html', 'pdf', 'docx', 'markdown']:
            logger.error(f"Invalid output format specified: {self.output_format}. Choose from 'html', 'pdf', 'docx', or 'markdown'.")
            sys.exit(1)
        if not os.path.isdir(self.output_dir):
            try:
                os.makedirs(self.output_dir)
                logger.info(f"Created output directory: {self.output_dir}")
            except OSError as e:
                logger.error(f"Failed to create output directory: {e}")
                sys.exit(1)
        if self.language not in ['en', 'fr', 'es', 'de']:
            logger.error(f"Invalid language specified: {self.language}. Choose from 'en', 'fr', 'es', or 'de'.")
            sys.exit(1)
        logger.info(f"Initialized DocGen with input file: {self.input_file}, output format: {self.output_format}, output directory: {self.output_dir}, language: {self.language}, config file: {self.config_file}")

    def generate(self):
        """Generate documentation based on the provided parameters."""
        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
        
        # Use pandoc to convert the input file to the desired format
        output_file = os.path.join(self.output_dir, f"{self.out_file_name}.{self.output_format}")
        pandoc.convert_file(
              self.input_file
            , to=self.output_format
            , outputfile=output_file
            , extra_args=['--standalone', '--toc', '--toc-depth=2']
            )
        
        logger.info(f"Documentation generated at {output_file}")