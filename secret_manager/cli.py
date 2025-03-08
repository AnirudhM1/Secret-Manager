"""Command line interface for Secret Manager."""

from pathlib import Path
import typer

from secret_manager.core import ProjectManager
from secret_manager.utils import logger


app = typer.Typer(name="Secrets", help="Secure Secret Management with AWS S3")


@app.command()
def register():
    """Register the current directory (and all it's sub directories) as a project"""

    current_dir = Path.cwd()
    manager = ProjectManager()

    # Check if the current directory is already registered
    if (project := manager.get_project(current_dir)) is not None:
        logger.error(f"Project already registered at {project.root}")
        return 1
    

    # Register the project
    try:
        manager.register(current_dir)
        logger.success(f"Project registered successfully at {current_dir}")
    
    except Exception as e:
        logger.exception(f"Failed to register project: {e}")
        return 1


@app.command()
def unregister():
    """Unregister the current directory as a project"""

    current_dir = Path.cwd()
    manager = ProjectManager()

    # Check if the current directory is already registered
    if (project := manager.get_project(current_dir)) is None:
        logger.error(f"Project not registered at {current_dir}")
        return 1
    

    # Unregister the project
    try:
        manager.delete(project.root)
        logger.success(f"Project unregistered successfully at {project.root}")
    
    except Exception as e:
        logger.exception(f"Failed to unregister project: {e}")
        return 1



def main():
    """Entry point for the CLI."""
    try:
        app()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    app()
