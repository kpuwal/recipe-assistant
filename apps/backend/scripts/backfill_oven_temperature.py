import argparse
import json
import os
import sys
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
from services.oven_backfill import apply_oven_proposals, build_oven_proposals
from storage.gcs_storage import GCSStorage
from utils.logger import logger


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Extract oven temperature/mode from existing recipe steps and "
            "optionally write them to GCS. Only fills empty values. "
            "Dry-run by default."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write detected oven settings.",
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


def write_report(path, bucket, dry_run, recipes_count, proposals, applied,
                 failures):
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "bucket": bucket,
        "dry_run": dry_run,
        "total_recipes": recipes_count,
        "proposals": [proposal.to_dict() for proposal in proposals],
        "applied": applied,
        "failures": failures,
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Report written to {path}")


def main():
    args = parse_args()

    bucket = args.bucket or settings.gcs_bucket_name
    repository = RecipeRepository(storage=GCSStorage(bucket_name=bucket))

    recipes = repository.list()
    if args.source:
        recipes = [recipe for recipe in recipes if recipe.source == args.source]
    if args.limit is not None:
        recipes = recipes[: args.limit]

    proposals = build_oven_proposals(recipes)

    print(f"Loaded {len(recipes)} recipes")
    print(f"Detected oven settings for {len(proposals)} recipes")

    for proposal in proposals:
        mode = proposal.mode or "default"
        print(
            f"[fill] {proposal.recipe_id:8} | "
            f"{proposal.title[:40]:40} | "
            f"{proposal.temperature} °C ({mode})"
        )

    applied = 0
    failures = []

    if not args.apply:
        print("Dry run: no recipes were written.")
        print("Re-run with --apply to write oven settings.")
    else:
        recipes_by_id = {recipe.id: recipe for recipe in recipes}
        applied, failures = apply_oven_proposals(
            proposals,
            recipes_by_id,
            repository,
        )
        print(f"Applied {applied} changes, {len(failures)} failures.")

    if args.report:
        write_report(
            args.report,
            bucket,
            not args.apply,
            len(recipes),
            proposals,
            applied,
            failures,
        )

    if failures:
        for failure in failures:
            logger.error("Failed: %s", failure)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
