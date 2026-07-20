import time

from utils.logger import logger


def retry(func, retries=3, delay=1):
    """Simple retry decorator with exponential backoff option."""
    last_error = None

    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            last_error = e

            if attempt < retries - 1:
                wait = delay * (2 ** attempt)  # simple backoff
                logger.warning("Attempt %d/%d failed for %s. Retrying in %d seconds...", 
                              attempt+1, retries, func.__name__, wait)
                time.sleep(wait)

    logger.error("All %d retries failed. Last error: %s", retries, last_error)
    raise last_error