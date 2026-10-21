import io
import os
import tempfile
from pathlib import Path
from typing import Optional

from PIL import Image

from utils.logger import logger

THUMB_CACHE_DIR = Path(os.environ.get("THUMB_CACHE_DIR", "/tmp/recipe_thumbs"))

MIN_WIDTH = 16
MAX_WIDTH = 1600

INGEST_MAX_DIMENSION = 1200
INGEST_JPEG_QUALITY = 82

MAX_UPLOAD_BYTES = 10 * 1024 * 1024

MEDIA_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}

UPLOAD_EXTENSIONS = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
}


def validate_image_upload(data: bytes) -> Optional[str]:
    """Return a safe extension for an uploaded image, or None if invalid."""
    if not data or len(data) > MAX_UPLOAD_BYTES:
        return None

    try:
        image = Image.open(io.BytesIO(data))
        image_format = image.format
        image.verify()
    except Exception as e:
        logger.warning("Rejected image upload: %s", e)
        return None

    return UPLOAD_EXTENSIONS.get(image_format)


def media_type_for(filename: str) -> str:
    extension = Path(filename).suffix.lower().lstrip(".")
    return MEDIA_TYPES.get(extension, "application/octet-stream")


def downscale_image(
    data: bytes,
    max_dimension: int = INGEST_MAX_DIMENSION,
    quality: int = INGEST_JPEG_QUALITY,
) -> Optional[bytes]:
    """Re-encode an image as JPEG, capped at ``max_dimension`` on the longest side.

    Returns ``None`` when the source cannot be decoded, so callers can fall
    back to uploading the original bytes.
    """
    try:
        image = Image.open(io.BytesIO(data))
    except Exception as e:
        logger.error("Failed to open image for downscaling: %s", e)
        return None

    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGBA")
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1])
        image = background
    else:
        image = image.convert("RGB")

    longest = max(image.width, image.height)
    if longest > max_dimension:
        ratio = max_dimension / longest
        size = (max(1, round(image.width * ratio)), max(1, round(image.height * ratio)))
        image = image.resize(size, Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()


def clamp_width(width: int) -> int:
    return max(MIN_WIDTH, min(int(width), MAX_WIDTH))


def _thumb_path(source: str, filename: str, width: int) -> Path:
    return THUMB_CACHE_DIR / source / str(width) / f"{Path(filename).stem}.jpg"


def make_thumbnail(data: bytes, width: int) -> bytes:
    image = Image.open(io.BytesIO(data))
    image = image.convert("RGB")

    if image.width > width:
        ratio = width / image.width
        height = max(1, round(image.height * ratio))
        image = image.resize((width, height), Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=80, optimize=True)
    return buffer.getvalue()


def get_or_create_thumbnail(
    storage,
    source: str,
    filename: str,
    width: int,
) -> Optional[bytes]:
    width = clamp_width(width)
    cache_path = _thumb_path(source, filename, width)

    if cache_path.exists():
        return cache_path.read_bytes()

    original = storage.download_bytes(
        f"images/{source}/{filename}",
        check_exists=False,
    )
    if original is None:
        return None

    try:
        thumbnail = make_thumbnail(original, width)
    except Exception as e:
        logger.error("Thumbnail generation failed for %s/%s: %s", source, filename, e)
        return None

    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=cache_path.parent, delete=False, suffix=".tmp"
        ) as tmp:
            tmp.write(thumbnail)
            tmp_path = tmp.name
        os.replace(tmp_path, cache_path)
    except Exception as e:
        logger.warning("Failed to cache thumbnail %s: %s", cache_path, e)

    return thumbnail
