#!/bin/bash

# Exit on error
set -e

echo "=== HR Data Pipeline Setup ==="

# 1. Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found. Please install Python 3."
    exit 1
fi

echo "Using Python: $(which python3)"
python3 --version

# 2. Create Virtual Environment
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in ./$VENV_DIR..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists."
fi

# 3. Activate and Install
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

echo "=== Setup Complete ==="
echo "To run the project, use:"
echo "  source venv/bin/activate"
echo "  python main.py"
