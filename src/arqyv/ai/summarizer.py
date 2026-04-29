"""Extractive text summarizer.

Uses a lightweight extractive approach (no heavy seq2seq model required)
based on sentence scoring. Can be swapped for a HuggingFace summarization
model when GPU resources are available.
"""

from __future__ import annotations

import logging
import re

log = logging.getLogger(__name__)

_MAX_SENTENCES = 3
_MIN_SENTENCE_LEN = 20


class Summarizer:
    def summarize(self, text: str, max_sentences: int = _MAX_SENTENCES) -> str:
        """Return a short extractive summary of the input text."""
        if not text.strip():
            return ""
        try:
            return self._extractive_summarize(text, max_sentences)
        except Exception:
            log.exception("Summarization failed; returning truncation.")
            return text[:300] + "…"

    def _extractive_summarize(self, text: str, n: int) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s for s in sentences if len(s) >= _MIN_SENTENCE_LEN]
        if not sentences:
            return text[:300]

        # Score by word frequency (simple TF weighting)
        word_freq: dict[str, int] = {}
        for sent in sentences:
            for word in sent.lower().split():
                word = re.sub(r"[^a-z]", "", word)
                if len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1

        def score(sent: str) -> float:
            words = [re.sub(r"[^a-z]", "", w.lower()) for w in sent.split()]
            return sum(word_freq.get(w, 0) for w in words if len(w) > 3) / max(len(words), 1)

        ranked = sorted(sentences, key=score, reverse=True)[:n]
        # Restore original order
        ordered = [s for s in sentences if s in set(ranked)]
        return " ".join(ordered[:n])
