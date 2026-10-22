from fastapi import APIRouter, HTTPException, Query, Depends, File, UploadFile
from typing import Optional

from services.recipe_service import RecipeService
from services.search_service import SearchService
from services.image_service import MAX_UPLOAD_BYTES, validate_image_upload
from core.dependencies import get_recipe_service, get_search_service
from services.recipe_scaler import recipe_scaler
from models.models import (
    Recipe,
    RecipeCreate,
    RecipeUpdate,
    TimerCreate,
)
from utils.logger import logger

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("", response_model=list[Recipe])
def list_recipes(
    source: Optional[str] = Query(None),
    favorites_only: bool = Query(False),
    category: Optional[str] = Query(None),
    service: RecipeService = Depends(get_recipe_service)
):
    recipes = service.list_recipes(
        source=source,
        favorites_only=favorites_only,
        category=category,
    )
    logger.info(
        "Listed %d recipes (source=%s, favorites=%s, category=%s)",
        len(recipes), source, favorites_only, category,
    )
    return recipes

@router.get("/search")
def search_recipes(
    q: str | None = None,
    ingredient: str | None = None,
    max_time: int | None = None,
    min_time: int | None = None,
    category: str | None = None,
    favorites_only: bool = False,
    search_service: SearchService = Depends(get_search_service)
):
    query = q or ingredient or ""
    recipes = search_service.search_recipes(
        query=query,
        max_time=max_time,
        min_time=min_time,
        category=category,
        favorites_only=favorites_only,
    )
    logger.info("Search returned %d recipes", len(recipes))
    return recipes

@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.get_recipe(recipe_id)
    if not recipe:
        logger.warning("Recipe not found: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.post("/{recipe_id}/image", response_model=Recipe)
async def upload_recipe_image(
    recipe_id: str,
    file: UploadFile = File(...),
    service: RecipeService = Depends(get_recipe_service)
):
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image is larger than 10 MB")

    extension = validate_image_upload(data)
    if not extension:
        raise HTTPException(
            status_code=415,
            detail="Invalid image. Use JPEG, PNG or WebP.",
        )

    recipe = service.set_recipe_image(recipe_id, data, extension)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    logger.info("Uploaded image for recipe %s", recipe_id)
    return recipe


@router.delete("/{recipe_id}/image", response_model=Recipe)
def delete_recipe_image(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.remove_recipe_image(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    logger.info("Removed image for recipe %s", recipe_id)
    return recipe


@router.post("/", response_model=Recipe)
def create_recipe(
    recipe_data: RecipeCreate,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.create_recipe(recipe_data.model_dump())
    logger.info("Created new recipe: %s", recipe.title)
    return recipe

@router.post("/ai", response_model=Recipe)
def create_ai_recipe(
    recipe_data: RecipeCreate,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.save_ai_recipe(recipe_data.model_dump())
    logger.info("Saved AI recipe: %s", recipe.title)
    return recipe

@router.put("/{recipe_id}/favorite")
def toggle_favorite(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.toggle_favorite(recipe_id)
    if not recipe:
        logger.warning("Recipe not found for favorite toggle: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    logger.info("Toggled favorite for recipe %s", recipe_id)
    return recipe

@router.post("/{recipe_id}/timers", response_model=Recipe)
def add_timer(
    recipe_id: str,
    timer_data: TimerCreate,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.add_timer(recipe_id, timer_data.model_dump())
    if not recipe:
        logger.warning("Recipe not found for timer creation: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    logger.info("Added timer to recipe %s", recipe_id)
    return recipe

@router.delete("/{recipe_id}/timers/{timer_id}", response_model=Recipe)
def delete_timer(
    recipe_id: str,
    timer_id: str,
    service: RecipeService = Depends(get_recipe_service)
):
    if not service.get_recipe(recipe_id):
        logger.warning("Recipe not found for timer deletion: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe = service.delete_timer(recipe_id, timer_id)
    if not recipe:
        logger.warning("Timer not found for deletion: %s", timer_id)
        raise HTTPException(status_code=404, detail="Timer not found")
    logger.info("Deleted timer %s from recipe %s", timer_id, recipe_id)
    return recipe

@router.post("/{recipe_id}/cooked", response_model=Recipe)
def mark_cooked(
    recipe_id: str,
    date: str = Query(..., description="Date cooked, YYYY-MM-DD"),
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.mark_cooked(recipe_id, date)
    if not recipe:
        logger.warning("Recipe not found for marking cooked: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    logger.info("Marked recipe %s as cooked on %s", recipe_id, date)
    return recipe

@router.delete("/{recipe_id}/cooked/{date}", response_model=Recipe)
def unmark_cooked(
    recipe_id: str,
    date: str,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.unmark_cooked(recipe_id, date)
    if not recipe:
        logger.warning("Recipe not found for unmarking cooked: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    logger.info("Unmarked recipe %s cooked on %s", recipe_id, date)
    return recipe

@router.get("/{recipe_id}/scale")
def scale_recipe(
    recipe_id: str,
    persons: int,
    service: RecipeService = Depends(get_recipe_service)
):
    recipe = service.get_recipe(recipe_id)
    if recipe is None:
        logger.warning("Recipe not found for scaling: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe_scaler.scale(recipe, persons)

@router.put("/{recipe_id}", response_model=Recipe)
def update_recipe(
    recipe_id: str,
    recipe_data: RecipeUpdate,
    service: RecipeService = Depends(get_recipe_service)
):
    existing = service.get_recipe(recipe_id)
    if not existing:
        logger.warning("Recipe not found for update: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")

    try:
        update_data = {**existing.model_dump(), **recipe_data.model_dump(exclude_unset=True)}
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
def delete_recipe(
    recipe_id: str,
    service: RecipeService = Depends(get_recipe_service)
):
    deleted = service.delete_recipe(recipe_id)
    if not deleted:
        logger.warning("Recipe not found for deletion: %s", recipe_id)
        raise HTTPException(status_code=404, detail="Recipe not found")
    logger.info("Deleted recipe: %s", recipe_id)
    return {"success": True}