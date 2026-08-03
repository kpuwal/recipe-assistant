from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import get_gcs_storage
from storage.gcs_storage import GCSStorage
from utils.logger import logger

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    logger.debug("Health check called")
    return {
        "status": "healthy",
        "service": "recipe-assistant",
    }


@router.get("/healthz")
def readiness_probe(
    storage: GCSStorage = Depends(get_gcs_storage),
):
    if not storage.health_check():
        logger.error("Readiness check failed: GCS unavailable")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "reason": "gcs_unavailable",
            },
        )

    return {
        "status": "healthy",
        "storage": "gcs",
    }


@router.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {
        "status": "Recipe Assistant API is running"
    }