"""Command line interface for Secret Manager."""

from pathlib import Path
import typer

from secret_manager.core import ProjectManager, SecretManager
from secret_manager.core.schemas import Project, SecretMode
from secret_manager.utils import logger
from secret_manager.utils.selection import select_from_list


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
        project = Project(root=current_dir)
        manager.register(project)
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
        manager.delete(project)  # Changed to pass the project object instead of project.root
        logger.success(f"Project unregistered successfully at {project.root}")

    except Exception as e:
        logger.exception(f"Failed to unregister project: {e}")
        return 1


@app.command()
def track(secrets_file: Path, environment: str = None):
    """Track a specific secrets file for secret management"""

    try:
        # Make sure the file exists
        if not secrets_file.exists():
            logger.error(f"Environment file does not exist: {secrets_file}")
            return 1

        current_dir = Path.cwd()
        project_manager = ProjectManager()

        # Find project that contains this file
        if (project := project_manager.get_project(current_dir)) is None:
            logger.error(f"No project registered for {current_dir}")
            return 1

        # If environment is not provided, prompt the user to select one
        env = environment or select_from_list(message="Select the environment to track secrets:", choices=["local", "dev", "prod"])
        env = SecretMode(env)

        # Use SecretManager to handle the business logic
        secret_manager = SecretManager(project)
        secret_manager.track_file(secrets_file, env)

        logger.success(f"Successfully added {secrets_file.name} to {env.value} secrets tracking")

    except Exception as e:
        logger.exception(f"Failed to track secrets file: {e}")
        return 1

    return 0


@app.command()
def list():
    """List all secrets tracked in the current project"""

    current_dir = Path.cwd()
    project_manager = ProjectManager()

    # Find project that contains this directory
    if (project := project_manager.get_project(current_dir)) is None:
        logger.error(f"No project registered for {current_dir}")
        return 1

    # Use SecretManager to get all secrets
    secret_manager = SecretManager(project)
    secrets = secret_manager.list_secrets()

    # Display the secrets
    logger.display_secrets(secrets, project_root=project.root)

    return 0


@app.command()
def diff(source: str = "local", target: str = "dev"):
    """Compare secrets between two environments

    NOTE:
    - By default it compares local and dev environments
    - If only one argument is provided, it compares local with that environment

    """

    try:
        current_dir = Path.cwd()
        project_manager = ProjectManager()

        # Find project for current directory
        if (project := project_manager.get_project(current_dir)) is None:
            logger.error(f"No project registered for {current_dir}")
            return 1

        # Use SecretManager to handle the comparison logic
        source_mode = SecretMode(source)
        target_mode = SecretMode(target)
        secret_manager = SecretManager(project)
        return secret_manager.compare_secrets(source_mode, target_mode)

    except Exception as e:
        logger.exception(f"Failed to compare environments: {e}")
        return 1


def main():
    """Entry point for the CLI."""
    try:
        app()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    app()
