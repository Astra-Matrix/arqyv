"""Logging configuration for ARQYV.

Sets up a Rich-enhanced console handler and a rotating file handler.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path


def configure_logging(debug: bool = False, log_dir: Path | None = None) -> None:
    level = logging.DEBUG if debug else logging.INFO

    handlers: list[logging.Handler] = []

    try:
        from rich.logging import RichHandler  # type: ignore[import]
        console = RichHandler(
            level=level,
            rich_tracebacks=True,
            tracebacks_show_locals=debug,
            show_time=True,
            show_path=debug,
        )
        handlers.append(console)
    except ImportError:
        stream = logging.StreamHandler()
        stream.setLevel(level)
        stream.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        handlers.append(stream)

    if log_dir is None:
        from platformdirs import user_log_dir
        log_dir = Path(user_log_dir("ARQYV", "Alaustrup"))
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "arqyv.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    handlers.append(file_handler)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
        force=True,
    )

    # Reduce noise from verbose third-party libs
    for noisy in ("httpx", "httpcore", "urllib3", "PIL", "chromadb"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
