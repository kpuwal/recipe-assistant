import io

import pytest
from PIL import Image

from services.image_service import MAX_UPLOAD_BYTES, validate_image_upload


def encode_image(image_format):
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), (231, 76, 60)).save(buffer, format=image_format)
    return buffer.getvalue()


@pytest.mark.parametrize(
    "image_format,expected",
    [
        ("JPEG", "jpg"),
        ("PNG", "png"),
        ("WEBP", "webp"),
    ],
)
def test_validate_image_upload_accepts_supported_formats(image_format, expected):
    assert validate_image_upload(encode_image(image_format)) == expected


def test_validate_image_upload_rejects_non_images():
    assert validate_image_upload(b"not an image") is None
    assert validate_image_upload(b"%PDF-1.4") is None


def test_validate_image_upload_rejects_empty_and_oversized_data():
    assert validate_image_upload(b"") is None
    assert validate_image_upload(b"x" * (MAX_UPLOAD_BYTES + 1)) is None
