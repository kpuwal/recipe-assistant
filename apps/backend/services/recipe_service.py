from typing import List, Optional
from uuid import uuid4

from models.models import MANUAL_EDITABLE_FIELDS, Recipe, Timer
from repositories.recipe_repository import RecipeRepository
from services.search_index import SearchIndex
from core.taxonomy import DEFAULT_CATEGORY, normalize_category
from utils.logger import logger


class RecipeService:
    def __init__(self, repo: RecipeRepository):
        self.repo = repo   

    def validate_recipe(self, recipe: Recipe) -> bool:
        if not recipe.title or len(recipe.title.strip()) == 0:
            return False
        if not recipe.ingredients or len(recipe.ingredients) == 0:
            return False
        if not recipe.steps or len(recipe.steps) == 0:
            return False
        return True

    @staticmethod
    def _mark_edited(recipe: Recipe, *fields: str) -> None:
        recipe.user_edited_fields = sorted(
            set(recipe.user_edited_fields or []) | set(fields)
        )

    def _record_manual_edits(self, recipe: Recipe, existing: Recipe) -> None:
        changed = [
            field
            for field in MANUAL_EDITABLE_FIELDS
            if getattr(existing, field) != getattr(recipe, field)
        ]
        if changed:
            self._mark_edited(recipe, *changed)

    def create_recipe(self, recipe_data: dict) -> Recipe:
        recipe = Recipe(**recipe_data)
        recipe.source = "personal"
        saved = self.repo.save(recipe)
        logger.info("Created new personal recipe: %s", recipe.title)
        return saved

    def set_recipe_image(
        self,
        recipe_id: str,
        data: bytes,
        extension: str,
    ) -> Optional[Recipe]:
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return None

        old_image = recipe.image
        recipe.image = f"{recipe.id}-{uuid4().hex[:8]}.{extension}"
        recipe.image_bytes = data
        recipe.image_extension = extension
        self._mark_edited(recipe, "image")

        updated = self.update_recipe(recipe)
        if updated and old_image and old_image != updated.image:
            self.repo.delete_image(updated.source, old_image)

        logger.info("Updated image for recipe %s", recipe_id)
        return updated

    def remove_recipe_image(self, recipe_id: str) -> Optional[Recipe]:
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return None

        old_image = recipe.image
        if not old_image:
            return recipe

        recipe.image = None
        self._mark_edited(recipe, "image")
        updated = self.update_recipe(recipe)
        if updated:
            self.repo.delete_image(updated.source, old_image)

        logger.info("Removed image for recipe %s", recipe_id)
        return updated

    def save_ai_recipe(self, recipe_data: dict) -> Recipe:
        recipe = Recipe(**recipe_data)
        recipe.source = "ai"
        if not self.validate_recipe(recipe):
            logger.warning("AI recipe validation failed for: %s", recipe.title)
            raise ValueError("AI recipe validation failed")
        saved = self.repo.save(recipe)
        logger.info("Saved AI recipe: %s", recipe.title)
        return saved

    def update_recipe(self, recipe: Recipe) -> Optional[Recipe]:
        if not self.validate_recipe(recipe):
            logger.warning("Recipe validation failed during update: %s", recipe.title)
            raise ValueError("Recipe validation failed")

        existing = self.repo.get(recipe.id)
        if not existing:
            logger.warning("Recipe not found for update: %s", recipe.id)
            return None

        self._record_manual_edits(recipe, existing)
        updated = self.repo.update(recipe)
        logger.info("Updated recipe: %s", recipe.title)
        return updated

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        return self.repo.get(recipe_id)

    def toggle_favorite(self, recipe_id: str) -> Optional[Recipe]:
        recipe = self.repo.get(recipe_id)
        if not recipe:
            return None
        recipe.is_favorite = not recipe.is_favorite
        saved = self.repo.save(recipe, clear_cache=False)
        logger.info("Toggled favorite for recipe %s -> %s", recipe_id, recipe.is_favorite)
        return saved

    def add_timer(self, recipe_id: str, timer_data: dict) -> Optional[Recipe]:
        recipe = self.repo.get(recipe_id)
        if not recipe:
            return None
        timer = Timer(id=str(uuid4()), **timer_data)
        recipe.timers.append(timer)
        saved = self.repo.save(recipe, clear_cache=False)
        logger.info("Added timer to recipe %s: %s", recipe_id, timer.label)
        return saved

    def delete_timer(self, recipe_id: str, timer_id: str) -> Optional[Recipe]:
        recipe = self.repo.get(recipe_id)
        if not recipe:
            return None

        remaining = [t for t in recipe.timers if t.id != timer_id]
        if len(remaining) == len(recipe.timers):
            return None

        recipe.timers = remaining
        saved = self.repo.save(recipe, clear_cache=False)
        logger.info("Deleted timer %s from recipe %s", timer_id, recipe_id)
        return saved

    def mark_cooked(self, recipe_id: str, date: str) -> Optional[Recipe]:
        recipe = self.repo.get(recipe_id)
        if not recipe:
            return None

        recipe.cooked_dates = recipe.cooked_dates or []
        if date not in recipe.cooked_dates:
            recipe.cooked_dates.append(date)
            saved = self.repo.save(recipe, clear_cache=False)
            logger.info("Marked recipe %s as cooked on %s", recipe_id, date)
            return saved

        return recipe

    def unmark_cooked(self, recipe_id: str, date: str) -> Optional[Recipe]:
        recipe = self.repo.get(recipe_id)
        if not recipe:
            return None

        recipe.cooked_dates = recipe.cooked_dates or []
        if date in recipe.cooked_dates:
            recipe.cooked_dates = [d for d in recipe.cooked_dates if d != date]
            saved = self.repo.save(recipe, clear_cache=False)
            logger.info("Unmarked recipe %s cooked on %s", recipe_id, date)
            return saved

        return recipe

    def get_history(self) -> List[dict]:
        entries = []
        for recipe in self.list_recipes():
            for date in recipe.cooked_dates or []:
                entries.append({
                    "recipe_id": recipe.id,
                    "title": recipe.title,
                    "image": recipe.image,
                    "source": recipe.source,
                    "date": date,
                })

        entries.sort(key=lambda e: e["title"])
        entries.sort(key=lambda e: e["date"], reverse=True)
        logger.info("Built cooking history with %d entries", len(entries))
        return entries

    def delete_recipe(self, recipe_id: str) -> bool:
        success = self.repo.delete(recipe_id)
        if success:
            logger.info("Deleted recipe: %s", recipe_id)
        else:
            logger.warning("Failed to delete recipe: %s (not found)", recipe_id)
        return success

    def get_search_index(self) -> Optional[SearchIndex]:
        return self.repo.get_search_index()

    def list_recipes(
        self,
        source: Optional[str] = None,
        favorites_only: bool = False,
        category: Optional[str] = None,
    ) -> List[Recipe]:
        recipes = self.repo.list()

        if source:
            recipes = [r for r in recipes if r.source == source]
        if favorites_only:
            recipes = [r for r in recipes if r.is_favorite]
        if category:
            normalized = normalize_category(category)
            if not normalized:
                logger.warning("Unknown category filter: %s", category)
                return []
            recipes = [
                r
                for r in recipes
                if normalize_category(
                    r.category,
                    default=DEFAULT_CATEGORY,
                ) == normalized
            ]

        logger.info(
            "Listed %d recipes (source=%s, favorites_only=%s, category=%s)",
            len(recipes), source, favorites_only, category,
        )
        return recipes