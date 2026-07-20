from fastapi import APIRouter
from utils.logger import logger
from core.settings import settings
import os

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    logger.debug("Health check called")
    return {"status": "healthy", "service": "recipe-assistant"}

@router.get("/healthz")
async def readiness_probe():
    image_dir = settings.image_dir
    image_dir = image_dir.resolve()

    if not image_dir.is_dir():
        logger.error("Image directory %s does not exist", image_dir)
        return {"status": "unhealthy", "reason": "image_dir_missing"}
    if not os.access(image_dir, os.R_OK | os.W_OK):
        logger.error("Image directory %s is not read/write accessible", image_dir)
        return {"status": "unhealthy", "reason": "image_dir_no_rw"}
    return {"status": "healthy", "image_dir": str(image_dir)}

@router.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"status": "Recipe Assistant API is running"}