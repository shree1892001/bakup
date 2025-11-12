from abc import ABC, abstractmethod
from typing import Optional
import subprocess
import os
from datetime import datetime
import pytz

from config.config_reader import DBConfig, DatabaseType
from logger.get_logger import get_logger
from aop.log.logging_aspect import log_calls
from aop.exception.error_handling_aspect import handle_errors


class DatabaseBackup(ABC):
    """Abstract base class for database backup operations."""
    
    def __init__(self, config: DBConfig):
        self.config = config
        self.logger = get_logger()
    
    @abstractmethod
    def backup(self, smtp_enabled: bool = True) -> None:
        """Perform database backup."""
        pass


class PostgresBackup(DatabaseBackup):
    """PostgreSQL database backup implementation."""
    
    @log_calls(lambda self: get_logger())
    @handle_errors(lambda self: get_logger())
    def backup(self, smtp_enabled: bool = True) -> None:
        """Perform PostgreSQL database backup using pg_dump."""
        os.makedirs(self.config.backup_path, exist_ok=True)
        backup_file = os.path.join(
            self.config.backup_path,
            f"backup_{self.config.database}_{datetime.now().strftime('%Y%m%d%H%M%S')}.dump"
        )

        backup_command = [
            'pg_dump',
            '-h', self.config.host,
            '-p', str(self.config.port),
            '-U', self.config.username,
            '-F', 'c', '-b', '-v',
            '-f', backup_file,
            self.config.database
        ]

        env = os.environ.copy()
        env['PGPASSWORD'] = self.config.password

        result = subprocess.run(backup_command, env=env, capture_output=True, text=True)

        if result.returncode == 0:
            self.logger.info(
                f"PostgreSQL backup for {self.config.database} completed successfully at "
                f"{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')} IST"
            )
        else:
            msg = f"PostgreSQL backup failed for {self.config.database}: {result.stderr.strip()}"
            self.logger.error(msg)
            raise Exception(msg)


class MSSQLBackup(DatabaseBackup):
    """MSSQL database backup implementation."""
    
    @log_calls(lambda self: get_logger())
    @handle_errors(lambda self: get_logger())
    def backup(self, smtp_enabled: bool = True) -> None:
        """Perform MSSQL database backup using sqlcmd and bcp."""
        os.makedirs(self.config.backup_path, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_file = os.path.join(
            self.config.backup_path,
            f"backup_{self.config.database}_{timestamp}.bak"
        )

        # Build the connection string
        instance_part = f"\\{self.config.instance}" if self.config.instance else ""
        server = f"{self.config.host}{instance_part},{self.config.port}"
        
        # Create backup command
        backup_command = [
            'sqlcmd',
            '-S', server,
            '-U', self.config.username,
            '-P', self.config.password,
            '-Q', f"BACKUP DATABASE [{self.config.database}] TO DISK='{backup_file}' WITH INIT, COMPRESSION"
        ]

        # Execute the backup command
        result = subprocess.run(backup_command, capture_output=True, text=True)

        if result.returncode == 0:
            self.logger.info(
                f"MSSQL backup for {self.config.database} completed successfully at "
                f"{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')} IST"
            )
        else:
            msg = f"MSSQL backup failed for {self.config.database}: {result.stderr.strip() or result.stdout.strip()}"
            self.logger.error(msg)
            raise Exception(msg)


def create_backup_service(config: DBConfig) -> DatabaseBackup:
    """Factory function to create the appropriate backup service based on database type."""
    if config.db_type == DatabaseType.MSSQL:
        return MSSQLBackup(config)
    else:  # Default to PostgreSQL
        return PostgresBackup(config)
