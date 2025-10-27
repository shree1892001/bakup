from functools import wraps
from typing import Callable, Any


def log_calls(logger_getter: Callable[[], Any]):
	"""AOP-style decorator to log function entry/exit and errors.

	logger_getter: a zero-arg callable that returns a logger with .info/.error
	"""
	def decorator(func: Callable):
		@wraps(func)
		def wrapper(*args, **kwargs):
			logger = logger_getter()
			logger.info(f"Entering {func.__name__}")
			try:
				result = func(*args, **kwargs)
				logger.info(f"Exiting {func.__name__}")
				return result
			except Exception as exc:  # pragma: no cover - passthrough to error aspect
				logger.error(f"Error in {func.__name__}: {exc}")
				raise
		return wrapper
	return decorator


