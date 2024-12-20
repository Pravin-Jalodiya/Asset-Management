import logging
from logging.handlers import RotatingFileHandler
from threading import Lock
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from typing import Optional
from contextvars import ContextVar

# Context variables to store user info
user_id_context: ContextVar[Optional[str]] = ContextVar('user_id', default='unknown')
user_role_context: ContextVar[Optional[str]] = ContextVar('user_role', default='unknown')


class LoggerMiddleware(BaseHTTPMiddleware):
    def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # Get user info from request state (set by auth middleware)
        user = getattr(request.state, 'user', {})
        user_id = user.get('user_id', 'unknown')
        role = user.get('role', 'unknown')

        # Set context variables
        user_id_context.set(user_id)
        user_role_context.set(role)

        response = call_next(request)
        return response


class Logger:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(Logger, cls).__new__(cls)
                cls._instance._initialize_logger()
            return cls._instance

    def _initialize_logger(self):
        self.logger = logging.getLogger("ThreadSafeLogger")
        self.logger.setLevel(logging.DEBUG)

        file_handler = RotatingFileHandler("app.log", maxBytes=5 * 1024 * 1024, backupCount=3)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - [user_id=%(user_id)s role=%(role)s] - %(message)s"
        )
        file_handler.setFormatter(formatter)

        if not self.logger.handlers:  # Prevent duplicate handlers
            self.logger.addHandler(file_handler)

    def sanitize_body(self, body):
        if not isinstance(body, dict):
            return body

        redacted_body = body.copy()
        sensitive_keys = {"password", "token", "secret"}
        for key in sensitive_keys:
            if key in redacted_body:
                redacted_body[key] = "***"
        return redacted_body

    def _get_extra(self):
        """Get context info for logging"""
        return {
            'user_id': user_id_context.get(),
            'role': user_role_context.get()
        }

    def info(self, message: str):
        self.logger.info(message, extra=self._get_extra())

    def error(self, message: str):
        self.logger.error(message, extra=self._get_extra())

    def warning(self, message: str):
        self.logger.warning(message, extra=self._get_extra())

    def debug(self, message: str):
        self.logger.debug(message, extra=self._get_extra())