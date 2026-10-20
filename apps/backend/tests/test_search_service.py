import pytest

from models.models import Ingredient, Recipe
from services.recipe_service import RecipeService
from services.search_index import build_search_index
from services.search_service import SearchService


def make_recipe(
    recipe_id,
    title,
    category="other",
    ingredients=(),
    time_minutes=None,
    is_favorite=False,
):
    recipe = Recipe(
        id=recipe_id,
        title=title,
        category=category,
        ingredients=[Ingredient(name=name) for name in ingredients],
        steps=["Bereid het gerecht."],
        time_minutes=time_minutes,
        is_favorite=is_favorite,
    )
    return build_search_index(recipe)


class FakeRecipeService:
    def __init__(self, recipes):
        self.recipes = recipes

    def list_recipes(self, source=None, favorites_only=False, category=None):
        recipes = self.recipes
        if favorites_only:
            recipes = [recipe for recipe in recipes if recipe.is_favorite]
        return recipes

    def get_search_index(self):
        return None


class FakeRepo:
    def __init__(self, recipes):
        self.recipes = recipes

    def list(self):
        return self.recipes


@pytest.fixture
def recipes():
    return [
        make_recipe("r1", "Rice bowl", "rice", ["rijst", "kip"], 25),
        make_recipe("r2", "Groente rijst", "rice", ["rijst"], 30),
        make_recipe("r3", "Pasta bolognese", "pasta", ["pasta", "gehakt"], 20),
        make_recipe("r4", "Pasta salade", "salad", ["pasta", "tomaat"], 15),
        make_recipe("r5", "Kippensoep", "soup", ["kip"], 40, is_favorite=True),
        make_recipe("r6", "Rijst met vis", "rijst", ["vis"], 20),
        make_recipe("r7", "Pizza margherita", "pizza", ["pizza"], 35),
    ]


@pytest.fixture
def service(recipes):
    return SearchService(FakeRecipeService(recipes))


def ids(recipes):
    return {recipe.id for recipe in recipes}


def test_dutch_category_synonym_finds_category(service):
    assert ids(service.search_recipes(query="rijst")) == {"r1", "r2", "r6"}


def test_category_synonym_also_keeps_text_matches(service):
    assert ids(service.search_recipes(query="pasta")) == {"r3", "r4"}


def test_multi_word_category_phrase_collapses(service):
    assert ids(service.search_recipes(query="pasta salade")) == {"r4"}


def test_category_and_word_both_must_match(service):
    assert ids(service.search_recipes(query="kip met rijst")) == {"r1"}


def test_favorites_word_sets_filter(service):
    assert ids(service.search_recipes(query="favorieten")) == {"r5"}


def test_fast_word_sets_time_filter(service):
    assert ids(service.search_recipes(query="snel")) == {"r3", "r4", "r6"}


def test_fast_word_combines_with_category(service):
    assert ids(service.search_recipes(query="snel pasta")) == {"r3", "r4"}


def test_compound_spice_is_not_a_category(service):
    assert service.search_recipes(query="currykruiden") == []


def test_apostrophe_plural_is_tokenized(service):
    assert ids(service.search_recipes(query="pizza's")) == {"r7"}


def test_explicit_category_accepts_dutch_label(service):
    assert ids(service.search_recipes(category="Rijst")) == {"r1", "r2", "r6"}


def test_explicit_category_combines_with_query(service):
    assert ids(service.search_recipes(query="kip", category="rijst")) == {"r1"}


def test_unknown_category_returns_empty(service):
    assert service.search_recipes(category="onbekend") == []


def test_favorites_only_parameter(service):
    assert ids(service.search_recipes(favorites_only=True)) == {"r5"}


def test_max_time_parameter(service):
    assert ids(service.search_recipes(max_time=20)) == {"r3", "r4", "r6"}


def test_min_time_parameter(service):
    assert ids(service.search_recipes(min_time=25)) == {"r1", "r2", "r5", "r7"}


def test_time_range_parameter(service):
    assert ids(service.search_recipes(min_time=15, max_time=25)) == {
        "r1",
        "r3",
        "r4",
        "r6",
    }


def test_explicit_time_overrides_query(service):
    assert ids(service.search_recipes(query="snel", max_time=40)) == {
        "r1",
        "r2",
        "r3",
        "r4",
        "r5",
        "r6",
        "r7",
    }


def test_empty_query_returns_all_sorted_by_title(service):
    recipes = service.search_recipes()
    assert len(recipes) == 7
    assert [recipe.title for recipe in recipes] == sorted(
        recipe.title for recipe in recipes
    )


def test_recipe_service_filters_by_category(recipes):
    service = RecipeService(FakeRepo(recipes))
    assert ids(service.list_recipes(category="rijst")) == {"r1", "r2", "r6"}


def test_recipe_service_rejects_unknown_category(recipes):
    service = RecipeService(FakeRepo(recipes))
    assert service.list_recipes(category="onbekend") == []
