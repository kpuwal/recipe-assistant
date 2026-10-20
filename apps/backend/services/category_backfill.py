from dataclasses import dataclass
from typing import Iterable, List, Optional

from models.models import Recipe
from core.taxonomy import DEFAULT_CATEGORY, is_known_category, normalize_category
from services.pdf_parser import detect_category
from utils.logger import logger


CONFLICT_KIND = "conflict"
SAFE_KINDS = {"normalize", "uncategorized", "unknown"}


@dataclass(frozen=True)
class CategoryProposal:
    recipe_id: str
    title: str
    source: str
    before: str
    after: str
    kind: str

    @property
    def is_conflict(self) -> bool:
        return self.kind == CONFLICT_KIND

    def to_dict(self) -> dict:
        return {
            "recipe_id": self.recipe_id,
            "title": self.title,
            "source": self.source,
            "before": self.before,
            "after": self.after,
            "kind": self.kind,
            "conflict": self.is_conflict,
        }


def classify_recipe(recipe: Recipe) -> Optional[CategoryProposal]:
    raw = (recipe.category or "").strip()
    detected = detect_category(recipe.title, recipe.ingredients)

    def proposal(after: str, kind: str) -> CategoryProposal:
        return CategoryProposal(
            recipe_id=recipe.id or "",
            title=recipe.title,
            source=recipe.source or "",
            before=raw,
            after=after,
            kind=kind,
        )

    if is_known_category(raw):
        if raw == detected:
            return None
        if raw == DEFAULT_CATEGORY:
            return proposal(detected, "uncategorized")
        return proposal(detected, CONFLICT_KIND)

    normalized = normalize_category(raw)
    if normalized:
        if normalized == DEFAULT_CATEGORY and detected != DEFAULT_CATEGORY:
            return proposal(detected, "uncategorized")
        return proposal(normalized, "normalize")

    if not raw and detected == DEFAULT_CATEGORY:
        return None

    return proposal(detected, "unknown")


def build_proposals(recipes: Iterable[Recipe]) -> List[CategoryProposal]:
    proposals = []

    for recipe in recipes:
        proposal = classify_recipe(recipe)
        if proposal:
            proposals.append(proposal)

    proposals.sort(key=lambda proposal: (proposal.is_conflict, proposal.recipe_id))
    return proposals


def apply_proposals(
    proposals: Iterable[CategoryProposal],
    recipes_by_id: dict,
    repository,
    include_conflicts: bool = False,
    conflict_ids: Optional[set] = None,
) -> tuple[int, List[dict]]:
    applied = 0
    failures = []

    for proposal in proposals:
        if proposal.is_conflict:
            allowed = include_conflicts or (
                conflict_ids is not None and proposal.recipe_id in conflict_ids
            )
            if not allowed:
                continue

        recipe = recipes_by_id.get(proposal.recipe_id)
        if recipe is None:
            failures.append({
                "recipe_id": proposal.recipe_id,
                "error": "Recipe not found in loaded set",
            })
            continue

        recipe.category = proposal.after

        try:
            repository.save(recipe)
        except Exception as error:
            logger.error(
                "Failed to save category for %s: %s",
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
