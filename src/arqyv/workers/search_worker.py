"""
Search microservice entry-point (Version B).

Exposes a lightweight HTTP endpoint at :8001 for semantic + BM25 queries,
brokered via Redis so the API gateway can fan out to multiple replicas.

Run:
    python -m arqyv.workers.search_worker
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
from arqyv.search.engine import SearchEngine

configure_logging(json_output=True)
log = logging.getLogger("arqyv.search_worker")

MAX_CRASHES  = int(os.getenv("MAX_CRASHES",  "10"))
BACKOFF_BASE = float(os.getenv("BACKOFF_BASE", "2.0"))
WORKER_PORT  = int(os.getenv("SEARCH_PORT", "8001"))


async def _run() -> None:
    cfg    = settings_from_env()
    db     = Database(url=cfg.db_url)
    events = RedisEventBus(url=cfg.redis_url)

    await db.init()
    await events.connect()

    engine = SearchEngine(db=db, config=cfg)

    # Serve a minimal FastAPI app so the docker healthcheck can hit /health
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="ARQYV Search Worker")

    @app.get("/health")
    async def health():
        return JSONResponse({"status": "ok", "service": "search"})

    @app.get("/search")
    async def search(q: str, limit: int = 20):
        results = await engine.search_async(q, limit=limit)
        return {"results": [{"path": r.path, "filename": r.filename, "id": r.id} for r in results]}

    async def _heartbeat() -> None:
        while True:
            await events.set_health("search", {"status": "ok"})
            await asyncio.sleep(10)

    config = uvicorn.Config(app, host="0.0.0.0", port=WORKER_PORT, log_level="warning")
    server = uvicorn.Server(config)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(server.serve(), name="search-http")
        tg.create_task(_heartbeat(),   name="search-heartbeat")


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
