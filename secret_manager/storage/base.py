"""Base storage backend interface for Secret Manager."""

from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    """Abstract base class for all storage backends."""

    @abstractmethod
    def write(self, key: str, local_path: Path) -> int:
        """Write data to the storage backend.

        Args:
            key: Key or path in remote
            local_path: Local file path
        """
        pass

    @abstractmethod
    def read(self, key: str) -> list[str]:
        """Read data from the storage backend.

        Args:
            key: Key or path in remote

        Returns:
            list of lines read from the remote file
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in the storage backend.

        Args:
            key: Key or path in remote
        """
        pass
