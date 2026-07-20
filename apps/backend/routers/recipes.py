from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from services.recipe_service import RecipeService
from services.search_service import SearchService
from core.dependencies import get_recipe_service, get_search_service
from services.recipe_scaler import recipe_scaler
from models.models import Recipe
from utils.logger import logger

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("")
async def list_recipes(
    source: Optional[str] = Query(None),
    favorites_only: bool = Query(False),
    service: RecipeService = Depends(get_recipe_service)
):
    recipes = service.list_recipes(source=source, favorites_only=favorites_only)
    logger.info("Listed %d recipes (source=%s, favorites=%s)", len(recipes), source, favorites_only)
    return recipes

@router.get("/search")
async def search_recipes(
    q: str | None = None,
    ingredient: str | None = None,
    max_time: int | None = None,
    search_service: SearchService = Depends(get_search_service)
):
    query = q or ingredient or ""
    recipes = search_service.search_recipes(query=query, max_time=max_time)
    logger.info("Search for '%s' returned %d recipes", query, len(recipes))
    return recipes

@router.get("/{recipe_id}")
async def get_recipe(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.get_recipe(recipe_id)
    if not recipe:
        logger.warning("Recipe not found: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.post("/")
async def create_recipe(
    recipe_data: dict,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.create_recipe(recipe_data)
    logger.info("Created new recipe: %s", recipe.title)
    return recipe

@router.post("/ai")
async def create_ai_recipe(
    recipe_data: dict,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.save_ai_recipe(recipe_data)
    logger.info("Saved AI recipe: %s", recipe.title)
    return recipe

@router.put("/{recipe_id}/favorite")
async def toggle_favorite(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.toggle_favorite(recipe_id)
    if not recipe:
        logger.warning("Recipe not found for favorite toggle: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    logger.info("Toggled favorite for recipe %s", recipe_id)
    return recipe

@router.get("/{recipe_id}/scale")
async def scale_recipe(
    recipe_id: str,
    persons: int,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.get_recipe(recipe_id)
    if recipe is None:
        logger.warning("Recipe not found for scaling: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe_scaler.scale(recipe, persons)

@router.put("/{recipe_id}")
async def update_recipe(
    recipe_id: str,
    recipe_data: dict,
    service: RecipeService = Depends(get_recipe_service)
):
    existing = service.get_recipe(recipe_id)
    if not existing:
        logger.warning("Recipe not found for update: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")

    try:
        update_data = {**existing.model_dump(), **recipe_data}
        update_data["id"] = recipe_id
        update_data["source"] = existing.source
        updated_recipe = Recipe(**update_data)
        result = service.update_recipe(updated_recipe)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update recipe")
        logger.info("Updated recipe: %s", recipe_id)
        return result
    except Exception as e:
        logger.error("Update failed for %s: %s", recipe_id, e)
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service)
):
    deleted = service.delete_recipe(recipe_id)
    if not deleted:
        logger.warning("Recipe not found for deletion: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    logger.info("Deleted recipe: %s", recipe_id)
    return {"success": True}