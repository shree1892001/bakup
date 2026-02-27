#!/usr/bin/env python3
import os
import subprocess
import datetime
import sys

def run_backup():
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/backups/full/snahack_full_{date_str}.dump"
    
    print(f"Running Full Backup at {datetime.datetime.now().isoformat()}")
    
    # Environment variables for postgres connection
    env = os.environ.copy()
    env["PGPASSWORD"] = os.getenv("PGPASSWORD", "your_postgres_pass")
    
    command = [
        "pg_dump",
        "-h", os.getenv("DB_HOST", "host.docker.internal"),
        "-p", os.getenv("DB_PORT", "5432"),
        "-U", os.getenv("DB_USER", "postgres"),
        "-d", os.getenv("DB_NAME", "SnapHack"),
        "-F", "c",
        "-f", backup_file
    ]
    
    try:
        subprocess.run(command, env=env, check=True)
        print(f"Full Backup Completed: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_backup()
