# DocGen

Tool to create pdf/html/doc  documentation from markdown file

## Usage

Parse command line arguments.
valid arguments:
- ` -i | --input`: Path to input markdown file.
- ` -f | --format`: Specify the output format (e.g., HTML, pdf, docx).
- ` -o | --output`: Specify the output directory for the generated documentation.
- ` -d | --debug`: Enable verbose logging.
- ` -l | --language`: Specify the language for the documentation (default is English).
- ` -c | --config`: Path to a configuration file for doc details. If no arguments are provided, default values will be used.
- ` -h | --help`: Show help message and exit.

### Config file

Config File is YAML file

```yml

title:
author: (string or list)
revision:
metadata:



```



**TODO**
