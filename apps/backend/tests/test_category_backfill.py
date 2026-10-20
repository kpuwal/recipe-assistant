import pytest

from models.models import Recipe
from services.category_backfill import (
    apply_proposals,
    build_proposals,
    classify_recipe,
)


def make_recipe(recipe_id, title, category, source="imported"):
    return Recipe(
        id=recipe_id,
        title=title,
        category=category,
        source=source,
    )


@pytest.mark.parametrize(
    "title,current,expected_kind,expected_after",
    [
        ("Kippensoep", "soup", None, None),
        ("Kippensoep", "other", "uncategorized", "soup"),
        ("Kippensoep", "rice", "conflict", "soup"),
        ("Kippensoep", "Overig", "uncategorized", "soup"),
        ("Rijst met kip", "rijst", "normalize", "rice"),
        ("Rijst met kip", "Rijst", "normalize", "rice"),
        ("Kippensoep", "rijst", "normalize", "rice"),
        ("Pizza margherita", "pasta salade", "normalize", "salad"),
        ("Kippensoep", "hoofdgerecht", "unknown", "soup"),
        ("Geheim", "hoofdgerecht", "unknown", "other"),
        ("Geheim", "", None, None),
        ("Kippensoep", "", "unknown", "soup"),
    ],
)
def test_classify_recipe(title, current, expected_kind, expected_after):
    proposal = classify_recipe(make_recipe("r1", title, current))

    if expected_kind is None:
        assert proposal is None
        return

    assert proposal.kind == expected_kind
    assert proposal.before == current
    assert proposal.after == expected_after


def test_build_proposals_puts_conflicts_last():
    recipes = [
        make_recipe("r5", "Kippensoep", "soup"),
        make_recipe("r4", "Pizza margherita", "rice"),
        make_recipe("r3", "Kippensoep", "other"),
        make_recipe("r2", "Rijst met kip", "rijst"),
        make_recipe("r1", "Kippensoep", "rice"),
    ]

    proposals = build_proposals(recipes)

    assert [proposal.recipe_id for proposal in proposals] == [
        "r2",
        "r3",
        "r1",
        "r4",
    ]
    assert [proposal.is_conflict for proposal in proposals] == [
        False,
        False,
        True,
        True,
    ]


class FakeRepository:
    def __init__(self, fail_ids=()):
        self.saved = []
        self.fail_ids = set(fail_ids)

    def save(self, recipe):
        if recipe.id in self.fail_ids:
            raise RuntimeError("save failed")
        self.saved.append((recipe.id, recipe.category))
        return recipe


def test_apply_skips_conflicts_by_default():
    recipes = [
        make_recipe("r1", "Kippensoep", "other"),
        make_recipe("r2", "Kippensoep", "rice"),
        make_recipe("r3", "Rijst met kip", "rijst"),
    ]
    proposals = build_proposals(recipes)
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    repository = FakeRepository()

    applied, failures = apply_proposals(
        proposals, recipes_by_id, repository, include_conflicts=False
    )

    assert applied == 2
    assert failures == []
    assert repository.saved == [("r1", "soup"), ("r3", "rice")]
    assert recipes_by_id["r2"].category == "rice"


def test_apply_can_include_conflicts():
    recipes = [
        make_recipe("r1", "Kippensoep", "other"),
        make_recipe("r2", "Kippensoep", "rice"),
    ]
    proposals = build_proposals(recipes)
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    repository = FakeRepository()

    applied, failures = apply_proposals(
        proposals, recipes_by_id, repository, include_conflicts=True
    )

    assert applied == 2
    assert failures == []
    assert repository.saved == [("r1", "soup"), ("r2", "soup")]


def test_apply_can_include_selected_conflicts():
    recipes = [
        make_recipe("r1", "Kippensoep", "rice"),
        make_recipe("r2", "Kippensoep", "rice"),
        make_recipe("r3", "Kippensoep", "rice"),
    ]
    proposals = build_proposals(recipes)
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    repository = FakeRepository()

    applied, failures = apply_proposals(
        proposals, recipes_by_id, repository, conflict_ids={"r2"}
    )

    assert applied == 1
    assert failures == []
    assert repository.saved == [("r2", "soup")]
    assert recipes_by_id["r1"].category == "rice"
    assert recipes_by_id["r3"].category == "rice"


def test_apply_records_save_failures_and_continues():
    recipes = [
        make_recipe("r1", "Kippensoep", "other"),
        make_recipe("r2", "Rijst met kip", "other"),
    ]
    proposals = build_proposals(recipes)
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    repository = FakeRepository(fail_ids={"r1"})

    applied, failures = apply_proposals(
        proposals, recipes_by_id, repository, include_conflicts=False
    )

    assert applied == 1
    assert len(failures) == 1
    assert failures[0]["recipe_id"] == "r1"
    assert repository.saved == [("r2", "rice")]


def test_apply_records_missing_recipes():
    recipes = [make_recipe("r1", "Kippensoep", "other")]
    proposals = build_proposals(recipes)
    repository = FakeRepository()

    applied, failures = apply_proposals(
        proposals, {}, repository, include_conflicts=False
    )

    assert applied == 0
    assert failures == [
        {"recipe_id": "r1", "error": "Recipe not found in loaded set"}
    ]
