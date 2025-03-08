import json
from pathlib import Path

from .constants import DEFAULT_BASE_DIR
from .schemas import Project


class ProjectManager:
    """Manages project registration and configuration."""
    
    def __init__(self, base_dir: Path=None):
        base_dir = base_dir or Path(DEFAULT_BASE_DIR)

        self.config_dir = base_dir.expanduser()
        self.projects_file = self.config_dir / "projects.json"

        self._ensure_config_dir()
        self.projects = self._load_projects()
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.projects_file.exists():
            json.dump([], self.projects_file.open('w'), indent=4)

    
    def _load_projects(self) -> dict[Path, Project]:
        """Load projects from the projects file."""
        if not self.projects_file.exists():
            return {}

        projects = json.load(self.projects_file.open())

        # Deserialize the projects
        projects = [Project.deserialize(project) for project in projects]
        projects = {project.root: project for project in projects}

        return projects

    
    def _save_projects(self):
        """Save projects to the projects file."""

        # Serialize the projects
        projects = [project.serialize() for project in self.projects.values()]
        json.dump(projects, self.projects_file.open('w'), indent=4)
    

    def get_project(self, project_dir: Path):
        """Get the project from the project directory"""

        if project_dir.absolute() in self.projects:
            return self.projects[project_dir.absolute()]
        
        while not (project_dir := project_dir.parent).samefile("/"):
            if (project := self.projects.get(project_dir.absolute())) is not None:
                return project
        
        return None

    
    def register(self, project: Project):
        """Register a new project."""

        if not project.root.is_dir():
            raise ValueError(f"Directory does not exist or is a file: {project.root}")
        
        # Register the project
        self.projects[project.root.absolute()] = project
        self._save_projects()

    
    def delete(self, project: Project):
        """Delete a project registration"""
        
        # Delete the project using its root path
        if project.root.absolute() not in self.projects:
            raise ValueError(f"Project not registered: {project.root}")
        
        # Delete the project
        del self.projects[project.root.absolute()]
        self._save_projects()
    

    def update(self, project: Project):
        """Updates the project"""

        # Check if the project is registered
        if project.root.absolute() not in self.projects:
            raise ValueError(f"Project not registered: {project.root}")
        
        # Update the project
        self.projects[project.root.absolute()] = project
        self._save_projects()