import subprocess
from log_config import get_logger

logger = get_logger(file_log=False)


def run_black():
    logger.info("Running Black...")
    try:
        subprocess.run(["black", "."], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Black failed: {e}")
        return False


def run_flake8():
    logger.info("Running Flake8...")
    try:
        subprocess.run(["flake8", "."], check=True)
        return True
    except subprocess.CalledProcessError:
        logger.warning("Flake8 would reformat the above.")
        return False


def run_linter():
    logger.info("Running Linter...")

    black_result = run_black()
    flake8_result = run_flake8()

    logger.info("Linter Results:")
    if not black_result:
        logger.error("black: Failed")

    if not flake8_result:
        logger.error("flake8: Failed")

    if black_result and flake8_result:
        logger.info("Passed")


if __name__ == "__main__":
    run_linter()
