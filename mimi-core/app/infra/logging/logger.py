"""
JSON logging configuration.
"""
import logging
import logging.config
import sys
from typing import Dict, Any


def setup_logger(app_env: str = "development") -> None:
    """Setup JSON logging to stdout."""
    
    log_level = "DEBUG" if app_env == "development" else "INFO"
    
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "default": {
                "level": log_level,
                "formatter": "json" if app_env == "production" else "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["default"]
        },
        "loggers": {
            "mimi": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"mimi.{name}")