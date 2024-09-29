#!/usr/bin/env bash

# Function to uninstall local installation
local_uninstall() {
    echo "Starting local uninstallation..."
    VENV_DIR="$DIR/../venv"
    BUILD_DIR="$DIR"

    # Remove the virtual environment
    if [ -d "$VENV_DIR" ]; then
        echo "Removing virtual environment..."
        rm -rf "$VENV_DIR"
    fi


    if [ -f "$BUILD_DIR/tone_generator.sh" ]; then
        echo "chmodding tone_generator.sh..."
        chmod -x "$BUILD_DIR/tone_generator.sh"
    fi

    # Optionally remove other directories like waveform_visualizer, CLI, gui, audio if needed
    echo "Local uninstallation complete."
}

# Function to uninstall system-wide installation
system_wide_uninstall() {
    echo "Starting system-wide uninstallation..."
    VENV_DIR="/lib/python-venvs/tone-generator-env"
    SRC_DIR="/usr/local/share/tone-generator/src"

    # Remove the virtual environment
    if [ -d "$VENV_DIR" ]; then
        echo "Removing system-wide virtual environment..."
        sudo rm -rf "$VENV_DIR"
    fi

    # Remove the directories under /usr/local/share/tone-generator/src
    if [ -d "$SRC_DIR" ]; then
        echo "Removing system-wide source directories..."
        sudo rm -rf "$SRC_DIR"
    fi

    # Remove the system-wide tone_generator script
    if [ -f "/usr/local/bin/tone_generator" ]; then
        echo "Removing system-wide tone_generator script..."
        sudo rm "/usr/local/bin/tone_generator"
    fi

    echo "System-wide uninstallation complete."
}

# Determine if the installation is local or system-wide
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$DIR/tone_generator.sh" ]; then
    # Local installation detected
    local_uninstall
fi
if [ -f "/usr/local/bin/tone_generator" ]; then
    # System-wide installation detected
    system_wide_uninstall
else
    echo "No installation detected. Nothing to uninstall."
    exit 1
fi

echo "Uninstallation process finished."

