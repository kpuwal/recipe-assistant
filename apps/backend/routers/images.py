from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from core.dependencies import get_gcs_storage

router = APIRouter(prefix="/images", tags=["images"])

ALLOWED_SOURCES = {"imported", "ai", "personal"}


@router.get("/{source}/{filename}")
def get_image(
    source: str,
    filename: str,
    storage=Depends(get_gcs_storage),
):

    if source not in ALLOWED_SOURCES:
        raise HTTPException(
            status_code=400,
            detail="Invalid source"
        )

    safe_filename = Path(filename).name

    if safe_filename != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    blob_name = f"images/{source}/{safe_filename}"

    image = storage.download_bytes(blob_name)

    if image is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )

    extension = Path(safe_filename).suffix.lower().lstrip(".")

    media_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }

    return Response(
        content=image,
        media_type=media_types.get(
            extension,
            "application/octet-stream",
        ),
    )