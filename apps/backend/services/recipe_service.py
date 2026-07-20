from typing import List, Optional

from models.models import Recipe
from repositories.recipe_repository import RecipeRepository
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

    def create_recipe(self, recipe_data: dict) -> Recipe:
        recipe = Recipe(**recipe_data)
        print("recipe before save, from form ", recipe)
        recipe.source = "personal"
        saved = self.repo.save(recipe)
        print("recipe in service ", saved)
        logger.info("Created new personal recipe: %s", recipe.title)
        return saved

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
        saved = self.repo.save(recipe)
        logger.info("Toggled favorite for recipe %s -> %s", recipe_id, recipe.is_favorite)
        return saved

    def delete_recipe(self, recipe_id: str) -> bool:
        success = self.repo.delete(recipe_id)
        if success:
            logger.info("Deleted recipe: %s", recipe_id)
        else:
            logger.warning("Failed to delete recipe: %s (not found)", recipe_id)
        return success

    def list_recipes(
        self, 
        source: Optional[str] = None, 
        favorites_only: bool = False
    ) -> List[Recipe]:
        recipes = self.repo.load_all()
        
        if source:
            recipes = [r for r in recipes if r.source == source]
        if favorites_only:
            recipes = [r for r in recipes if r.is_favorite]
        
        logger.info("Listed %d recipes (source=%s, favorites_only=%s)", 
                   len(recipes), source, favorites_only)
        return recipes