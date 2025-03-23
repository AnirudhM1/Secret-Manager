"""Logging and console output utilities."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from secret_manager.core.schemas import Backend, Remote, Secret

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
        console.print(
            f"\n[dim]Found {total_diffs} difference(s): "
            f"{len(diff_data['additions'])} addition(s), "
            f"{len(diff_data['deletions'])} deletion(s), "
            f"{len(diff_data['changes'])} change(s)[/dim]"
        )


def display_secrets(secrets_data: list[dict[str]], project_root: Path = None):
    """Display secrets in a nicely formatted table."""
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Environment", style="cyan")
    table.add_column("Secret File Path", style="green")
    table.add_column("Backend", style="magenta")
    table.add_column("Remote Path", style="yellow")

    has_secrets = False
    for item in secrets_data:
        has_secrets = True
        env_name = item["environment"]
        secret: Secret = item["secret"]

        # For S3 backend, show the S3 key if available
        remote_path = ""
        if secret.backend == Backend.S3 and secret.s3_key:
            remote_path = f"s3://{secret.s3_key}"

        table.add_row(f"[bold]{env_name}[/bold]", str(secret.path), secret.backend.value, remote_path)

    if has_secrets:
        title = "Secrets"
        if project_root:
            title = f"[bold]Secrets for project[/bold]: {project_root}"

        console.print(Panel(table, title=title, border_style="cyan", padding=(1, 2)))
    else:
        message = "No secrets are currently tracked"
        if project_root:
            message = f"No secrets are currently tracked for project at {project_root}"
        info(message)


def display_remotes(remotes: list[Remote]):
    """Display remotes in a nicely formatted table."""
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("AWS Region", style="magenta")

    has_remotes = False
    for remote in remotes:
        has_remotes = True
        aws_region = remote.aws_config.AWS_REGION if remote.aws_config else "N/A"

        table.add_row(f"[bold]{remote.name}[/bold]", remote.type.value, aws_region)

    if has_remotes:
        console.print(Panel(table, title="[bold]Configured Remotes[/bold]", border_style="cyan", padding=(1, 2)))
    else:
        info("No remotes are currently configured")


def display_remote_details(remote: Remote):
    """Display detailed information about a specific remote."""

    table = Table(title=f"Remote: {remote.name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Name", remote.name)
    table.add_row("Type", remote.type.value)

    if remote.aws_config:
        table.add_row("AWS Region", remote.aws_config.AWS_REGION)

        # Show redacted credentials for security
        table.add_row("AWS Access Key", remote.aws_config.AWS_ACCESS_KEY_ID)
        table.add_row("AWS Secret Access Key", f"**********{remote.aws_config.AWS_SECRET_ACCESS_KEY[-4:]}")

    console.print(table)
    console.print()
