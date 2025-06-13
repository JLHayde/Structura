import logging
import os

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def get_logger(name="structura", log_file="structura.log", level=None):
    """
    Log configuration.
    """

    if level:
        # Set the log level globally
        log_level = level
        os.environ["LOG_LEVEL"] = log_level
    else:
        log_level = os.getenv("LOG_LEVEL", "info")

    level = LOG_LEVELS.get(log_level, logging.DEBUG)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Log to file
        file_handler = logging.FileHandler(os.path.join(os.getcwd(), log_file))
        file_handler.setLevel(level)
        file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s - %(name)s] %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Log to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    else:
        for handler in logger.handlers:
            handler.setLevel(level)

    return logger