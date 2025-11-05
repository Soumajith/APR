# files/logger.py
import logging
import os

class AppLogger:
    def __init__(self):
        self.version = "0.0.0"
        self.module_name = "AppLogger"

        # Project root: one level above this file
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Ensure logs directory inside project folder
        log_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Log file path
        log_path = os.path.join(log_dir, "app.log")

        self.logger = logging.getLogger("APR_Proj_Logger")
        self.logger.setLevel(logging.INFO)

        # Add handler if not present (prevents duplicate handlers)
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def module_info(self) -> dict:
        return {"module_name": self.module_name, "version": self.version}

# exported singleton
logger = AppLogger()
