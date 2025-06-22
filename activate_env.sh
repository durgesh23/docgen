#!/bin/bash
# activate_env.sh - Automatically activates a specified conda environment and runs optional commands

# Configuration - Change these variables as needed
ENV_NAME="docgen"  # Name of your conda environment
AUTO_COMMAND=""    # Optional command to run after activation, leave empty for just activation

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Display a header
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}Conda Environment Activation Script${NC}"
echo -e "${BLUE}=============================================${NC}"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo -e "${RED}Error: conda command not found.${NC}"
    echo -e "Please make sure Conda is installed and in your PATH."
    exit 1
fi

# Alternative environment name can be passed as first argument
if [ -n "$1" ]; then
    ENV_NAME="$1"
fi

echo -e "Attempting to activate environment: ${YELLOW}$ENV_NAME${NC}"

# Check if the environment exists
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo -e "${RED}Error: Environment '$ENV_NAME' does not exist.${NC}"
    echo -e "Available environments:"
    conda env list
    exit 1
fi

# This enables conda in script
eval "$(conda shell.bash hook)"

# Activate the environment
conda activate "$ENV_NAME"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate environment '$ENV_NAME'${NC}"
    exit 1
fi

echo -e "${GREEN}Successfully activated environment: ${YELLOW}$ENV_NAME${NC}"

# Check conda Python is being used
PYTHON_PATH=$(which python)
echo -e "Using Python: ${YELLOW}$PYTHON_PATH${NC}"

# Print environment info
echo -e "${BLUE}---------------------------------------------${NC}"
echo -e "${BLUE}Python version:${NC}"
python --version

# Execute additional command if specified
if [ -n "$AUTO_COMMAND" ]; then
    echo -e "${BLUE}---------------------------------------------${NC}"
    echo -e "${BLUE}Executing command: ${YELLOW}$AUTO_COMMAND${NC}"
    $AUTO_COMMAND
fi

echo -e "${BLUE}---------------------------------------------${NC}"
echo -e "${GREEN}Environment is ready!${NC}"

# Note: This script must be sourced to work properly (not executed directly)
# This warning is shown if the script was executed directly
echo -e "${YELLOW}IMPORTANT: This script should be sourced, not executed directly.${NC}"
echo -e "${YELLOW}Run with: ${GREEN}source activate_env.sh${NC}"

# If the script detects it's being sourced, the process will stay in the activated environment
# Otherwise, the environment activation will be lost when script exits

# Start an interactive shell if the script was executed directly (not sourced)
# This is a workaround to keep the environment activated
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo -e "${YELLOW}Starting a new shell with the activated environment...${NC}"
    exec $SHELL
fi
