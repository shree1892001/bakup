@echo off
cd /d E:\bakup
call .\venv\Scripts\activate.bat
python main.py >> E:\bakup\backup_task.log 2>&1