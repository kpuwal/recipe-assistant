import pytest

from models.models import Ingredient
from services.pdf_parser import detect_category


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Kippensoep", "soup"),
        ("Tomatensoep", "soup"),
        ("Rijst met kip", "rice"),
        ("Nasi goreng", "rice"),
        ("Zilvervliesrijst", "rice"),
        ("Volkorenpasta", "pasta"),
        ("Pasta salade", "salad"),
        ("Pasta salad", "salad"),
        ("Griekse salade", "salad"),
        ("Tortillawrap", "wrap"),
        ("Taco's", "wrap"),
        ("Tortillas", "wrap"),
        ("Woknoedels", "noodle"),
        ("Mihoen", "noodle"),
        ("Rice noodles", "noodle"),
        ("Noedelsoep", "soup"),
        ("Currypasta met kip", "curry"),
        ("Groene curry", "curry"),
        ("Broodje hamburger", "burger"),
        ("Pizza margherita", "pizza"),
        ("Pizza's", "pizza"),
        ("Chicken soup", "soup"),
        ("Fried rice", "rice"),
    ],
)
def test_title_detection(title, expected):
    assert detect_category(title, []) == expected


@pytest.mark.parametrize(
    "ingredient,expected",
    [
        ("rijst", "rice"),
        ("zilvervliesrijst", "rice"),
        ("volkorenpasta", "pasta"),
        ("woknoedels", "noodle"),
        ("tortillas", "wrap"),
        ("currypasta", "curry"),
        ("soepgroenten", "other"),
        ("rijstazijn", "other"),
        ("currykruiden", "other"),
        ("pizzabodem", "other"),
        ("tomatenpasta", "other"),
    ],
)
def test_ingredient_detection_avoids_compounds(ingredient, expected):
    assert detect_category("Kip", [{"name": ingredient}]) == expected


def test_compound_traps_stay_other():
    assert detect_category("Rijstazijn kip", []) == "other"
    assert detect_category("Currykruiden kip", []) == "other"
    assert detect_category("Pizzabodem", []) == "other"


def test_compound_trap_does_not_beat_real_dish():
    assert detect_category("Soepgroenten met pasta", []) == "pasta"


def test_title_beats_single_ingredient_hint():
    assert detect_category("Kippensoep", [{"name": "pasta"}]) == "soup"


def test_phrase_beats_single_word():
    assert detect_category("Pasta salade", []) == "salad"


def test_ingredient_cap_does_not_beat_title():
    ingredients = [{"name": "pasta"} for _ in range(10)]
    assert detect_category("Kippensoep", ingredients) == "soup"


def test_unknown_recipe_is_other():
    assert detect_category("Geheim familierecept", [{"name": "liefde"}]) == "other"


def test_accepts_ingredient_objects():
    assert detect_category("Kip", [Ingredient(name="rijst")]) == "rice"
