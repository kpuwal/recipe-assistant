from datetime import datetime
from pathlib import Path

import pymupdf as fitz
import re
from unicodedata import normalize
from services.search_index import build_search_index
from core.helpers import slugify
from core.taxonomy import (
    CATEGORIES,
    CATEGORY_ALIASES,
    CATEGORY_LABELS,
    DEFAULT_CATEGORY,
    contains_term,
    normalize_term,
)

from models.models import Recipe
from services.image_extractor import ImageExtractor
from utils.logger import logger


TITLE_EXACT_SCORE = 3
TITLE_PHRASE_BONUS = 2
TITLE_COMPOUND_SCORE = 1
INGREDIENT_SCORE = 1
MAX_INGREDIENT_SCORE = 3
MIN_COMPOUND_LENGTH = 4

STOP_LINES = [
    "Wat vond je", "Bereidingswijze niet meer", "Meld je dan hier af",
    "Charlotte", "Klantenservice", "Actievoorwaarden", "Mijn profiel",
    "Elke dag van", "Vragen?", "Fijne dag"
]


def clean_line(text: str) -> str:
    text = normalize("NFKC", text)
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()

def extract_text(pdf: fitz.Document) -> str:
    return "\n".join(page.get_text() for page in pdf)


def looks_like_quantity(line: str) -> bool:
    return bool(
        re.match(r"^\d+(?:[.,]\d+)?\s*(g|kg|ml|l|el|tl|stuk|stuks)?$", line.strip(), re.I)
    )

def build_ingredients(lines):
    ingredients = []
    i = 0

    while i < len(lines):
        current = lines[i].strip()
        if not current:
            i += 1
            continue

        if (i + 1 < len(lines) and looks_like_quantity(lines[i + 1])):
            ingredients.append({"name": current, "quantity": lines[i + 1]})
            i += 2
            continue

        if looks_like_quantity(current):
            if i + 1 < len(lines):
                ingredients.append({"name": lines[i + 1], "quantity": current})
                i += 2
                continue

        ingredients.append({"name": current, "quantity": None})
        i += 1
    return ingredients

def _category_terms(category: str) -> set[str]:
    terms = (
        *CATEGORY_ALIASES[category],
        category,
        CATEGORY_LABELS[category],
    )
    return {term for term in (normalize_term(value) for value in terms) if term}


def _title_match_score(term: str, title: str, title_tokens: list[str]) -> int:
    if " " in term:
        if contains_term(title, term):
            return TITLE_EXACT_SCORE + TITLE_PHRASE_BONUS
        return 0

    if term in title_tokens:
        return TITLE_EXACT_SCORE

    if len(term) >= MIN_COMPOUND_LENGTH:
        if f"{term}s" in title_tokens:
            return TITLE_EXACT_SCORE
        if any(token.endswith(term) for token in title_tokens):
            return TITLE_COMPOUND_SCORE

    return 0


def _ingredient_matches(term: str, ingredient: str) -> bool:
    if not ingredient:
        return False

    if " " in term:
        return contains_term(ingredient, term)

    tokens = ingredient.split()
    if term in tokens:
        return True

    return len(term) >= MIN_COMPOUND_LENGTH and f"{term}s" in tokens


def _ingredient_name(ingredient) -> str:
    if isinstance(ingredient, dict):
        return normalize_term(ingredient.get("name") or "")
    return normalize_term(getattr(ingredient, "name", "") or "")


def detect_category(title: str, ingredients) -> str:
    title_text = normalize_term(title)
    title_tokens = title_text.split()
    ingredient_names = [
        _ingredient_name(ingredient) for ingredient in (ingredients or [])
    ]

    candidates = []

    for category in CATEGORIES:
        if category == DEFAULT_CATEGORY:
            continue

        terms = _category_terms(category)
        title_hits = 0
        score = 0

        for term in terms:
            term_score = _title_match_score(term, title_text, title_tokens)
            if term_score:
                title_hits += 1
                score += term_score

        ingredient_hits = sum(
            1
            for name in ingredient_names
            if any(_ingredient_matches(term, name) for term in terms)
        )
        score += min(ingredient_hits, MAX_INGREDIENT_SCORE) * INGREDIENT_SCORE

        candidates.append((category, title_hits, score))

    title_candidates = [candidate for candidate in candidates if candidate[1] > 0]
    pool = title_candidates or candidates

    category, _, score = max(pool, key=lambda candidate: (candidate[2], candidate[1]))

    return category if score > 0 else DEFAULT_CATEGORY


def parse_pdf_bytes(
    pdf_bytes: bytes,
    recipe_id: str,
) -> Recipe:

    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    image_data = ImageExtractor.extract_main_image(pdf, recipe_id)

    raw_text = extract_text(pdf)
    lines = [clean_line(l) for l in raw_text.splitlines() if clean_line(l)]

    title = None
    persons = None
    time_minutes = None

    ingredient_lines = []
    steps = []
    tips = []

    state = "search"
    current_step = []

    for line in lines:
        if line.startswith("Recept:"):
            title = line.replace("Recept:", "").strip()
            continue

        meta = re.search(r"(\d+)\s+personen.*?(\d+)\s+minuten", line, re.I)
        if meta:
            persons = int(meta.group(1))
            time_minutes = int(meta.group(2))
            continue

        if any(stop in line for stop in STOP_LINES):
            state = "finished"
            continue

        if "Ingrediënten" in line:
            state = "ingredients"
            continue

        if "Zo maak je het!" in line:
            state = "steps"
            continue

        if line in ["Tip", "Tip:"]:
            if current_step:
                steps.append(" ".join(current_step))
                current_step = []
            state = "tip"
            continue

        if state == "ingredients":
            ingredient_lines.append(line)
            continue

        if state == "steps":
            if re.match(r"Stap\s+\d+", line, re.I):
                if current_step:
                    steps.append(" ".join(current_step))
                current_step = []
                continue
            current_step.append(line)

        if state == "tip":
            tips.append(line)

    if current_step:
        steps.append(" ".join(current_step))

    ingredients = build_ingredients(ingredient_lines)

    if not title:
        title = recipe_id

    category = detect_category(title, ingredients)

    recipe = Recipe(
        id=recipe_id,
        slug=slugify(title),
        title=title,
        category=category,
        persons=persons,
        time_minutes=time_minutes,
        ingredients=ingredients,
        steps=steps,
        tips="\n".join(tips),
        image=image_data["filename"] if image_data else None,
        image_bytes=image_data["bytes"] if image_data else None,
        image_extension=image_data["extension"] if image_data else None,
        source="picnic",
        processed_at=datetime.now().isoformat()
    )

    build_search_index(recipe)

    logger.info("Parsed recipe: %s (image=%s)", title, bool(image_data))
    return recipe