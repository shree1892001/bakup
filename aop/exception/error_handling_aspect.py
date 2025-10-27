from functools import wraps
from typing import Callable, Any

from .exceptions import AppError, BackupError


def handle_errors(logger_getter: Callable[[], Any]):
	"""AOP-style error handler that converts exceptions to AppError and logs.

	It re-raises AppError as-is; wraps generic exceptions into BackupError by default.
	"""
	def decorator(func: Callable):
		@wraps(func)
		def wrapper(*args, **kwargs):
			logger = logger_getter()
			try:
				return func(*args, **kwargs)
			except AppError:
				raise
			except Exception as exc:
				wrapped = BackupError(message=f"{func.__name__} failed", detail=str(exc))
				logger.error(str(wrapped))
				raise wrapped
		return wrapper
	return decorator


