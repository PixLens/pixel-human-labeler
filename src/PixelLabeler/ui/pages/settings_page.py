from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SettingsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        title = QLabel("설정")
        title.setObjectName("pageTitle")
        body = QLabel("앱 환경 설정은 이후 이 페이지에서 구성합니다.")
        body.setWordWrap(True)
        body.setObjectName("pageBody")
        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(body)
        layout.addStretch()
