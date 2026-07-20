from pathlib import Path

from google.cloud import storage
import json
from typing import Optional, Dict, Any
from utils.logger import logger


class GCSStorage:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)


    def upload_json(self, data: Dict[Any, Any], blob_name: str) -> bool:
        try:
            blob = self.bucket.blob(blob_name)
            json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
            
            blob.upload_from_string(json_str, content_type="application/json")
            logger.info(f"Uploaded to gs://{self.bucket_name}/{blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload {blob_name}: {e}")
            return False
        
    def upload_file(self, local_path: Path, blob_name: str) -> bool:
        try:
            blob = self.bucket.blob(blob_name)
            blob.upload_from_filename(str(local_path))
            logger.info("Uploaded file %s", blob_name)
            return True

        except Exception as e:
            logger.error("Failed upload %s: %s", blob_name, e)
            return False
        
    def upload_bytes(
        self,
        data: bytes,
        blob_name: str,
        content_type: str = "application/octet-stream",
    ) -> bool:

        try:
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(data, content_type=content_type)
            logger.info("Uploaded bytes to GCS: %s", blob_name)
            return True

        except Exception as e:
            logger.error("Failed uploading bytes %s: %s", blob_name, e)
            return False
        

    def download_json(
        self,
        blob_name: str,
    ) -> Optional[Dict]:

        try:
            blob = self.bucket.blob(blob_name)

            if not blob.exists():
                logger.warning("File not found: %s", blob_name)
                return None

            content = blob.download_as_text()
            return json.loads(content)

        except Exception as e:
            logger.error("Failed to download %s: %s", blob_name, e)
            return None
        
    def download_bytes(
        self,
        blob_name: str,
    ) -> bytes | None:

        try:
            blob = self.bucket.blob(blob_name)

            if not blob.exists():
                logger.warning("Blob not found: %s", blob_name)
                return None

            return blob.download_as_bytes()

        except Exception as e:
            logger.error("Failed downloading %s: %s", blob_name, e)
            return None
        

    def list_files(self, prefix: str = ""):
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    
    def delete_file(
        self,
        blob_name: str,
    ) -> bool:

        try:
            blob = self.bucket.blob(blob_name)

            if not blob.exists():
                logger.warning("Cannot delete missing blob: %s", blob_name)
                return False

            blob.delete()
            logger.info("Deleted gs://%s/%s", self.bucket_name, blob_name)
            return True

        except Exception as e:
            logger.error("Failed deleting %s: %s", blob_name, e)
            return False
        
    def exists(self, blob_name: str) -> bool:
        try:
            blob = self.bucket.blob(blob_name)
            return blob.exists()

        except Exception as e:
            logger.error("Failed checking existence of %s: %s", blob_name, e)
            return False