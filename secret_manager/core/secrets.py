from pathlib import Path

from secret_manager.storage import get_storage_backend
from secret_manager.utils import diff, logger

from .projects import ProjectManager
from .remotes import RemoteManager
from .schemas import Backend, Project, Secret, SecretMode


class SecretManager:
    """Manages secret tracking operations."""

    def __init__(self, project: Project):
        self.project = project
        self.project_manager = ProjectManager()

    def track_file(self, file: Path, mode: SecretMode):
        """Track a specific secrets file for a project in the specified mode"""

        # Create a Secret for the selected mode
        secret = Secret(path=file, backend=Backend.NONE)

        if mode == SecretMode.LOCAL:
            self.project.local = secret

        elif mode == SecretMode.DEV:
            self.project.dev = secret

        elif mode == SecretMode.PROD:
            self.project.prod = secret

        else:
            raise ValueError(f"Invalid mode: {mode}")

        # Update the project with the given secret
        self.project_manager.update(self.project)

    def track_remote(self, mode: SecretMode, remote_name: str, s3_key: str = None) -> int:
        """Associate a remote backend with a secret file for the specified mode.

        Args:
            mode: The environment mode (LOCAL, DEV, PROD)
            remote_name: Name of the remote backend to use
            s3_key: S3 key path (for S3 backends only)

        Returns:
            0 on success, 1 on failure
        """
        # Get the secret for this mode
        secret = self.get_secret(mode)
        if not secret:
            logger.error(f"No secret tracked for {mode.value} environment. Track a local file first.")
            return 1

        # Get the remote configuration
        remote_manager = RemoteManager()
        remote = remote_manager.get_remote(remote_name)
        if not remote:
            logger.error(f"Remote '{remote_name}' does not exist")
            return 1

        # Update the secret with remote backend information
        secret.backend = remote.type

        # For S3 backend, ensure we have an S3 key
        if remote.type == Backend.S3:
            if not s3_key:
                logger.error("S3 key is required for S3 backend")
                return 1

            # Copy AWS config from the remote to the secret
            secret.aws_config = remote.aws_config
            # Store S3 key in the secret
            secret.s3_key = s3_key

        # Update the project with the modified secret
        if mode == SecretMode.LOCAL:
            self.project.local = secret
        elif mode == SecretMode.DEV:
            self.project.dev = secret
        elif mode == SecretMode.PROD:
            self.project.prod = secret

        # Save the updated project
        self.project_manager.update(self.project)
        logger.success(f"Secret for {mode.value} environment is now tracked with remote '{remote_name}'")
        return 0

    def get_secret(self, mode: SecretMode) -> Secret:
        """Get the secret for the specified mode"""

        if mode == SecretMode.LOCAL:
            return self.project.local
        elif mode == SecretMode.DEV:
            return self.project.dev
        elif mode == SecretMode.PROD:
            return self.project.prod
        else:
            return None

    def list_secrets(self):
        """Get all secrets for the current project"""

        secrets = []

        # Check each environment and add to the list if it exists
        if self.project.local:
            secrets.append({"environment": "Local", "secret": self.project.local})
        if self.project.dev:
            secrets.append({"environment": "Development", "secret": self.project.dev})
        if self.project.prod:
            secrets.append({"environment": "Production", "secret": self.project.prod})

        return secrets

    def compare_secrets(self, source_mode: SecretMode, target_mode: SecretMode) -> int:
        """Compare secrets between two modes"""

        # Get secrets for both environments
        source_secret = self.get_secret(source_mode)
        target_secret = self.get_secret(target_mode)

        # Check if both secrets exist
        if not source_secret:
            logger.error(f"No secrets tracked for {source_mode.value} environment")
            return 1
        if not target_secret:
            logger.error(f"No secrets tracked for {target_mode.value} environment")
            return 1

        # Read the content of both secret files
        try:
            source_content = source_secret.path.read_text().strip().splitlines()
            target_content = target_secret.path.read_text().strip().splitlines()
        except Exception as e:
            logger.error(f"Failed to read secret files: {e}")
            return 1

        # Generate diff
        diff_data = diff.compute_diff(source_content, target_content)

        # Display diff
        if not any(diff_data.values()):
            logger.info(f"No differences found between {source_mode.value} and {target_mode.value} environments")
        else:
            logger.display_diff(diff_data, source_mode.value, target_mode.value)

        return 0

    def push_to_remote(self, env: SecretMode):
        """Push local secrets to the configured remote backend"""

        # Get the secret for this environment
        if not (secret := self.get_secret(env)):
            return 1

        # Check if remote is configured
        if not secret.backend:
            logger.error(f"No remote configured for {env} environment")
            return 1

        # Get based based on backend type
        if secret.backend == Backend.S3:
            backend = get_storage_backend("s3", secret.aws_config.serialize())

        else:
            logger.error(f"Unsupported backend type: {secret.backend}")
            return 1

        # Push secrets to remote
        return backend.write(secret.s3_key, secret.path)

    def fetch_from_remote(self, env: SecretMode):
        """Fetch secrets from the configured remote backend and show diff"""

        # Get the secret for this environment
        if not (secret := self.get_secret(env)):
            return 1

        # Check if remote is configured
        if not secret.backend:
            logger.error(f"No remote configured for {env} environment")
            return 1

        # Get based based on backend type
        if secret.backend == Backend.S3:
            backend = get_storage_backend("s3", secret.aws_config.serialize())

        else:
            logger.error(f"Unsupported backend type: {secret.backend}")
            return 1

        # Fetch secret content from remote
        remote_content = backend.read(secret.s3_key)
        local_content = secret.path.read_text().strip().splitlines()

        # Generate diff
        diff_data = diff.compute_diff(local_content, remote_content)

        # Display diff
        if not any(diff_data.values()):
            logger.info("No differences found between remote and local secrets")
        else:
            logger.display_diff(diff_data, "Remote", "Local")

        return 0

    def pull_from_remote(self, env: SecretMode):
        """Pull secrets from remote and update local file"""

        # Get the secret for this environment
        if not (secret := self.get_secret(env)):
            return 1

        # Check if remote is configured
        if not secret.backend:
            logger.error(f"No remote configured for {env} environment")
            return 1

        # Get based based on backend type
        if secret.backend == Backend.S3:
            backend = get_storage_backend("s3", secret.aws_config.serialize())

        else:
            logger.error(f"Unsupported backend type: {secret.backend}")
            return 1

        # Fetch secret content from remote
        remote_content = backend.read(secret.s3_key)

        # Write content to local file
        secret.path.write_text("\n".join(remote_content) + "\n")

        logger.success(f"Successfully pulled secrets from remote to local file: {secret.path}")
        return 0

    def remove_remote(self, mode: SecretMode) -> int:
        """Remove remote backend association from a secret for the specified mode"""

        # Get the secret for this mode
        if not (secret := self.get_secret(mode)):
            logger.error(f"No secret tracked for {mode.value} environment.")
            return 1

        # Check if there's a remote backend configured
        if not secret.backend:
            logger.error(f"No remote backend configured for {mode.value} environment.")
            return 1

        # Store the remote backend type for logging
        previous_backend = secret.backend

        # Reset the backend configuration
        secret.backend = Backend.NONE

        # Clear S3-specific configurations if they exist
        if previous_backend is Backend.S3:
            secret.aws_config = None
            secret.s3_key = None

        # Update the project with the modified secret
        if mode == SecretMode.LOCAL:
            self.project.local = secret
        elif mode == SecretMode.DEV:
            self.project.dev = secret
        elif mode == SecretMode.PROD:
            self.project.prod = secret

        # Save the updated project
        self.project_manager.update(self.project)
        logger.success(f"Remote {previous_backend.value} backend removed from {mode.value} environment secret")
        return 0
