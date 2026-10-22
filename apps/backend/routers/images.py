import hashlib
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from core.dependencies import get_gcs_storage
from services.image_service import get_or_create_thumbnail, media_type_for
from utils.logger import logger

router = APIRouter(prefix="/images", tags=["images"])

ALLOWED_SOURCES = {"imported", "ai", "personal"}

CACHE_CONTROL = "private, max-age=86400"


def _image_response(content: bytes, media_type: str, request: Request) -> Response:
    etag = '"%s"' % hashlib.md5(content).hexdigest()

    if request.headers.get("if-none-match") == etag:
        return Response(
            status_code=304,
            headers={"ETag": etag, "Cache-Control": CACHE_CONTROL},
        )

    return Response(
        content=content,
        media_type=media_type,
        headers={"ETag": etag, "Cache-Control": CACHE_CONTROL},
    )


@router.get("/{source}/{filename}")
def get_image(
    source: str,
    filename: str,
    request: Request,
    w: int | None = Query(None, description="Optional thumbnail width in pixels"),
    storage=Depends(get_gcs_storage),
):

    if source not in ALLOWED_SOURCES:
        raise HTTPException(status_code=400, detail="Invalid source")

    safe_filename = Path(filename).name

    if safe_filename != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if w is not None:
        thumbnail = get_or_create_thumbnail(storage, source, safe_filename, w)
        if thumbnail is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return _image_response(thumbnail, "image/jpeg", request)

    image = storage.download_bytes(
        f"images/{source}/{safe_filename}",
        check_exists=False,
    )

    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    media_type = media_type_for(safe_filename)

    return _image_response(image, media_type, request)
