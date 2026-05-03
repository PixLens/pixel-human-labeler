from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QListWidget, QListWidgetItem, QSizePolicy


class Sidebar(QListWidget):
    """Left navigation rail (ChatGPT-style)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSpacing(2)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(220)
        self.setMaximumWidth(280)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def add_nav_item(self, label: str, data: object | None = None) -> QListWidgetItem:
        item = QListWidgetItem(label)
        if data is not None:
            item.setData(Qt.ItemDataRole.UserRole, data)
        self.addItem(item)
        return item
