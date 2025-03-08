"""Logging and console output utilities."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from secret_manager.core.schemas import Secret

# Initialize console
console = Console()

def success(message: str) -> None:
    """Log a success message."""
    console.print(f"[bold green]✓ SUCCESS:[/bold green] {message}")

def error(message: str) -> None:
    """Log an error message."""
    console.print(f"[bold red]✗ ERROR:[/bold red] {message}")

def exception(message: str) -> None:
    """Log an error message with its traceback."""
    error(message)
    console.print_exception()

def info(message: str) -> None:
    """Log an information message."""
    console.print(f"[bold blue]ℹ INFO:[/bold blue] {message}")



def display_diff(diff_data: dict, source_env: str, target_env: str):
    """Display formatted diff output between two environments.
    
    Args:
        diff_data: Dictionary with keys 'additions', 'deletions', and 'changes'
        source_env: Source environment name
        target_env: Target environment name
    """
    console.print(f"\n[bold]Comparing secrets:[/bold] {source_env} → {target_env}\n")
    
    # Display additions (green)
    for key, value in sorted(diff_data["additions"]):
        console.print(f"[bold green]+ {key}={value}[/bold green]")
    
    # Display deletions (red)
    for key, value in sorted(diff_data["deletions"]):
        console.print(f"[bold red]- {key}={value}[/bold red]")
    
    # Display changes (yellow)
    for key, old_value, new_value in sorted(diff_data["changes"]):
        console.print(f"[bold yellow]~ {key}=[/bold yellow][red]{old_value}[/red] → [green]{new_value}[/green]")
    
    # Print summary
    total_diffs = sum(len(items) for items in diff_data.values())
    if total_diffs > 0:
        console.print(f"\n[dim]Found {total_diffs} difference(s): "
                     f"{len(diff_data['additions'])} addition(s), "
                     f"{len(diff_data['deletions'])} deletion(s), "
                     f"{len(diff_data['changes'])} change(s)[/dim]")


def display_secrets(secrets_data: list[dict[str]], project_root: Path = None):
    """Display secrets in a nicely formatted table."""
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Environment", style="cyan")
    table.add_column("Secret File Path", style="green")
    table.add_column("Backend", style="magenta")
    
    has_secrets = False
    for item in secrets_data:
        has_secrets = True
        env_name = item["environment"]
        secret: Secret = item["secret"]
        
        table.add_row(
            f"[bold]{env_name}[/bold]",
            str(secret.path),
            secret.backend.value
        )
    
    if has_secrets:
        title = "Secrets"
        if project_root:
            title = f"[bold]Secrets for project[/bold]: {project_root}"
            
        console.print(Panel(
            table,
            title=title,
            border_style="cyan",
            padding=(1, 2)
        ))
    else:
        message = "No secrets are currently tracked"
        if project_root:
            message = f"No secrets are currently tracked for project at {project_root}"
        info(message)