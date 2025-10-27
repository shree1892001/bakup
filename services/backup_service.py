import os
import subprocess
from datetime import datetime
import pytz
from typing import Callable, Any

from config.config_reader import DBConfig
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
	def backup_postgres_db(self, db: DBConfig, smtp_enabled: bool = True) -> None:
		os.makedirs(db.backup_path, exist_ok=True)
		backup_file = os.path.join(
			db.backup_path,
			f"backup_{db.database}_{datetime.now().strftime('%Y%m%d%H%M%S')}.dump"
		)

		backup_command = [
			'pg_dump',
			'-h', db.host,
			'-p', str(db.port),
			'-U', db.username,
			'-F', 'c', '-b', '-v',
			'-f', backup_file,
			db.database
		]

		env = os.environ.copy()
		env['PGPASSWORD'] = db.password

		result = subprocess.run(backup_command, env=env, capture_output=True, text=True)

		logger = get_logger()
		if result.returncode == 0:
			logger.info(
				f"Backup for {db.database} completed successfully at "
				f"{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')} IST"
			)
			# Send success email for visibility in Outlook inbox
			self._notification_service.send_success_email(
				subject=f"Backup Success: {db.database}",
				body=f"Backup for {db.database} completed successfully. File stored in {db.backup_path}."
			)
		else:
			msg = f"Backup failed for {db.database}: {result.stderr.strip()}"
			logger.error(msg)
			if smtp_enabled:
				self._notification_service.send_failure_email(
					subject=f"Backup Failed: {db.database}",
					body=msg
				)
			raise BackupError(message=msg)


