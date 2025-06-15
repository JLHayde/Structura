import logging
import os
import sys
import traceback

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def get_logger(
    level=None,
    file_log=True,
    console_log=True,
):
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

    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Place log in app root if we are frozen, otherwise use temp dir
    log_file = "structura.log"
    if not hasattr(sys, "_MEIPASS"):
        log_file =  os.path.join("tmp", log_file)
    log_file_path = os.path.join(os.getcwd(), log_file)

    if log_level == "debug":
        file_formatter_str = (
            "[%(asctime)s] [%(levelname)s - %(module)s:%(funcName)s] %(message)s"
        )
        console_formatter_str = "[%(levelname)s - %(module)s:%(funcName)s] %(message)s"
    else:
        file_formatter_str = "[%(asctime)s] [%(levelname)s - %(module)s] %(message)s"
        console_formatter_str = "[%(levelname)s - %(module)s] %(message)s"

    # Avoid adding handlers multiple times
    if not logger.handlers:

        # Log to console
        if console_log:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_formatter = logging.Formatter(console_formatter_str)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # Log to file, attempt to add file handler for aws, discord
        if file_log:
            try:
                os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
                file_handler = logging.FileHandler(
                    os.path.join(os.getcwd(), log_file_path)
                )
                file_handler.setLevel(level)
                file_formatter = logging.Formatter(file_formatter_str)

                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except Exception:
                logger.exception("Could not setup logging file handlder for file {} skipping.".format(log_file_path))

    else:
        for handler in logger.handlers:
            handler.setLevel(level)
            formatter = None

            # Dynamically remove handlers when called.
            if isinstance(handler, logging.StreamHandler):
                formatter = logging.Formatter(console_formatter_str)
                if not console_log:
                    logger.removeHandler(handler)
                    handler.close()
            elif isinstance(handler, logging.FileHandler):
                formatter = logging.Formatter(file_formatter_str)
                if not file_log:
                    logger.removeHandler(handler)
                    handler.close()

            if formatter:
                handler.setFormatter(formatter)

    return logger
