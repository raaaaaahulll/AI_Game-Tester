"""
Structured logging configuration for the AI Game Testing System.

Provides JSON-formatted logs for production and human-readable logs for development.
"""
import logging
import sys
from pathlib import Path
from typing import Any
import json
from datetime import datetime

from config.settings import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable formatter for development."""
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging() -> None:
    """
    Configure application-wide logging.
    
    Sets up:
    - Console handler with appropriate formatter
    - File handler for logs directory
    - Log level from settings
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    if settings.LOG_FORMAT == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(TextFormatter())
    
    root_logger.addHandler(console_handler)
    
    # File handler (always JSON for production analysis)
    log_file = settings.LOGS_DIR / "app.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # Capture all levels to file
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Set levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("stable_baselines3").setLevel(logging.WARNING)
    logging.getLogger("gymnasium").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

