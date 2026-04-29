"""Abstract base class for all cloud storage providers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass
class CloudFile:
    id: str
    name: str
    path: str
    size_bytes: int
    mime_type: str | None
    modified_at: str | None
    download_url: str | None = None


class CloudProvider(ABC):
    """Interface every cloud backend must implement."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def authenticate(self) -> bool:
        """Trigger OAuth flow or load cached token. Returns True on success."""
        ...

    @abstractmethod
    def is_authenticated(self) -> bool: ...

    @abstractmethod
    def list_files(self, remote_path: str = "/", recursive: bool = False) -> list[CloudFile]: ...

    @abstractmethod
    def download_file(self, cloud_file: CloudFile, local_dest: Path) -> bool: ...

    @abstractmethod
    def upload_file(self, local_path: Path, remote_dest: str) -> CloudFile | None: ...

    @abstractmethod
    def delete_file(self, cloud_file: CloudFile) -> bool: ...

    def sync_folder(self, remote_path: str, local_path: Path, download_only: bool = True) -> int:
        """Sync remote folder to local. Returns number of files synced."""
        local_path.mkdir(parents=True, exist_ok=True)
        files = self.list_files(remote_path, recursive=True)
        synced = 0
        for cf in files:
            dest = local_path / cf.name
            if not dest.exists():
                if self.download_file(cf, dest):
                    synced += 1
        log.info("Synced %d files from %s:%s → %s", synced, self.name, remote_path, local_path)
        return synced
