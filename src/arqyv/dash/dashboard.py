"""
ARQYV CLI Dashboard (Version B).

Run:
    python -m arqyv.dash.dashboard
    REDIS_URL=redis://localhost:6379/0 python -m arqyv.dash.dashboard

Shows:
  - Live service health (api, indexer, search, ai, db)
  - Redis event stream log
  - Events-per-second sparkline

Requires:
    pip install textual redis
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime

from textual.app        import App, ComposeResult
from textual.widgets    import Header, Footer, DataTable, Label, Log, Sparkline
from textual.containers import Vertical
from textual.reactive   import reactive

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SERVICES  = ["api", "indexer", "search", "ai", "db"]

_COL_HEADERS = ("Service", "Status", "Latency ms", "Events/s", "Last seen")


class ArqyvDashboard(App):
    """Live ARQYV service health dashboard."""

    TITLE = "ARQYV  ·  Service Dashboard"

    CSS = """
    Screen      { background: $background; }
    #services   { height: 14; border: round $primary; padding: 1 2; }
    #event-log  { height: 1fr; border: round $primary; padding: 0 1; }
    #event-rate { height: 5; border: round $accent; }
    Label.title { text-style: bold; color: $accent; margin-bottom: 1; }
    """

    BINDINGS = [
        ("q", "quit",    "Quit"),
        ("r", "refresh", "Force refresh"),
    ]

    _tick: reactive[int] = reactive(0)

    def __init__(self) -> None:
        super().__init__()
        self._redis     = None
        self._sparkdata: list[float] = [0.0] * 60
        self._event_cnt = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Label("Service health", classes="title")
            yield DataTable(id="services", zebra_stripes=True)
            yield Label("Event stream", classes="title")
            yield Log(id="event-log", max_lines=300)
            yield Sparkline(self._sparkdata, id="event-rate",
                            summary_function=max)
        yield Footer()

    def on_mount(self) -> None:
        table: DataTable = self.query_one("#services", DataTable)
        table.add_columns(*_COL_HEADERS)
        for svc in SERVICES:
            table.add_row(svc, "—", "—", "—", "—", key=svc)

        self.set_interval(2.0,  self._poll_health)
        self.set_interval(0.5,  self._drain_events)
        self.set_interval(1.0,  self._update_sparkline)

    # ── Polling ───────────────────────────────────────────────────────────────

    async def _ensure_redis(self) -> bool:
        if self._redis:
            return True
        try:
            import redis.asyncio as aioredis
            self._redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
            return True
        except Exception:
            return False

    async def _poll_health(self) -> None:
        if not await self._ensure_redis():
            return
        table: DataTable = self.query_one("#services", DataTable)
        for svc in SERVICES:
            try:
                raw = await self._redis.get(f"health:{svc}")
                if not raw:
                    continue
                data    = json.loads(raw)
                status  = data.get("status", "?")
                latency = f"{data.get('latency_ms', 0.0):.1f}"
                eps     = f"{data.get('events_per_s', 0.0):.1f}"
                seen    = datetime.now().strftime("%H:%M:%S")
                table.update_cell(svc, "Status",     status,  update_width=True)
                table.update_cell(svc, "Latency ms", latency, update_width=True)
                table.update_cell(svc, "Events/s",   eps,     update_width=True)
                table.update_cell(svc, "Last seen",  seen,    update_width=True)
            except Exception:
                pass

    async def _drain_events(self) -> None:
        if not await self._ensure_redis():
            return
        log_widget: Log = self.query_one("#event-log", Log)
        try:
            msgs = await self._redis.xrevrange("events:log", count=5)
            for _, fields in msgs:
                ts  = fields.get("ts",  "")
                msg = fields.get("msg", "")
                log_widget.write_line(f"[{ts}]  {msg}")
                self._event_cnt += 1
        except Exception:
            pass

    def _update_sparkline(self) -> None:
        self._sparkdata.append(float(self._event_cnt))
        self._event_cnt = 0
        if len(self._sparkdata) > 60:
            self._sparkdata.pop(0)
        spark: Sparkline = self.query_one("#event-rate", Sparkline)
        spark.data = self._sparkdata

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_refresh(self) -> None:
        self._tick += 1
        self.run_worker(self._poll_health(), exclusive=False)


if __name__ == "__main__":
    ArqyvDashboard().run()
