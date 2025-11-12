"""
MSSQL database backup implementation.
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


class MSSQLBackup(DatabaseBackup):
    """MSSQL database backup implementation."""
    
    def __init__(self, config: DBConfig, notification_service: Optional[NotificationService] = None):
        super().__init__(config)
        self.notification_service = notification_service
    
    def backup(self, smtp_enabled: bool = True) -> str:
        """
        Perform MSSQL database backup using sqlcmd.
        
        Args:
            smtp_enabled: Whether to send email notifications
            
        Returns:
            str: Path to the backup file
            
        Raises:
            Exception: If the backup fails
        """
        backup_dir = self._ensure_backup_dir()
        backup_file = Path(backup_dir) / self._generate_backup_filename('.bak')
        
        # Build the connection string
        server = f"{self.config.host}\\{self.config.instance}" if hasattr(self.config, 'instance') and self.config.instance else self.config.host
        
        # Create backup command
        try:
            self.logger.info(f"Starting MSSQL backup of {self.config.database}")
            
            backup_command = [
                'sqlcmd',
                '-S', server,
                '-U', self.config.username,
                '-P', self.config.password,
                '-Q', f"BACKUP DATABASE [{self.config.database}] TO DISK='{backup_file}' WITH INIT, COMPRESSION"
            ]
            
            result = subprocess.run(
                backup_command,
                check=True,
                capture_output=True,
                text=True,
                shell=True  # Required for Windows to handle paths with spaces
            )
            
            success_msg = f"MSSQL backup completed: {backup_file}"
            self.logger.info(success_msg)
            
            # Send success notification if smtp_enabled is True
            if hasattr(self, 'notification_service') and smtp_enabled:
                self.notification_service.send_success_email(
                    subject=f"Backup Success: {self.config.database} (MSSQL)",
                    body=f"Backup for {self.config.database} completed successfully.\n"
                         f"File: {backup_file}\n"
                         f"Size: {backup_file.stat().st_size / (1024 * 1024):.2f} MB",
                    databases=[f"{self.config.database} (MSSQL) - {self.config.host}:{self.config.port}"]
                )
                
            return str(backup_file)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"MSSQL backup failed for {self.config.database}: {e.stderr.strip()}"
            self.logger.error(error_msg)
            
            # Send failure notification if smtp_enabled is True
            if hasattr(self, 'notification_service') and smtp_enabled:
                self.notification_service.send_failure_email(
                    subject=f"Backup Failed: {self.config.database} (MSSQL)",
                    body=error_msg
                )
                
            raise BackupError(message=error_msg) from e

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
