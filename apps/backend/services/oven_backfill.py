from dataclasses import dataclass
from typing import Iterable, List, Optional

from models.models import Recipe
from services.oven import extract_oven_settings
from utils.logger import logger


@dataclass(frozen=True)
class OvenProposal:
    recipe_id: str
    title: str
    source: str
    temperature: int
    mode: Optional[str]

    def to_dict(self) -> dict:
        return {
            "recipe_id": self.recipe_id,
            "title": self.title,
            "source": self.source,
            "oven_temperature": self.temperature,
            "oven_mode": self.mode,
        }


def recipe_text(recipe: Recipe) -> str:
    parts = list(recipe.steps or [])
    if recipe.tips:
        parts.append(recipe.tips)
    return "\n".join(parts)


def build_oven_proposals(recipes: Iterable[Recipe]) -> List[OvenProposal]:
    proposals = []

    for recipe in recipes:
        if recipe.oven_temperature is not None:
            continue

        temperature, mode = extract_oven_settings(recipe_text(recipe))
        if temperature is None:
            continue

        proposals.append(
            OvenProposal(
                recipe_id=recipe.id or "",
                title=recipe.title,
                source=recipe.source or "",
                temperature=temperature,
                mode=mode,
            )
        )

    proposals.sort(key=lambda proposal: proposal.recipe_id)
    return proposals


def apply_oven_proposals(
    proposals: Iterable[OvenProposal],
    recipes_by_id: dict,
    repository,
) -> tuple[int, List[dict]]:
    applied = 0
    failures = []

    for proposal in proposals:
        recipe = recipes_by_id.get(proposal.recipe_id)
        if recipe is None:
            failures.append({
                "recipe_id": proposal.recipe_id,
                "error": "Recipe not found in loaded set",
            })
            continue

        recipe.oven_temperature = proposal.temperature
        if proposal.mode is not None:
            recipe.oven_mode = proposal.mode

        try:
            repository.save(recipe)
        except Exception as error:
            logger.error(
                "Failed to save oven settings for %s: %s",
                proposal.recipe_id,
                error,
            )
            failures.append({
                "recipe_id": proposal.recipe_id,
                "error": str(error),
            })
            continue

        applied += 1

    return applied, failures
