"""Local storage backend for Secret Manager."""

import shutil
from pathlib import Path

from secret_manager.core.constants import DEFAULT_BASE_DIR
from secret_manager.storage.base import StorageBackend
from secret_manager.utils import logger


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self, base_dir: Path = None):
        """Initialize the local storage backend"""
        self.base_dir = base_dir or Path(DEFAULT_BASE_DIR) / "storage"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write(self, key: str, local_path: Path):
        """Write data to local storage"""

        try:
            # Get destination path and make sure parent directories exist
            dest_path = self.base_dir / key
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy2(local_path, dest_path)

            logger.info(f"Copied file to {dest_path}")
            return 0
        except Exception as e:
            logger.error(f"Failed to write to {key}: {e}")
            return 1

    def read(self, key: str) -> list[str]:
        """Read data from local storage"""

        try:
            # Get destination path
            dest_path = self.base_dir / key

            if not dest_path.exists():
                raise FileNotFoundError(f"File not found: {dest_path}")

            if dest_path.is_dir():
                raise IsADirectoryError(f"Path is a directory: {dest_path}")

            lines = [line.strip() for line in dest_path.read_text().strip().splitlines() if line.strip()]
            return lines

        except Exception as e:
            logger.error(f"Failed to read from {key}: {e}")
            return []

    def exists(self, key: str) -> bool:
        """Check if a key exists in local storage"""
        file_path = self.base_dir / key
        return file_path.exists()
