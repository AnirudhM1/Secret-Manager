"""Interactive wizards for remote configuration."""

import questionary
from typing import Optional
from pathlib import Path

from secret_manager.core.schemas import AWSConfig
from secret_manager.core.remotes import RemoteManager
from secret_manager.utils import logger
from secret_manager.utils.selection import select_from_list
from secret_manager.utils.aws_profiles import read_aws_profiles, get_aws_profile_credentials


def configure_aws_backend() -> Optional[AWSConfig]:
    """Interactive wizard to configure AWS backend"""

    # Ask whether to use AWS profile or manual credentials
    credential_method = select_from_list(
        message="How would you like to provide AWS credentials?",
        choices=["Use AWS Profile", "Enter manually"]
    )
    
    aws_access_key_id = None
    aws_secret_access_key = None
    aws_region = "ap-south-1"  # Default region
    
    if credential_method == "Use AWS Profile":
        # Read available AWS profiles
        profiles = read_aws_profiles()
        
        if not profiles:
            logger.error("No AWS profiles found. Please check your ~/.aws directory or enter credentials manually.")
            return None
        
        # Prompt user to select a profile
        selected_profile = select_from_list(message="Select AWS profile:" ,choices=profiles)
        
        # Get credentials for selected profile
        aws_access_key_id, aws_secret_access_key, aws_region = get_aws_profile_credentials(selected_profile)
        
        if not aws_access_key_id or not aws_secret_access_key:
            logger.error(f"Could not find credentials for profile {selected_profile}")
            return None
        
    else:  # Enter manually
        # Prompt for credentials
        aws_access_key_id = questionary.text("AWS Access Key ID:").ask()
        if not aws_access_key_id:
            logger.error("AWS Access Key ID is required")
            return None
        
        aws_secret_access_key = questionary.password("AWS Secret Access Key:").ask()
        if not aws_secret_access_key:
            logger.error("AWS Secret Access Key is required")
            return None
        
        aws_region = questionary.text("AWS Region (default: us-east-1):").ask() or "us-east-1"
    
    # Create and return AWS config
    return AWSConfig(
        AWS_ACCESS_KEY_ID=aws_access_key_id,
        AWS_SECRET_ACCESS_KEY=aws_secret_access_key,
        AWS_REGION=aws_region
    )


def select_or_create_remote() -> tuple[str, bool]:
    """Interactive wizard to select an existing remote or create a new one.
    
    Returns:
        Tuple of (remote_name, is_new_remote)
    """
    remote_manager = RemoteManager()
    remotes = remote_manager.list_remotes()
    
    # Prepare choice list
    choices = ["Create new remote"]
    if remotes:
        choices.extend([f"{r.name} ({r.type.value})" for r in remotes])
    
    # Prompt user to select a remote or create a new one
    selection = select_from_list(
        message="Select a remote or create a new one:",
        choices=choices
    )
    
    # Handle selection
    if selection == "Create new remote":
        # Ask for remote name
        remote_name = questionary.text("Enter name for the new remote:").ask()
        if not remote_name:
            logger.error("Remote name cannot be empty")
            return None, False
        
        return remote_name, True
    else:
        # Extract remote name from selection (format: "name (type)")
        remote_name = selection.split(" (")[0]
        return remote_name, False


def configure_s3_key():
    """Interactive wizard to configure S3 key for a secret"""
    
    # Prompt user for S3 key with default suggestion
    s3_key: str = questionary.text("Enter S3 key for this secret: ").ask()

    # If the s3_key is of the form s3://bucket/path/to/file, extract bucket/path/to/file
    if s3_key.startswith("s3://"):
        s3_key = s3_key.replace("s3://", "", count=1)

    return s3_key
