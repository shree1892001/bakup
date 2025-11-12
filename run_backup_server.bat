@echo off
REM Enhanced backup script for server execution
REM Set the working directory
cd /d E:\bakup

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%
set PATH=C:\Python39;C:\Python39\Scripts;C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;%PATH%

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found at venv\Scripts\activate.bat
    echo Please ensure virtual environment is properly set up
)

REM Install/update dependencies
pip install -r requirements.txt

REM Test network connectivity
echo Testing network connectivity...
ping -n 1 smtp.gmail.com >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Cannot reach smtp.gmail.com - email notifications may fail
)

REM Run the backup script with enhanced logging
echo Starting backup process at %date% %time%
python main.py >> backup_task.log 2>&1
echo Backup process completed at %date% %time%

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat 2>nul
