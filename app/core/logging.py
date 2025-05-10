import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from app.config import settings

def setup_logging():
    log_level = logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10485760,
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)
    
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    
    return app_logger

logger = setup_logging()