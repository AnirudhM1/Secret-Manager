from pathlib import Path

from .projects import ProjectManager
from .schemas import Project, Secret, Backend, SecretMode


class SecretManager:
    """Manages secret tracking operations."""
    
    def __init__(self, project: Project):
        self.project = project
        self.project_manager = ProjectManager()
    
    
    def track_file(self, file: Path, mode: SecretMode):
        """Track a specific secrets file for a project in the specified mode.
        
        Args:
            file: Path to the secrets file
            mode: The environment mode ('local', 'dev', 'prod')
        """
        
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
    
    def get_all_secrets(self):
        """Get all secrets for the current project.
        
        Returns:
            List of dictionaries containing environment name and secret object
        """
        secrets = []
        
        # Check each environment and add to the list if it exists
        if self.project.local:
            secrets.append({"environment": "Local", "secret": self.project.local})
        if self.project.dev:
            secrets.append({"environment": "Development", "secret": self.project.dev})
        if self.project.prod:
            secrets.append({"environment": "Production", "secret": self.project.prod})
        
        return secrets
