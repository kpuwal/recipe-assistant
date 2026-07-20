from dropbox_client import DropboxClient
from sources.base import PDFSource
import time

from utils.logger import logger


class DropboxSource(PDFSource):

    def __init__(self, client: DropboxClient):
        self.client = client

    def list_pdfs(self):
        files = self.client.list_files()

        pdfs = [
            file for file in files
            if file.name.lower().endswith(".pdf")
        ]

        logger.info("Found %d PDF files in Dropbox", len(pdfs))
        return pdfs

    def get_pdf_bytes(self, path: str, retries: int = 3):
        for attempt in range(retries):
            try:
                metadata, content = self.client.download_file(path)
                logger.debug("Downloaded %s (%d bytes)", metadata.name, len(content))
                return metadata.name, content

            except Exception as e:
                if attempt == retries - 1:
                    logger.error("Failed to download %s after %d attempts: %s", 
                                path, retries, e)
                    raise

                wait = 2 ** attempt
                logger.warning("Download failed for %s (attempt %d/%d). Retrying in %d seconds...", 
                              path, attempt+1, retries, wait)
                time.sleep(wait)