import logging
import os
from logging.handlers import RotatingFileHandler

from .infra.settings import SettingsLoader


def setup_logging():
    settings = SettingsLoader()
    os.makedirs(settings.LOGS_DIR, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = RotatingFileHandler(os.path.join(settings.LOGS_DIR, "actions.log"), maxBytes=1048576, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)

    logger = logging.getLogger("valutatrade")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
