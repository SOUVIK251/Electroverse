import logging
import os
import sys

def setup_logger() -> logging.Logger:
    """Sets up a dual-destination logger writing to console and to a local log file."""
    logger = logging.getLogger("ElectroVerse")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    log_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_file = os.path.join(log_dir, "electroverse.log")
    
    try:
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"Log file initialized at: {log_file}")
    except Exception as e:
        logger.warning(f"Failed to create file logger: {e}. Logging to console only.")

    return logger

# Global logger instance
log = setup_logger()
