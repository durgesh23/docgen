import os
import sys
import logging
from ruamel.yaml import YAML
from pathlib import Path
import pypandoc
import traceback

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
    def validate(input_file: Path
            , output_format: str
            , output_dir: Path
        ):
        """Validate the input parameters for DocGen."""
        logger.info("Validating input parameters for DocGen...")

        logger.info("#"*50)
        # Validate input file
        DocGenValidator.validate_input_file(input_file)
        # Validate output format
        DocGenValidator.validate_output_format(output_format)
        # Validate output directory
        DocGenValidator.validate_output_directory(output_dir)
        logger.info("#"*50)
    
    @staticmethod
    def validate_pandoc_cfg_files(pandoc_metadata_file: Path
            , template_file: Path
        ):
        """Validate the Pandoc configuration files."""

        # Validate Pandoc metadata file
        DocGenValidator.validate_pandoc_metadata_file(pandoc_metadata_file)
        # Validate template file
        DocGenValidator.validate_template_file(template_file)

    @staticmethod
    def validate_input_file(input_file: Path):
        """Validate the input file path."""
        
        logger.info(f"Input file: ./{input_file}")
        if not os.path.isfile(input_file):
            logger.error(f"Input file does not exist: {input_file}")
            sys.exit(1)

    @staticmethod
    def validate_output_format(output_format: str):
        """Validate the output format."""

        logger.info(f"Output format: {output_format}")
        if output_format not in ['html', 'pdf', 'docx']:
            logger.error(f"Invalid output format specified: {output_format}. Choose from 'html', 'pdf', 'docx'.")
            sys.exit(1)
    
    @staticmethod
    def validate_output_directory(output_dir: Path):
        """Validate the output directory."""

        logger.info(f"Output directory: {output_dir}")
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")
            except OSError as e:
                logger.error(f"Failed to create output directory: {e}")
                sys.exit(1)
    
    @staticmethod
    def validate_metadata_file(metadata_file: Path):
        """Validate the metadata file."""

        logger.info(f"Document Metadata file: {metadata_file}")
        if metadata_file and not os.path.isfile(metadata_file):
            logger.error(f"Metadata file not found: {metadata_file}")
            sys.exit(1)

    @staticmethod
    def validate_pandoc_metadata_file(pandoc_metadata_file: Path):
        """Validate the Pandoc metadata file."""

        logger.debug(f"Pandoc metadata/config file: {pandoc_metadata_file}")
        if pandoc_metadata_file and not os.path.isfile(pandoc_metadata_file):
            logger.error(f"Pandoc metadata file not found: {pandoc_metadata_file}")
            sys.exit(1)
    
    @staticmethod
    def validate_template_file(template_file: Path):
        """Validate the template file."""

        logger.debug(f"Pandoc Template file:{template_file}")
        if template_file and not os.path.isfile(template_file):
            logger.error(f"Template file not found: {template_file}")
            sys.exit(1)

    @staticmethod
    def validate_markdown_file(markdown_file: Path):
        """Validate the Markdown file for basic syntax errors."""
        
        logger.debug(f"Validating Markdown file: {markdown_file}")
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
    parent_folder = Path(__file__).parents[1]
    # Pandoc configuration file
    DEF_PANDOC_CFG = parent_folder / 'configs' / 'docgen_config.yml'
    # Pandoc Default templates
    DEF_TEMPLATE_PDF  = parent_folder / 'templates' /'default.latex'
    DEF_TEMPALTE_HTML = parent_folder / 'templates' / 'default_html_template.html'
    DEF_TEMPLATE_DOCX = parent_folder / 'templates' / 'default_docx_template.yaml'

    def __init__(self
            , output_dir: Path
            , pandoc_cfg_file: Path
            , template_file: Path
        ):
        """Initialize the DocGenCore with input file and output format."""
        
        self.output_dir = Path(output_dir)
        self.pandoc_cfg_file = pandoc_cfg_file
        self.template_file = template_file
        self.is_custom_template = True if template_file else False

        # Set parameters
        if(self.pandoc_cfg_file is None):
            self.pandoc_cfg_file = DocGen.DEF_PANDOC_CFG
        
        # Validate Pandoc configuration files existence
        DocGenValidator.validate_pandoc_cfg_files(
            pandoc_metadata_file= self.pandoc_cfg_file,
            template_file= self.template_file
        )
        
        # TODO: Validate if the template file is compatible with the output format

        #Create a consolidated metadata file for pandoc      
        self.docgen_metadata_file = self.output_dir / 'logs' / 'docgen_metadata.yml'

    def convert(self
            , input_file: Path
            , output_format: str
            , output_file: Path=None
            , metadata: dict=None
        ):
        """Convert the input Markdown file to the specified output format using Pandoc."""
        logger.info(f"Converting {input_file} to {output_format} format...")

        # Generate pandoc conslidated metadata yml file
        self.dump_docgen_metadata_file(metadata)

        # Set Extra aruments
        extra_args = []
        extra_args = self.get_pandoc_extra_args()
        
        # Set intermediate format
        is_intermediate = False
        intermediate_format = self.output_format
        if(self.output_format == DocGenFormats.PDF):
            is_intermediate = True
            intermediate_format = 'latex'
        # TODO write this method
        # intermediate_format = self.get_intermediate_format(self.output_format)

        try:
            if(self.output_format == DocGenFormats.PDF):
                tex_file = self.output_dir / 'logs' / f"{input_file.stem}.tex"
                # Step1: Generate .tex file
                try:
                    pypandoc.convert_file(
                        input_file
                        , format=DocGenFormats.MARKDOWN
                        , to=intermediate_format
                        , outputfile=tex_file
                        , extra_args=extra_args
                    )
                except Exception as e:
                    logger.error(f"Failed to convert {input_file} to {intermediate_format}: {e}")
                    sys.exit(1)
                # Log the generated intermediate file
                logger.debug(f"Generated intermediate file: {tex_file}")
                
                # Step2: Convert .tex file to PDF
                try:
                    pypandoc.convert_file(
                        tex_file
                        , to=self.output_format
                        , outputfile=output_file
                        , extra_args=extra_args
                    )
                except Exception as e:
                    logger.error(f"Failed to convert {tex_file} to {self.output_format}: {e}")
                    sys.exit(1)
                logger.info(f"Generated output file: {output_file}")
            else:
                # Convert directly to the output format
                try:
                    pypandoc.convert_file(
                        input_file
                        , to=self.output_format
                        , outputfile=output_file
                        , extra_args=extra_args
                    )
                except Exception as e:
                    logger.error(f"Failed to convert {input_file} to {self.output_format}: {e}")
                    sys.exit(1)
                logger.info(f"Generated output file: {output_file}")
        except Exception as e:
            logger.error(f"An error occurred during conversion: {e}")
            sys.exit(1)

        logger.info(f"Conversion completed. Output file: {output_file}")

    def get_intermediate_format(self, output_format: str) -> str:
        """Get the intermediate format for Pandoc conversion."""
        # Pandoc supports various formats, but we will use Markdown as an intermediate format.
        # This is because Pandoc can convert from Markdown to any other format.
        if output_format  == DocGenFormats.PDF:
            return 'latex'
        elif output_format == DocGenFormats.HTML:
            return 'html'
        elif output_format == DocGenFormats.DOCX:
            return 'docx'
        else:
            logger.error(f"Unsupported output format: {output_format}")
            sys.exit(1)

    
    def get_pandoc_extra_args(self) -> list:
        """ Generate additional arguments for Pandoc conversion."""
        extra_args = []
        
        # Get Pandoc metadata-file
        extra_args.append(f"--metadata-file={self.docgen_metadata_file}")
        # Get Pandoc template file
        if self.is_custom_template:
            extra_args.append(f"--template={self.template_file}")
        else:
            # Use default template based on output format
            if self.template_file is None:
                if self.pandoc_cfg_file.suffix == '.pdf':
                    extra_args.append(f"--template={DocGenCore.DEF_TEMPLATE_PDF}")
                elif self.pandoc_cfg_file.suffix == '.html':
                    extra_args.append(f"--template={DocGenCore.DEF_TEMPALTE_HTML}")
                elif self.pandoc_cfg_file.suffix == '.docx':
                    extra_args.append(f"--template={DocGenCore.DEF_TEMPLATE_DOCX}")
        return extra_args

    def get_doc_args(self, metadata: dict=None)-> dict:
        """Get additional arguments for Pandoc conversion."""
        extra_args = []
       
        if(metadata.get('title')):
            extra_args.append(f"--variable=title:{metadata['title']}")
        if(metadata.get('author')):
            extra_args.append(f"--variable=author:{metadata['author']}")
        if(metadata.get('date')):
            extra_args.append(f"--variable=date:{metadata['date']}")

        logger.debug(f"Doc Args: {extra_args}")
        return extra_args
    
    def dump_docgen_metadata_file(self, doc_metadata: dict=None):
        """Generate a consolidated metadata file for Pandoc."""
        logger.info(f"Generating consolidated metadata file: {self.docgen_metadata_file}")
        
        # Get Document arguments for Pandoc conversion
        doc_args = doc_metadata
        # Get Pandoc metadata
        pandoc_args = self.get_pandoc_metadata()
        
        logger.debug(f"Document Args: {doc_args}")
        logger.debug(f"Pandoc Args: {pandoc_args}")

        # Combine both dicts
        consolidated_metadata = {**doc_args, **pandoc_args}
        # Dump the consolidated metadata to a YAML file
        DocGenCore.dump_yaml(consolidated_metadata, self.docgen_metadata_file)

    def get_pandoc_metadata(self):
        """Parse Pandoc metadata from a YAML file."""
        pandoc_metadata = {}
        logger.debug(f"Parsing Pandoc metadata from file: {self.pandoc_cfg_file}")
        try:
            pandoc_metadata = DocGenCore.parse_yaml(self.pandoc_cfg_file)
            return pandoc_metadata
        except Exception as e:
            logger.error(f"Failed to parse Pandoc metadata file: {e}")
            sys.exit(1)

    @staticmethod
    def parse_yaml(yaml_file):
        """Parse a YAML file and return its content."""
        try:
            yaml = YAML()
            with open(yaml_file, 'r') as file:
                data = yaml.load(file)
                logger.debug(f"Parsed YAML file: {yaml_file}")
                logger.debug(f"YAML content: {data}")
                return data
        except FileNotFoundError:
            logger.error(f"YAML file not found: {yaml_file}")
            sys.exit(1)
        except Exception as e:
            logger.error("Failed to parse YAML file: {yaml_file}")
            logger.error(f"Unexpected error parsing YAML file: {e}")
            logger.error(f"Exception Type: {type(e).__name__}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            sys.exit(1)

    @staticmethod
    def dump_yaml(data: dict, output_file: Path):
        """Dump data to a YAML file."""
        # Check if `output_file` is a valid Path object
        if not isinstance(output_file, Path):
            logger.error(f"Output file must be a Path object, got {type(output_file)}")
            sys.exit(1)
        # Ensure the output directory exists
        if not output_file.parent.exists():
            try:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created output directory: {output_file.parent}")
            except OSError as e:
                logger.error(f"Failed to create output directory: {e}")
                sys.exit(1)
        # Remove the file if it already exists
        if output_file.exists():
            try:
                output_file.unlink()
                logger.info(f"Removed existing file: {output_file}")
            except OSError as e:
                logger.error(f"Failed to remove existing file: {e}")
                logger.error(traceback)
                sys.exit(1)
        
        # Write the YAML content to the file
        try:
            yaml = YAML()
            yaml.indent(mapping=2, sequence=4, offset=2)
            yaml.preserve_quotes = True  # Preserve quotes in the output

            with open(output_file, 'w') as file:
                yaml.dump(data, file)
                logger.debug(f"YAML content written to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write YAML file: {e}")
            sys.exit(1)




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
            , pandoc_config_file={self.pandoc_config_file}\
            , template={self.template_file})"

    def __init__(self
            , input_file: Path
            , output_format: str
            , output_dir: Path
            , metadata_file: Path=None
            , pandoc_config_file: Path=None
            , template_file: Path=None
        ):
        self.input_file = Path(input_file)
        self.output_format = output_format
        self.output_dir = Path(output_dir)
        self.metadata_file = Path(metadata_file) if metadata_file else None
        # self.pandoc_config_file = Path(pandoc_config_file) if pandoc_config_file else None
        # self.template_file = Path(template_file) if template_file else None

        # Initialize the DocGenCore with Pandoc configuration and template
        super().__init__(output_dir = self.output_dir
            , pandoc_cfg_file=Path(pandoc_config_file) if pandoc_config_file else None
            , template_file=Path(template_file) if template_file else None
        )

        # Validate Pandoc configuration files
        DocGenValidator.validate(input_file = self.input_file
            , output_format = self.output_format
            , output_dir= self.output_dir
        )
        # Validate metadata file if provided
        if self.metadata_file:
            DocGenValidator.validate_metadata_file(self.metadata_file)


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

        # Convert
        self.convert(self.input_file
            , self.output_format
            , output_file=self.output_dir / f"{self.input_file.stem}.{self.output_format}"
            , metadata=metadata
        )

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
        try:
            metadata = self.parse_yaml(self.metadata_file)
            return metadata
        except Exception as e:
            logger.error(f"Failed to parse metadata file: {e}")
            sys.exit(1)
