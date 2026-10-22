from models.models import Ingredient, Recipe
from services.recipe_service import RecipeService


class FakeRepository:
    def __init__(self, recipe):
        self.recipe = recipe

    def get(self, recipe_id):
        if self.recipe and self.recipe.id == recipe_id:
            return self.recipe
        return None

    def update(self, recipe):
        self.recipe = recipe
        return recipe


def make_recipe(**overrides):
    data = {
        "id": "r001",
        "title": "Old title",
        "ingredients": [Ingredient(name="bloem", quantity="200 g")],
        "steps": ["Meng alles."],
        "tips": "Old tip",
    }
    data.update(overrides)
    return Recipe(**data)


def test_update_records_changed_fields():
    existing = make_recipe()
    service = RecipeService(FakeRepository(existing))
    updated = existing.model_copy(deep=True)
    updated.title = "New title"
    updated.tips = "New tip"

    result = service.update_recipe(updated)

    assert result.title == "New title"
    assert result.user_edited_fields == ["tips", "title"]


def test_update_keeps_previously_edited_fields():
    existing = make_recipe(user_edited_fields=["title"])
    service = RecipeService(FakeRepository(existing))
    updated = existing.model_copy(deep=True)
    updated.tips = "New tip"

    result = service.update_recipe(updated)

    assert result.user_edited_fields == ["tips", "title"]


def test_update_does_not_mark_unchanged_fields():
    existing = make_recipe()
    service = RecipeService(FakeRepository(existing))
    updated = existing.model_copy(deep=True)

    result = service.update_recipe(updated)

    assert result.user_edited_fields == []
