"""Plugin base classes and loader for ARQYV extensions.

A plugin is any Python package that:
  1. Declares an entry-point in the ``arqyv.plugins`` group.
  2. Exports a class that subclasses one of the plugin ABCs below.

Example entry-point in a plugin's pyproject.toml:
    [project.entry-points."arqyv.plugins"]
    my_plugin = "my_package.plugin:MyMetadataPlugin"
"""

from __future__ import annotations

import importlib.metadata
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_ENTRY_POINT_GROUP = "arqyv.plugins"


# ── Plugin ABCs ────────────────────────────────────────────────────────────────

class MetadataPlugin(ABC):
    """Extract extra metadata from a file. Return a dict merged into MediaFile."""

    #: Human-readable name shown in the UI
    name: str = "unnamed_metadata_plugin"
    #: File extensions this plugin handles, e.g. [".mp4", ".mkv"]
    supported_extensions: list[str] = []

    @abstractmethod
    def extract(self, path: Path) -> dict[str, Any]:
        """Return a dict of metadata fields to merge into the DB record."""
        ...


class TaggerPlugin(ABC):
    """Generate AI tags for a file."""

    name: str = "unnamed_tagger_plugin"
    supported_extensions: list[str] = []

    @abstractmethod
    def tag(self, path: Path) -> list[str]:
        """Return a list of tag strings for the given file."""
        ...


class PostProcessPlugin(ABC):
    """Run after indexing completes for a file — e.g. thumbnail enhancement."""

    name: str = "unnamed_postprocess_plugin"
    supported_extensions: list[str] = []

    @abstractmethod
    def process(self, path: Path, db_record: dict[str, Any]) -> None:
        """Perform any side-effect work; return value is ignored."""
        ...


# ── Plugin registry ────────────────────────────────────────────────────────────

class PluginRegistry:
    """Loads and manages all installed ARQYV plugins via entry-points."""

    def __init__(self) -> None:
        self._metadata: list[MetadataPlugin] = []
        self._taggers:  list[TaggerPlugin]   = []
        self._post:     list[PostProcessPlugin] = []

    def load(self) -> None:
        """Discover and instantiate all installed plugins."""
        eps = importlib.metadata.entry_points(group=_ENTRY_POINT_GROUP)
        for ep in eps:
            try:
                cls = ep.load()
                instance = cls()
                if isinstance(instance, MetadataPlugin):
                    self._metadata.append(instance)
                    log.info("Loaded metadata plugin: %s (%s)", instance.name, ep.name)
                elif isinstance(instance, TaggerPlugin):
                    self._taggers.append(instance)
                    log.info("Loaded tagger plugin: %s (%s)", instance.name, ep.name)
                elif isinstance(instance, PostProcessPlugin):
                    self._post.append(instance)
                    log.info("Loaded post-process plugin: %s (%s)", instance.name, ep.name)
                else:
                    log.warning("Unknown plugin type: %s", cls)
            except Exception:
                log.exception("Failed to load plugin: %s", ep.name)

    @property
    def metadata_plugins(self) -> list[MetadataPlugin]:
        return list(self._metadata)

    @property
    def tagger_plugins(self) -> list[TaggerPlugin]:
        return list(self._taggers)

    @property
    def post_process_plugins(self) -> list[PostProcessPlugin]:
        return list(self._post)

    def run_metadata(self, path: Path) -> dict[str, Any]:
        """Run all applicable metadata plugins and merge results."""
        ext = path.suffix.lower()
        merged: dict[str, Any] = {}
        for plugin in self._metadata:
            if not plugin.supported_extensions or ext in plugin.supported_extensions:
                try:
                    merged.update(plugin.extract(path))
                except Exception:
                    log.exception("Metadata plugin %s failed for %s", plugin.name, path)
        return merged

    def run_taggers(self, path: Path) -> list[str]:
        """Run all applicable tagger plugins and merge tag lists."""
        ext = path.suffix.lower()
        all_tags: list[str] = []
        for plugin in self._taggers:
            if not plugin.supported_extensions or ext in plugin.supported_extensions:
                try:
                    all_tags.extend(plugin.tag(path))
                except Exception:
                    log.exception("Tagger plugin %s failed for %s", plugin.name, path)
        return list(dict.fromkeys(all_tags))   # deduplicate, preserve order

    def run_post_process(self, path: Path, db_record: dict[str, Any]) -> None:
        ext = path.suffix.lower()
        for plugin in self._post:
            if not plugin.supported_extensions or ext in plugin.supported_extensions:
                try:
                    plugin.process(path, db_record)
                except Exception:
                    log.exception("Post-process plugin %s failed for %s", plugin.name, path)


# Global registry — import and call load() at startup
registry = PluginRegistry()
