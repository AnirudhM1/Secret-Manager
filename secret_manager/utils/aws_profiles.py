"""Utilities for handling AWS profiles and credentials."""

import configparser
from pathlib import Path
from typing import Optional


def read_aws_profiles() -> list[str]:
    """Read AWS profiles from ~/.aws/credentials and ~/.aws/config files.
    
    Returns:
        List of profile names
    """
    aws_dir = Path.home() / ".aws"
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"
    
    profiles = set()
    
    # Read profiles from credentials file
    if credentials_file.exists():
        credentials = configparser.ConfigParser()
        credentials.read(credentials_file)
        for section in credentials.sections():
            profiles.add(section)
    
    # Read profiles from config file
    if config_file.exists():
        config = configparser.ConfigParser()
        config.read(config_file)
        for section in config.sections():
            # In config file, profiles are named "profile xxx" except for 'default'
            if section.startswith("profile "):
                profiles.add(section[8:])  # Remove "profile " prefix
            else:
                profiles.add(section)
    
    return list(profiles)


def get_aws_profile_credentials(profile_name: str) -> tuple[Optional[str], Optional[str], str]:
    """Get AWS credentials from a specific profile.
    
    Args:
        profile_name: Name of the AWS profile
        
    Returns:
        Tuple of (access_key, secret_key, region)
    """
    aws_dir = Path.home() / ".aws"
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"
    
    # Initialize with default values
    access_key = None
    secret_key = None
    region = "us-east-1"  # Default AWS region
    
    # Read credentials
    if credentials_file.exists():
        credentials = configparser.ConfigParser()
        credentials.read(credentials_file)
        if profile_name in credentials:
            access_key = credentials[profile_name].get("aws_access_key_id")
            secret_key = credentials[profile_name].get("aws_secret_access_key")
    
    # Read region from config
    if config_file.exists():
        config = configparser.ConfigParser()
        config.read(config_file)
        config_section = f"profile {profile_name}" if profile_name != "default" else "default"
        if config_section in config:
            if "region" in config[config_section]:
                region = config[config_section]["region"]
    
    return access_key, secret_key, region
