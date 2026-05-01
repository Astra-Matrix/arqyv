"""
Indexer microservice entry-point (Version B).

Run inside its own Docker container:
    python -m arqyv.workers.indexer_worker

Features:
  - Supervised crash-recovery loop with exponential back-off
  - Structured JSON logging
  - Redis heartbeat for the TUI dashboard
  - Graceful SIGINT / SIGTERM handling
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys

from arqyv.utils.logger import configure_logging
from arqyv.core.redis   import RedisEventBus
from arqyv.database.db  import Database
from arqyv.config       import settings_from_env
from arqyv.backend.indexer import Indexer

configure_logging(json_output=True)
log = logging.getLogger("arqyv.indexer_worker")

MAX_CRASHES  = int(os.getenv("MAX_CRASHES",  "10"))
BACKOFF_BASE = float(os.getenv("BACKOFF_BASE", "2.0"))   # seconds


async def _run() -> None:
    cfg    = settings_from_env()
    db     = Database(url=cfg.db_url)
    events = RedisEventBus(url=cfg.redis_url)

    await db.init()
    await events.connect()

    indexer = Indexer(db=db, config=cfg, events=events)

    async def _heartbeat() -> None:
        while True:
            await events.set_health("indexer", {"status": "ok"})
            await asyncio.sleep(10)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(indexer.run_forever(), name="indexer-loop")
        tg.create_task(_heartbeat(),          name="indexer-heartbeat")


async def _supervised() -> None:
    """Restart worker on crash with exponential back-off."""
    crashes = 0
    while crashes < MAX_CRASHES:
        try:
            log.info("worker_start", extra={"attempt": crashes + 1})
            await _run()
        except asyncio.CancelledError:
            log.info("worker_cancelled")
            break
        except Exception as exc:
            crashes += 1
            wait = min(BACKOFF_BASE ** crashes, 60.0)
            log.error(
                "worker_crash",
                extra={"error": str(exc), "crashes": crashes, "retry_in": wait},
                exc_info=True,
            )
            if crashes >= MAX_CRASHES:
                log.critical("worker_max_crashes_exceeded")
                sys.exit(1)
            await asyncio.sleep(wait)


def _on_signal(*_) -> None:
    log.info("signal_received_shutting_down")
    for task in asyncio.all_tasks():
        task.cancel()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _on_signal)
        except NotImplementedError:
            pass   # Windows — signals handled via KeyboardInterrupt
    loop.run_until_complete(_supervised())
