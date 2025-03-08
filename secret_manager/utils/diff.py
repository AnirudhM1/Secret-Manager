"""Utility for computing differences between files."""

import re


def filter_content(content: list[str]):
    """Pre-Process the content of a file before computing the diff"""

    # Patterns to match: 'key=value' or 'export key=value'
    key_value_pattern = re.compile(r"^[A-Za-z0-9_]+=.+$")
    export_pattern = re.compile(r"^export\s+([A-Za-z0-9_]+=.+)$")

    filtered_lines = []
    for line in content:
        # For lines with inline comments, keep only the part before the comment
        if "#" in line:
            line, _ = line.split("#", 1)

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


def compute_diff(source_content: list[str], target_content: list[str]) -> dict:
    """Compute the diff between two file contents treating each line as a key-value pair"""

    # Get filtered content
    filtered_source = filter_content(source_content)
    filtered_target = filter_content(target_content)

    # Create dictionaries with key-value pairs
    source_dict = {}
    target_dict = {}

    for line in filtered_source:
        key, value = line.split("=", 1)
        source_dict[key] = value

    for line in filtered_target:
        key, value = line.split("=", 1)
        target_dict[key] = value

    # Find additions, deletions and changes
    source_keys = set(source_dict.keys())
    target_keys = set(target_dict.keys())

    added_keys = target_keys - source_keys
    deleted_keys = source_keys - target_keys
    common_keys = source_keys & target_keys

    # Create structured diff data
    diff_data = {
        "additions": [(key, target_dict[key]) for key in added_keys],
        "deletions": [(key, source_dict[key]) for key in deleted_keys],
        "changes": [(key, source_dict[key], target_dict[key]) for key in common_keys if source_dict[key] != target_dict[key]],
    }

    return diff_data
