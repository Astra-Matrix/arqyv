"""Tests for the search filter parser."""

import pytest
from arqyv.search.filters import FilterParser


def test_parse_type_filter() -> None:
    f, query = FilterParser.parse("beach vacation type:video")
    assert f.type_group == "video"
    assert query == "beach vacation"


def test_parse_extension_filter() -> None:
    f, query = FilterParser.parse("portrait ext:.jpg")
    assert f.extension == ".jpg"
    assert query == "portrait"


def test_parse_size_filter() -> None:
    f, query = FilterParser.parse("big files size:>100mb")
    assert f.size_op == ">"
    assert f.size_bytes == 100 * 1024 * 1024
    assert query == "big files"


def test_parse_date_filter() -> None:
    f, query = FilterParser.parse("old footage date:<2020-01-01")
    assert f.date_op == "<"
    assert f.date_value is not None
    assert f.date_value.year == 2020


def test_no_filters() -> None:
    f, query = FilterParser.parse("simple search")
    assert f.type_group is None
    assert query == "simple search"


def test_multiple_filters() -> None:
    f, query = FilterParser.parse("holidays type:image size:>1mb")
    assert f.type_group == "image"
    assert f.size_bytes == 1024 * 1024
    assert query == "holidays"
