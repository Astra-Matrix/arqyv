"""ShareManager — single public API for file sharing.

Usage:
    mgr = ShareManager(config)
    session = mgr.share_file(Path("/music/song.flac"))
    print(session.url)      # hand to recipient
    print(session.qr_pixmap)  # show QR in UI

The session stops automatically after all downloads or timeout.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from PyQt6.QtGui import QPixmap

from arqyv.config import AppConfig
from arqyv.share.server import ShareServer

log = logging.getLogger(__name__)


@dataclass
class ShareSession:
    path: Path
    url: str
    token: str
    server: ShareServer
    qr_pixmap: QPixmap | None = None
    download_count: int = 0
    on_download: Callable[[str], None] | None = None

    def stop(self) -> None:
        self.server.stop()

    @property
    def is_active(self) -> bool:
        return self.server.is_running


class ShareManager:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._sessions: list[ShareSession] = []
        self._discovery_active = False

    def share_file(
        self,
        path: Path,
        max_downloads: int = 50,
        timeout_seconds: int = 7200,
        on_download: Callable[[str], None] | None = None,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> ShareSession:
        """Start serving a file and return the ShareSession with URL + QR."""
        if not path.exists():
            raise FileNotFoundError(path)

        server = ShareServer(
            path=path,
            max_downloads=max_downloads,
            timeout_seconds=timeout_seconds,
            on_download=on_download,
            on_progress=on_progress,
        )
        server.start()

        from arqyv.share.qr import generate_pixmap
        qr = generate_pixmap(server.share_url, size=300)

        session = ShareSession(
            path=path,
            url=server.share_url,
            token=server.token,
            server=server,
            qr_pixmap=qr,
            on_download=on_download,
        )
        self._sessions.append(session)
        log.info("Sharing: %s → %s", path.name, server.share_url)
        return session

    def stop_all(self) -> None:
        for s in self._sessions:
            s.stop()
        self._sessions.clear()

    def active_sessions(self) -> list[ShareSession]:
        self._sessions = [s for s in self._sessions if s.is_active]
        return self._sessions

    def start_discovery(self) -> None:
        """Begin advertising and browsing for LAN peers."""
        try:
            from arqyv.share.discovery import PeerDiscovery
            self._discovery = PeerDiscovery()
            self._discovery.browse()
            self._discovery_active = True
        except Exception:
            log.debug("LAN discovery unavailable.")
