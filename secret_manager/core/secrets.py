from pathlib import Path

from .projects import ProjectManager
from .schemas import Project, Secret, Backend, SecretMode
from secret_manager.utils import diff, logger
from .remotes import RemoteManager


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
                logger.error(f"S3 key is required for S3 backend")
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
