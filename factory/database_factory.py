
from typing import Dict, Type

from config.config_reader import DBConfig, DatabaseType
from services.database.base import DatabaseBackup


class DatabaseBackupFactory:
    """Factory for creating database backup services."""
    
    _backup_services: Dict[DatabaseType, Type[DatabaseBackup]] = {}
    
    @classmethod
    def register_backup_service(cls, db_type: DatabaseType, service_class: Type[DatabaseBackup]) -> None:
        """Register a backup service for a database type."""
        cls._backup_services[db_type] = service_class
    
    @classmethod
    def create_backup_service(cls, config: DBConfig, notification_service=None) -> DatabaseBackup:
        """
        Create a backup service for the given database configuration.
        
        Args:
            config: Database configuration
            notification_service: Optional notification service for sending email alerts
            
        Returns:
            An instance of the appropriate backup service
            
        Raises:
            ValueError: If no backup service is registered for the database type
        """
        service_class = cls._backup_services.get(config.db_type)
        if not service_class:
            raise ValueError(f"No backup service registered for database type: {config.db_type}")
            
        # Pass the notification service to the backup service if it accepts it
        if notification_service is not None:
            return service_class(config, notification_service=notification_service)
        return service_class(config)
