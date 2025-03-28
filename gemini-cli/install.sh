#!/bin/bash

# install.sh
# Installation script for Gemini CLI

LOG_FILE="installation.log"

# --- Color Codes ---
COLOR_RESET='\033[0m'
COLOR_INFO='\033[0;32m'  # Green
COLOR_ERROR='\033[0;31m' # Red

# --- Logging Function ---
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""

    case "${level}" in
        INFO) color="${COLOR_INFO}" ;;
        ERROR) color="${COLOR_ERROR}" ;;
        *) color="${COLOR_RESET}" ;;
    esac

    # Print colored level and reset, then the message
    echo -e "${timestamp} [${color}${level}${COLOR_RESET}] - ${message}"
}

# Redirect stdout and stderr to log file and console
exec > >(tee -a "${LOG_FILE}") 2>&1

log_message "INFO" "Starting Gemini CLI installation... Log file: ${LOG_FILE}"
echo "" # Add gap


# Install using pip
log_message "INFO" "Installing gemini-cli package using pip3..."
if pip3 install . ; then
    log_message "INFO" "Gemini CLI installed successfully."
else
    log_message "ERROR" "Failed to install Gemini CLI using pip3. Check the logs for details."
    exit 1
fi
echo "" # Add gap

log_message "INFO" "Installation completed."

# --- Check if gemini-cli command is available ---
log_message "INFO" "Checking if gemini-cli is available in PATH..."

if command -v gemini-cli >/dev/null 2>&1; then
  log_message "INFO" "gemini-cli is available. You can now use the 'gemini-cli' command."
else
  log_message "ERROR" "gemini-cli is not available in your PATH. Please ensure that your Python user base binary directory (~/.local/bin by default) is added to your PATH environment variable and try again."
  exit 1
fi
