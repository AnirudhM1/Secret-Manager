"""Utility functions for user selections and input gathering."""

import questionary
from typing import Optional


def select_from_list(
    message: str,
    choices: list[str],
    default: Optional[str] = None
) -> str:
    """Select an option from a list.
    
    Args:
        message: The message to display.
        choices: The list of choices to select from.
        default: The default choice, if any.
    
    Returns:
        The selected choice.
    """
    return questionary.select(
        message=message,
        choices=choices,
        default=default
    ).ask()

