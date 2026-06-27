@echo off
title Ambilight

REM Go to the project directory
cd /d F:\uniled

REM Activate the virtual environment
call .\.venv\Scripts\activate.bat

REM Run the Python script
python ambw.py

REM Keep the window open if the script exits
pause