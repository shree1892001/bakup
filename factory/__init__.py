"""
Factory module for creating database backup services.
"""

from config.config_reader import DatabaseType
from .database_factory import DatabaseBackupFactory

# Import backup implementations from their respective modules
from services.database.postgres_backup import PostgresBackup
from services.database.mssql_backup import MSSQLBackup

# Register the backup services
DatabaseBackupFactory.register_backup_service(DatabaseType.POSTGRES, PostgresBackup)
DatabaseBackupFactory.register_backup_service(DatabaseType.MSSQL, MSSQLBackup)

# Alias for backward compatibility
create_backup_service = DatabaseBackupFactory.create_backup_service

__all__ = ['DatabaseBackupFactory', 'create_backup_service']
