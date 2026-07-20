import re

def slugify(text: str) -> str:
    text = text.lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")