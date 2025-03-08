"""Logging and console output utilities."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Initialize console
console = Console()

def success(message: str) -> None:
    """Log a success message."""
    console.print(f"[bold green]✓ SUCCESS:[/bold green] {message}")

def error(message: str) -> None:
    """Log an error message."""
    console.print(f"[bold red]✗ ERROR:[/bold red] {message}")

def exception(message: str) -> None:
    """Log an error message with it's traceback"""
    error(message)
    console.print_exception()

def info(message: str) -> None:
    """Log an information message."""
    console.print(f"[bold blue]ℹ INFO:[/bold blue] {message}")



def panel(*args, **kwargs):
    """Display a panel"""
    console.print(Panel.fit(*args, **kwargs))



def display_secret_value(name: str, value: str) -> None:
    """Display a secret value in a panel."""
    panel = Panel.fit(
        value,
        title=f"Secret: {name}",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)

def display_secrets_table(secrets) -> None:
    """Display a table of secrets."""
    if not secrets:
        info("No secrets found")
        return
    
    # Create a table to display secrets
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Tags")
    table.add_column("Created At")
    
    for secret in secrets:
        tags_str = ", ".join(secret.tags) if secret.tags else ""
        table.add_row(
            secret.name,
            tags_str,
            secret.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    console.print(table)

def display_welcome_banner() -> None:
    """Display a welcome banner for the CLI."""
    title = Text("Secret Manager", style="bold cyan")
    subtitle = Text("Secure secret management with AWS S3", style="italic")
    console.print(Panel.fit(f"{title}\n{subtitle}", border_style="cyan", padding=(1, 2)))

def display_project_registration_panel(current_dir) -> None:
    """Display a panel for project registration."""
    console.print(Panel.fit(f"Registering project in [bold]{current_dir}[/bold]", 
                        title="Project Registration", 
                        border_style="green"))