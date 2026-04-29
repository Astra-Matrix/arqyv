"""Integration tests for the async Database layer."""

import asyncio
import pytest
from pathlib import Path

from arqyv.database.db import Database


@pytest.fixture
def db(tmp_path: Path) -> Database:
    url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    d = Database(url=url, echo=False)
    asyncio.run(d.init())
    return d


def test_upsert_and_get_file(db: Database, tmp_path: Path) -> None:
    test_file = tmp_path / "test_video.mp4"
    test_file.write_bytes(b"fake video data")

    record = asyncio.run(db.upsert_file(test_file, {"mime_type": "video/mp4"}))
    assert record.path == str(test_file)
    assert record.filename == "test_video.mp4"
    assert record.extension == ".mp4"

    fetched = asyncio.run(db.get_file(str(test_file)))
    assert fetched is not None
    assert fetched.mime_type == "video/mp4"


def test_list_files(db: Database, tmp_path: Path) -> None:
    for name in ["a.mp4", "b.mkv", "c.mp3"]:
        f = tmp_path / name
        f.write_bytes(b"x")
        asyncio.run(db.upsert_file(f, {}))

    all_files = asyncio.run(db.list_files())
    assert len(all_files) == 3

    mp4_files = asyncio.run(db.list_files(extension=".mp4"))
    assert len(mp4_files) == 1


def test_delete_file(db: Database, tmp_path: Path) -> None:
    f = tmp_path / "temp.mp4"
    f.write_bytes(b"x")
    asyncio.run(db.upsert_file(f, {}))
    asyncio.run(db.delete_file(str(f)))
    result = asyncio.run(db.get_file(str(f)))
    assert result is None


def test_search_files(db: Database, tmp_path: Path) -> None:
    f = tmp_path / "holiday_beach.mp4"
    f.write_bytes(b"x")
    asyncio.run(db.upsert_file(f, {}))

    results = asyncio.run(db.search_files("holiday"))
    assert len(results) == 1
    assert "holiday" in results[0].filename
