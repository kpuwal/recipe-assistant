from pathlib import Path
import os

class Settings:

    def __init__(self):
        self.base_dir = Path(os.getenv("BASE_DIR", ".")).resolve()
        self.recipe_dir = self.base_dir / "recipes"


        self.gcs_bucket_name = os.getenv(
            "GCS_BUCKET_NAME",
            "my-recipes-json"
        )

        self.dropbox_folder = os.getenv(
            "DROPBOX_RECIPE_FOLDER",
            "/Recipes",
        )

        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        self.cors_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:19006,http://127.0.0.1:19006"
        ).split(",")

        self._ensure_directories()


    def _ensure_directories(self):
        directories = [
            self.recipe_dir,
            self.recipe_dir / "imported",
            self.recipe_dir / "ai",
            self.recipe_dir / "personal",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

settings = Settings()