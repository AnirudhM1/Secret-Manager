"""Command line interface for Secret Manager."""

from pathlib import Path
import typer

from secret_manager.core import ProjectManager, SecretManager
from secret_manager.core.schemas import Project, SecretMode, Remote, Backend
from secret_manager.core.remotes import RemoteManager
from secret_manager.utils import logger
from secret_manager.utils.selection import select_from_list
from secret_manager.wizards.remote import configure_aws_backend
from secret_manager.wizards.project import select_environment, resolve_comparison_environments


app = typer.Typer(name="Secrets", help="Secure Secret Management with AWS S3")
remote_app = typer.Typer(name="Remote", help="Manage remote backends")
app.add_typer(remote_app, name="remote")


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

        # Use wizard to select environment if not provided
        env = SecretMode(environment) if environment else select_environment(
            "Select the environment to track secrets:"
        )

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
def diff(source: str = None, target: str = None):
    """Compare secrets between two environments

    NOTE:
    - By default compares local and dev environments
    - If neither source nor target is provided, uses interactive selection
    """

    try:
        current_dir = Path.cwd()
        project_manager = ProjectManager()

        # Find project for current directory
        if (project := project_manager.get_project(current_dir)) is None:
            logger.error(f"No project registered for {current_dir}")
            return 1

        # Use the wizard to resolve environments based on provided parameters
        source_mode, target_mode = resolve_comparison_environments(source, target)

        # Use SecretManager to handle the comparison logic
        secret_manager = SecretManager(project)
        return secret_manager.compare_secrets(source_mode, target_mode)

    except Exception as e:
        logger.exception(f"Failed to compare environments: {e}")
        return 1


@remote_app.command("add")
def remote_add(name: str = typer.Argument(..., help="Name of the remote")):
    """Add a new remote backend"""
    
    try:
        remote_manager = RemoteManager()
        
        # Check if remote already exists
        if remote_manager.get_remote(name):
            logger.error(f"Remote with name '{name}' already exists")
            return 1
        
        # Select backend type - currently only S3 supported
        backend_type = select_from_list(
            message="Select backend type:",
            choices=["s3"],
        )
        remote_type = Backend(backend_type)
        
        # Configure based on backend type
        if remote_type == Backend.S3:
            # Use wizard to handle the complex AWS configuration
            aws_config = configure_aws_backend()
            if not aws_config:
                return 1
            
            # Create and add the remote with the configured backend
            remote = Remote(name=name, type=remote_type, aws_config=aws_config)
            remote_manager.add_remote(remote)
            logger.success(f"Remote '{name}' added successfully")
        else:
            logger.error(f"Remote type '{backend_type}' is not supported yet")
            return 1
            
    except Exception as e:
        logger.exception(f"Failed to add remote: {e}")
        return 1
        
    return 0
    
    
@remote_app.command("remove")
def remote_remove(name: str = typer.Argument(..., help="Name of the remote to remove")):
    """Remove a remote backend"""
    
    try:
        remote_manager = RemoteManager()
        
        # Check if remote exists
        if not remote_manager.get_remote(name):
            logger.error(f"Remote with name '{name}' does not exist")
            return 1
            
        # Remove the remote
        remote_manager.remove_remote(name)
        logger.success(f"Remote '{name}' removed successfully")
            
    except Exception as e:
        logger.exception(f"Failed to remove remote: {e}")
        return 1
        
    return 0
    
    
@remote_app.command("list")
def remote_list():
    """List all configured remotes"""
    
    try:
        remote_manager = RemoteManager()
        remotes = remote_manager.list_remotes()
        
        # Display the remotes
        logger.display_remotes(remotes)
            
    except Exception as e:
        logger.exception(f"Failed to list remotes: {e}")
        return 1
        
    return 0


def main():
    """Entry point for the CLI."""
    try:
        app()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    app()
