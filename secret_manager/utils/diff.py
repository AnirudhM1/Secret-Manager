"""Utility for computing differences between files."""

import difflib
import re


def filter_content(content: list[str]):
    """Pre-Process the content of a file before computing the diff"""
    
    # Patterns to match: 'key=value' or 'export key=value'
    key_value_pattern = re.compile(r'^[A-Za-z0-9_]+=.+$')
    export_pattern = re.compile(r'^export\s+([A-Za-z0-9_]+=.+)$')

    filtered_lines = []
    for line in content:
        # For lines with inline comments, keep only the part before the comment
        if '#' in line:
            line, _ = line.split('#', 1)

        # Skip completely empty lines
        line = line.strip()
        if not line:
            continue
        
        # Check for export pattern and standardize to key=value format
        export_match = export_pattern.match(line)
        if export_match:
            # Extract the key=value part from "export key=value"
            line = export_match.group(1)
            filtered_lines.append(line)
            continue
            
        # Check for standard key=value pattern
        if key_value_pattern.match(line):
            filtered_lines.append(line)
            
    return filtered_lines


def compute_diff(source_content: list[str], target_content: list[str]) -> list[str]:
    """Compute the diff between two file contents"""

    filtered_source = filter_content(source_content)
    filtered_target = filter_content(target_content)

    full_diff = difflib.unified_diff(
        filtered_source,
        filtered_target,
        n=0  # Set context lines to zero
    )
    
    # Still need to filter headers but don't need to filter context lines
    changes_only = []
    for line in full_diff:
        # Skip file headers and chunk headers
        if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
            continue
        changes_only.append(line)
    
    return changes_only

