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
# Note: This redirects *all* stdout/stderr, including from the log_message function itself.
exec > >(tee -a "${LOG_FILE}") 2>&1

log_message "INFO" "Starting Gemini CLI installation... Log file: ${LOG_FILE}"
echo "" # Add gap

# Step 2: Install Dependencies
log_message "INFO" "Installing dependencies from requirements.txt..."
if pip3 install -r requirements.txt; then
    log_message "INFO" "Dependencies installed successfully."
else
    log_message "ERROR" "Failed to install dependencies. Please check your pip3 installation and requirements.txt."
    exit 1
fi
echo "" # Add gap

# Step 3: Make the Script Executable
log_message "INFO" "Making the main script executable (src/cli.py)..."
if chmod +x src/cli.py; then
    log_message "INFO" "Script permissions updated successfully."
else
    log_message "ERROR" "Failed to update script permissions for src/cli.py."
    exit 1
fi
echo "" # Add gap

# Step 4: Create a Symbolic Link in ~/.local/bin
log_message "INFO" "Ensuring ~/.local/bin directory exists..."
mkdir -p ~/.local/bin
log_message "INFO" "Creating symbolic link 'gemini-cli' in ~/.local/bin pointing to $(pwd)/src/cli.py..."
# Remove existing link if it exists to avoid error
rm -f ~/.local/bin/gemini-cli
if ln -s "$(pwd)/src/cli.py" ~/.local/bin/gemini-cli; then
    log_message "INFO" "Symbolic link created successfully."
    log_message "INFO" "Ensure ~/.local/bin is in your PATH for the command to be accessible directly."
else
    log_message "ERROR" "Failed to create symbolic link."
    exit 1
fi
echo "" # Add gap

# Step 5: Create alias in .zshrc (Optional)
log_message "INFO" "Checking for existing 'gemini-cli' alias in ~/.zshrc..."
if ! grep -q 'alias gemini-cli=' ~/.zshrc; then
    log_message "INFO" "Adding alias 'gemini-cli' to ~/.zshrc..."
    echo '' >> ~/.zshrc # Add a blank line before the alias for readability
    echo '# Alias for Gemini CLI' >> ~/.zshrc
    echo 'alias gemini-cli="python3 ~/.local/bin/gemini-cli"' >> ~/.zshrc
    log_message "INFO" "Alias added to ~/.zshrc."
    # Source .zshrc to apply changes immediately for the current session
    log_message "INFO" "Sourcing ~/.zshrc to apply alias..."
    source ~/.zshrc
    log_message "INFO" ".zshrc sourced."
else
    log_message "INFO" "Alias 'gemini-cli' already exists in ~/.zshrc. Skipping."
fi
echo "" # Add gap

log_message "INFO" "Installation steps completed."
echo "" # Add gap
log_message "INFO" "Next steps:"
log_message "INFO" "1. Ensure ~/.local/bin is included in your shell's PATH environment variable."
log_message "INFO" "2. Set your GEMINI_API_KEY environment variable (e.g., in your ~/.zshrc)."
log_message "INFO" "   Example: export GEMINI_API_KEY='YOUR_API_KEY_HERE'"
log_message "INFO" "3. Restart your terminal or run 'source ~/.zshrc' for changes (like the alias) to take effect."