from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from PixelLabeler.ui.pages import DatasetPage, HomePage, SettingsPage, TrainingPage
from PixelLabeler.ui.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PixelLabeler")
        self.resize(1100, 700)
        self.setMinimumSize(800, 520)

        self._sidebar = Sidebar(self)
        self._stack = QStackedWidget(self)

        for label, page in (
            ("홈", HomePage(self)),
            ("데이터셋", DatasetPage(self)),
            ("학습", TrainingPage(self)),
            ("설정", SettingsPage(self)),
        ):
            self._sidebar.add_nav_item(label)
            self._stack.addWidget(page)

        self._sidebar.currentRowChanged.connect(self._stack.setCurrentIndex)

        shell = QWidget(self)
        shell.setObjectName("mainRoot")
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._sidebar)
        layout.addWidget(self._stack, stretch=1)
        self.setCentralWidget(shell)

        self._sidebar.setCurrentRow(0)
