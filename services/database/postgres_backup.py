"""
PostgreSQL database backup implementation.
"""
import os
import subprocess
from pathlib import Path
from typing import Optional

from config.config_reader import DBConfig
from logger.get_logger import get_logger
from aop.log.logging_aspect import log_calls
from aop.exception.error_handling_aspect import handle_errors
from aop.exception.exceptions import BackupError

from .base import DatabaseBackup
from services.notification_service import NotificationService


class PostgresBackup(DatabaseBackup):
    """PostgreSQL database backup implementation."""
    
    def __init__(self, config: DBConfig, notification_service: Optional[NotificationService] = None):
        super().__init__(config)
        self.notification_service = notification_service
    
    def backup(self, smtp_enabled: bool = True) -> str:
        """
        Perform PostgreSQL database backup using pg_dump.
        
        Args:
            smtp_enabled: Whether to send email notifications
            
        Returns:
            str: Path to the backup file
            
        Raises:
            Exception: If the backup fails
        """
        backup_dir = self._ensure_backup_dir()
        backup_file = Path(backup_dir) / self._generate_backup_filename('.sql')
        
        # Build the pg_dump command
        cmd = [
            'pg_dump',
            '-h', self.config.host,
            '-p', str(self.config.port),
            '-U', self.config.username,
            '-d', self.config.database,
            '-f', str(backup_file)
        ]
        
        # Set PGPASSWORD as environment variable (more secure than command line)
        env = os.environ.copy()
        env['PGPASSWORD'] = self.config.password

        try:
            self.logger.info(f"Starting PostgreSQL backup of {self.config.database}")
            result = subprocess.run(
                cmd,
                env=env,
                check=True,
                capture_output=True,
                text=True
            )
            
            success_msg = f"PostgreSQL backup completed: {backup_file}"
            self.logger.info(success_msg)
            
            # Send success notification if smtp_enabled is True
            if hasattr(self, 'notification_service') and smtp_enabled:
                self.notification_service.send_success_email(
                    subject=f"Backup Success: {self.config.database} (PostgreSQL)",
                    body=f"Backup for {self.config.database} completed successfully.\n"
                         f"File: {backup_file}\n"
                         f"Size: {backup_file.stat().st_size / (1024 * 1024):.2f} MB",
                    databases=[f"{self.config.database} (PostgreSQL) - {self.config.host}:{self.config.port}"]
                )
                
            return str(backup_file)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"PostgreSQL backup failed for {self.config.database}: {e.stderr.strip()}"
            self.logger.error(error_msg)
            
            # Send failure notification if smtp_enabled is True
            if hasattr(self, 'notification_service') and smtp_enabled:
                self.notification_service.send_failure_email(
                    subject=f"Backup Failed: {self.config.database} (PostgreSQL)",
                    body=error_msg
                )
                
            raise BackupError(message=error_msg) from e
