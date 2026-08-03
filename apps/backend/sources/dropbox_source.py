from dropbox_client import DropboxClient
from sources.base import PDFSource
from utils.retry import retry
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

    @retry(max_attempts=3, exceptions=(Exception,))
    def get_pdf_bytes(self, path: str):
        metadata, content = self.client.download_file(path)
        logger.debug("Downloaded %s (%d bytes)", metadata.name, len(content))
        return metadata.name, content
