from datetime import datetime
from pathlib import Path

import fitz
import re
from unicodedata import normalize
from services.search_index import build_search_index
from core.helpers import slugify

from models.models import Recipe
from services.image_extractor import ImageExtractor
from utils.logger import logger


CATEGORY_RULES = {
    "wrap": ["wrap", "tortilla"],
    "rice": ["rijst", "risotto", "paella"],
    "noodle": ["noedel", "woknoedel", "udon", "ramen"],
    "pasta": ["pasta", "penne", "spaghetti", "fusilli", "tagliatelle", "linguine", "lasagne"],
    "salad": ["salade"],
    "soup": ["soep"],
    "curry": ["curry"],
    "burger": ["burger"],
    "pizza": ["pizza"]
}

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

def detect_category(title: str, ingredients):
    text = (title + " " + " ".join(i["name"] for i in ingredients)).lower()

    for category, keywords in CATEGORY_RULES.items():
        if any(k in text for k in keywords):
            return category

    return "other"


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