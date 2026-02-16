"""Google Cloud Storage service for resume file uploads."""

import uuid
from datetime import timedelta
from pathlib import Path

from google.cloud import storage

from ..config import get_settings


class StorageService:
    """Handles file uploads/downloads to Google Cloud Storage."""

    def __init__(self):
        self.settings = get_settings()
        self._client: storage.Client | None = None
        self._bucket: storage.Bucket | None = None

    @property
    def client(self) -> storage.Client:
        if self._client is None:
            self._client = storage.Client()
        return self._client

    @property
    def bucket(self) -> storage.Bucket:
        if self._bucket is None:
            self._bucket = self.client.bucket(self.settings.gcs_bucket_name)
        return self._bucket

    def upload_resume(self, user_id: str, file_name: str, file_data: bytes, content_type: str) -> str:
        """Upload a resume file to GCS.

        Returns the GCS object path (not a signed URL).
        """
        ext = Path(file_name).suffix.lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        blob_path = f"resumes/{user_id}/{unique_name}"

        blob = self.bucket.blob(blob_path)
        blob.upload_from_string(file_data, content_type=content_type)

        return blob_path

    def get_signed_url(self, blob_path: str, expiration_minutes: int = 60) -> str:
        """Generate a signed URL for temporary file access."""
        blob = self.bucket.blob(blob_path)
        return blob.generate_signed_url(
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
        )

    def delete_file(self, blob_path: str) -> None:
        """Delete a file from GCS."""
        blob = self.bucket.blob(blob_path)
        blob.delete()


class LocalStorageService:
    """Local filesystem storage for development (no GCS dependency)."""

    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def upload_resume(self, user_id: str, file_name: str, file_data: bytes, content_type: str) -> str:
        ext = Path(file_name).suffix.lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        user_dir = self.base_dir / "resumes" / user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        file_path = user_dir / unique_name
        file_path.write_bytes(file_data)

        return str(file_path)

    def get_signed_url(self, blob_path: str, expiration_minutes: int = 60) -> str:
        return f"/files/{blob_path}"

    def delete_file(self, blob_path: str) -> None:
        path = Path(blob_path)
        if path.exists():
            path.unlink()


def get_storage_service() -> StorageService | LocalStorageService:
    """Factory: returns GCS in production, local filesystem in dev."""
    settings = get_settings()
    if settings.gcs_bucket_name:
        return StorageService()
    return LocalStorageService()
