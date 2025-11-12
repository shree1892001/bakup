from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Optional

from config.config_reader import DBConfig
from logger.get_logger import get_logger


class DatabaseBackup(ABC):
    """Abstract base class for database backup implementations."""
    
    def __init__(self, config: DBConfig):
        self.config = config
        self.logger = get_logger()
    
    @abstractmethod
    def backup(self, smtp_enabled: bool = True) -> str:
        """Perform the database backup."""
        pass
    
    def _ensure_backup_dir(self) -> str:
        """Ensure backup directory exists and return its path."""
        backup_path = Path(self.config.backup_path)
        backup_path.mkdir(parents=True, exist_ok=True)
        return str(backup_path)
    
    def _generate_backup_filename(self, extension: str = '.backup') -> str:
        """Generate a timestamped backup filename."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{self.config.database}_{timestamp}{extension}"
