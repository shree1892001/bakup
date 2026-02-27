import os
import subprocess
import sys

# Add the project root (E:\pg_cron) to sys.path to allow 'from app.src...' imports
# __file__ is .../app/src/services/backup_service.py
# parent 1: .../app/src/services
# parent 2: .../app/src
# parent 3: .../app
# parent 4: ... (E:\pg_cron)
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SERVICE_DIR)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.src.centralized import config
from app.src.aop.logger import log_task, retry

@retry(retries=3, delay=10)
@log_task("Full Database Backup")
def run_backup():
    # Use standard date command
    date_str = subprocess.check_output(['date', '+"%Y%m%d_%H%M%S"']).decode().strip() if os.name != 'nt' else \
               subprocess.check_output(['powershell', 'Get-Date -Format "yyyyMMdd_HHmmss"']).decode().strip()
    
    # Generate unique filename using database name and timestamp
    backup_filename = f"{config.DB_NAME}_{date_str}.dump"
    backup_file = os.path.join(config.FULL_BACKUP_PATH, backup_filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
    
    env = os.environ.copy()
    env["PGPASSWORD"] = config.DB_PASS
    
    command = [
        "pg_dump",
        "-h", config.DB_HOST,
        "-p", config.DB_PORT,
        "-U", config.DB_USER,
        "-d", config.DB_NAME,
        "-F", "c",
        "-f", backup_file
    ]
    
    subprocess.run(command, env=env, check=True)
    print(f"Full Backup Created Sucessfully: {backup_file}")

if __name__ == "__main__":
    try:
        run_backup()
    except Exception as e:
        sys.exit(1)
