from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class HomePage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        title = QLabel("홈")
        title.setObjectName("pageTitle")
        body = QLabel("PixelLabeler에 오신 것을 환영합니다.\n픽셀 이미지와 생성형 학습 워크플로는 왼쪽 메뉴에서 이동할 수 있습니다.")
        body.setWordWrap(True)
        body.setObjectName("pageBody")
        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(body)
        layout.addStretch()
