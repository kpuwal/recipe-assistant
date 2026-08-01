import logging
import sys
from functools import lru_cache

from core.settings import settings


@lru_cache(maxsize=1)
def get_logger(name: str = "recipe_app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    if logger.handlers:
        return logger

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger

# Global application logger
logger = get_logger()