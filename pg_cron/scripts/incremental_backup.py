#!/usr/bin/env python3
import os
import subprocess
import datetime
import sys

def run_incremental_backup():
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Running Incremental Backup at {datetime.datetime.now().isoformat()}")
    
    src = os.getenv("WAL_ARCHIVE_SRC", "/pg_wal_archive/")
    dest = os.getenv("WAL_ARCHIVE_DEST", "/backups/incremental/")
    
    if not os.path.exists(src):
        print(f"Source directory {src} does not exist. Skipping.")
        return

    # Sync WAL files
    try:
        subprocess.run(["rsync", "-av", src, dest], check=True)
        print("WAL files synchronized successfully.")
        
        # Cleanup source directory
        # Using a list comprehension to delete files while keeping it readable and safe
        files = [os.path.join(src, f) for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
        for f in files:
            os.remove(f)
        
        print(f"Incremental Backup Completed and {len(files)} source files cleaned up.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during rsync: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during cleanup: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_incremental_backup()
