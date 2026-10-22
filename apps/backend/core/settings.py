import os


class Settings:

    def __init__(self):
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

        # Shared secret required on every non-health endpoint. There is no
        # default: main.py refuses to boot when this is empty so that a
        # misconfigured deploy fails loudly instead of serving publicly.
        self.api_key = os.getenv("APP_API_KEY", "").strip()

        self.chat_rate_limit = int(os.getenv("CHAT_RATE_LIMIT", "30"))
        self.chat_rate_window = int(os.getenv("CHAT_RATE_WINDOW_SECONDS", "60"))
        self.sync_rate_limit = int(os.getenv("SYNC_RATE_LIMIT", "3"))
        self.sync_rate_window = int(os.getenv("SYNC_RATE_WINDOW_SECONDS", "300"))


settings = Settings()