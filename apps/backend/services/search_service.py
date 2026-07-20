import re
from typing import List, Optional
from difflib import SequenceMatcher

from models.models import Recipe
from services.search_parser import extract_time_filter
from services.recipe_service import RecipeService
from utils.logger import logger


class SearchService:
    def __init__(self, recipe_service: RecipeService):
        self.recipe_service = recipe_service

    def search_recipes(
        self,
        query: str = "",
        max_time: Optional[int] = None
    ) -> List[Recipe]:

        query = query.lower().strip()
        time_filter = extract_time_filter(query)

        if isinstance(max_time, int):
            time_filter = {"type": "max", "value": max_time}

        query_words = self.clean_query(query)

        if not query_words and not time_filter:
            recipes = self.recipe_service.list_recipes()
            logger.info("Returning all recipes (%d total)", len(recipes))
            return sorted(recipes, key=lambda r: r.title)

        results = []
        recipes = self.recipe_service.list_recipes()
        logger.info("Searching %d recipes for query: '%s'", len(recipes), query)

        for recipe in recipes:
            # TIME FILTERS
            if time_filter and recipe.time_minutes:
                if time_filter["type"] == "max" and recipe.time_minutes > time_filter["value"]:
                    continue
                elif time_filter["type"] == "min" and recipe.time_minutes < time_filter["value"]:
                    continue
                elif time_filter["type"] == "exact" and recipe.time_minutes != time_filter["value"]:
                    continue
                elif time_filter["type"] == "range":
                    if (recipe.time_minutes < time_filter.get("min") or 
                        recipe.time_minutes > time_filter.get("max")):
                        continue

            if not query_words:
                results.append((recipe, 0))
                continue

            score = 0
            matched_words = 0

            for word in query_words:
                word_matched = False

                # Use public fields
                if word in (recipe.search_text or ""):
                    score += 30
                    word_matched = True
                elif word in (getattr(recipe, 'ingredient', '') or ""):
                    score += 20
                    word_matched = True
                elif word in (getattr(recipe, 'category', '') or ""):
                    score += 40
                    word_matched = True

                # Typo tolerance using tokens
                if not word_matched and hasattr(recipe, 'tokens'):
                    for token in recipe.tokens:
                        similarity = SequenceMatcher(None, word, token).ratio()
                        if similarity >= 0.85:
                            score += 2
                            word_matched = True
                            break

                if word_matched:
                    matched_words += 1

            match_ratio = matched_words / len(query_words) if query_words else 0

            if match_ratio >= 0.7:
                results.append((recipe, score))

        results.sort(
            key=lambda x: (
                -x[1],
                x[0].time_minutes or 999,
                x[0].title
            )
        )

        logger.info("Search for '%s' returned %d results", query, len(results))

        return [recipe for recipe, score in results]

    # clean_query, tokenize, normalize remain the same
    def clean_query(self, text: str) -> List[str]:
        stop_words = { ... }  # your stop words

        words = self.tokenize(text)

        return [
            word for word in words
            if word not in stop_words and not word.isdigit()
        ]

    def tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower())

    def normalize(self, text: str) -> str:
        return text.lower().replace("-", " ")