from typing import List, Optional, Protocol
from difflib import SequenceMatcher

from models.models import Recipe
from core.taxonomy import (
    CATEGORIES,
    CATEGORY_ALIASES,
    DEFAULT_CATEGORY,
    contains_term,
    normalize_category,
    normalize_term,
)
from services.search_parser import extract_time_filter
from services.search_index import SearchIndex, tokenize
from utils.logger import logger


FAVORITES_WORDS = {"favoriet", "favorieten", "favorite", "favorites"}
TIME_WORDS = {"snel", "snelle", "kort", "korte"}

MULTI_WORD_ALIASES = tuple(
    sorted(
        {
            normalize_term(alias)
            for category in CATEGORIES
            for alias in CATEGORY_ALIASES[category]
            if " " in alias
        },
        key=lambda alias: len(alias.split()),
        reverse=True,
    )
)


class RecipeServicePort(Protocol):
    def list_recipes(
        self,
        source: Optional[str] = None,
        favorites_only: bool = False,
        category: Optional[str] = None,
    ) -> List[Recipe]: ...

    def get_search_index(self) -> Optional[SearchIndex]: ...


class SearchService:
    def __init__(self, recipe_service: RecipeServicePort):
        self.recipe_service = recipe_service

    def search_recipes(
        self,
        query: str = "",
        max_time: Optional[int] = None,
        min_time: Optional[int] = None,
        category: Optional[str] = None,
        favorites_only: bool = False,
    ) -> List[Recipe]:
        raw_query = (query or "").strip()

        time_filter = extract_time_filter(raw_query)
        if isinstance(min_time, int) and isinstance(max_time, int):
            time_filter = {"type": "range", "min": min_time, "max": max_time}
        elif isinstance(max_time, int):
            time_filter = {"type": "max", "value": max_time}
        elif isinstance(min_time, int):
            time_filter = {"type": "min", "value": min_time}

        requested_category = None
        if category:
            requested_category = normalize_category(category)
            if not requested_category:
                logger.warning("Unknown category filter: %s", category)
                return []

        terms, query_favorites = self._parse_query(raw_query)
        favorites_only = favorites_only or query_favorites

        recipes = self.recipe_service.list_recipes(favorites_only=favorites_only)

        if requested_category:
            recipes = [
                recipe
                for recipe in recipes
                if self._recipe_category(recipe) == requested_category
            ]

        if not terms:
            filtered = [
                recipe
                for recipe in recipes
                if self._matches_time(recipe, time_filter)
            ]
            logger.info(
                "Returning %d recipes (category=%s, favorites=%s, time_filter=%s)",
                len(filtered),
                requested_category,
                favorites_only,
                time_filter,
            )
            return sorted(filtered, key=lambda recipe: recipe.title)

        results = []
        for recipe in recipes:
            if not self._matches_time(recipe, time_filter):
                continue

            score, matched = self._score_recipe(recipe, terms)
            if matched / len(terms) >= 0.7:
                results.append((recipe, score))

        results.sort(
            key=lambda item: (
                -item[1],
                item[0].time_minutes or 999,
                item[0].title,
            )
        )

        logger.info("Search returned %d results", len(results))
        return [recipe for recipe, _ in results]

    def _parse_query(self, query: str) -> tuple[List[str], bool]:
        words = self.clean_query(query)
        favorites_only = any(word in FAVORITES_WORDS for word in words)

        words = [
            word
            for word in words
            if word not in FAVORITES_WORDS and word not in TIME_WORDS
        ]

        terms = list(words)
        normalized_query = normalize_term(query)

        for alias in MULTI_WORD_ALIASES:
            if not contains_term(normalized_query, alias):
                continue

            alias_words = set(alias.split())
            if not alias_words.intersection(terms):
                continue

            terms = [term for term in terms if term not in alias_words]
            terms.append(alias)

        return list(dict.fromkeys(terms)), favorites_only

    @staticmethod
    def _recipe_category(recipe: Recipe) -> str:
        return normalize_category(
            getattr(recipe, "category", None),
            default=DEFAULT_CATEGORY,
        )

    @staticmethod
    def _matches_time(recipe: Recipe, time_filter) -> bool:
        if not time_filter:
            return True

        if recipe.time_minutes is None:
            return False

        filter_type = time_filter["type"]

        if filter_type == "max":
            return recipe.time_minutes <= time_filter["value"]
        if filter_type == "min":
            return recipe.time_minutes >= time_filter["value"]
        if filter_type == "exact":
            return recipe.time_minutes == time_filter["value"]
        if filter_type == "range":
            return (
                time_filter.get("min", 0)
                <= recipe.time_minutes
                <= time_filter.get("max", 9999)
            )

        return True

    @staticmethod
    def _score_recipe(recipe: Recipe, terms: List[str]) -> tuple[int, int]:
        search_lower = (recipe.search_text or "").lower()
        ingredient_text = " ".join(
            ingredient.name for ingredient in recipe.ingredients
        ).lower()
        recipe_category = SearchService._recipe_category(recipe)
        tokens = getattr(recipe, "tokens", []) or []

        score = 0
        matched = 0

        for term in terms:
            term_category = normalize_category(term)

            if term_category and recipe_category == term_category:
                score += 40
                matched += 1
            elif term in search_lower:
                score += 30
                matched += 1
            elif term in ingredient_text:
                score += 20
                matched += 1
            elif len(term) >= 4:
                for token in tokens:
                    if SequenceMatcher(None, term, token.lower()).ratio() >= 0.85:
                        score += 2
                        matched += 1
                        break

        return score, matched

    def clean_query(self, text: str) -> List[str]:
        stop_words = {
            "de", "het", "een", "en", "van", "met", "voor", "in", "op", "is",
            "om", "te", "ook", "er", "als", "a", "an", "the", "and", "or", "for",
            "with", "of", "to", "recept", "recepten",
            "min", "minuten", "minute",
        }

        words = tokenize(text)

        return [
            word
            for word in words
            if word not in stop_words and not word.isdigit() and len(word) > 1
        ]
