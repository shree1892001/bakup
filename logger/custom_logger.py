import logging
from logging.handlers import RotatingFileHandler


class CustomLogger:
	def __init__(self, log_file: str) -> None:
		self.logger = logging.getLogger('backup_logger')
		self.logger.setLevel(logging.DEBUG)

		if not self.logger.handlers:
			handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
			handler.setLevel(logging.DEBUG)

			console_handler = logging.StreamHandler()
			console_handler.setLevel(logging.INFO)

			formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
			handler.setFormatter(formatter)
			console_handler.setFormatter(formatter)

			self.logger.addHandler(handler)
			self.logger.addHandler(console_handler)

	def debug(self, message: str) -> None:
		"""Log a debug message.
		
		Args:
		    message: The message to log
		"""
		self.logger.debug(message)

	def info(self, message: str) -> None:
		"""Log an info message.
		
		Args:
		    message: The message to log
		"""
		self.logger.info(message)

	def error(self, message: str) -> None:
		"""Log an error message.
		
		Args:
		    message: The message to log
		"""
		self.logger.error(message)


