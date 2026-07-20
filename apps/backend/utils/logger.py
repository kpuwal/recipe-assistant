import logging
import sys
from functools import lru_cache
from pathlib import Path

from core.settings import settings

@lru_cache(maxsize=1)
def get_logger(name: str = "recipe_app") -> logging.Logger:
    logger = logging.getLogger(name)
    # logger.setLevel(logging.INFO)
    logger.setLevel(getattr(logging, settings.log_level))

    if logger.handlers:
        return logger

    # === Console Handler (always enabled) ===
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console.setFormatter(formatter)
    logger.addHandler(console)

    # === File Handler (optional, with safety) ===
    try:
        log_dir = settings.debug_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=5 * 1024 * 1024,   # 5 MB
            backupCount=3,
            encoding="utf-8",
            delay=True                  # Important: open file only when first log is written
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    except Exception:
        # Silently skip file logging if permissions fail
        pass

    return logger


# Global logger
logger = get_logger()