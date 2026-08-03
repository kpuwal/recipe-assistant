import time
import functools
import logging
from typing import Callable, TypeVar, Tuple

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[type, ...] = (Exception,),
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        logger.error(
                            "%s failed after %d attempts: %s",
                            func.__name__,
                            max_attempts,
                            e,
                        )
                        raise
                    wait = initial_delay * (exponential_base ** attempt)
                    logger.warning(
                        "%s failed (attempt %d/%d). Retrying in %.1fs...",
                        func.__name__,
                        attempt + 1,
                        max_attempts,
                        wait,
                    )
                    time.sleep(wait)
            raise last_exception  # unreachable
        return wrapper
    return decorator
