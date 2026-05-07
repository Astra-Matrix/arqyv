"""
ARQYV Empty State — shown in the content area when no file is selected.

Adapts its message to the current sidebar context (library, search, collections…).
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from arqyv.ui.themes.dark import PALETTE as P


class EmptyStateWidget(QWidget):
    """
    Full-area placeholder shown when no content is loaded.

    Signals
    -------
    open_folder_requested  — user clicked "Open Folder"
    open_files_requested   — user clicked "Open Files"
    """

    open_folder_requested = pyqtSignal()
    open_files_requested  = pyqtSignal()

    _CONTEXTS: dict[str, tuple[str, str, str]] = {
        "library": (
            "⊞",
            "Your library is empty",
            "Add a folder to start indexing your media.",
        ),
        "search": (
            "⌕",
            "Start typing to search",
            "Search by filename, extension, or AI-generated content tags.",
        ),
        "collections": (
            "⊟",
            "No collections yet",
            "Collections are built automatically after your library is indexed.",
        ),
        "queue": (
            "≣",
            "Queue is empty",
            "Double-click any file to add it to the playback queue.",
        ),
        "default": (
            "⬡",
            "Nothing selected",
            "Pick a file from the sidebar to preview it here.",
        ),
    }

    def __init__(self, context: str = "library", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context = context
        self.setStyleSheet(f"background: {P['bg0']};")
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(2)

        center = QWidget()
        cl = QVBoxLayout(center)
        cl.setContentsMargins(40, 0, 40, 0)
        cl.setSpacing(0)
        cl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        icon, title, body = self._CONTEXTS.get(self._context, self._CONTEXTS["default"])

        # Icon glyph — large, faint
        self._icon_lbl = QLabel(icon)
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._icon_lbl.setStyleSheet(f"""
            color: {P['bg4']};
            font-size: 64px;
            font-weight: 300;
            padding-bottom: 24px;
        """)
        cl.addWidget(self._icon_lbl)

        # Title
        self._title_lbl = QLabel(title)
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._title_lbl.setStyleSheet(f"""
            color: {P['text']};
            font-size: 18px;
            font-weight: 600;
            letter-spacing: -0.01em;
        """)
        cl.addWidget(self._title_lbl)
        cl.addSpacing(10)

        # Body text
        self._body_lbl = QLabel(body)
        self._body_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._body_lbl.setWordWrap(True)
        self._body_lbl.setStyleSheet(f"""
            color: {P['text2']};
            font-size: 13px;
            line-height: 1.6;
            max-width: 320px;
        """)
        cl.addWidget(self._body_lbl)

        # Action buttons (only for library context)
        if self._context == "library":
            cl.addSpacing(28)
            btn_row = QWidget()
            bl = QHBoxLayout(btn_row)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setSpacing(10)
            bl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            open_folder_btn = QPushButton("Open Folder…")
            open_folder_btn.setObjectName("primary")
            open_folder_btn.setFixedHeight(36)
            open_folder_btn.setMinimumWidth(140)
            open_folder_btn.clicked.connect(self.open_folder_requested)

            open_files_btn = QPushButton("Open Files…")
            open_files_btn.setFixedHeight(36)
            open_files_btn.setMinimumWidth(120)
            open_files_btn.clicked.connect(self.open_files_requested)

            bl.addWidget(open_folder_btn)
            bl.addWidget(open_files_btn)
            cl.addWidget(btn_row)

            # Keyboard shortcut hint
            cl.addSpacing(20)
            hint = QLabel("Or press  Ctrl+P  to open the command palette")
            hint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            hint.setStyleSheet(f"color: {P['text3']}; font-size: 11px;")
            cl.addWidget(hint)

        outer.addWidget(center)
        outer.addStretch(3)

    def set_context(self, context: str) -> None:
        """Swap the displayed message without rebuilding the full widget."""
        self._context = context
        icon, title, body = self._CONTEXTS.get(context, self._CONTEXTS["default"])
        self._icon_lbl.setText(icon)
        self._title_lbl.setText(title)
        self._body_lbl.setText(body)
