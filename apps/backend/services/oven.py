import re
from typing import Optional, Tuple

FAN_MODE = "fan"
CONVENTIONAL_MODE = "conventional"

MIN_TEMPERATURE = 50
MAX_TEMPERATURE = 300

_RANGE_RE = re.compile(
    r"(?<![\d.,])(\d{2,3})\s*(?:-|–|—|tot)\s*(\d{2,3})\s*"
    r"(?:graden(?:\s+celsius)?|°\s*c|℃)",
    re.IGNORECASE,
)
_SINGLE_RE = re.compile(
    r"(?<![\d.,])(\d{2,3})\s*(?:graden(?:\s+celsius)?|°\s*c|℃)",
    re.IGNORECASE,
)
_OVEN_RE = re.compile(
    r"\boven\b|voorverwarm|hetelucht|boven[\s\-/]*(?:en[\s\-]*)?onder|"
    r"bovenwarmte|onderwarmte",
    re.IGNORECASE,
)
_NON_OVEN_RE = re.compile(
    r"\bwater\b|kamertemperatuur|frituur|friteuse|\bolie\b|\bsuiker\b|"
    r"vriezer|koelkast|magnetron",
    re.IGNORECASE,
)
_FAN_RE = re.compile(r"\bhetelucht|\bhete\s+lucht", re.IGNORECASE)
_CONVENTIONAL_RE = re.compile(
    r"boven[\s\-/]*(?:en[\s\-]*)?onder|bovenwarmte|onderwarmte",
    re.IGNORECASE,
)


def _detect_mode(text: str) -> Optional[str]:
    if _FAN_RE.search(text):
        return FAN_MODE
    if _CONVENTIONAL_RE.search(text):
        return CONVENTIONAL_MODE
    return None


def _line_temperature(line: str) -> Optional[int]:
    match = _RANGE_RE.search(line)
    if match:
        return int(match.group(1))

    match = _SINGLE_RE.search(line)
    if match:
        return int(match.group(1))

    return None


def extract_oven_settings(text: str) -> Tuple[Optional[int], Optional[str]]:
    """Extract the (lower) oven temperature and mode from recipe text."""
    if not text:
        return None, None

    normalized = text.replace("℃", "°C")
    candidates = []

    for line in normalized.splitlines():
        temperature = _line_temperature(line)
        if temperature is None:
            continue
        if not MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE:
            continue
        if _NON_OVEN_RE.search(line) and not _OVEN_RE.search(line):
            continue
        candidates.append((temperature, line))

    if not candidates:
        return None, None

    temperature, line = next(
        (candidate for candidate in candidates if _OVEN_RE.search(candidate[1])),
        candidates[0],
    )
    mode = _detect_mode(line) or _detect_mode(normalized)

    return temperature, mode
