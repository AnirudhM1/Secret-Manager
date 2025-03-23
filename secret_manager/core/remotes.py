import json
from pathlib import Path

from .constants import DEFAULT_BASE_DIR, REMOTES_FILE
from .schemas import Remote


class RemoteManager:
    """Manages remote configurations for secret syncing."""

    def __init__(self, base_dir: Path = None):
        base_dir = base_dir or Path(DEFAULT_BASE_DIR)

        self.config_dir = base_dir.expanduser()
        self.remotes_file = self.config_dir / REMOTES_FILE

        self._ensure_config_dir()
        self.remotes = self._load_remotes()

    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.remotes_file.exists():
            json.dump([], self.remotes_file.open("w"), indent=4)

    def _load_remotes(self) -> dict[str, Remote]:
        """Load remotes from the remotes file."""
        if not self.remotes_file.exists():
            return {}

        remotes_data = json.load(self.remotes_file.open())

        # Deserialize the remotes
        remotes = [Remote.deserialize(remote) for remote in remotes_data]
        remotes_dict = {remote.name: remote for remote in remotes}

        return remotes_dict

    def _save_remotes(self):
        """Save remotes to the remotes file."""
        # Serialize the remotes
        remotes_data = [remote.serialize() for remote in self.remotes.values()]
        json.dump(remotes_data, self.remotes_file.open("w"), indent=4)

    def get_remote(self, name: str):
        """Get a remote by name."""
        return self.remotes.get(name)

    def add_remote(self, remote: Remote):
        """Add a new remote."""
        if remote.name in self.remotes:
            raise ValueError(f"Remote already exists with name: {remote.name}")

        self.remotes[remote.name] = remote
        self._save_remotes()

    def remove_remote(self, name: str):
        """Remove a remote by name."""
        if name not in self.remotes:
            raise ValueError(f"Remote not found: {name}")

        del self.remotes[name]
        self._save_remotes()

    def list_remotes(self) -> list[Remote]:
        """List all remotes"""
        return list(self.remotes.values())
