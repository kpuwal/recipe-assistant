import re

def extract_time_filter(message: str):
    msg = message.lower().strip()

    # Range: tussen 15 en 30, 15-30, 15 tot 30
    match = re.search(r"(?:tussen|van|)\s*(\d+)\s*(?:-|tot|en|tot)\s*(\d+)\s*(?:min|minuten)?", msg)
    if match:
        return {
            "type": "range",
            "min": int(match.group(1)),
            "max": int(match.group(2))
        }

    # Max time: onder 15, minder dan 20, max 25, tot 30
    match = re.search(r"(onder|minder dan|maximaal|max|tot|korter dan)\s*(\d+)\s*(min|minuten)?", msg)
    if match:
        return {"type": "max", "value": int(match.group(2))}

    # Min time: langer dan 30, meer dan 30, vanaf 45
    match = re.search(r"(langer dan|meer dan|vanaf|minimaal)\s*(\d+)\s*(min|minuten)?", msg)
    if match:
        return {"type": "min", "value": int(match.group(2))}

    # Exact: 20 min, 25 minuten
    match = re.search(r"(\d+)\s*(min|minuten|minute)", msg)
    if match:
        return {"type": "exact", "value": int(match.group(1))}

    # Quick keywords
    if any(word in msg for word in ["snel", "snelle", "snelle recepten", "kort"]):
        return {"type": "max", "value": 20}

    return None