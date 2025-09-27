"""
Centralized logging configuration for the checkout system.
"""

import logging
import logging.config
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """
    Configure centralized logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, logs only to console.
    """

    # Create logs directory if logging to file
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            # Application loggers
            "checkout": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "checkout.rest": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "checkout.service": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "checkout.repository": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Third-party loggers (reduced verbosity)
            "uvicorn": {"level": "INFO", "handlers": ["console"], "propagate": False,},
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {"level": log_level, "handlers": ["console"],},
    }

    # Add file handler if log_file is specified
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        }

        # Add file handler to all loggers
        for logger_name in config["loggers"]:
            config["loggers"][logger_name]["handlers"].append("file")
        config["root"]["handlers"].append("file")

    # Apply configuration
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Request ID context for tracing (simple implementation)
import contextvars

request_id_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context."""
    request_id_context.set(request_id)


def get_request_id() -> str:
    """Get the request ID for the current context."""
    return request_id_context.get("")


class RequestContextFilter(logging.Filter):
    """Filter to add request ID to log records."""

    def filter(self, record):
        record.request_id = get_request_id()
        return True
