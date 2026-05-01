"""
Ephemeral HTTP file server with streaming, progress callbacks, and
connection-level timeouts.

Zero external dependencies — stdlib only.

Key improvements over v1:
  - Streaming delivery (no full file read into RAM)
  - Per-connection 10 s socket timeout (kills stale `10.3.5.165` hangs)
  - Transfer-speed tracking via on_progress callback
  - Proper HEAD support for clients that probe first
  - Range-request support (seek to byte offset without re-serving)
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

_CHUNK = 65_536          # 64 KB streaming chunks
_CONN_TIMEOUT = 10       # seconds — kills stalled peer connections immediately


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _local_ip() -> str:
    """Best-guess non-loopback LAN IP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


class ShareServer:
    """
    One-shot streaming file server with token auth.

    Callbacks
    ---------
    on_download(ip)           called once per completed download
    on_progress(sent, total)  called every chunk (~64 KB) during transfer
    """

    def __init__(
        self,
        path: Path,
        max_downloads: int = 50,
        timeout_seconds: int = 7200,
        on_download: Callable[[str], None] | None = None,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> None:
        self._path = path
        self._max_downloads = max_downloads
        self._timeout = timeout_seconds
        self._on_download = on_download
        self._on_progress = on_progress
        self._token = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        self._port = _find_free_port()
        self._ip = _local_ip()
        self._download_count = 0
        self._bytes_sent = 0
        self._last_request = time.monotonic()
        self._server: http.server.HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._stopped = threading.Event()
        self._lock = threading.Lock()

    # ── Public properties ─────────────────────────────────────────────────

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

    @property
    def bytes_sent(self) -> int:
        return self._bytes_sent

    @property
    def is_running(self) -> bool:
        return not self._stopped.is_set() and self._server is not None

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def start(self) -> None:
        engine = self

        class _Handler(http.server.BaseHTTPRequestHandler):
            timeout = _CONN_TIMEOUT  # per-connection socket timeout

            def log_message(self, fmt: str, *args: object) -> None:  # type: ignore[override]
                pass  # silence default access log

            def log_error(self, fmt: str, *args: object) -> None:  # type: ignore[override]
                log.debug("ShareServer handler: " + fmt, *args)

            def _check_token(self) -> bool:
                ok = (
                    self.path == f"/share/{engine._token}"
                    or self.path.startswith(f"/share/{engine._token}?")
                )
                if not ok:
                    self.send_error(404)
                return ok

            def do_HEAD(self) -> None:  # noqa: N802
                if not self._check_token():
                    return
                size = self._file_size()
                self.send_response(200)
                self._send_file_headers(size, preview=False)
                self.end_headers()

            def do_GET(self) -> None:  # noqa: N802
                if not self._check_token():
                    return
                if engine._stopped.is_set():
                    self.send_error(503, "Share session ended")
                    return

                engine._last_request = time.monotonic()
                path = engine._path

                # Build payload (stream file or zip directory)
                if path.is_dir():
                    data = engine._zip_directory(path)
                    total = len(data)
                    stream = BytesIO(data)
                    filename = path.name + ".zip"
                    ctype = "application/zip"
                else:
                    total = path.stat().st_size
                    filename = path.name
                    ctype = "application/octet-stream"
                    stream = None  # will open file directly

                # Parse Range header
                start = 0
                range_hdr = self.headers.get("Range", "")
                if range_hdr.startswith("bytes="):
                    try:
                        part = range_hdr[6:].split("-")[0]
                        start = int(part)
                    except ValueError:
                        start = 0

                send_total = total - start
                if start > 0:
                    self.send_response(206)
                    self.send_header("Content-Range", f"bytes {start}-{total-1}/{total}")
                else:
                    self.send_response(200)

                self._send_file_headers(send_total, filename=filename, ctype=ctype)
                self.end_headers()

                # Stream to client
                try:
                    sent = 0
                    if stream:
                        stream.seek(start)
                        while True:
                            chunk = stream.read(_CHUNK)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            sent += len(chunk)
                            with engine._lock:
                                engine._bytes_sent += len(chunk)
                            if engine._on_progress:
                                engine._on_progress(engine._bytes_sent, total)
                    else:
                        with open(path, "rb") as fh:
                            fh.seek(start)
                            while True:
                                chunk = fh.read(_CHUNK)
                                if not chunk:
                                    break
                                self.wfile.write(chunk)
                                sent += len(chunk)
                                with engine._lock:
                                    engine._bytes_sent += len(chunk)
                                if engine._on_progress:
                                    engine._on_progress(sent, total)

                    with engine._lock:
                        engine._download_count += 1

                    log.info(
                        "Served %s → %s  (%d/%d dl, %.1f KB)",
                        filename,
                        self.client_address[0],
                        engine._download_count,
                        engine._max_downloads,
                        sent / 1024,
                    )
                    if engine._on_download:
                        engine._on_download(self.client_address[0])
                    if engine._download_count >= engine._max_downloads:
                        engine.stop()

                except (BrokenPipeError, ConnectionResetError, TimeoutError) as exc:
                    log.debug("Client %s disconnected: %s", self.client_address[0], exc)

            # ── helpers ────────────────────────────────────────────────────

            def _file_size(self) -> int:
                p = engine._path
                return p.stat().st_size if p.is_file() else 0

            def _send_file_headers(
                self,
                size: int,
                filename: str = "",
                ctype: str = "application/octet-stream",
                preview: bool = False,
            ) -> None:
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(size))
                self.send_header("Accept-Ranges", "bytes")
                if filename and not preview:
                    self.send_header(
                        "Content-Disposition", f'attachment; filename="{filename}"'
                    )

        # HTTPServer with SO_REUSEADDR
        self._server = http.server.HTTPServer(("", self._port), _Handler)
        self._server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._thread = threading.Thread(target=self._serve_loop, daemon=True, name="arqyv-share")
        self._thread.start()

        # Inactivity watchdog
        def _watchdog() -> None:
            while not self._stopped.wait(timeout=15):
                idle = time.monotonic() - self._last_request
                if idle > self._timeout:
                    log.info("ShareServer idle timeout — stopping.")
                    self.stop()
                    break

        threading.Thread(target=_watchdog, daemon=True, name="arqyv-share-wd").start()
        log.info("ShareServer ready: %s", self.share_url)

    def stop(self) -> None:
        if self._stopped.is_set():
            return
        self._stopped.set()
        if self._server:
            self._server.shutdown()
            self._server = None
        log.info("ShareServer stopped.")

    def _serve_loop(self) -> None:
        assert self._server
        self._server.serve_forever()

    # ── Directory support ─────────────────────────────────────────────────

    @staticmethod
    def _zip_directory(path: Path) -> bytes:
        buf = BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in path.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(path))
        return buf.getvalue()
