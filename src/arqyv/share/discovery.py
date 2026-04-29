"""LAN peer discovery via mDNS / Zeroconf.

Advertises the local ARQYV share server so other ARQYV instances on
the same network can find it without typing an IP address.

Requires the `zeroconf` package (pure Python, installed automatically).
Gracefully degrades to IP-only sharing if zeroconf is unavailable.
"""

from __future__ import annotations

import logging
import socket
from dataclasses import dataclass
from threading import Thread
from typing import Callable

log = logging.getLogger(__name__)

_SERVICE_TYPE = "_arqyv._tcp.local."
_SERVICE_NAME_PREFIX = "ARQYV-Share"


@dataclass
class Peer:
    name: str
    ip: str
    port: int
    share_url: str

    @property
    def display_name(self) -> str:
        return self.name.replace(f".{_SERVICE_TYPE}", "")


class PeerDiscovery:
    """Advertise ourselves and discover other ARQYV instances on LAN."""

    def __init__(self) -> None:
        self._zc: object | None = None
        self._info: object | None = None
        self._browser: object | None = None
        self._peers: dict[str, Peer] = {}
        self._on_found: Callable[[Peer], None] | None = None
        self._on_lost: Callable[[str], None] | None = None

    def set_callbacks(
        self,
        on_found: Callable[[Peer], None],
        on_lost: Callable[[str], None],
    ) -> None:
        self._on_found = on_found
        self._on_lost = on_lost

    def advertise(self, port: int, token: str, hostname: str | None = None) -> bool:
        """Advertise this machine's share server on the LAN."""
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
                    "version": b"1",
                },
            )
            self._zc = Zeroconf()
            self._zc.register_service(self._info)  # type: ignore[attr-defined]
            log.info("mDNS: advertising %s on port %d", service_name, port)
            return True
        except ImportError:
            log.debug("zeroconf not installed; LAN discovery unavailable.")
            return False
        except Exception:
            log.exception("mDNS advertise failed.")
            return False

    def browse(self) -> bool:
        """Start browsing for other ARQYV peers."""
        try:
            from zeroconf import ServiceBrowser, Zeroconf  # type: ignore[import]

            if self._zc is None:
                self._zc = Zeroconf()

            listener = self._make_listener()
            self._browser = ServiceBrowser(self._zc, _SERVICE_TYPE, listener)
            log.info("mDNS: browsing for peers.")
            return True
        except ImportError:
            return False
        except Exception:
            log.exception("mDNS browse failed.")
            return False

    def stop(self) -> None:
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

    # ── Internal ───────────────────────────────────────────────────────────

    def _make_listener(self) -> object:
        discovery = self

        class _Listener:
            def add_service(self, zc: object, stype: str, name: str) -> None:
                Thread(target=self._resolve, args=(zc, stype, name), daemon=True).start()

            def remove_service(self, zc: object, stype: str, name: str) -> None:
                discovery._peers.pop(name, None)
                if discovery._on_lost:
                    discovery._on_lost(name)
                log.debug("Peer lost: %s", name)

            def update_service(self, zc: object, stype: str, name: str) -> None:
                pass

            def _resolve(self, zc: object, stype: str, name: str) -> None:
                try:
                    from zeroconf import ServiceInfo  # type: ignore[import]
                    info = ServiceInfo(stype, name)
                    if info.request(zc, 3000):  # type: ignore[attr-defined]
                        props = {
                            k.decode(): v.decode() if isinstance(v, bytes) else v
                            for k, v in (info.properties or {}).items()
                        }
                        ip = socket.inet_ntoa(info.addresses[0])
                        token = props.get("token", "")
                        peer = Peer(
                            name=name,
                            ip=ip,
                            port=info.port,
                            share_url=f"http://{ip}:{info.port}/share/{token}",
                        )
                        discovery._peers[name] = peer
                        if discovery._on_found:
                            discovery._on_found(peer)
                        log.info("Peer found: %s @ %s:%d", name, ip, info.port)
                except Exception:
                    log.debug("Could not resolve peer %s", name)

        return _Listener()

    @staticmethod
    def _local_ip() -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"
