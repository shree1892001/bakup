import os
import configparser

# Default paths
# Find config file relative to this script: ../etc/config.properties
CENTRALIZED_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CENTRALIZED_DIR)
DEFAULT_CONFIG_FILE = os.path.join(SRC_DIR, "etc", "config.properties")

CONFIG_FILE = os.getenv("CONFIG_FILE", DEFAULT_CONFIG_FILE)

config = configparser.ConfigParser()
if os.path.exists(CONFIG_FILE):
    # Use a dummy section for standard properties format
    with open(CONFIG_FILE, 'r') as f:
        config_string = '[DEFAULT]\n' + f.read()
    config.read_string(config_string)

def get_config(key, default=None):
    # Try env var first (UPPERCASE_SNAKE_CASE)
    env_key = key.replace('.', '_').upper()
    val = os.getenv(env_key)
    if val:
        return val
    
    # Try config file
    try:
        return config.get('DEFAULT', key)
    except (configparser.NoOptionError, KeyError):
        return default

# Database Configuration
DB_HOST = get_config("db.host", "host.docker.internal")
DB_PORT = get_config("db.port", "5432")
DB_USER = get_config("db.user", "postgres")
DB_PASS = get_config("db.pass", "your_postgres_pass")
DB_NAME = get_config("db.name", "SnapHack")

# WAL Configuration
WAL_ARCHIVE_SRC = get_config("wal.archive_src", "/pg_wal_archive/")
WAL_ARCHIVE_DEST = get_config("wal.archive_dest", "/backups/incremental/")

# Backup Paths
FULL_BACKUP_PATH = get_config("full_backup_path", "/backups/full/")
INCREMENTAL_BACKUP_PATH = get_config("incremental_backup_path", "/backups/incremental/")
