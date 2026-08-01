import re

from models.models import Recipe


def normalize(text: str) -> str:
    if not text:
        return ""

    return text.lower().replace("-", " ")


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower())


def build_search_index(recipe: Recipe) -> Recipe:
    ingredient_text = " ".join(
        ingredient.name for ingredient in recipe.ingredients
    )

    recipe.search_text = normalize(
        " ".join([
            recipe.title,
            recipe.category or "",
            ingredient_text,
            " ".join(recipe.steps),
            recipe.tips or "",
        ])
    )

    recipe.tokens = tokenize(recipe.search_text)

    return recipe