from functools import lru_cache

from repositories.recipe_repository import RecipeRepository
from services.recipe_service import RecipeService
from services.search_service import SearchService
from storage.gcs_storage import GCSStorage
from core.settings import settings


@lru_cache(maxsize=1)
def get_gcs_storage() -> GCSStorage:
    return GCSStorage(bucket_name=settings.gcs_bucket_name)

@lru_cache(maxsize=1)
def get_recipe_repository() -> RecipeRepository:
    return RecipeRepository(storage=get_gcs_storage())

@lru_cache(maxsize=1)
def get_recipe_service() -> RecipeService:
    return RecipeService(get_recipe_repository())


@lru_cache(maxsize=1)
def get_search_service() -> SearchService:
    return SearchService(get_recipe_service())
