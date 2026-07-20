from abc import ABC, abstractmethod

class PDFSource(ABC):
    @abstractmethod
    def list_pdfs(self):
        """Return list of available PDFs"""
        pass

    @abstractmethod
    def get_pdf_bytes(self, path: str):
        """ Returns: (filename: str, pdf_bytes: bytes)"""
        pass