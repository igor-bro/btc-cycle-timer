# logger.py

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name="btc_cycle_timer", level=None):
    """
    Setup logger for the application
    
    Args:
        name (str): Logger name
        level: Logging level (default: INFO for production, DEBUG for development)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    if level is None:
        # Set level based on environment
        level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler for production
    if not os.getenv("DEBUG", "false").lower() == "true":
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler with daily rotation
        log_file = logs_dir / f"btc_cycle_timer_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name="btc_cycle_timer"):
    """
    Get logger instance
    
    Args:
        name (str): Logger name
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

# Create default logger
logger = setup_logger()

# Export functions
__all__ = ['setup_logger', 'get_logger', 'logger'] 