"""
LAN peer discovery via mDNS / Zeroconf.

Improvements over v1:
  - resolve() timeout reduced to 1 500 ms (was 3 000 ms) — kills the
    "10.3.5.165 taking too long" hang
  - Parallel resolve via ThreadPoolExecutor (max 8 workers)
  - Connection probe before advertising a peer as reachable
  - IPv4 preference when a peer advertises multiple addresses
  - Graceful degradation if zeroconf is not installed
"""

from __future__ import annotations

import logging
import socket
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from threading import Thread
from typing import Callable

log = logging.getLogger(__name__)

_SERVICE_TYPE = "_arqyv._tcp.local."
_SERVICE_NAME_PREFIX = "ARQYV-Share"
_RESOLVE_TIMEOUT_MS = 1_500      # was 3 000 — halved to stop long hangs
_PROBE_TIMEOUT_S = 1.5           # TCP connect probe before advertising peer
_MAX_RESOLVE_WORKERS = 8


def _probe_reachable(ip: str, port: int) -> bool:
    """Return True if ip:port accepts a TCP connection within _PROBE_TIMEOUT_S."""
    try:
        with socket.create_connection((ip, port), timeout=_PROBE_TIMEOUT_S):
            return True
    except OSError:
        return False


def _best_ipv4(addresses: list[bytes]) -> str | None:
    """Pick first valid IPv4 address from a list of packed bytes."""
    for addr in addresses:
        if len(addr) == 4:
            try:
                return socket.inet_ntoa(addr)
            except OSError:
                continue
    return None


@dataclass
class Peer:
    name: str
    ip: str
    port: int
    share_url: str
    reachable: bool = field(default=True)

    @property
    def display_name(self) -> str:
        return self.name.replace(f".{_SERVICE_TYPE}", "").replace(
            f"{_SERVICE_NAME_PREFIX}-", ""
        )


class PeerDiscovery:
    """Advertise ourselves and discover other ARQYV instances on LAN."""

    def __init__(self) -> None:
        self._zc: object | None = None
        self._info: object | None = None
        self._browser: object | None = None
        self._peers: dict[str, Peer] = {}
        self._on_found: Callable[[Peer], None] | None = None
        self._on_lost: Callable[[str], None] | None = None
        self._executor = ThreadPoolExecutor(
            max_workers=_MAX_RESOLVE_WORKERS, thread_name_prefix="arqyv-mdns"
        )

    def set_callbacks(
        self,
        on_found: Callable[[Peer], None],
        on_lost: Callable[[str], None],
    ) -> None:
        self._on_found = on_found
        self._on_lost = on_lost

    # ── Advertising ───────────────────────────────────────────────────────

    def advertise(self, port: int, token: str, hostname: str | None = None) -> bool:
        try:
            from zeroconf import ServiceInfo, Zeroconf  # type: ignore[import]

            name = hostname or socket.gethostname()
            service_name = f"{_SERVICE_NAME_PREFIX}-{name}.{_SERVICE_TYPE}"
            ip_bytes = socket.inet_aton(self._local_ip())

            self._info = ServiceInfo(
                _SERVICE_TYPE,
                service_name,
                addresses=[ip_bytes],
                port=port,
                properties={
                    "token": token.encode(),
                    "host": name.encode(),
                    "version": b"2",
                },
            )
            if self._zc is None:
                self._zc = Zeroconf()
            self._zc.register_service(self._info)  # type: ignore[attr-defined]
            log.info("mDNS: advertising %s on port %d", service_name, port)
            return True
        except ImportError:
            log.debug("zeroconf not installed.")
            return False
        except Exception:
            log.exception("mDNS advertise failed.")
            return False

    # ── Browsing ──────────────────────────────────────────────────────────

    def browse(self) -> bool:
        try:
            from zeroconf import ServiceBrowser, Zeroconf  # type: ignore[import]

            if self._zc is None:
                self._zc = Zeroconf()
            self._browser = ServiceBrowser(self._zc, _SERVICE_TYPE, self._make_listener())
            log.info("mDNS: browsing for ARQYV peers.")
            return True
        except ImportError:
            return False
        except Exception:
            log.exception("mDNS browse failed.")
            return False

    def stop(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)
        try:
            if self._zc:
                if self._info:
                    self._zc.unregister_service(self._info)  # type: ignore[attr-defined]
                self._zc.close()  # type: ignore[attr-defined]
        except Exception:
            pass
        self._zc = None
        self._info = None
        self._browser = None

    @property
    def peers(self) -> list[Peer]:
        return list(self._peers.values())

    # ── Internal ──────────────────────────────────────────────────────────

    def _make_listener(self) -> object:
        discovery = self

        class _Listener:
            def add_service(self, zc: object, stype: str, name: str) -> None:
                discovery._executor.submit(discovery._resolve, zc, stype, name)

            def remove_service(self, zc: object, stype: str, name: str) -> None:
                discovery._peers.pop(name, None)
                if discovery._on_lost:
                    discovery._on_lost(name)
                log.debug("Peer lost: %s", name)

            def update_service(self, zc: object, stype: str, name: str) -> None:
                discovery._executor.submit(discovery._resolve, zc, stype, name)

        return _Listener()

    def _resolve(self, zc: object, stype: str, name: str) -> None:
        """Resolve a peer — runs in thread pool with tight timeout."""
        try:
            from zeroconf import ServiceInfo  # type: ignore[import]

            info = ServiceInfo(stype, name)
            if not info.request(zc, _RESOLVE_TIMEOUT_MS):  # type: ignore[attr-defined]
                log.debug("mDNS resolve timeout for %s", name)
                return

            ip = _best_ipv4(info.addresses or [])
            if not ip:
                log.debug("No IPv4 address for peer %s", name)
                return

            props = {
                k.decode() if isinstance(k, bytes) else k:
                v.decode() if isinstance(v, bytes) else v
                for k, v in (info.properties or {}).items()
            }
            token = props.get("token", "")
            port = info.port

            # Quick TCP probe — skip unreachable peers immediately
            if not _probe_reachable(ip, port):
                log.debug("Peer %s (%s:%d) not reachable — skipped.", name, ip, port)
                return

            peer = Peer(
                name=name,
                ip=ip,
                port=port,
                share_url=f"http://{ip}:{port}/share/{token}",
                reachable=True,
            )
            self._peers[name] = peer
            if self._on_found:
                self._on_found(peer)
            log.info("Peer ready: %s @ %s:%d", peer.display_name, ip, port)

        except Exception as exc:
            log.debug("Could not resolve peer %s: %s", name, exc)

    @staticmethod
    def _local_ip() -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"
