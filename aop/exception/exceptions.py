from dataclasses import dataclass
from typing import Optional


@dataclass
class AppError(Exception):
	message: str
	status_code: int = 500
	detail: Optional[str] = None

	def __str__(self) -> str:
		return f"{self.message} (status={self.status_code})"


class ConfigError(AppError):
	def __init__(self, message: str, detail: Optional[str] = None) -> None:
		super().__init__(message=message, status_code=400, detail=detail)


class BackupError(AppError):
	def __init__(self, message: str, detail: Optional[str] = None) -> None:
		super().__init__(message=message, status_code=502, detail=detail)


class NotificationError(AppError):
	def __init__(self, message: str, detail: Optional[str] = None) -> None:
		super().__init__(message=message, status_code=500, detail=detail)


