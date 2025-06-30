import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

from app.core.config import settings

def setup_logging() -> logging.Logger:
    """Configure logging for the application"""
    
    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Ensure log directory exists
    log_dir = Path(settings.BASE_PATH) / "config"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup file handler with rotation
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup audit log handler
    audit_handler = RotatingFileHandler(
        settings.AUDIT_LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    audit_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Setup audit logger
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)
    
    # Create and return application logger
    logger = root_logger.getChild('app')
    logger.info('Logging system initialized')
    
    return logger 