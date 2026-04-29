"""Unit tests for the EventBus."""

import pytest
from arqyv.core.events import EventBus


def test_subscribe_and_emit() -> None:
    bus = EventBus()
    received: list[dict] = []

    def handler(**kwargs):  # type: ignore[no-untyped-def]
        received.append(kwargs)

    bus.subscribe("test.event", handler)
    bus.emit("test.event", value=42, label="hello")

    assert len(received) == 1
    assert received[0] == {"value": 42, "label": "hello"}


def test_unsubscribe() -> None:
    bus = EventBus()
    count = [0]

    def handler(**kwargs):  # type: ignore[no-untyped-def]
        count[0] += 1

    bus.subscribe("ev", handler)
    bus.emit("ev")
    bus.unsubscribe("ev", handler)
    bus.emit("ev")

    assert count[0] == 1


def test_no_subscribers_no_error() -> None:
    bus = EventBus()
    bus.emit("nonexistent.event", x=1)  # should not raise


def test_handler_exception_does_not_stop_others() -> None:
    bus = EventBus()
    results = []

    def bad_handler(**kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("boom")

    def good_handler(**kwargs):  # type: ignore[no-untyped-def]
        results.append("ok")

    bus.subscribe("ev", bad_handler)
    bus.subscribe("ev", good_handler)
    bus.emit("ev")

    assert results == ["ok"]
