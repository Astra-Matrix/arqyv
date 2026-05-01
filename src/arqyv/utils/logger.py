"""
Logging configuration — shared by monolith (Version A) and microservices (Version B).

Modes:
    debug=True              → human-readable coloured output via Rich
    json_output=True        → JSON-L lines for log aggregators (Loki, Datadog, etc.)
    default (prod)          → JSON-L (machine-parseable, no colour)
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── Formatters ────────────────────────────────────────────────────────────────

class _JsonFormatter(logging.Formatter):
    """Emit one JSON object per log record — compatible with any log aggregator."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts":     datetime.now(timezone.utc).isoformat(),
            "level":  record.levelname,
            "logger": record.name,
            "msg":    record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Merge caller-supplied extra= fields
        _std = logging.LogRecord.__dict__
        for key, val in record.__dict__.items():
            if key not in _std and not key.startswith("_"):
                payload[key] = val
        return json.dumps(payload, default=str)


class _DevFormatter(logging.Formatter):
    """ANSI-coloured human-readable output for local development."""

    _COLOURS = {
        "DEBUG":    "\033[37m",    # grey
        "INFO":     "\033[36m",    # cyan
        "WARNING":  "\033[33m",    # yellow
        "ERROR":    "\033[31m",    # red
        "CRITICAL": "\033[35m",    # magenta
    }
    _RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self._COLOURS.get(record.levelname, "")
        return f"{colour}{super().format(record)}{self._RESET}"


# ── Public API ────────────────────────────────────────────────────────────────

def configure_logging(
    *,
    debug:       bool       = False,
    json_output: bool       = False,
    log_dir:     Path | None = None,
    level:       int | None  = None,
) -> None:
    """
    Configure the root logger.  Call once at process start.

    Args:
        debug:       Enable DEBUG level + coloured dev output.
        json_output: Emit JSON-L on stdout (overrides Rich/colour).
        log_dir:     Directory for the rotating file sink.  Defaults to
                     the platform log dir.
        level:       Explicit log level (overrides debug flag).
    """
    root = logging.getLogger()
    root.setLevel(level or (logging.DEBUG if debug else logging.INFO))
    root.handlers.clear()

    # ── Console handler ───────────────────────────────────────────────────────
    # sys.stdout is None under pythonw.exe (windowless mode) — skip console sink.
    _stdout = sys.stdout
    if _stdout is not None:
        if json_output:
            console: logging.Handler = logging.StreamHandler(_stdout)
            console.setFormatter(_JsonFormatter())
        elif debug:
            try:
                from rich.logging import RichHandler  # type: ignore[import]
                console = RichHandler(
                    level=logging.DEBUG,
                    rich_tracebacks=True,
                    tracebacks_show_locals=True,
                    show_path=True,
                )
            except ImportError:
                console = logging.StreamHandler(_stdout)
                console.setFormatter(_DevFormatter(
                    fmt="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
                    datefmt="%H:%M:%S",
                ))
        else:
            console = logging.StreamHandler(_stdout)
            console.setFormatter(_DevFormatter(
                fmt="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
                datefmt="%H:%M:%S",
            ))
        root.addHandler(console)

    # ── Rotating file sink ────────────────────────────────────────────────────
    if log_dir is None:
        try:
            from platformdirs import user_log_dir
            log_dir = Path(user_log_dir("ARQYV", "Alaustrup"))
        except Exception:
            log_dir = Path.home() / ".arqyv" / "logs"

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "arqyv.log",
            maxBytes=5 * 1024 * 1024,   # 5 MB
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(_JsonFormatter())
        root.addHandler(file_handler)
    except Exception:
        pass  # Non-fatal: keep going without a file sink

    # Suppress noisy third-party loggers
    for noisy in ("httpx", "httpcore", "urllib3", "PIL", "chromadb",
                  "sentence_transformers", "transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
