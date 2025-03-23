"""Storage backends registry for Secret Manager.

This module provides a registry of available storage backends and functions
to register and retrieve them.
"""

from typing import Callable

from secret_manager.storage.base import StorageBackend
from secret_manager.storage.local import LocalStorageBackend
from secret_manager.storage.s3 import S3StorageBackend

# Type for storage backend factory functions
BackendFactory = Callable[[dict[str]], StorageBackend]

# Registry of available storage backends and their factory functions
STORAGE_BACKENDS: dict[str, StorageBackend] = {}
BACKEND_FACTORIES: dict[str, BackendFactory] = {}


def register_backend(backend_type: str, backend_class: type[StorageBackend], factory_func: BackendFactory):
    """Register a storage backend and its factory function.

    Args:
        backend_type: The storage type name
        backend_class: The backend class
        factory_func: Function that creates and configures the backend instance
    """
    STORAGE_BACKENDS[backend_type] = backend_class
    BACKEND_FACTORIES[backend_type] = factory_func


def get_storage_backend(storage_type: str, config: dict[str]):
    """Get configured storage backend instance.

    Args:
        storage_type: Storage backend type name
        config: Backend configuration

    Returns:
        Initialized StorageBackend
    """
    if not (factory := BACKEND_FACTORIES.get(storage_type)):
        supported = ", ".join(STORAGE_BACKENDS.keys())
        raise ValueError(f"Unknown storage backend type: {storage_type}. Supported types: {supported}")

    # Call the factory function with the configuration
    return factory(config)


# Register the Local storage backend
def _create_local_backend(config: dict[str, str]):
    """Factory function for LocalStorageBackend."""
    backend = LocalStorageBackend()
    backend.initialize(**config)
    return backend


register_backend("local", LocalStorageBackend, _create_local_backend)


# Register the S3 storage backend
def _create_s3_backend(config: dict[str, str]):
    """Factory function for S3StorageBackend."""
    backend = S3StorageBackend(config["AWS_ACCESS_KEY_ID"], config["AWS_SECRET_ACCESS_KEY"], config["AWS_REGION"])
    return backend


register_backend("s3", S3StorageBackend, _create_s3_backend)
