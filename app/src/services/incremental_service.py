import os
import subprocess
import sys
import shutil
import time

# Add the project root (E:\pg_cron) to sys.path to allow 'from app.src...' imports
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SERVICE_DIR)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.src.centralized import config
from app.src.aop.logger import log_task

@log_task("Incremental WAL Backup")
def run_incremental_backup():
    src = config.WAL_ARCHIVE_SRC
    dest = config.WAL_ARCHIVE_DEST
    
    print(f"Source directory: {src}")
    print(f"Destination directory: {dest}")
    
    if not os.path.exists(src):
        print(f"Source directory {src} does not exist. Skipping.")
        return
    
    # List files in source
    files_in_src = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
    print(f"Files in source: {len(files_in_src)} - {files_in_src}")

    # Ensure dest exists
    os.makedirs(dest, exist_ok=True)

    # Attempt to sync WAL files
    try:
        if shutil.which("rsync"):
            print("Using rsync for synchronization...")
            subprocess.run(["rsync", "-av", src, dest], check=True)
        else:
            print("rsync not found. Falling back to native Python copy...")
            # Manual copy loop for robustness and cross-platform support
            copied_count = 0
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dest, item)
                if os.path.isfile(s):
                    shutil.copy2(s, d) # copy2 preserves metadata
                    copied_count += 1
            print(f"Successfully copied {copied_count} files using shutil.")
            
        print("WAL files synchronized successfully.")
        print("Incremental Backup Completed (source cleanup disabled).")
    except Exception as e:
        print(f"Error during synchronization: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    interval = int(os.getenv("INCREMENTAL_INTERVAL_SECONDS", "1800"))  # Default: 30 minutes
    print(f"Starting continuous incremental backup (interval: {interval}s)...")
    
    while True:
        try:
            run_incremental_backup()
        except Exception as e:
            print(f"Error in backup cycle: {e}", file=sys.stderr)
        
        time.sleep(interval)
