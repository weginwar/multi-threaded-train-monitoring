import os
import json
import logging
from typing import Dict, Any

class LoggerUtility:
    _config: Dict[str, Any] = {}
    _initialized = False
    _current_invalid_log_file: str = "output_reports/invalid_records.log"

    DEFAULT_CONFIG = {
        "log_level": "INFO",
        "log_format": "%(asctime)s - [%(levelname)s] - [%(name)s] - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "invalid_records_log_file": "output_reports/invalid_records.log",
        "app_log_file": "output_reports/app.log"
    }

    @classmethod
    def load_config(cls, config_path: str = "config/logger_config.json") -> Dict[str, Any]:
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cls._config = json.load(f)
            except Exception:
                cls._config = cls.DEFAULT_CONFIG.copy()
        else:
            cls._config = cls.DEFAULT_CONFIG.copy()
        cls._initialized = True
        cls._current_invalid_log_file = cls._config.get("invalid_records_log_file", cls.DEFAULT_CONFIG["invalid_records_log_file"])
        return cls._config

    @classmethod
    def set_invalid_log_file(cls, filepath: str):
        if not cls._initialized:
            cls.load_config()
        cls._current_invalid_log_file = filepath
        cls._config["invalid_records_log_file"] = filepath

        logger = logging.getLogger("InvalidRecordsLogger")
        for handler in list(logger.handlers):
            handler.close()
            logger.removeHandler(handler)

        cls.get_logger("InvalidRecordsLogger", is_invalid_record_logger=True, target_file=filepath)

    @classmethod
    def get_invalid_log_file(cls) -> str:
        """Returns the active log file path set for the current test or run."""
        return cls._current_invalid_log_file

    @classmethod
    def get_logger(cls, name: str, is_invalid_record_logger: bool = False, target_file: str = None) -> logging.Logger:
        if not cls._initialized:
            cls.load_config()

        logger = logging.getLogger(name)
        if logger.handlers:
            return logger

        raw_level = cls._config.get("log_level", "INFO").upper()
        level = getattr(logging, raw_level, logging.INFO)
        logger.setLevel(level)
        logger.propagate = False

        fmt = cls._config.get("log_format", cls.DEFAULT_CONFIG["log_format"])
        date_fmt = cls._config.get("date_format", cls.DEFAULT_CONFIG["date_format"])
        formatter = logging.Formatter(fmt=fmt, datefmt=date_fmt)

        if is_invalid_record_logger:
            filepath = target_file or cls._current_invalid_log_file
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            handler = logging.FileHandler(filepath, mode="w", encoding="utf-8")
            handler.setLevel(logging.ERROR)
        else:
            filepath = target_file or cls._config.get("app_log_file", "output_reports/app.log")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            handler = logging.FileHandler(filepath, mode="a", encoding="utf-8")
            handler.setLevel(level)

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger