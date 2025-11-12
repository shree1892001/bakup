from logger.custom_logger import CustomLogger
from logger.get_logger import get_logger
from config.config_reader import read_config, DatabaseType
from services.notification_service import NotificationService
from services.backup_service import BackupService


def _get_logger_instance():
    # Backward-compatible alias; aspects now use get_logger()
    return get_logger()


if __name__ == '__main__':
    logger = _get_logger_instance()
    configs, smtp_config = read_config('application.properties')

    notifier = NotificationService(smtp_config=smtp_config, logger_getter=_get_logger_instance)
    backup_service = BackupService(logger_getter=_get_logger_instance, notification_service=notifier)

    for db in configs:
        backup_service.backup_database(db)
