import re
from typing import Optional
from unicodedata import combining, normalize

DEFAULT_CATEGORY = "other"

CATEGORIES = (
    "pasta",
    "rice",
    "noodle",
    "wrap",
    "salad",
    "soup",
    "curry",
    "burger",
    "pizza",
    "other",
)

CATEGORY_LABELS = {
    "pasta": "Pasta",
    "rice": "Rijst",
    "noodle": "Noedels",
    "wrap": "Wrap",
    "salad": "Salade",
    "soup": "Soep",
    "curry": "Curry",
    "burger": "Burger",
    "pizza": "Pizza",
    "other": "Overig",
}

CATEGORY_EMOJI = {
    "pasta": "🍝",
    "rice": "🍚",
    "noodle": "🍜",
    "wrap": "🌯",
    "salad": "🥗",
    "soup": "🥣",
    "curry": "🍛",
    "burger": "🍔",
    "pizza": "🍕",
    "other": "🍽️",
}

CATEGORY_ALIASES = {
    "pasta": (
        "pasta",
        "penne",
        "spaghetti",
        "fusilli",
        "tagliatelle",
        "linguine",
        "lasagne",
        "lasagna",
        "macaroni",
        "rigatoni",
        "tortellini",
        "ravioli",
        "gnocchi",
        "cannelloni",
        "farfalle",
        "orecchiette",
        "carbonara",
        "bolognese",
        "puttanesca",
        "arrabbiata",
        "alfredo",
        "mac and cheese",
        "volkorenpasta",
        "speltpasta",
        "tarwepasta",
    ),
    "rice": (
        "rijst",
        "rice",
        "risotto",
        "paella",
        "nasi",
        "nasi goreng",
        "biryani",
        "pilav",
        "pilaf",
        "sushi",
        "onigiri",
        "fried rice",
        "sticky rice",
        "basmati",
        "jasmine rice",
        "zilvervliesrijst",
        "basmatirijst",
        "sushirijst",
        "jasmijnrijst",
        "pandanrijst",
    ),
    "noodle": (
        "noedel",
        "noedels",
        "noodle",
        "noodles",
        "udon",
        "ramen",
        "bami",
        "bami goreng",
        "mie",
        "mie goreng",
        "vermicelli",
        "soba",
        "rice noodles",
        "glass noodles",
        "woknoedel",
        "woknoedels",
        "instant noodles",
        "pho",
        "pad thai",
        "lo mein",
        "chow mein",
        "mihoen",
        "glasnoedels",
        "eiernoedels",
        "rijstnoedels",
    ),
    "wrap": (
        "wrap",
        "wraps",
        "tortilla",
        "burrito",
        "burritos",
        "quesadilla",
        "quesadillas",
        "taco",
        "tacos",
        "enchilada",
        "enchiladas",
        "fajita",
        "fajitas",
        "shawarma",
        "gyros",
    ),
    "salad": (
        "salade",
        "salades",
        "salad",
        "salads",
        "coleslaw",
        "caesar salad",
        "caesar salade",
        "maaltijdsalade",
        "pastasalade",
        "pasta salad",
        "pasta salade",
        "rijstsalade",
        "rijst salade",
        "couscoussalade",
        "couscous salade",
        "quinoa salade",
        "quinoa salad",
        "waldorf",
        "caprese",
        "tabbouleh",
        "tabouleh",
        "griekse salade",
        "greek salad",
        "nicoise",
    ),
    "soup": (
        "soep",
        "soepen",
        "soup",
        "soups",
        "bouillon",
        "tomatensoep",
        "groentesoep",
        "erwtensoep",
        "uienensoep",
        "chowder",
        "bisque",
        "gazpacho",
        "minestrone",
        "consomme",
    ),
    "curry": (
        "curry",
        "curries",
        "kerrie",
        "currypasta",
        "kerriepasta",
        "korma",
        "tikka masala",
        "tikka",
        "dahl",
        "dal",
        "daal",
        "rendang",
        "massaman",
        "green curry",
        "red curry",
        "yellow curry",
        "katsu curry",
        "japanese curry",
    ),
    "burger": (
        "burger",
        "burgers",
        "hamburger",
        "hamburgers",
        "cheeseburger",
        "cheeseburgers",
        "veggieburger",
        "veggieburgers",
        "slider",
        "sliders",
        "smashburger",
    ),
    "pizza": (
        "pizza",
        "pizzas",
        "pizza margherita",
        "margherita",
        "calzone",
        "calzones",
    ),
    "other": (),
}


def normalize_term(value: str) -> str:
    text = normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not combining(char))
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def _build_category_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}

    for category in CATEGORIES:
        terms = (category, CATEGORY_LABELS[category], *CATEGORY_ALIASES[category])
        for term in terms:
            key = normalize_term(term)
            if not key:
                continue
            if key in lookup and lookup[key] != category:
                raise ValueError(
                    f"Category alias '{term}' maps to both "
                    f"'{lookup[key]}' and '{category}'"
                )
            lookup[key] = category

    return lookup


_CATEGORY_LOOKUP = _build_category_lookup()


def normalize_category(value: Optional[str], default: Optional[str] = None) -> Optional[str]:
    key = normalize_term(value)
    if not key:
        return default
    return _CATEGORY_LOOKUP.get(key, default)


def is_known_category(value: Optional[str]) -> bool:
    return value in CATEGORY_LABELS


def contains_term(text: str, term: str) -> bool:
    haystack = normalize_term(text)
    needle = normalize_term(term)
    if not haystack or not needle:
        return False

    pattern = rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])"
    return re.search(pattern, haystack) is not None


def category_terms(value: Optional[str]) -> tuple[str, ...]:
    category = normalize_category(value)
    if not category:
        return ()

    terms = {category, normalize_term(CATEGORY_LABELS[category])}
    terms.update(normalize_term(alias) for alias in CATEGORY_ALIASES[category])
    return tuple(sorted(term for term in terms if term))


def category_choices() -> list[dict[str, str]]:
    return [
        {
            "value": category,
            "label": CATEGORY_LABELS[category],
            "emoji": CATEGORY_EMOJI[category],
        }
        for category in CATEGORIES
    ]
