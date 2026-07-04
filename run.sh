#!/bin/bash

echo "========================================"
echo "   KIRO REGISTRATION BOT - LINUX/MAC"
echo "========================================"
echo

# Check if virtual environment exists
if [ -f "venv/bin/python" ]; then
    echo "Virtual environment detected."
    PYTHON_PATH="venv/bin/python"
else
    echo "No virtual environment found."
    echo "Using system Python..."
    PYTHON_PATH="python3"
fi

# Check arguments
if [ "$1" = "--headless" ]; then
    echo "Running in HEADLESS mode..."
    echo
    $PYTHON_PATH main.py --headless
    exit 0
fi

if [ "$1" = "--test" ]; then
    echo "Running tests..."
    echo
    $PYTHON_PATH test_bot.py
    exit 0
fi

if [ "$1" = "--setup" ]; then
    echo "Running setup..."
    echo
    $PYTHON_PATH setup.py
    exit 0
fi

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: ./run.sh [OPTION]"
    echo
    echo "Options:"
    echo "  --headless    Run bot in headless mode"
    echo "  --test        Run test suite"
    echo "  --setup       Run setup wizard"
    echo "  --help, -h    Show this help"
    echo
    echo "Without options: Run bot normally"
    exit 0
fi

echo "Running bot normally..."
echo
$PYTHON_PATH main.py