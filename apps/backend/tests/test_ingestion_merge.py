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
        oven_temperature=180,
        oven_mode="fan",
    )
    parsed = Recipe(
        id="r043",
        title="Foe yong hai",
        category="other",
        is_favorite=False,
        created_at=None,
        oven_temperature=220,
        oven_mode="conventional",
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
    assert result.oven_temperature == 180
    assert result.oven_mode == "fan"
    assert pipeline.repository.saved is parsed


def test_resync_preserves_manually_edited_fields(monkeypatch):
    existing = Recipe(
        id="r043",
        title="Mijn eigen titel",
        steps=["Mijn eigen stap"],
        tips="Mijn eigen tip",
        user_edited_fields=["title", "steps", "tips"],
    )
    parsed = Recipe(
        id="r043",
        title="Foe yong hai",
        steps=["Nieuwe stap uit PDF"],
        tips="Nieuwe tip uit PDF",
    )
    monkeypatch.setattr(
        "pipeline.pdf_ingestion_pipeline.parse_pdf_bytes",
        lambda pdf_bytes, recipe_id: parsed,
    )

    pipeline = _pipeline(existing)
    result = pipeline._process_file(FakeFile(), 1)

    assert result.title == "Mijn eigen titel"
    assert result.steps == ["Mijn eigen stap"]
    assert result.tips == "Mijn eigen tip"
    assert set(result.user_edited_fields) == {"steps", "tips", "title"}


def test_resync_preserves_existing_image(monkeypatch):
    existing = Recipe(
        id="r043",
        title="Old title",
        image="r043-abc123.jpg",
    )
    parsed = Recipe(
        id="r043",
        title="Foe yong hai",
        image="r043.jpg",
        image_bytes=b"new image from pdf",
        image_extension="jpg",
    )
    monkeypatch.setattr(
        "pipeline.pdf_ingestion_pipeline.parse_pdf_bytes",
        lambda pdf_bytes, recipe_id: parsed,
    )

    pipeline = _pipeline(existing)
    result = pipeline._process_file(FakeFile(), 1)

    assert result.image == "r043-abc123.jpg"
    assert result.image_bytes is None
    assert result.image_extension is None


def test_resync_keeps_pdf_image_when_recipe_has_none(monkeypatch):
    existing = Recipe(id="r043", title="Old title")
    parsed = Recipe(
        id="r043",
        title="Foe yong hai",
        image="r043.jpg",
        image_bytes=b"new image from pdf",
        image_extension="jpg",
    )
    monkeypatch.setattr(
        "pipeline.pdf_ingestion_pipeline.parse_pdf_bytes",
        lambda pdf_bytes, recipe_id: parsed,
    )

    pipeline = _pipeline(existing)
    result = pipeline._process_file(FakeFile(), 1)

    assert result.image == "r043.jpg"
    assert result.image_bytes == b"new image from pdf"


def test_resync_fills_missing_oven_settings(monkeypatch):
    existing = Recipe(id="r043", title="Old title")
    parsed = Recipe(
        id="r043",
        title="Foe yong hai",
        oven_temperature=200,
        oven_mode="conventional",
    )
    monkeypatch.setattr(
        "pipeline.pdf_ingestion_pipeline.parse_pdf_bytes",
        lambda pdf_bytes, recipe_id: parsed,
    )

    pipeline = _pipeline(existing)
    result = pipeline._process_file(FakeFile(), 1)

    assert result.oven_temperature == 200
    assert result.oven_mode == "conventional"


def test_new_recipe_keeps_parsed_values(monkeypatch):
    parsed = Recipe(
        id="r999",
        title="New",
        category="soup",
        is_favorite=False,
        oven_temperature=180,
        oven_mode="fan",
    )
    monkeypatch.setattr(
        "pipeline.pdf_ingestion_pipeline.parse_pdf_bytes",
        lambda pdf_bytes, recipe_id: parsed,
    )

    pipeline = _pipeline(None, recipe_id=None)
    result = pipeline._process_file(FakeFile(), 1)

    assert result.category == "soup"
    assert result.is_favorite is False
    assert result.cooked_dates == []
    assert result.oven_temperature == 180
    assert result.oven_mode == "fan"
    assert pipeline.repository.saved is parsed
