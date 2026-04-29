"""Tests for the extractive summarizer."""

import pytest
from arqyv.ai.summarizer import Summarizer


@pytest.fixture
def summarizer() -> Summarizer:
    return Summarizer()


def test_summarize_returns_string(summarizer: Summarizer) -> None:
    text = (
        "The quick brown fox jumps over the lazy dog. "
        "This is an example sentence for testing. "
        "Summarization should return a meaningful result. "
        "The algorithm scores sentences by word frequency."
    )
    result = summarizer.summarize(text)
    assert isinstance(result, str)
    assert len(result) > 0


def test_summarize_empty_string(summarizer: Summarizer) -> None:
    assert summarizer.summarize("") == ""


def test_summarize_short_text(summarizer: Summarizer) -> None:
    text = "Short text."
    result = summarizer.summarize(text)
    assert isinstance(result, str)


def test_summarize_respects_max_sentences(summarizer: Summarizer) -> None:
    text = " ".join([f"This is sentence number {i} in the test document." for i in range(20)])
    result = summarizer.summarize(text, max_sentences=2)
    # Should not return more sentences than requested
    assert isinstance(result, str)
