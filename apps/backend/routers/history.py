from fastapi import APIRouter, Depends

from services.recipe_service import RecipeService
from core.dependencies import get_recipe_service
from utils.logger import logger

router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
def get_history(
    service: RecipeService = Depends(get_recipe_service)
):
    entries = service.get_history()
    logger.info("Returning cooking history with %d entries", len(entries))
    return entries
