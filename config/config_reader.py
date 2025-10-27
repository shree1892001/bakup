import configparser
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

from aop.log.logging_aspect import log_calls
from aop.exception.error_handling_aspect import handle_errors
from logger.get_logger import get_logger


@dataclass
class DBConfig:
    host: str
    port: int
    username: str
    password: str
    database: str
    backup_path: str
    retain_count: int = 5


@log_calls(lambda: get_logger())
@handle_errors(lambda: get_logger())
def read_config(config_path: str = "application.properties") -> Tuple[List[DBConfig], Dict[str, Any]]:
    config = configparser.ConfigParser()
    config.read(config_path)

    default_backup_path = config.get('BACKUP', 'default_backup_path', fallback='/backups')
    default_retain_count = config.getint('BACKUP', 'retain_count', fallback=5)

    # Update SMTP configuration
    smtp_config = {
        'host': config.get('NOTIFICATION', 'smtp_host', fallback='smtp.gmail.com'),
        'port': config.getint('NOTIFICATION', 'smtp_port', fallback=587),
        'username': config.get('NOTIFICATION', 'username', fallback=None),
        'app_password': config.get('NOTIFICATION', 'app_password', fallback=None),  # Changed from 'password'
        'from_email': config.get('NOTIFICATION', 'sender_email', fallback='shreyas.deodhare@redberyltech.com'),
        'recipients': [
            email.strip()
            for email in config.get(
                'NOTIFICATION',
                'recipient_emails',
                fallback='gaurav.more@redberyltech.com'
            ).split(',')
        ]  # Now supports multiple recipients
    }

    db_configs: List[DBConfig] = []
    for section in config.sections():
        if section.startswith("DATABASE"):
            db_backup_path = config.get('BACKUP', f"backup_path_{section.lower()}", fallback=default_backup_path)
            db_retain_count = config.getint('BACKUP', f"retain_count_{section.lower()}", fallback=default_retain_count)

            db_configs.append(DBConfig(
                host=config.get(section, 'host'),
                port=config.getint(section, 'port'),
                username=config.get(section, 'username'),
                password=config.get(section, 'password'),
                database=config.get(section, 'database'),
                backup_path=db_backup_path,
                retain_count=db_retain_count
            ))

    return db_configs, smtp_config
