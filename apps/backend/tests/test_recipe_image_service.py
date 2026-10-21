from models.models import Ingredient, Recipe
from services.recipe_service import RecipeService


class FakeRepository:
    def __init__(self, recipe):
        self.recipe = recipe
        self.deleted = []

    def get(self, recipe_id):
        if self.recipe and self.recipe.id == recipe_id:
            return self.recipe
        return None

    def update(self, recipe):
        recipe.image_bytes = None
        self.recipe = recipe
        return recipe

    def delete_image(self, source, filename):
        self.deleted.append((source, filename))
        return True


def make_recipe(image=None):
    return Recipe(
        id="r001",
        title="Test",
        source="personal",
        image=image,
        ingredients=[Ingredient(name="bloem")],
        steps=["Meng alles."],
    )


def test_set_recipe_image_replaces_old_image():
    recipe = make_recipe(image="r001-old.jpg")
    repository = FakeRepository(recipe)
    service = RecipeService(repository)

    updated = service.set_recipe_image("r001", b"image-bytes", "png")

    assert updated.image.startswith("r001-")
    assert updated.image.endswith(".png")
    assert updated.image_bytes is None
    assert repository.deleted == [("personal", "r001-old.jpg")]


def test_set_recipe_image_returns_none_for_unknown_recipe():
    service = RecipeService(FakeRepository(None))

    assert service.set_recipe_image("r999", b"image-bytes", "png") is None


def test_remove_recipe_image_deletes_blob():
    recipe = make_recipe(image="r001-old.jpg")
    repository = FakeRepository(recipe)
    service = RecipeService(repository)

    updated = service.remove_recipe_image("r001")

    assert updated.image is None
    assert repository.deleted == [("personal", "r001-old.jpg")]


def test_remove_recipe_image_is_noop_without_image():
    recipe = make_recipe()
    repository = FakeRepository(recipe)
    service = RecipeService(repository)

    updated = service.remove_recipe_image("r001")

    assert updated.image is None
    assert repository.deleted == []
