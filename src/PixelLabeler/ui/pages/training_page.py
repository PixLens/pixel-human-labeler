from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TrainingPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        title = QLabel("학습")
        title.setObjectName("pageTitle")
        body = QLabel("생성형 모델 학습 설정과 실행은 이후 core 모듈과 연동해 이곳에 붙입니다.")
        body.setWordWrap(True)
        body.setObjectName("pageBody")
        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(body)
        layout.addStretch()
