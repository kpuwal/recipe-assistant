import pytest

from core.taxonomy import (
    CATEGORIES,
    CATEGORY_ALIASES,
    CATEGORY_EMOJI,
    CATEGORY_LABELS,
    DEFAULT_CATEGORY,
    category_choices,
    category_terms,
    is_known_category,
    normalize_category,
    normalize_term,
)


def test_taxonomy_is_complete_and_ordered():
    assert CATEGORIES[-1] == DEFAULT_CATEGORY
    assert set(CATEGORY_LABELS) == set(CATEGORIES)
    assert set(CATEGORY_EMOJI) == set(CATEGORIES)
    assert set(CATEGORY_ALIASES) == set(CATEGORIES)


def test_every_slug_label_and_alias_resolves_to_its_category():
    for category in CATEGORIES:
        assert normalize_category(category) == category
        assert normalize_category(CATEGORY_LABELS[category]) == category
        for alias in CATEGORY_ALIASES[category]:
            assert normalize_category(alias) == category


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Rijst", "rice"),
        ("RIJST", "rice"),
        ("  Rijst!  ", "rice"),
        ("Noedels", "noodle"),
        ("Noodles", "noodle"),
        ("Salade", "salad"),
        ("SOEP", "soup"),
        ("kerrie", "curry"),
        ("Nasi Goreng", "rice"),
        ("Mac and Cheese", "pasta"),
        ("Niçoise", "salad"),
        ("calzone", "pizza"),
    ],
)
def test_normalize_category_accepts_labels_and_aliases(value, expected):
    assert normalize_category(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "soepgroenten",
        "rijstazijn",
        "currykruiden",
        "pizzabodem",
        "burger bowl",
        "hoofdgerecht",
    ],
)
def test_compound_or_unknown_values_are_not_categories(value):
    assert normalize_category(value) is None


def test_unknown_values_can_fall_back_to_default():
    assert normalize_category("onbekend", default=DEFAULT_CATEGORY) == "other"
    assert normalize_category(None, default=DEFAULT_CATEGORY) == "other"
    assert normalize_category("", default=DEFAULT_CATEGORY) == "other"


def test_normalize_term_strips_diacritics_and_punctuation():
    assert normalize_term("Crème Brûlée") == "creme brulee"
    assert normalize_term("  Pasta!! ") == "pasta"


def test_is_known_category_checks_slugs_only():
    assert is_known_category("rice") is True
    assert is_known_category("Rijst") is False
    assert is_known_category(None) is False


def test_category_terms_include_search_synonyms():
    terms = category_terms("rice")
    assert "rice" in terms
    assert "rijst" in terms
    assert "risotto" in terms
    assert category_terms("onbekend") == ()


def test_category_choices_matches_categories():
    choices = category_choices()
    assert [choice["value"] for choice in choices] == list(CATEGORIES)
    assert choices[0] == {"value": "pasta", "label": "Pasta", "emoji": "🍝"}
