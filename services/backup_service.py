"""
Backup service for managing database backups.
"""
from typing import Callable, Any, Optional

from config.config_reader import DBConfig, DatabaseType
from services.notification_service import NotificationService
from aop.log.logging_aspect import log_calls
from aop.exception.error_handling_aspect import handle_errors
from logger.get_logger import get_logger
from aop.exception.exceptions import BackupError


class BackupService:
    def __init__(self, logger_getter: Callable[[], Any], notification_service: NotificationService) -> None:
        self._logger_getter = logger_getter
        self._notification_service = notification_service

    @log_calls(lambda self=None: get_logger())
    @handle_errors(lambda self=None: get_logger())
    def backup_database(self, db: DBConfig, smtp_enabled: bool = True) -> None:
        """
        Backup a database using the appropriate backup service based on database type.
        
        Args:
            db: Database configuration
            smtp_enabled: Whether to send email notifications
        """
        logger = self._logger_getter()
        db_type = getattr(db, 'db_type', DatabaseType.POSTGRES)
        
        try:
            # Import the factory here to avoid circular imports
            from factory import create_backup_service
            
            # Create the appropriate backup service with notification service
            backup_service = create_backup_service(db, notification_service=self._notification_service)
            
            # Perform the backup (notifications will be handled by the backup service)
            backup_service.backup(smtp_enabled=smtp_enabled)
            
        except Exception as e:
            error_msg = str(e)
            msg = f"Backup failed for {db.database} ({db_type.name}): {error_msg}"
            # Log the full traceback using logger.exception if available
            if hasattr(logger, 'exception'):
                logger.exception(msg)
            else:
                logger.error(msg)
            
            if smtp_enabled:
                self._notification_service.send_failure_email(
                    subject=f"Backup Failed: {db.database} ({db_type.name})",
                    body=msg
                )
            raise BackupError(message=msg) from e
    
    # For backward compatibility
    def backup_postgres_db(self, db: DBConfig, smtp_enabled: bool = True) -> None:
        """Legacy method for backward compatibility."""
        self.backup_database(db, smtp_enabled)


