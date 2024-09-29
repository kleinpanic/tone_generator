#!/usr/bin/env bash

# Function to check for required dependencies
check_dependencies() {
    echo "Checking for required dependencies..."

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Python3 is not installed. Please install it and try again."
        exit 1
    fi

    # Check if venv is installed
    if ! python3 -m venv --help &> /dev/null; then
        echo "Python venv is not installed. Please install it and try again."
        exit 1
    fi

    # Check if libportaudio2 is installed
    if ! dpkg -s libportaudio2 &> /dev/null; then
        echo "libportaudio2 is not installed. Installing it..."
        sudo apt-get install libportaudio2 -y
    fi

    echo "All dependencies are satisfied."
}

# Function to choose installation type
choose_install_type() {
    echo "Do you want to install the program locally or system-wide?"
    echo "0) Cancel"
    echo "1) Locally (current user)"
    echo "2) System-wide (requires sudo)"
    read -p "Choose an option [0/1/2]: " install_option

    # Check if the input is valid
    if [[ -z "$install_option" || ! "$install_option" =~ ^[012]$ ]]; then
        echo "Invalid option. Exiting."
        exit 1
    fi

    # If the user chooses to cancel
    if [ "$install_option" -eq 0 ]; then
        echo "Installation canceled."
        exit 0
    fi

    return $install_option
}

# Function for local installation
local_install() {
    echo "Starting local installation..."
    VENV_DIR="$DIR/../venv"
    SRC_FILE="$DIR/../main.py"

    # Check if the virtual environment exists, if not, create it
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi

    # Install the required packages
    echo "Installing dependencies..."
    "$VENV_DIR/bin/pip" install -r "$DIR/requirements.txt"

    # Make the wrapper script executable
    chmod +x "$DIR/tone_generator.sh"
    
    # Make the uninstall script executable
    chmod +x "$DIR/uninstall.sh"

    echo "Local install complete. Manually run the startup script using ./tone_generator.sh"
}

# Function for system-wide installation
system_wide_install() {
    echo "Starting system-wide installation..."
    VENV_DIR="/lib/python-venvs/tone-generator-env"
    SRC_DIR="/usr/local/share/tone-generator/src"
    DIR_NAMES=("gui" "cli" "audio" "waveform_visualizer")
    # Create a directory for system-wide Python virtual environments if it doesn't exist
    if [ ! -d "/lib/python-venvs" ]; then
        sudo mkdir -p /lib/python-venvs
        sudo chmod 755 /lib/python-venvs
    fi

    # Check if the virtual environment exists, if not, create it
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating system-wide virtual environment..."
        sudo python3 -m venv "$VENV_DIR"
    fi

    # Install the required packages
    echo "Installing dependencies system-wide..."

    sudo "$VENV_DIR/bin/pip" install -r "$DIR/requirements.txt"

    # Create the necessary directories and copy the source code
    sudo mkdir -p "$SRC_DIR"
    for dir in "${DIR_NAMES[@]}"; do 
        sudo mkdir -p "$SRC_DIR/$dir"
        echo "Created Dir: $SRC_DIR/$dir"
    done
    sudo cp -r "$DIR/../waveform_visualizer/"* "$SRC_DIR/waveform_visualizer/"
    sudo cp -r "$DIR/../cli/"* "$SRC_DIR/cli/"
    sudo cp -r "$DIR/../gui/"* "$SRC_DIR/gui/"
    sudo cp -r "$DIR/../audio/"* "$SRC_DIR/audio/"
    sudo cp "$DIR/../main.py" "$SRC_DIR/"

    # Create the tone_generator script with updated paths
    sudo cp "$DIR/tone_generator.sh" "/usr/local/bin/tone_generator"
    sudo chmod +x "/usr/local/bin/tone_generator"

    echo "Global install complete. Run 'tone_generator' from /usr/local/bin or in the shell."
}

# Main installation logic
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
check_dependencies
choose_install_type
install_option=$?

if [ "$install_option" -eq 1 ]; then
    local_install
elif [ "$install_option" -eq 2 ]; then
    system_wide_install
fi

