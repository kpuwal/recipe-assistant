from datetime import datetime

from models.models import Recipe, Timer
from pipeline.pdf_ingestion_pipeline import PDFIngestionPipeline


class FakeFile:
    path_lower = "/recipes/foo.pdf"
    name = "foo.pdf"
    content_hash = "new-hash"


class FakeSource:
    def get_pdf_bytes(self, path_lower):
        return "foo.pdf", b"%PDF-1.4"


class FakeRepository:
    def __init__(self, existing=None):
        self.existing = existing
        self.saved = None

    def generate_id(self, source):
        return "r999"

    def get(self, recipe_id):
        return self.existing

    def save(self, recipe):
        self.saved = recipe
        return recipe


class FakeState:
    def __init__(self, recipe_id):
        self.recipe_id = recipe_id

    def get_recipe_id(self, path_lower):
        return self.recipe_id

    def get_hash(self, path_lower):
        return "old-hash"

    def update(self, *args):
        pass


def _pipeline(existing, recipe_id="r043"):
    return PDFIngestionPipeline(
        FakeSource(),
        FakeRepository(existing),
        FakeState(recipe_id),
    )


def test_resync_preserves_user_data(monkeypatch):
    existing = Recipe(
        id="r043",
        title="Old title",
        category="rice",
        is_favorite=True,
        cooked_dates=["2026-10-01"],
        timers=[Timer(id="t1", label="Kook", duration_seconds=600)],
        created_at=datetime(2024, 1, 1),
    )
    parsed = Recipe(
        id="r043",
        title="Foe yong hai",
        category="other",
        is_favorite=False,
        created_at=None,
    )
    monkeypatch.setattr(
        "pipeline.pdf_ingestion_pipeline.parse_pdf_bytes",
        lambda pdf_bytes, recipe_id: parsed,
    )

    pipeline = _pipeline(existing)
    result = pipeline._process_file(FakeFile(), 1)

    assert result is parsed
    assert result.title == "Foe yong hai"
    assert result.is_favorite is True
    assert result.cooked_dates == ["2026-10-01"]
    assert result.timers[0].id == "t1"
    assert result.created_at == datetime(2024, 1, 1)
    assert result.category == "rice"
    assert pipeline.repository.saved is parsed


def test_new_recipe_keeps_parsed_values(monkeypatch):
    parsed = Recipe(id="r999", title="New", category="soup", is_favorite=False)
    monkeypatch.setattr(
        "pipeline.pdf_ingestion_pipeline.parse_pdf_bytes",
        lambda pdf_bytes, recipe_id: parsed,
    )

    pipeline = _pipeline(None, recipe_id=None)
    result = pipeline._process_file(FakeFile(), 1)

    assert result.category == "soup"
    assert result.is_favorite is False
    assert result.cooked_dates == []
    assert pipeline.repository.saved is parsed
