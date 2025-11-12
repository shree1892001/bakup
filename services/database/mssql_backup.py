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
            BackupError: If the backup fails or backup file is not created
        """
        backup_dir = self._ensure_backup_dir()
        backup_file = Path(backup_dir) / self._generate_backup_filename('.bak')
        
        # Ensure the backup directory exists and is writable
        try:
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            # Test if directory is writable
            test_file = backup_file.parent / '.write_test'
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            error_msg = f"Cannot write to backup directory {backup_file.parent}: {str(e)}"
            self.logger.error(error_msg)
            raise BackupError(message=error_msg) from e
        
        # Build the connection string
        server = f"{self.config.host}\\{self.config.instance}" if hasattr(self.config, 'instance') and self.config.instance else self.config.host
        
        # Create backup command
        try:
            self.logger.info(f"Starting MSSQL backup of {self.config.database}")
            self.logger.debug(f"Backup file will be created at: {backup_file}")
            
            # Ensure the backup file doesn't exist already
            if backup_file.exists():
                self.logger.warning(f"Backup file {backup_file} already exists and will be overwritten")
                backup_file.unlink()
            
            backup_command = [
                'sqlcmd',
                '-S', server,
                '-U', self.config.username,
                '-P', self.config.password,
                '-Q', f"BACKUP DATABASE [{self.config.database}] TO DISK='{backup_file}' WITH INIT, STATS=10"
            ]
            
            # Log the command without the password for security
            safe_cmd = ' '.join(arg if arg != self.config.password else '*****' for arg in backup_command)
            self.logger.debug(f"Executing command: {safe_cmd}")
            
            result = subprocess.run(
                backup_command,
                check=True,
                capture_output=True,
                text=True,
                shell=True  # Required for Windows to handle paths with spaces
            )
            
            # Log the command output
            if result.stdout:
                self.logger.debug(f"Command output: {result.stdout}")
            
            # Verify backup file was created
            if not backup_file.exists():
                # Get SQL Server service account info
                service_account = 'NT SERVICE\MSSQLSERVER'  # Default for default instance
                if hasattr(self.config, 'instance') and self.config.instance:
                    service_account = f'NT SERVICE\MSSQL${self.config.instance.upper()}'
                
                # Check directory permissions
                perms_issue = (
                    f"The SQL Server service account ({service_account}) needs full control permissions on the directory: {backup_file.parent}"
                )
                
                error_msg = (
                    f"Backup command succeeded but backup file was not created at {backup_file}.\n"
                    f"Possible causes:\n"
                    f"1. SQL Server service account ({service_account}) lacks write permissions to the backup directory\n"
                    f"2. The backup path doesn't exist or is not accessible\n"
                    f"3. There's not enough disk space on the target drive\n\n"
                    f"To resolve this issue:\n"
                    f"1. Create the directory if it doesn't exist: {backup_file.parent}\n"
                    f"2. Grant full control permissions to {service_account} on the directory\n"
                    f"3. Verify there's enough disk space on the target drive\n\n"
                    f"Command output: {result.stdout or 'No output'}"
                )
                
                self.logger.error(perms_issue)
                self.logger.error(error_msg)
                if result.stderr:
                    self.logger.error(f"Command error output: {result.stderr}")
                    
                raise BackupError(message=f"{perms_issue}. {error_msg}")
            
            file_size_mb = backup_file.stat().st_size / (1024 * 1024)
            success_msg = f"MSSQL backup completed: {backup_file} ({file_size_mb:.2f} MB)"
            self.logger.info(success_msg)
            
            # Send success notification if smtp_enabled is True
            if hasattr(self, 'notification_service') and smtp_enabled:
                try:
                    self.notification_service.send_success_email(
                        subject=f"Backup Success: {self.config.database} (MSSQL)",
                        body=f"Backup for {self.config.database} completed successfully.\n"
                             f"File: {backup_file}\n"
                             f"Size: {file_size_mb:.2f} MB",
                        databases=[f"{self.config.database} (MSSQL) - {self.config.host}:{self.config.port}"]
                    )
                except Exception as email_error:
                    self.logger.error(f"Failed to send success email: {email_error}")
            
            return str(backup_file)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"MSSQL backup command failed for {self.config.database}"
            if e.stderr:
                error_msg += f": {e.stderr.strip()}"
            if e.stdout:
                self.logger.error(f"Command output: {e.stdout.strip()}")
            
            self.logger.error(error_msg, exc_info=True)
            
            # Check if backup file was partially created and clean up
            if backup_file.exists():
                try:
                    backup_file.unlink()
                    self.logger.info(f"Removed incomplete backup file: {backup_file}")
                except Exception as cleanup_error:
                    self.logger.error(f"Failed to remove incomplete backup file {backup_file}: {cleanup_error}")
            
            # Send failure notification if smtp_enabled is True
            if hasattr(self, 'notification_service') and smtp_enabled:
                try:
                    self.notification_service.send_failure_email(
                        subject=f"Backup Failed: {self.config.database} (MSSQL)",
                        body=error_msg + f"\n\nCommand: {safe_cmd}"
                    )
                except Exception as email_error:
                    self.logger.error(f"Failed to send failure email: {email_error}")
            
            raise BackupError(message=error_msg) from e
        else:
            msg = f"MSSQL backup failed for {self.config.database}: {result.stderr.strip() or result.stdout.strip()}"
            self.logger.error(msg)
            raise Exception(msg)
