import os
import sys
import logging
import yaml
from pathlib import Path
import pandoc
# Importing pandoc types for type annotations
from pandoc.types import *

# Configure logging
logger = logging.getLogger(__name__)


class DocGenFormats:
    """A class to hold the supported output formats for DocGen."""

    # Output Formats
    # These formats are supported by Pandoc and can be used for documentation generation.
    # HTML, PDF, and DOCX are the most common formats for documentation.
    HTML = 'html'
    PDF  = 'pdf'
    DOCX = 'docx'
    
    # Input Formats
    # Markdown is the supported as an input format.
    MARKDOWN = 'markdown'
    RST      = 'rst'  # reStructuredText is another common format, but not implemented here.

    @classmethod
    def get_supported_output_formats(cls):
        """Return a list of supported output formats."""
        output_formats = [cls.HTML, cls.PDF, cls.DOCX]
        logger.info(f"Supported output formats: {output_formats}")
        return output_formats

    @classmethod
    def get_supported_input_formats(cls):
        """Return a list of supported input formats."""
        # TODO: Add support for reStructuredText (RST) if needed.
        # Currently, only Markdown is supported as an input format.
        # This can be extended in the future to support other formats like RST.
        input_formats = [cls.MARKDOWN]
        logger.info(f"Supported input formats: {input_formats}")
        return input_formats

class DocGenValidator:
    """A simple validator for DocGen parameters."""

    def __init__(self):
        """Initialize the DocGenValidator."""
        pass


    @staticmethod
    def validate(input_file, output_format, output_dir, metadata_file=None, pandoc_metadata_file=None, template_file=None):
        """Validate the input parameters for DocGen."""
        logger.info("Validating input parameters for DocGen...")

        # Validate input file
        DocGenValidator.validate_input_file(input_file)
        # Validate output format
        DocGenValidator.validate_output_format(output_format)
        # Validate output directory
        DocGenValidator.validate_output_directory(output_dir)
    
    @staticmethod
    def validate_pandoc_files(metadata_file, pandoc_metadata_file, template_file):
        """Validate the Pandoc configuration files."""

        # Validate metadata file
        DocGenValidator.validate_metadata_file(metadata_file)
        # Validate Pandoc metadata file
        DocGenValidator.validate_pandoc_metadata_file(pandoc_metadata_file)
        # Validate template file
        DocGenValidator.validate_template_file(template_file)

    @staticmethod
    def validate_input_file(input_file):
        """Validate the input file path."""
        
        logger.info(f"Input file: {input_file}")
        if not os.path.isfile(input_file):
            logger.error(f"Input file does not exist: {input_file}")
            sys.exit(1)

    @staticmethod
    def validate_output_format(output_format):
        """Validate the output format."""

        logger.info(f"Output format: {output_format}")
        if output_format not in ['html', 'pdf', 'docx']:
            logger.error(f"Invalid output format specified: {output_format}. Choose from 'html', 'pdf', 'docx'.")
            sys.exit(1)
    
    @staticmethod
    def validate_output_directory(output_dir):
        """Validate the output directory."""

        logger.info(f"Output directory: {output_dir.str()}")
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")
            except OSError as e:
                logger.error(f"Failed to create output directory: {e}")
                sys.exit(1)
    
    @staticmethod
    def validate_metadata_file(metadata_file):
        """Validate the metadata file."""

        logger.info(f"Document Metadata file: {metadata_file}")
        if metadata_file and not os.path.isfile(metadata_file):
            logger.error(f"Metadata file not found: {metadata_file}")
            sys.exit(1)

    @staticmethod
    def validate_pandoc_metadata_file(pandoc_metadata_file):
        """Validate the Pandoc metadata file."""

        logger.info(f"Pandoc metadata/config file: {pandoc_metadata_file}")
        if pandoc_metadata_file and not os.path.isfile(pandoc_metadata_file):
            logger.error(f"Pandoc metadata file not found: {pandoc_metadata_file}")
            sys.exit(1)
    
    @staticmethod
    def validate_template_file(template_file):
        """Validate the template file."""

        logger.info(f"Template file: {template_file}")
        if template_file and not os.path.isfile(template_file):
            logger.error(f"Template file not found: {template_file}")
            sys.exit(1)

    @staticmethod
    def validate_markdown_file(markdown_file):
        """Validate the Markdown file for basic syntax errors."""
        
        logger.info(f"Validating Markdown file: {markdown_file}")
        try:
            with open(markdown_file, 'r') as file:
                content = file.read()
                # Simple validation: check for empty file or basic structure
                if not content.strip():
                    logger.error(f"Markdown file is empty: {markdown_file}")
                    sys.exit(1)
                if not content.startswith('#'):
                    logger.warning(f"Markdown file does not start with a header: {markdown_file}")
        except Exception as e:
            logger.error(f"Failed to read Markdown file: {e}")
            sys.exit(1)


class DocGenCore:
    """    A core class for generating documentation using Pandoc.

    This class serves as the base class for the DocGen. It interfaces with Pandoc to convert Markdown files
    to various formats such as HTML, PDF, and DOCX.

    This class provides methods to convert Markdown files to various formats (HTML, PDF, DOCX) using Pandoc.
    
    Attributes:
        pandoc_cfg (str): Path to the Pandoc configuration file (YAML).
        template (str): Path to the Pandoc template file (YAML) for custom generation.
        xargs (dict): A dictionary to hold additional parameters for Pandoc conversion.

    Methods:
        - generate():
            Generate documentation based on the provided parameters.
                   
    Returns:
        bool : Status of documentation generation.
    """
    
    # Global class attributes
    parent_folder = Path(__file__).parent
    # Pandoc configuration file
    DEF_PANDOC_CFG = parent_folder / 'configs' / 'docgen_config.yaml'
    # Pandoc Default templates
    DEF_TEMPLATE_PDF  = parent_folder / 'templates' /'default_pdf.tex'
    DEF_TEMPALTE_HTML = parent_folder / 'templates' / 'default_html_template.html'
    DEF_TEMPLATE_DOCX = parent_folder / 'templates' / 'default_docx_template.yaml'

    def __init__(self, output_format, metadata_file, pandoc_cfg, template):
        """Initialize the DocGenCore with input file and output format."""
        
        self.output_format = output_format
        self.metadata_file = metadata_file
        self.pandoc_cfg = pandoc_cfg
        self.template = template
        self.is_custom_temaplte = False
        # Set parameters
        if self.pandoc_cfg is None:
            self.pandoc_cfg = DocGen.DEF_PANDOC_CFG
        if self.template is None:
            if self.output_format == DocGenFormats.PDF:
                self.template = self.DEF_TEMPLATE_PDF
            elif self.output_format == DocGenFormats.HTML:
                self.template = self.DEF_TEMPALTE_HTML
            elif self.output_format == DocGenFormats.DOCX:
                self.template = self.DEF_TEMPLATE_DOCX
            else:
                logger.error(f"Unsupported output format: {self.output_format}")
                sys.exit(1)
        else:
            self.is_custom_template = True
        
        # Validate Pandoc configuration files existence
        DocGenValidator.validate_pandoc_files(
            metadata_file= self.metadata_file,  # Metadata file is optional
            pandoc_metadata_file=self.pandoc_cfg,
            template_file=self.template
        )
        
        # TODO: Validate if the template file is compatible with the output format

    
    def  generate(self):
        """Generate documentation based on the provided parameters."""
        raise NotImplementedError("This method should be implemented in subclasses.")


# DocGen: A simple documentation generator using Pandoc
class DocGen (DocGenCore):
    """    A simple documentation generator that converts Markdown files to various formats using Pandoc.

    Attributes:
        input_file (str): Path to the input Markdown file.
        out_file_name (str): Name of the output file.
        output_format (str): Format of the output file (e.g., 'html', 'pdf', 'docx', 'markdown').
        output_dir (str): Directory where the output file will be saved.
        language (str): Language for the documentation (default is 'en').
        metadata_file (str): Path to a metadata file (YAML) for doc metadata.
        pandoc_metadata_file (str): Path to a Pandoc metadata file (YAML) for full custom generation.
        template (str): Path to a Pandoc template file (YAML) for custom generation.
    """

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"DocGen(input_file={self.input_file} \
            , out_file_name={self.out_file_name}\
            , output_format={self.output_format}\
            , output_dir={self.output_dir}\
            , metadata_file={self.metadata_file}\
            , pandoc_metadata_file={self.pandoc_metadata_file}\
            , template={self.template})"

    def __init__(self, input_file, output_format, output_dir, metadata_file=None, pandoc_metadata_file=None, template=None):
        self.input_file = input_file
        self.output_format = output_format
        self.output_dir = output_dir
        self.metadata_file = metadata_file
        self.pandoc_metadata_file = pandoc_metadata_file
        self.template = template

        # Validate Pandoc configuration files
        DocGenValidator.validate(input_file = self.input_file
            , output_format = self.output_format
            , output_dir= self.output_dir
            , metadata_file = self.metadata_file
            # pandoc_metadata_file = self.pandoc_metadata_file,
            # template_file = self.template
        )

        # Initialize the DocGenCore with Pandoc configuration and template
        super().__init__(output_format=self.output_format
            , metadata_file=self.metadata_file
            , pandoc_cfg= self.pandoc_metadata_file
            , template=self.template
        )

        logger.info(f"Initialized DocGen with input file: {self.input_file}, output format: {self.output_format}, output directory: {self.output_dir}, language: {self.language}, config file: {self.config_file}")

    def generate(self):
        """Generate documentation based on the provided parameters."""
        
        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
        
        self.validate_markdown_file(self.input_file)

        # Parse metadata if provided               
        metadata = self.get_metadata()
        pandoc_metadata = self.get_pandoc_metadata()
    
        if(self.output_format == 'pdf'):
            self.convert_md_to_pdf(metadata, pandoc_metadata)
        elif(self.output_format == 'docx'):
            self.convert_md_to_docx(metadata, pandoc_metadata)
        elif(self.output_format == 'html'):
            self.convert_md_to_html(metadata, pandoc_metadata)
        else:
            logger.error(f"Unsupported output format: {self.output_format}")
            sys.exit(1)



    def convert_md_to_pdf(self):
        """Convert Markdown file to PDF using Pandoc."""

        # Get default configuration for Pandoc
        config_file = self.default_config_file if self.
        # Get pdf tempalate
        template = self.DEF_TEMPLATE_PDF if self.template is None else self.template
        if not os.path.isfile(template):
            logger.error(f"Template file not found: {template}")
            sys.exit(1)
        ...

    def convert_md_to_docx(self):
        """Convert Markdown file to DOCX using Pandoc."""
        ...
    
    def convert_md_to_html(self):
        """Convert Markdown file to HTML using Pandoc."""
        ...
    

    def validate_markdown_file(self, markdown_file):
        """Validate the Markdown file for basic syntax errors."""
        try:
            with open(markdown_file, 'r') as file:
                content = file.read()
                # Simple validation: check for empty file or basic structure
                if not content.strip():
                    logger.error(f"Markdown file is empty: {markdown_file}")
                    sys.exit(1)
                if not content.startswith('#'):
                    logger.warning(f"Markdown file does not start with a header: {markdown_file}")
        except Exception as e:
            logger.error(f"Failed to read Markdown file: {e}")
            sys.exit(1)

    def get_metadata(self):
        """Parse metadata from a YAML file."""
        metadata = {}
        if self.metadata_file is None:
            return metadata
        try:
            metadata = self.parse_yaml(self.metadata_file)
            return metadata
        except Exception as e:
            logger.error(f"Failed to parse metadata file: {e}")
            sys.exit(1)

    def parse_pandoc_metadata(self):
        """Parse Pandoc metadata from a YAML file."""
        pandoc_metadata = {}
        if self.pandoc_metadata_file is None:
            return pandoc_metadata
        try:
            pandoc_metadata = self.parse_yaml(self.pandoc_metadata_file)
            return pandoc_metadata
        except Exception as e:
            logger.error(f"Failed to parse Pandoc metadata file: {e}")
            sys.exit(1)

    def parse_yaml(self, yaml_file):
        """Parse a YAML file and return its content."""
        try:
            with open(yaml_file, 'r') as file:
                data = yaml.safe_load(file)
                logger.info(f"Parsed YAML file: {yaml_file}")
                return data
        except Exception as e:
            logger.error(f"Failed to parse YAML file: {e}")
            sys.exit(1)