from models.models import Recipe
from services.oven_backfill import (
    apply_oven_proposals,
    build_oven_proposals,
)


def make_recipe(recipe_id, steps, oven_temperature=None, oven_mode=None):
    return Recipe(
        id=recipe_id,
        title=f"Recipe {recipe_id}",
        steps=steps,
        oven_temperature=oven_temperature,
        oven_mode=oven_mode,
        source="imported",
    )


class FakeRepository:
    def __init__(self, fail_ids=()):
        self.saved = []
        self.fail_ids = set(fail_ids)

    def save(self, recipe):
        if recipe.id in self.fail_ids:
            raise RuntimeError("save failed")
        self.saved.append(
            (recipe.id, recipe.oven_temperature, recipe.oven_mode)
        )
        return recipe


def test_build_proposals_skips_existing_and_missing_temperatures():
    recipes = [
        make_recipe("r1", ["Verwarm de oven op 200 graden."]),
        make_recipe("r2", ["Meng de ingrediënten."]),
        make_recipe(
            "r3",
            ["Verwarm de oven op 220 graden."],
            oven_temperature=180,
        ),
    ]

    proposals = build_oven_proposals(recipes)

    assert [(proposal.recipe_id, proposal.temperature) for proposal in proposals] == [
        ("r1", 200)
    ]


def test_build_proposals_detects_mode_from_steps_and_tips():
    recipes = [
        make_recipe(
            "r1",
            ["Verwarm de heteluchtoven op 180 graden."],
        ),
        Recipe(
            id="r2",
            title="Recipe r2",
            steps=["Bak 25 minuten op 200 graden."],
            tips="Gebruik boven- en onderwarmte.",
        ),
    ]

    proposals = build_oven_proposals(recipes)

    assert [(proposal.recipe_id, proposal.mode) for proposal in proposals] == [
        ("r1", "fan"),
        ("r2", "conventional"),
    ]


def test_apply_writes_temperature_and_mode():
    recipes = [make_recipe("r1", ["Verwarm de oven op 200 graden."])]
    proposals = build_oven_proposals(recipes)
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    repository = FakeRepository()

    applied, failures = apply_oven_proposals(
        proposals,
        recipes_by_id,
        repository,
    )

    assert applied == 1
    assert failures == []
    assert repository.saved == [("r1", 200, None)]
    assert recipes_by_id["r1"].oven_temperature == 200


def test_apply_keeps_existing_mode_when_detection_has_none():
    recipes = [
        make_recipe(
            "r1",
            ["Verwarm de oven op 200 graden."],
            oven_mode="fan",
        )
    ]
    proposals = build_oven_proposals(recipes)
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    repository = FakeRepository()

    applied, failures = apply_oven_proposals(
        proposals,
        recipes_by_id,
        repository,
    )

    assert applied == 1
    assert failures == []
    assert recipes_by_id["r1"].oven_mode == "fan"


def test_apply_records_failures_and_continues():
    recipes = [
        make_recipe("r1", ["Verwarm de oven op 200 graden."]),
        make_recipe("r2", ["Verwarm de oven op 180 graden."]),
    ]
    proposals = build_oven_proposals(recipes)
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    repository = FakeRepository(fail_ids={"r1"})

    applied, failures = apply_oven_proposals(
        proposals,
        recipes_by_id,
        repository,
    )

    assert applied == 1
    assert failures == [{"recipe_id": "r1", "error": "save failed"}]
    assert repository.saved == [("r2", 180, None)]


def test_apply_records_missing_recipes():
    recipes = [make_recipe("r1", ["Verwarm de oven op 200 graden."])]
    proposals = build_oven_proposals(recipes)
    repository = FakeRepository()

    applied, failures = apply_oven_proposals(proposals, {}, repository)

    assert applied == 0
    assert failures == [
        {"recipe_id": "r1", "error": "Recipe not found in loaded set"}
    ]
