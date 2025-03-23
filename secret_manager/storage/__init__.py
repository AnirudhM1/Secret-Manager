"""Storage backends for Secret Manager.

This module provides access to storage backends for Secret Manager.
"""

from secret_manager.storage.base import StorageBackend
from secret_manager.storage.local import LocalStorageBackend
from secret_manager.storage.s3 import S3StorageBackend
from secret_manager.storage.registry import get_storage_backend, register_backend
