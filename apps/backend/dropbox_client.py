import dropbox
from dotenv import load_dotenv
import os

from utils.logger import logger

load_dotenv()

class DropboxClient:
    def __init__(self):
        self.dbx = dropbox.Dropbox(
            oauth2_refresh_token=os.getenv("DROPBOX_REFRESH_TOKEN"),
            app_key=os.getenv("DROPBOX_APP_KEY"),
            app_secret=os.getenv("DROPBOX_APP_SECRET"),
        )

        self.recipe_folder = os.getenv("DROPBOX_RECIPE_FOLDER", "/Recipes")
        # Example DROPBOX_RECIPE_SUBFOLDERS=Italian,Mexican,Asian,Desserts
        subfolders_str = os.getenv("DROPBOX_RECIPE_SUBFOLDERS", "")
        self.recipe_subfolders = [s.strip() for s in subfolders_str.split(",") if s.strip()]

    def test_connection(self):
        try:
            account = self.dbx.users_get_current_account()
            logger.info("Dropbox connected successfully as: %s", account.name.display_name)
            return account
        except Exception as e:
            logger.error("Dropbox connection failed: %s", e)
            raise

    def list_files(self):
        if not self.recipe_subfolders:
            logger.warning("No recipe subfolders configured (DROPBOX_RECIPE_SUBFOLDERS is empty)")
            return []

        all_pdfs = []

        for subfolder in self.recipe_subfolders:
            folder_path = f"{self.recipe_folder.rstrip('/')}/{subfolder}"
            logger.info("Listing PDFs in: %s", folder_path)

            try:
                result = self.dbx.files_list_folder(folder_path)

                pdfs = [
                    entry for entry in result.entries
                    if isinstance(entry, dropbox.files.FileMetadata)
                    and entry.name.lower().endswith(".pdf")
                ]

                logger.info("Found %d PDF(s) in %s", len(pdfs), folder_path)
                all_pdfs.extend(pdfs)

            except dropbox.exceptions.ApiError as e:
                logger.error("Failed to list folder %s: %s", folder_path, e)
                continue

        logger.info("Total PDFs found across all subfolders: %d", len(all_pdfs))
        return all_pdfs

    def download_file(self, dropbox_path: str):
        logger.info("Downloading file: %s", dropbox_path)

        try:
            metadata, response = self.dbx.files_download(dropbox_path)
            logger.info("Successfully downloaded %s (%s bytes)",
                       metadata.name, len(response.content))
            return metadata, response.content
        except Exception as e:
            logger.error("Download failed for %s: %s", dropbox_path, e)
            raise