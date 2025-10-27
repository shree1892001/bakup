from .custom_logger import CustomLogger


_LOGGER_SINGLETON = None


def get_logger() -> CustomLogger:
	global _LOGGER_SINGLETON
	if _LOGGER_SINGLETON is None:
		_LOGGER_SINGLETON = CustomLogger('backup.log')
	return _LOGGER_SINGLETON


