import re
from models.models import Recipe


def normalize(text: str) -> str:
    if not text:
        return ""
    return text.lower().replace("-", " ")


def tokenize(text: str):
    return re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower())


def build_search_index(recipe: Recipe) -> Recipe:
    recipe._title_text = normalize(getattr(recipe, 'title', ''))
    recipe._ingredient_text = normalize(
        " ".join(i.name for i in getattr(recipe, 'ingredients', []))
    )
    recipe._category_text = normalize(getattr(recipe, 'category', ''))

    recipe.search_text = normalize(
        " ".join([
            getattr(recipe, 'title', ''),
            getattr(recipe, 'category', ''),
            " ".join(i.name for i in getattr(recipe, 'ingredients', [])),
            " ".join(getattr(recipe, 'steps', [])),
            getattr(recipe, 'tips', '') or ""
        ])
    )

    # if not hasattr(recipe, '_tokens'):
    #     recipe._tokens = set()

    recipe.tokens = list(tokenize(recipe.search_text))

    return recipe
