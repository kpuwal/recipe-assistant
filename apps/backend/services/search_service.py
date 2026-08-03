from typing import List, Optional, Protocol
from difflib import SequenceMatcher
from collections import defaultdict

from models.models import Recipe
from services.search_parser import extract_time_filter
from services.search_index import SearchIndex, normalize, tokenize
from utils.logger import logger


class RecipeServicePort(Protocol):
    def list_recipes(
        self,
        source: Optional[str] = None,
        favorites_only: bool = False,
    ) -> List[Recipe]: ...

    def get_search_index(self) -> Optional[SearchIndex]: ...


class SearchService:
    def __init__(self, recipe_service: RecipeServicePort):
        self.recipe_service = recipe_service

    def search_recipes(
        self,
        query: str = "",
        max_time: Optional[int] = None,
    ) -> List[Recipe]:

        query = query.lower().strip()
        time_filter = extract_time_filter(query)

        if isinstance(max_time, int):
            time_filter = {"type": "max", "value": max_time}

        query_words = self.clean_query(query)

        recipes = self.recipe_service.list_recipes()
        search_index = self.recipe_service.get_search_index()

        if not query_words and not time_filter:
            logger.info("Returning all recipes (%d total)", len(recipes))
            return sorted(recipes, key=lambda r: r.title)

        if not query_words:
            filtered = []
            for recipe in recipes:
                if time_filter:
                    if recipe.time_minutes is None:
                        continue
                    if time_filter["type"] == "max" and recipe.time_minutes > time_filter["value"]:
                        continue
                    elif time_filter["type"] == "min" and recipe.time_minutes < time_filter["value"]:
                        continue
                    elif time_filter["type"] == "exact" and recipe.time_minutes != time_filter["value"]:
                        continue
                    elif time_filter["type"] == "range" and (
                        recipe.time_minutes < time_filter.get("min", 0)
                        or recipe.time_minutes > time_filter.get("max", 9999)
                    ):
                        continue
                filtered.append(recipe)
            logger.info("Time-filtered %d recipes (no query)", len(filtered))
            return sorted(filtered, key=lambda r: r.title)

        recipes_by_id = {r.id: r for r in recipes}

        candidate_ids = set()
        if search_index and isinstance(search_index, SearchIndex):
            for word in query_words:
                hits = search_index.lookup(word)
                for ids in hits.values():
                    candidate_ids.update(ids)

        if not candidate_ids:
            if time_filter:
                filtered = []
                for recipe in recipes:
                    if recipe.time_minutes is None:
                        continue
                    if time_filter["type"] == "max" and recipe.time_minutes > time_filter["value"]:
                        continue
                    elif time_filter["type"] == "min" and recipe.time_minutes < time_filter["value"]:
                        continue
                    elif time_filter["type"] == "exact" and recipe.time_minutes != time_filter["value"]:
                        continue
                    elif time_filter["type"] == "range" and (
                        recipe.time_minutes < time_filter.get("min", 0)
                        or recipe.time_minutes > time_filter.get("max", 9999)
                    ):
                        continue
                    filtered.append(recipe)
                logger.info("Time-filtered %d recipes (no index hits)", len(filtered))
                return sorted(filtered, key=lambda r: r.title)
            else:
                logger.info("Search for '%s' returned 0 results (no index hits)", query)
                return []

        candidates = [recipes_by_id[rid] for rid in candidate_ids if rid in recipes_by_id]

        recipe_scores: dict = defaultdict(int)
        recipe_matched: dict = defaultdict(int)

        for recipe in candidates:
            if time_filter:
                if recipe.time_minutes is None:
                    continue
                if time_filter["type"] == "max" and recipe.time_minutes > time_filter["value"]:
                    continue
                elif time_filter["type"] == "min" and recipe.time_minutes < time_filter["value"]:
                    continue
                elif time_filter["type"] == "exact" and recipe.time_minutes != time_filter["value"]:
                    continue
                elif time_filter["type"] == "range" and (
                    recipe.time_minutes < time_filter.get("min", 0)
                    or recipe.time_minutes > time_filter.get("max", 9999)
                ):
                    continue

            ing_text = " ".join(i.name for i in recipe.ingredients).lower()
            search_lower = (recipe.search_text or "").lower()
            category_lower = (getattr(recipe, "category", "") or "").lower()
            tokens = getattr(recipe, "tokens", []) or []

            for word in query_words:
                word_matched = False

                if word in search_lower:
                    recipe_scores[recipe.id] += 30
                    word_matched = True
                elif word in ing_text:
                    recipe_scores[recipe.id] += 20
                    word_matched = True
                elif word in category_lower:
                    recipe_scores[recipe.id] += 40
                    word_matched = True
                elif len(word) >= 4:
                    for token in tokens:
                        if SequenceMatcher(None, word.lower(), token.lower()).ratio() >= 0.85:
                            recipe_scores[recipe.id] += 2
                            word_matched = True
                            break

                if word_matched:
                    recipe_matched[recipe.id] += 1

        results = []
        for recipe in candidates:
            if recipe.id not in recipe_scores:
                continue
            match_ratio = recipe_matched[recipe.id] / len(query_words)
            if match_ratio >= 0.7:
                results.append((recipe, recipe_scores[recipe.id]))

        results.sort(
            key=lambda x: (
                -x[1],
                x[0].time_minutes or 999,
                x[0].title,
            )
        )

        logger.info("Search for '%s' returned %d results", query, len(results))
        return [recipe for recipe, _ in results]

    def clean_query(self, text: str) -> List[str]:
        stop_words = {
            "de", "het", "een", "en", "van", "met", "voor", "in", "op", "is",
            "om", "te", "ook", "er", "als", "a", "an", "the", "and", "or", "for",
            "with", "of", "to", "recept", "recepten",
            "min", "minuten", "minute",
        }

        words = tokenize(text)

        return [
            word for word in words
            if word not in stop_words and not word.isdigit()
        ]


