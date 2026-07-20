from fastapi import APIRouter, Depends, HTTPException
from functools import lru_cache

from pipeline.pdf_ingestion_pipeline import PDFIngestionPipeline
from core.settings import settings
from core.dependencies import get_recipe_repository
from utils.logger import logger

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

@lru_cache(maxsize=1)
def get_dropbox_client():
    from dropbox_client import DropboxClient
    client = DropboxClient()
    client.test_connection()
    return client

def get_pipeline(
    repository = Depends(get_recipe_repository),
    dbx_client = Depends(get_dropbox_client),
) -> PDFIngestionPipeline:
    from sources.dropbox_source import DropboxSource
    from storage.ingestion_state import IngestionState

    source = DropboxSource(dbx_client)
    state = IngestionState(storage=repository.storage)

    return PDFIngestionPipeline(
        source=source,
        repository=repository,
        state=state
    )

@router.post("/sync-recipes")
async def sync_recipes(
    dry_run: bool = False,
    pipeline: PDFIngestionPipeline = Depends(get_pipeline)
):
    try:
        logger.info("Starting recipe sync (dry_run=%s)", dry_run)
        result = pipeline.run(dry_run=dry_run)
        logger.info("Sync completed successfully")
        return result
    except Exception as e:
        logger.error("Sync failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")