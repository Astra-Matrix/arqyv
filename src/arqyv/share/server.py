"""Ephemeral HTTP file server.

Spins up a one-shot HTTP server on a random free port that serves a
single file (or a directory zip) for download.  The server shuts itself
down after either:
  - The file has been downloaded `max_downloads` times, or
  - `timeout_seconds` have elapsed with no new request.

Uses only Python stdlib — zero extra dependencies.
"""

from __future__ import annotations

import hashlib
import http.server
import logging
import os
import socket
import threading
import time
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Callable

log = logging.getLogger(__name__)


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _local_ip() -> str:
    """Best-guess LAN IP address (prefers non-loopback)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


class ShareServer:
    """One-shot file server with token authentication.

    Usage:
        server = ShareServer(path)
        server.start()
        print(server.share_url)   # hand this to the recipient
        # server auto-stops after download or timeout
    """

    def __init__(
        self,
        path: Path,
        max_downloads: int = 10,
        timeout_seconds: int = 3600,
        on_download: Callable[[str], None] | None = None,
    ) -> None:
        self._path = path
        self._max_downloads = max_downloads
        self._timeout = timeout_seconds
        self._on_download = on_download
        self._token = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        self._port = _find_free_port()
        self._ip = _local_ip()
        self._download_count = 0
        self._last_request = time.time()
        self._server: http.server.HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._stopped = threading.Event()

    @property
    def share_url(self) -> str:
        return f"http://{self._ip}:{self._port}/share/{self._token}"

    @property
    def token(self) -> str:
        return self._token

    @property
    def port(self) -> int:
        return self._port

    @property
    def local_ip(self) -> str:
        return self._ip

    @property
    def download_count(self) -> int:
        return self._download_count

    def start(self) -> None:
        engine = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, fmt: str, *args: object) -> None:  # type: ignore[override]
                pass  # suppress access log noise

            def do_GET(self) -> None:  # noqa: N802
                expected = f"/share/{engine._token}"
                if self.path != expected and not self.path.startswith(expected + "?"):
                    self.send_error(404)
                    return

                engine._last_request = time.time()
                path = engine._path

                # Serve directory as zip
                if path.is_dir():
                    data = engine._zip_directory(path)
                    filename = path.name + ".zip"
                    content_type = "application/zip"
                else:
                    data = path.read_bytes()
                    filename = path.name
                    content_type = "application/octet-stream"

                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.send_header(
                    "Content-Disposition", f'attachment; filename="{filename}"'
                )
                self.end_headers()
                self.wfile.write(data)

                engine._download_count += 1
                log.info("File served (%d/%d): %s to %s",
                         engine._download_count, engine._max_downloads,
                         filename, self.client_address[0])
                if engine._on_download:
                    engine._on_download(self.client_address[0])
                if engine._download_count >= engine._max_downloads:
                    engine.stop()

        self._server = http.server.HTTPServer(("", self._port), Handler)
        self._thread = threading.Thread(target=self._serve_loop, daemon=True)
        self._thread.start()

        # Watchdog: stop after timeout with no requests
        def watchdog() -> None:
            while not self._stopped.is_set():
                time.sleep(10)
                if time.time() - self._last_request > self._timeout:
                    log.info("ShareServer timeout — stopping.")
                    self.stop()

        threading.Thread(target=watchdog, daemon=True).start()
        log.info("ShareServer started: %s", self.share_url)

    def stop(self) -> None:
        self._stopped.set()
        if self._server:
            self._server.shutdown()
            self._server = None
        log.info("ShareServer stopped.")

    @property
    def is_running(self) -> bool:
        return not self._stopped.is_set() and self._server is not None

    def _serve_loop(self) -> None:
        assert self._server
        self._server.serve_forever()

    @staticmethod
    def _zip_directory(path: Path) -> bytes:
        buf = BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in path.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(path))
        return buf.getvalue()
