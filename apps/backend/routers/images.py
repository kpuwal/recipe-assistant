from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from core.dependencies import get_gcs_storage

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/{source}/{filename}")
async def get_image(
    source: str,
    filename: str,
    storage=Depends(get_gcs_storage),
):

    blob_name = f"images/{source}/{filename}"
    image = storage.download_bytes(blob_name)

    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    extension = filename.split(".")[-1].lower()

    media_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }

    return Response(
        content=image,
        media_type=media_types.get(extension, "application/octet-stream")
    )