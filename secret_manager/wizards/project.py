"""Interactive wizards for project configuration."""

from pathlib import Path
from typing import Tuple, Optional

from secret_manager.core.schemas import SecretMode
from secret_manager.utils.selection import select_from_list


def select_environment(prompt_message: str = None) -> SecretMode:
    """Interactive wizard to select an environment.
    
    Args:
        prompt_message: Custom message for the prompt
        
    Returns:
        Selected SecretMode
    """
    message = prompt_message or "Select environment:"
    env = select_from_list(
        message=message,
        choices=["local", "dev", "prod"]
    )
    return SecretMode(env)


def resolve_comparison_environments(source: Optional[str] = None, target: Optional[str] = None) -> Tuple[SecretMode, SecretMode]:
    """Resolve source and target environments for comparison, prompting if needed.
    
    Args:
        source: Source environment name (optional)
        target: Target environment name (optional)
        
    Returns:
        Tuple of (source_mode, target_mode)
    """
    available_envs = ["local", "dev", "prod"]
    
    # Case 1: Both source and target are provided
    if source and target:
        return SecretMode(source), SecretMode(target)
    
    # Case 2: Only source is provided, need to select target
    if source:
        source_mode = SecretMode(source)
        # Filter out source from available targets
        target_choices = [env for env in available_envs if env != source]
        default_target = "dev" if "dev" in target_choices else target_choices[0]
        
        target = select_from_list(
            message="Select target environment:",
            choices=target_choices,
            default=default_target
        )
        target_mode = SecretMode(target)
        return source_mode, target_mode
    
    # Case 3: Only target is provided, need to select source
    if target:
        target_mode = SecretMode(target)
        # Filter out target from available sources
        source_choices = [env for env in available_envs if env != target]
        default_source = "local" if "local" in source_choices else source_choices[0]
        
        source = select_from_list(
            message="Select source environment:",
            choices=source_choices,
            default=default_source
        )
        source_mode = SecretMode(source)
        return source_mode, target_mode
    
    # Case 4: Neither provided, select both
    source = select_from_list(
        message="Select source environment:",
        choices=available_envs,
        default="local"
    )
    
    # Filter out the source from target choices
    target_choices = [env for env in available_envs if env != source]
    default_target = "dev" if "dev" in target_choices else target_choices[0]
    
    target = select_from_list(
        message="Select target environment:",
        choices=target_choices,
        default=default_target
    )
    
    return SecretMode(source), SecretMode(target)
