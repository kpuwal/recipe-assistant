from storage.gcs_storage import GCSStorage
from utils.logger import logger


class IngestionState:

    def __init__(
        self,
        storage: GCSStorage,
        blob_name: str = "state/ingestion_state.json",
    ):
        self.storage = storage
        self.blob_name = blob_name

        self.data = (
            self.storage.download_json(blob_name)
            or {}
        )

    def get_hash(self, file_id: str):
        entry = self.data.get(file_id)

        if not entry:
            return None

        return entry.get("hash")

    def get_recipe_id(self, file_id: str):
        entry = self.data.get(file_id)

        if not entry:
            return None

        return entry.get("recipe_id")

    def update(
        self,
        file_id: str,
        file_hash: str,
        recipe_id: str,
    ):
        self.data[file_id] = {"hash": file_hash, "recipe_id": recipe_id}

    def save(self):
        uploaded = self.storage.upload_json(
            self.data,
            self.blob_name,
        )

        if uploaded:
            logger.debug("Saved ingestion state (%d entries)", len(self.data))
        else:
            logger.error("Failed to save ingestion state")