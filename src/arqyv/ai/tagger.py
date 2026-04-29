"""Auto-tagger using spaCy NLP pipeline.

Extracts named entities, noun phrases, and key concepts from text
to generate searchable tags for media files.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

_MODEL = "en_core_web_sm"
_MAX_TAGS = 20


class Tagger:
    def __init__(self) -> None:
        self._nlp: Any = None

    def _load(self) -> Any:
        if self._nlp is None:
            import spacy  # type: ignore[import]
            try:
                self._nlp = spacy.load(_MODEL)
            except OSError:
                log.warning("spaCy model '%s' not found. Run: python -m spacy download %s", _MODEL, _MODEL)
                # Fallback: blank English model
                self._nlp = spacy.blank("en")
        return self._nlp

    def tag_text(self, text: str) -> list[str]:
        nlp = self._load()
        doc = nlp(text[:10000])

        tags: set[str] = set()

        # Named entities
        for ent in doc.ents:
            if ent.label_ in {"PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "WORK_OF_ART"}:
                tags.add(ent.text.strip().lower())

        # Noun chunks (key concepts)
        for chunk in doc.noun_chunks:
            normalized = chunk.root.lemma_.lower()
            if len(normalized) > 2 and not chunk.root.is_stop:
                tags.add(normalized)

        return sorted(tags)[:_MAX_TAGS]
