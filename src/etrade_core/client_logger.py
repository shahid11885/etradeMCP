import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger('my_logger')
    # If handlers already exist, don't add them again to avoid duplication
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # Define project root and construct path to log file in the root 'logs' directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    log_file = os.path.join(project_root, 'logs', 'python_client.log')
    
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    FORMAT = "%(asctime)-15s %(message)s"
    fmt = logging.Formatter(FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger

logger = setup_logger()
