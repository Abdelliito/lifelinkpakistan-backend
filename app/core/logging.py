"""
Logging configuration for production and development environments.
Provides structured logging with proper formatting and handlers.
"""

import json
import logging
import logging.config
import sys
from datetime import datetime
from typing import Any

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id

        return json.dumps(log_obj)


def setup_logging() -> None:
    """Configure logging for the application."""
    is_prod = settings.ENVIRONMENT.lower() == "production"

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "json": {
                "()": JSONFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO" if is_prod else "DEBUG",
                "formatter": "json" if is_prod else "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "app": {
                "level": "INFO" if is_prod else "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO" if is_prod else "DEBUG",
            "handlers": ["console"],
        },
    }

    logging.config.dictConfig(log_config)
