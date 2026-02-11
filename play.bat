@echo off
echo Starting CertQuest...
python main.py
if errorlevel 1 (
    echo.
    echo Python not found. Please install Python 3.6 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
)
