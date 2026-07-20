from functools import lru_cache
from fastapi import Depends

from repositories.recipe_repository import RecipeRepository
from services.recipe_service import RecipeService
from services.search_service import SearchService
from storage.gcs_storage import GCSStorage
from core.settings import settings


@lru_cache(maxsize=1)
def get_gcs_storage() -> GCSStorage:
    return GCSStorage(bucket_name=settings.gcs_bucket_name)

@lru_cache(maxsize=1)
def get_recipe_repository(
    storage: GCSStorage = Depends(get_gcs_storage)
) -> RecipeRepository:
    return RecipeRepository(storage=storage)

@lru_cache(maxsize=1)
def get_recipe_service(
    repo: RecipeRepository = Depends(get_recipe_repository)
) -> RecipeService:
    return RecipeService(repo)


@lru_cache(maxsize=1)
def get_search_service(
    service: RecipeService = Depends(get_recipe_service)
) -> SearchService:
    return SearchService(service)
