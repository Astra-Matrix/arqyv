"""Application entry point.

Responsible only for bootstrapping: parse CLI args, configure logging,
instantiate QApplication, and hand off to the core App controller.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from PyQt6.QtWidgets import QApplication

from arqyv import __version__
from arqyv.core.app import Application
from arqyv.utils.logger import configure_logging


@click.command()
@click.version_option(version=__version__, prog_name="ARQYV")
@click.option("--debug", is_flag=True, help="Enable verbose debug logging.")
@click.option(
    "--data-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Override the default data directory.",
)
def main(debug: bool, data_dir: Path | None) -> None:
    """ARQYV — AI-powered smart media organizer."""
    configure_logging(debug=debug)

    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("ARQYV")
    qt_app.setApplicationVersion(__version__)
    qt_app.setOrganizationName("Alaustrup")

    app = Application(qt_app=qt_app, data_dir=data_dir, debug=debug)
    app.start()

    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
