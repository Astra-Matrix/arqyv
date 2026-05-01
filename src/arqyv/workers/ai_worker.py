"""
AI microservice entry-point (Version B).

Consumes an async task queue from Redis, runs inference (captioning,
embedding, Whisper transcription) in a configurable thread-pool,
and writes results back to Postgres.

Run:
    python -m arqyv.workers.ai_worker
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
from arqyv.ai.analyzer  import AIAnalyzer

configure_logging(json_output=True)
log = logging.getLogger("arqyv.ai_worker")

MAX_CRASHES  = int(os.getenv("MAX_CRASHES",  "10"))
BACKOFF_BASE = float(os.getenv("BACKOFF_BASE", "2.0"))
WORKER_POOL  = int(os.getenv("AI_WORKER_POOL", "4"))


async def _run() -> None:
    cfg    = settings_from_env()
    db     = Database(url=cfg.db_url)
    events = RedisEventBus(url=cfg.redis_url)

    await db.init()
    await events.connect()

    analyzer = AIAnalyzer(config=cfg, events=events)

    # Subscribe to file.added events and analyse each new file
    await events.subscribe("file.added")

    processed = 0

    async def _heartbeat() -> None:
        while True:
            await events.set_health("ai", {
                "status": "ok",
                "processed": processed,
            })
            await asyncio.sleep(10)

    async def _consume() -> None:
        nonlocal processed
        async for channel, payload in events.listen():
            path = payload.get("path", "")
            if not path:
                continue
            try:
                log.info("ai_analyse_start path=%s", path)
                from pathlib import Path as _Path
                await asyncio.get_event_loop().run_in_executor(
                    None, analyzer.analyze, _Path(path)
                )
                processed += 1
                log.info("ai_analyse_done path=%s total=%d", path, processed)
            except Exception as exc:
                log.error("ai_analyse_error path=%s error=%s", path, exc, exc_info=True)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(_consume(),    name="ai-consumer")
        tg.create_task(_heartbeat(),  name="ai-heartbeat")


async def _supervised() -> None:
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
            pass
    loop.run_until_complete(_supervised())
