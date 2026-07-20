import threading
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from storage.gcs_storage import GCSStorage
from models.models import Recipe
from services.search_index import build_search_index
from core.helpers import slugify
from utils.logger import logger


class RecipeRepository:
    _lock = threading.Lock()

    def __init__(self, storage: GCSStorage):
        self.storage = storage

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
    
    def load_all(self) -> List[Recipe]:
        recipes = []

        files = self.storage.list_files(prefix="recipes/")

        for blob_name in files:
            if not blob_name.endswith(".json"):
                continue

            data = self.storage.download_json(blob_name)
            if not data:
                continue

            parts = blob_name.split("/")
            source = parts[1]
            data["source"] = source

            recipe = Recipe(**data)
            build_search_index(recipe)
            recipes.append(recipe)

        return recipes

    def list(self) -> List[Recipe]:
        return self.load_all()

    def get(self, recipe_id: str) -> Optional[Recipe]:

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
    
    def save(self, recipe: Recipe) -> Recipe:
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
                image_blob = (f"images/" f"{recipe.source}/" f"{recipe.image}")

                uploaded_image = self.storage.upload_bytes(
                    data=recipe.image_bytes,
                    blob_name=image_blob,
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

        return self.save(recipe)

    def delete(self, recipe_id: str) -> bool:
        with self._lock:
            recipe = self.get(recipe_id)

            if not recipe:
                logger.warning("Recipe not found: %s", recipe_id)
                return False

            self.storage.delete_file(
                f"recipes/{recipe.source}/{recipe.id}.json"
            )

            if recipe.image:
                self.storage.delete_file(
                    f"images/{recipe.source}/{recipe.image}"
                )

            logger.info("Deleted recipe: %s", recipe_id)
            return True
    
    def _map_source(self, source: str) -> str:
        if source == "picnic":
            return "imported"
        return source
