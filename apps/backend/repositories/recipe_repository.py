import threading
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from storage.gcs_storage import GCSStorage
from models.models import Recipe
from services.image_service import downscale_image, media_type_for
from services.search_index import build_search_index, SearchIndexBuilder, SearchIndex
from core.helpers import slugify
from utils.logger import logger


class RecipeRepository:
    _lock = threading.Lock()

    def __init__(self, storage: GCSStorage):
        self.storage = storage
        self._cached_recipes: Optional[List[Recipe]] = None
        self._cached_index: Optional[SearchIndex] = None
        self._cached_recipes_by_id: Optional[dict] = None

    def _clear_cache(self) -> None:
        self._cached_recipes = None
        self._cached_index = None
        self._cached_recipes_by_id = None

    def _rebuild_by_id_cache(self) -> None:
        self._cached_recipes_by_id = {r.id: r for r in self._cached_recipes or []}

    def generate_id(self, source: str) -> str:
        source = source.lower()

        if source == "imported":
            prefix = "r"
        elif source == "ai":
            prefix = "ai"
        else:
            prefix = "per"

        files = self.storage.list_files(prefix=f"recipes/{source}/")
        numbers = []

        for blob_name in files:
            filename = Path(blob_name).stem

            try:
                number = int(filename.replace(prefix, ""))
                numbers.append(number)

            except ValueError:
                continue

        next_number = max(numbers, default=0) + 1
        return f"{prefix}{next_number:03d}"

    def _load_one(self, blob_name: str) -> Optional[Recipe]:
        data = self.storage.download_json(blob_name, check_exists=False)
        if not data:
            return None

        source = blob_name.split("/")[1]
        data["source"] = source

        recipe = Recipe(**data)
        build_search_index(recipe)
        return recipe

    def load_all(self) -> List[Recipe]:
        files = [
            blob_name
            for blob_name in self.storage.list_files(prefix="recipes/")
            if blob_name.endswith(".json")
        ]

        if not files:
            return []

        with ThreadPoolExecutor(max_workers=16) as executor:
            loaded = executor.map(self._load_one, files)

        return [recipe for recipe in loaded if recipe is not None]

    def list(self) -> List[Recipe]:
        if self._cached_recipes is None or self._cached_index is None:
            with self._lock:
                if self._cached_recipes is None or self._cached_index is None:
                    self._cached_recipes = self.load_all()
                    self._cached_index = SearchIndexBuilder().build(self._cached_recipes)
                    self._rebuild_by_id_cache()
        return self._cached_recipes

    def get_search_index(self) -> Optional[SearchIndex]:
        if self._cached_index is None:
            with self._lock:
                if self._cached_index is None:
                    self._cached_recipes = self.load_all()
                    self._cached_index = SearchIndexBuilder().build(self._cached_recipes)
                    self._rebuild_by_id_cache()
        return self._cached_index

    def get(self, recipe_id: str) -> Optional[Recipe]:
        if self._cached_recipes_by_id is not None and recipe_id in self._cached_recipes_by_id:
            return self._cached_recipes_by_id[recipe_id]

        recipe = self._load_from_gcs(recipe_id)

        if recipe is not None and self._cached_recipes is not None:
            self._cached_recipes_by_id[recipe_id] = recipe

        return recipe

    def _load_from_gcs(self, recipe_id: str) -> Optional[Recipe]:
        for source in ["imported", "ai", "personal"]:
            blob_name = (f"recipes/" f"{source}/" f"{recipe_id}.json")

            try:
                data = self.storage.download_json(blob_name)

                if data:
                    data["source"] = source
                    return Recipe(**data)

            except Exception as e:
                logger.error("Failed loading %s: %s", blob_name, e)

        return None

    def save(self, recipe: Recipe, clear_cache: bool = True) -> Recipe:
        with self._lock:
            recipe.source = self._map_source(recipe.source or "personal")

            if not recipe.id:
                recipe.id = self.generate_id(recipe.source)

            if not recipe.slug:
                recipe.slug = slugify(recipe.title)

            build_search_index(recipe)
            recipe.updated_at = datetime.now()

            if not recipe.created_at:
                recipe.created_at = datetime.now()

            if recipe.image_bytes and recipe.image:
                original_bytes = recipe.image_bytes
                downscaled = downscale_image(original_bytes)

                if downscaled is not None and len(downscaled) < len(original_bytes):
                    recipe.image_bytes = downscaled
                    recipe.image = f"{Path(recipe.image).stem}.jpg"
                    recipe.image_extension = "jpg"

                image_blob = (f"images/" f"{recipe.source}/" f"{recipe.image}")

                uploaded_image = self.storage.upload_bytes(
                    data=recipe.image_bytes,
                    blob_name=image_blob,
                    content_type=media_type_for(recipe.image),
                )

                if not uploaded_image:
                    raise Exception(f"GCS image upload failed: {image_blob}")

            data = recipe.model_dump(exclude_none=True, exclude={"image_bytes", "image_extension"})
            blob_name = (f"recipes/" f"{recipe.source}/" f"{recipe.id}.json")
            uploaded = self.storage.upload_json(data=data, blob_name=blob_name)

            if not uploaded:
                raise Exception(f"GCS upload failed: {blob_name}")

            recipe.image_bytes = None
            recipe.image_extension = None

            if clear_cache:
                self._clear_cache()
            logger.info( "Saved recipe to GCS: %s (source=%s)", recipe.id, recipe.source)
            return recipe

    def update(self, recipe: Recipe) -> Optional[Recipe]:
        existing = self.get(recipe.id)

        if not existing:
            return None

        old_source = existing.source
        new_source = self._map_source(recipe.source)

        if old_source != new_source:
            old_blob = (f"recipes/" f"{old_source}/" f"{recipe.id}.json")
            self.storage.delete_file(old_blob)

        self._clear_cache()
        return self.save(recipe)

    def delete(self, recipe_id: str) -> bool:
        with self._lock:
            recipe = self.get(recipe_id)

            if not recipe:
                logger.warning("Recipe not found: %s", recipe_id)
                return False

            self.storage.delete_file(
                f"recipes/{recipe.source}/{recipe_id}.json"
            )

            if recipe.image:
                self.storage.delete_file(
                    f"images/{recipe.source}/{recipe.image}"
                )

            self._clear_cache()
            logger.info("Deleted recipe: %s", recipe_id)
            return True

    def _map_source(self, source: str) -> str:
        if source == "picnic":
            return "imported"
        return source
