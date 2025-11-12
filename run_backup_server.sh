#!/bin/bash

# Set the working directory
cd /path/to/your/backup/directory

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PATH="/usr/bin:/bin:/usr/local/bin:$PATH"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi

# Install/update dependencies
pip install -r requirements.txt

# Run the backup script with full path logging
python main.py >> backup_task.log 2>&1

# Deactivate virtual environment
deactivate 2>/dev/null || true
