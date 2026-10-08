import functools
import logging
from datetime import datetime


def log_action(action_type, verbose=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("valutatrade")
            log_data = {"timestamp": datetime.now().isoformat(), "action": action_type}
            try:
                result = func(*args, **kwargs)
                log_data["result"] = "OK"
                logger.info(str(log_data))
                return result
            except Exception as e:
                log_data["result"] = "ERROR"
                log_data["error_type"] = type(e).__name__
                log_data["error_message"] = str(e)
                logger.error(str(log_data))
                raise

        return wrapper

    return decorator
