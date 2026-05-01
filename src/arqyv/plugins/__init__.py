"""ARQYV plugin system.

Import `registry` and call `registry.load()` once at startup to discover
all installed plugins declared under the ``arqyv.plugins`` entry-point group.
"""

from arqyv.plugins.base import (
    MetadataPlugin,
    TaggerPlugin,
    PostProcessPlugin,
    PluginRegistry,
    registry,
)

__all__ = [
    "MetadataPlugin",
    "TaggerPlugin",
    "PostProcessPlugin",
    "PluginRegistry",
    "registry",
]
