import logging
import os
from logging.handlers import RotatingFileHandler
import functools
import datetime
import sys
import time

# Ensure log directory exists
LOG_DIR = "/app/src/log"
if not os.path.exists(LOG_DIR):
    LOG_DIR = os.path.join(os.getcwd(), "log") # Fallback for local testing
    os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logger = logging.getLogger("pg_cron_advanced")
logger.setLevel(logging.INFO)

# Console Handler
c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)

# File Handler
f_handler = RotatingFileHandler(os.path.join(LOG_DIR, "app.log"), maxBytes=10*1024*1024, backupCount=5)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)

def log_task(task_name):
    """
    Advanced AOP decorator for logging and performance tracking.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"STARTING: {task_name}")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                logger.info(f"SUCCESS: {task_name} | Duration: {duration:.2f}s")
                return result
            except Exception as e:
                logger.error(f"FAILURE: {task_name} | Error: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator

def retry(retries=3, delay=5):
    """
    Retry decorator for robust service calls.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Retry {i+1}/{retries} for {func.__name__} after error: {e}")
                    time.sleep(delay)
            logger.error(f"All {retries} retries failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator
