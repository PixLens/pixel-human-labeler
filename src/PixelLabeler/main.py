from __future__ import annotations

import sys

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from PixelLabeler.ui import MainWindow

_APP_STYLESHEET = """
QWidget#mainRoot {
    background-color: #1e1e1e;
    color: #e8e8e8;
}
QListWidget#sidebar {
    background-color: #252526;
    color: #d4d4d4;
    border: none;
    border-right: 1px solid #3c3c3c;
    padding: 8px 4px;
    outline: 0;
}
QListWidget#sidebar::item {
    padding: 10px 12px;
    border-radius: 6px;
}
QListWidget#sidebar::item:selected {
    background-color: #3a3d41;
    color: #ffffff;
}
QListWidget#sidebar::item:hover:!selected {
    background-color: #2d2d30;
}
QStackedWidget {
    background-color: #1e1e1e;
}
QLabel#pageTitle {
    font-size: 22px;
    font-weight: 600;
    color: #f3f3f3;
}
QLabel#pageBody {
    font-size: 13px;
    color: #b0b0b0;
}
QLabel#pageTitleLabel {
    font-size: 22px;
    font-weight: 600;
    color: #f3f3f3;
}
QListWidget#imageListWidget {
    background-color: #252526;
    color: #d4d4d4;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 4px;
    outline: 0;
}
QListWidget#imageListWidget::item:selected {
    background-color: #3a3d41;
    color: #ffffff;
}
QScrollArea#featureScrollArea {
    border: 1px solid #3c3c3c;
    background-color: #252526;
}
QComboBox {
    background-color: #2d2d30;
    color: #e8e8e8;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 4px 8px;
}
"""


def _apply_dark_fusion(app: QApplication) -> None:
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#e8e8e8"))
    pal.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor("#252526"))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2d2d30"))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor("#e8e8e8"))
    pal.setColor(QPalette.ColorRole.Text, QColor("#e8e8e8"))
    pal.setColor(QPalette.ColorRole.Button, QColor("#2d2d30"))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor("#e8e8e8"))
    pal.setColor(QPalette.ColorRole.Highlight, QColor("#3a3d41"))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)
    app.setStyleSheet(_APP_STYLESHEET)


def main() -> int:
    app = QApplication(sys.argv)
    _apply_dark_fusion(app)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
