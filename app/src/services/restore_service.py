import os
import subprocess
import sys
import glob
import shutil

# Add the project root (E:\pg_cron) to sys.path to allow 'from app.src...' imports
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SERVICE_DIR)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.src.centralized import config
from app.src.aop.logger import log_task, retry

@retry(retries=3, delay=15)
@log_task("Database Restoration")
def run_restore(target_time=None, restore_db_name=None):
    """Restore database from full backup + incremental WAL files
    
    Args:
        target_time: Optional timestamp for point-in-time recovery (format: 'YYYY-MM-DD HH:MM:SS')
        restore_db_name: Name for restored database (default: original_name + '_restored')
    """
    # Find latest full backup
    backup_files = glob.glob(os.path.join(config.FULL_BACKUP_PATH, "*.dump"))
    if not backup_files:
        print(f"No full backup found in {config.FULL_BACKUP_PATH}")
        sys.exit(1)
    
    latest_backup = max(backup_files, key=os.path.getmtime)
    print(f"Using full backup: {latest_backup}")
    
    env = os.environ.copy()
    env["PGPASSWORD"] = config.DB_PASS
    
    # Determine restore database name
    if not restore_db_name:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        restore_db_name = f"{config.DB_NAME}_restored_{timestamp}"
    
    print(f"Restoring to new database: {restore_db_name}")
    
    # Create new database
    print("Creating new database...")
    subprocess.run([
        "psql", "-h", config.DB_HOST, "-p", config.DB_PORT, "-U", config.DB_USER,
        "-d", "postgres", "-c", f"CREATE DATABASE {restore_db_name};"
    ], env=env, check=True)
    
    # Restore full backup
    print("Restoring full backup...")
    subprocess.run([
        "pg_restore", "-h", config.DB_HOST, "-p", config.DB_PORT,
        "-U", config.DB_USER, "-d", restore_db_name, "-v", latest_backup
    ], env=env, check=True)
    
    # Step 3: Apply incremental WAL files
    wal_files = sorted(glob.glob(os.path.join(config.INCREMENTAL_BACKUP_PATH, "*")))
    if wal_files:
        print(f"Found {len(wal_files)} WAL files to apply")
        
        # Create recovery directory
        data_dir = f"C:\\Program Files\\PostgreSQL\\14\\data"
        pg_wal_dir = os.path.join(data_dir, "pg_wal")
        
        # Copy WAL files to pg_wal for recovery
        for wal_file in wal_files:
            dest = os.path.join(pg_wal_dir, os.path.basename(wal_file))
            shutil.copy2(wal_file, dest)
            print(f"Copied {os.path.basename(wal_file)}")
        
        # Create recovery signal file for PostgreSQL 12+
        recovery_signal = os.path.join(data_dir, "recovery.signal")
        with open(recovery_signal, 'w') as f:
            f.write("")
        
        # Create recovery configuration
        if target_time:
            recovery_conf = f"recovery_target_time = '{target_time}'\n"
        else:
            recovery_conf = "recovery_target = 'immediate'\n"
        
        # Append to postgresql.auto.conf
        auto_conf = os.path.join(data_dir, "postgresql.auto.conf")
        with open(auto_conf, 'a') as f:
            f.write(recovery_conf)
        
        print("WAL files prepared. Restart PostgreSQL to apply incremental changes.")
        print("Run: net stop postgresql-x64-14 && net start postgresql-x64-14")
    else:
        print("No incremental WAL files found. Restore complete with full backup only.")
    
    print("Restoration Completed Successfully")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Restore database from full + incremental backups')
    parser.add_argument('--target-time', help='Point-in-time recovery target (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--db-name', help='Name for restored database (default: original_restored)')
    args = parser.parse_args()
    
    try:
        run_restore(target_time=args.target_time, restore_db_name=args.db_name)
    except Exception as e:
        print(f"Restore failed: {e}", file=sys.stderr)
        sys.exit(1)
