"""Content deduplication — find identical and near-duplicate files.

Two-pass strategy:
  1. Exact: SHA-256 hash of file content → identical files across any path.
  2. Near: Perceptual hash (pHash / dHash) for images → visually similar files.

DedupScanner runs off the main thread. Results are returned as DedupGroup lists.
"""

from __future__ import annotations

import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_CHUNK = 65_536      # read chunk size for hashing
_PHASH_THRESHOLD = 8  # Hamming distance threshold for near-duplicates


@dataclass
class DedupGroup:
    """A group of files considered identical or very similar."""
    kind: str           # "exact" or "near"
    files: list[str]    # absolute paths, first = canonical (keep), rest = duplicates
    size_bytes: int     # size of one copy (savings = size * (len-1))

    @property
    def wasted_bytes(self) -> int:
        return self.size_bytes * (len(self.files) - 1)


class DedupScanner:
    """Synchronous scanner — run in a ThreadPoolExecutor, not on the main thread."""

    def __init__(self, paths: list[str]) -> None:
        self._paths = paths

    def scan(self) -> list[DedupGroup]:
        """Return all duplicate groups (exact + near) found in self._paths."""
        groups: list[DedupGroup] = []
        groups.extend(self._exact_duplicates())
        groups.extend(self._near_duplicates())
        return groups

    # ── Exact duplicates ───────────────────────────────────────────────────

    def _exact_duplicates(self) -> list[DedupGroup]:
        hash_to_paths: dict[str, list[str]] = defaultdict(list)
        for path in self._paths:
            p = Path(path)
            if not p.is_file():
                continue
            try:
                digest = self._sha256(p)
                hash_to_paths[digest].append(path)
            except OSError:
                continue

        groups = []
        for paths in hash_to_paths.values():
            if len(paths) > 1:
                size = Path(paths[0]).stat().st_size
                groups.append(DedupGroup(kind="exact", files=paths, size_bytes=size))
        return groups

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            while chunk := f.read(_CHUNK):
                h.update(chunk)
        return h.hexdigest()

    # ── Near-duplicate (perceptual hash for images) ────────────────────────

    def _near_duplicates(self) -> list[DedupGroup]:
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}
        images = [p for p in self._paths if Path(p).suffix.lower() in image_exts and Path(p).is_file()]
        if len(images) < 2:
            return []

        try:
            import imagehash  # type: ignore[import]
            from PIL import Image
        except ImportError:
            log.debug("imagehash not installed; skipping perceptual deduplication.")
            return []

        hashes: list[tuple[str, Any]] = []
        for path in images:
            try:
                img = Image.open(path)
                ph = imagehash.phash(img)
                hashes.append((path, ph))
            except Exception:
                continue

        # O(n²) comparison — fine for libraries up to a few thousand images
        groups: list[DedupGroup] = []
        seen: set[int] = set()
        for i, (path_a, hash_a) in enumerate(hashes):
            if i in seen:
                continue
            group_paths = [path_a]
            for j, (path_b, hash_b) in enumerate(hashes[i + 1:], start=i + 1):
                if j in seen:
                    continue
                if hash_a - hash_b <= _PHASH_THRESHOLD:
                    group_paths.append(path_b)
                    seen.add(j)
            if len(group_paths) > 1:
                seen.add(i)
                size = Path(path_a).stat().st_size
                groups.append(DedupGroup(kind="near", files=group_paths, size_bytes=size))

        return groups
