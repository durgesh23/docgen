#!/bin/bash
# docgen.sh - Script to run docgen/main.py with the conda environment
# This script can be run from any directory

# Get the directory where this script is located, regardless of where it's called from
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Name of the conda environment
ENV_NAME="docgen"

# Path to the main Python script (relative to the script directory)
MAIN_SCRIPT="${SCRIPT_DIR}/docgen/main.py"

# Check if the main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo -e "${RED}Error: Main script not found at ${MAIN_SCRIPT}${NC}"
    exit 1
fi

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}Error: conda is not installed or not in PATH${NC}"
    exit 1
fi

# Setup conda activation
CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"

# Check if the environment exists
if ! conda env list | grep -q "^${ENV_NAME} "; then
    echo -e "${RED}Error: Conda environment '${ENV_NAME}' not found${NC}"
    echo -e "Available environments:"
    conda env list
    exit 1
fi

echo -e "${BLUE}Activating conda environment '${ENV_NAME}'...${NC}"
conda activate "${ENV_NAME}"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate environment '${ENV_NAME}'${NC}"
    exit 1
fi

echo -e "${GREEN}Running docgen/main.py with conda environment '${ENV_NAME}'${NC}"
echo -e "${YELLOW}Python path: $(which python)${NC}"

# Run the main script with all arguments passed to this script
python "$MAIN_SCRIPT" "$@"

# Capture the exit code of the Python script
EXIT_CODE=$?

# Exit with the same code as the Python script
exit $EXIT_CODE