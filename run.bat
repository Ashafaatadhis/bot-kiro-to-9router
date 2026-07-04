@echo off
chcp 65001 >nul
echo ========================================
echo   KIRO REGISTRATION BOT - WINDOWS
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\python.exe" (
    echo Virtual environment detected.
    set PYTHON_PATH=venv\Scripts\python
) else (
    echo No virtual environment found.
    echo Using system Python...
    set PYTHON_PATH=python
)

REM Check arguments
if "%1"=="--headless" (
    echo Running in HEADLESS mode...
    echo.
    %PYTHON_PATH% main.py --headless
    goto :end
)

if "%1"=="--test" (
    echo Running tests...
    echo.
    %PYTHON_PATH% test_bot.py
    goto :end
)

if "%1"=="--setup" (
    echo Running setup...
    echo.
    %PYTHON_PATH% setup.py
    goto :end
)

if "%1"=="--help" (
    echo Usage: run.bat [OPTION]
    echo.
    echo Options:
    echo   --headless    Run bot in headless mode
    echo   --test        Run test suite
    echo   --setup       Run setup wizard
    echo   --help        Show this help
    echo.
    echo Without options: Run bot normally
    goto :end
)

echo Running bot normally...
echo.
%PYTHON_PATH% main.py

:end
echo.
echo ========================================
echo   Press any key to exit...
echo ========================================
pause >nul