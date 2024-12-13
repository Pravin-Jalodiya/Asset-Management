import logging
from logging.handlers import RotatingFileHandler
from threading import Lock


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
        self.logger.setLevel(logging.DEBUG)  # Set to the lowest level to capture all logs

        # Rotating File Handler (Thread-Safe)
        file_handler = RotatingFileHandler('app.log')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Adding Handler
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

    # Convenience methods for logging
    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def debug(self, message: str):
        self.logger.debug(message)