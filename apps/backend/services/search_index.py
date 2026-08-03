import re
from collections import defaultdict
from typing import List, Optional, Dict, Set

from models.models import Recipe


def normalize(text: str) -> str:
    if not text:
        return ""
    return text.lower().replace("-", " ")


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower())


class SearchIndex:
    def __init__(self):
        self.title_index: Dict[str, List[str]] = defaultdict(list)
        self.category_index: Dict[str, List[str]] = defaultdict(list)
        self.ingredient_index: Dict[str, List[str]] = defaultdict(list)
        self.token_index: Dict[str, List[str]] = defaultdict(list)

    def index(self, recipe: Recipe) -> None:
        for word in tokenize(recipe.title):
            self.title_index[word].append(recipe.id)

        category = getattr(recipe, "category", "") or ""
        for word in tokenize(category):
            self.category_index[word].append(recipe.id)

        ingredient_words: Set[str] = set()
        for ingredient in recipe.ingredients:
            for word in tokenize(ingredient.name):
                ingredient_words.add(word)
        for word in ingredient_words:
            self.ingredient_index[word].append(recipe.id)

        for token in getattr(recipe, "tokens", []) or []:
            self.token_index[token.lower()].append(recipe.id)

    def lookup(self, word: str):
        word = word.lower()
        return {
            "title": self.title_index.get(word, []),
            "category": self.category_index.get(word, []),
            "ingredient": self.ingredient_index.get(word, []),
            "token": self.token_index.get(word, []),
        }


class SearchIndexBuilder:
    def build(self, recipes: List[Recipe]) -> SearchIndex:
        index = SearchIndex()
        for recipe in recipes:
            index.index(recipe)
        return index


def build_search_index(recipe: Recipe) -> Recipe:
    ingredient_text = " ".join(
        ingredient.name for ingredient in recipe.ingredients
    )

    recipe.search_text = normalize(
        " ".join(
            [
                recipe.title,
                recipe.category or "",
                ingredient_text,
                " ".join(recipe.steps),
                recipe.tips or "",
            ]
        )
    )

    recipe.tokens = tokenize(recipe.search_text)

    return recipe
