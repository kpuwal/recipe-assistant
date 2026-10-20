import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv(BACKEND_DIR / ".env")

def resolve_credentials(raw_path: str) -> str | None:
    path = Path(raw_path)
    if path.is_file():
        return str(path)

    if not path.is_absolute():
        candidate = (BACKEND_DIR / path).resolve()
        if candidate.is_file():
            return str(candidate)

    # .env may contain the container path (e.g. /app/keys/key.json).
    for base in (BACKEND_DIR, *BACKEND_DIR.parents):
        candidate = base / "keys" / path.name
        if candidate.is_file():
            return str(candidate)

    return None


credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials:
    resolved = resolve_credentials(credentials)
    if resolved:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = resolved

from core.settings import settings
from repositories.recipe_repository import RecipeRepository
from services.category_backfill import apply_proposals, build_proposals
from storage.gcs_storage import GCSStorage
from utils.logger import logger


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Re-detect recipe categories and optionally write them to GCS. "
            "Dry-run by default."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write safe changes (normalize, uncategorized, unknown).",
    )
    parser.add_argument(
        "--apply-conflicts",
        action="store_true",
        help=(
            "Also write conflicts (existing valid categories that differ "
            "from detection). Implies --apply."
        ),
    )
    parser.add_argument(
        "--apply-ids",
        help=(
            "Comma-separated recipe IDs whose conflicts should be applied. "
            "Safe changes are applied too."
        ),
    )
    parser.add_argument(
        "--source",
        choices=["imported", "ai", "personal"],
        help="Only process recipes from this source.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Only process the first N recipes.",
    )
    parser.add_argument(
        "--bucket",
        help="Override GCS bucket name (defaults to GCS_BUCKET_NAME).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Write a JSON report to this path.",
    )
    return parser.parse_args()


def print_summary(
    recipes_count,
    proposals,
    counts,
    include_conflicts,
    apply_changes,
    selected_conflicts=0,
):
    safe_count = sum(count for kind, count in counts.items() if kind != "conflict")
    conflict_count = counts.get("conflict", 0)

    print(f"Loaded {recipes_count} recipes")
    print(f"Proposals: {len(proposals)} (safe={safe_count}, conflicts={conflict_count})")

    for kind in ("normalize", "uncategorized", "unknown", "conflict"):
        if counts.get(kind):
            print(f"  {kind:12} {counts[kind]}")

    if not proposals:
        print("Nothing to change.")
        return

    print()
    for proposal in proposals:
        marker = "review" if proposal.is_conflict else "safe"
        print(
            f"[{marker:6}] {proposal.recipe_id:8} | "
            f"{proposal.title[:40]:40} | "
            f"{proposal.before!r} -> {proposal.after!r} ({proposal.kind})"
        )

    print()
    if not apply_changes:
        print("Dry run: no recipes were written.")
        print("Re-run with --apply to write safe changes.")
        print("Add --apply-conflicts after reviewing conflicts.")
    elif not include_conflicts and conflict_count > selected_conflicts:
        remaining = conflict_count - selected_conflicts
        print(f"Skipped {remaining} conflicts (use --apply-conflicts).")


def write_report(path, bucket, dry_run, include_conflicts, recipes_count, proposals,
                 applied, failures, apply_ids=()):
    counts = Counter(proposal.kind for proposal in proposals)
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "bucket": bucket,
        "dry_run": dry_run,
        "include_conflicts": include_conflicts,
        "apply_ids": sorted(apply_ids),
        "total_recipes": recipes_count,
        "counts": dict(counts),
        "applied": applied,
        "failures": failures,
        "proposals": [proposal.to_dict() for proposal in proposals],
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Report written to {path}")


def main():
    args = parse_args()
    conflict_ids = {
        item.strip()
        for item in (args.apply_ids or "").split(",")
        if item.strip()
    }
    apply_changes = args.apply or args.apply_conflicts or bool(conflict_ids)
    include_conflicts = args.apply_conflicts

    bucket = args.bucket or settings.gcs_bucket_name
    repository = RecipeRepository(storage=GCSStorage(bucket_name=bucket))

    recipes = repository.list()
    if args.source:
        recipes = [recipe for recipe in recipes if recipe.source == args.source]
    if args.limit is not None:
        recipes = recipes[: args.limit]

    proposals = build_proposals(recipes)
    counts = Counter(proposal.kind for proposal in proposals)

    conflict_recipe_ids = {
        proposal.recipe_id for proposal in proposals if proposal.is_conflict
    }
    unknown_ids = conflict_ids - conflict_recipe_ids
    if unknown_ids:
        print(
            "Unknown or non-conflicting recipe IDs: "
            + ", ".join(sorted(unknown_ids))
        )
        return 2

    print_summary(
        len(recipes),
        proposals,
        counts,
        include_conflicts,
        apply_changes,
        selected_conflicts=len(conflict_ids),
    )

    applied = 0
    failures = []

    if apply_changes:
        recipes_by_id = {recipe.id: recipe for recipe in recipes}
        applied, failures = apply_proposals(
            proposals,
            recipes_by_id,
            repository,
            include_conflicts=include_conflicts,
            conflict_ids=conflict_ids,
        )
        print(f"Applied {applied} changes, {len(failures)} failures.")

    if args.report:
        write_report(
            args.report,
            bucket,
            not apply_changes,
            include_conflicts,
            len(recipes),
            proposals,
            applied,
            failures,
            apply_ids=conflict_ids,
        )

    if failures:
        for failure in failures:
            logger.error("Failed: %s", failure)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
