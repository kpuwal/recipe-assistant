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

    def test_connection(self):
        try:
            account = self.dbx.users_get_current_account()
            logger.info("Dropbox connected successfully as: %s", account.name.display_name)
            return account
        except Exception as e:
            logger.error("Dropbox connection failed: %s", e)
            raise

    def list_files(self, path: str = None):
        folder_path = path or self.recipe_folder
        logger.info("Listing Dropbox folder: %s", folder_path)

        try:
            result = self.dbx.files_list_folder(folder_path)
            logger.info("Found %d items in folder", len(result.entries))
            return result.entries
        except Exception as e:
            logger.error("Failed to list folder %s: %s", folder_path, e)
            raise

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