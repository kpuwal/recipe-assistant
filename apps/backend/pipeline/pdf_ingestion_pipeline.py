from pathlib import Path

from utils.logger import logger
from services.pdf_parser import parse_pdf_bytes


class PDFIngestionPipeline:

    def __init__(self, source, repository, state):
        self.source = source
        self.repository = repository
        self.state = state

    def _process_file(self, file, index: int, dry_run: bool = False):
        file_hash = file.content_hash
        existing_recipe_id = self.state.get_recipe_id(file.path_lower)

        if self.state.get_hash(file.path_lower) == file_hash:
            logger.info("Skipped unchanged file: %s", file.name)
            return "skipped"

        filename, pdf_bytes = self.source.get_pdf_bytes(file.path_lower)

        if existing_recipe_id:
            recipe_id = existing_recipe_id
        else:
            recipe_id = self.repository.generate_id("imported")

        try:
            recipe = parse_pdf_bytes(pdf_bytes=pdf_bytes, recipe_id=recipe_id)

            if not dry_run:
                self.repository.save(recipe)
                self.state.update(file.path_lower, file_hash, recipe.id)

            logger.info("Processed: %s -> %s", filename, recipe.title)
            return recipe

        except Exception as e:
            logger.error("Failed to process %s: %s", filename, e)
            raise

    def run(self, dry_run: bool = False):
        logger.info("Starting ingestion (dry_run=%s)", dry_run)

        events = []
        processed = []
        skipped = []
        failed = []

        files = self.source.list_pdfs()
        logger.info("Found %d PDFs", len(files))
        events.append({"type": "start", "total_files": len(files)})

        for file in files:
            try:
                result = self._process_file(file, len(processed) + 1, dry_run=dry_run)

                if result == "skipped":
                    skipped.append(file.path_lower)
                    events.append({"type": "skip", "file": file.path_lower})
                    continue

                if result:
                    processed.append(result)
                    events.append({
                        "type": "success",
                        "file": file.path_lower,
                        "recipe_id": result.id,
                        "title": result.title
                    })

            except Exception as e:
                logger.error("Failed file %s: %s", file.path_lower, e)
                events.append({
                    "type": "error",
                    "file": file.path_lower,
                    "error": str(e)
                })
                failed.append({
                    "file": file.path_lower,
                    "error": str(e),
                })

        if not dry_run:
            self.state.save()

        events.append({
            "type": "done",
            "processed": len(processed),
            "skipped": len(skipped),
            "failed": len(failed),
        })

        logger.info("Ingestion completed - Processed: %d, Skipped: %d, Failed: %d",
                    len(processed), len(skipped), len(failed))

        return {
            "status": "success",
            "summary": {
                "total": len(files),
                "processed": len(processed),
                "skipped": len(skipped),
                "failed": len(failed),
            },
            "processed_files": [
                {"id": r.id, "title": r.title}
                for r in processed
            ],
            "skipped_files": skipped,
            "failed_files": failed,
            "events": events
        }