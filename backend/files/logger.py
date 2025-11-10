import logging
import os

class AppLogger:
    def __init__(self):
        self.version = "0.0.0"
        self.module_name = "AppLogger"

        # Project root (one level above this file's folder)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # logs/app.log path
        log_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "app.log")
        self.log_path = log_path  # <-- expose path for API

        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, msg: str): self.logger.info(msg)
    def warning(self, msg: str): self.logger.warning(msg)
    def error(self, msg: str): self.logger.error(msg)

    def module_info(self) -> dict:
        return {"module_name": self.module_name, "version": self.version}

logger = AppLogger()
