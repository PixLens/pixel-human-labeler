from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QResizeEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QListWidgetItem,
    QSizePolicy,
    QWidget,
)

from PixelLabeler.core.feature_schema import (
    FeatureSchema,
    label_file_payload,
    load_feature_schema,
    normalize_label_values,
    parse_label_file,
)

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def _label_sidecar_path(image_path: Path) -> Path:
    return image_path.parent / f"{image_path.name}.label.json"


class DatasetPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        with resources.as_file(resources.files("PixelLabeler.ui.forms") / "dataset_page.ui") as ui_path:
            uic.loadUi(str(ui_path), self)

        schema_path = resources.files("PixelLabeler.resources") / "feature_schema.json"
        with resources.as_file(schema_path) as p:
            self._schema: FeatureSchema = load_feature_schema(Path(p))
        self._folder: Path | None = None
        self._images: list[Path] = []
        self._combos: dict[str, QComboBox] = {}

        self._configure_layout_fill()
        self.mainSplitter.setSizes([280, 600])
        self.imagePreviewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imagePreviewLabel.setMinimumHeight(96)
        self.imagePreviewLabel.setScaledContents(False)
        self.imagePreviewLabel.setStyleSheet("border: 1px solid #3c3c3c; background-color: #252526;")

        self._build_feature_form()
        self._wire()

    def _configure_layout_fill(self) -> None:
        """Let title/top bar stay compact; splitter and inner panels consume remaining space."""
        expand = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizePolicy(expand)

        outer = self.layout()
        if outer is None:
            return
        outer.setContentsMargins(8, 8, 8, 8)
        for i in range(outer.count()):
            outer.setStretch(i, 0)
        if outer.count() >= 1:
            outer.setStretch(outer.count() - 1, 1)

        top_item = outer.itemAt(1)
        if top_item is not None and top_item.layout() is not None:
            hbox = top_item.layout()
            for i in range(hbox.count()):
                hbox.setStretch(i, 0)
            if hbox.count() >= 2:
                hbox.setStretch(1, 1)

        self.mainSplitter.setSizePolicy(expand)
        self.imageListWidget.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding),
        )
        self.rightPanel.setSizePolicy(expand)

        rp = self.rightPanel.layout()
        if rp is not None:
            for i in range(rp.count()):
                rp.setStretch(i, 0)
            if rp.count() >= 3:
                rp.setStretch(0, 1)
                rp.setStretch(1, 2)
                rp.setStretch(2, 0)

        self.imagePreviewLabel.setSizePolicy(expand)
        self.featureScrollArea.setSizePolicy(expand)
        self.saveLabelButton.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed),
        )

    def _wire(self) -> None:
        self.browseFolderButton.clicked.connect(self._on_browse_folder)
        self.imageListWidget.currentItemChanged.connect(self._on_current_item_changed)
        self.saveLabelButton.clicked.connect(self._on_save_label)

    def _build_feature_form(self) -> None:
        host = self.featureFormHost
        layout = QFormLayout(host)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        self._combos.clear()
        for dim in self._schema.dimensions:
            combo = QComboBox(host)
            combo.addItems(list(dim.options))
            combo.setObjectName(f"featureCombo_{dim.id}")
            self._combos[dim.id] = combo
            layout.addRow(QLabel(dim.label + ":", host), combo)

    def _on_browse_folder(self) -> None:
        start = str(self._folder) if self._folder else str(Path.home())
        picked = QFileDialog.getExistingDirectory(self, "데이터 폴더 선택", start)
        if not picked:
            return
        folder = Path(picked)
        self._folder = folder
        self.folderPathLabel.setText(self._elide_path(folder))
        self._images = sorted(
            p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in _IMAGE_SUFFIXES
        )
        self.imageListWidget.clear()
        for path in self._images:
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self.imageListWidget.addItem(item)
        if self._images:
            self.imageListWidget.setCurrentRow(0)
        else:
            self._clear_preview()
            self._reset_combos_to_defaults()

    def _elide_path(self, path: Path, max_len: int = 80) -> str:
        s = str(path)
        if len(s) <= max_len:
            return s
        return "…" + s[-(max_len - 1) :]

    def _current_image_path(self) -> Path | None:
        row = self.imageListWidget.currentRow()
        if row < 0 or row >= len(self._images):
            return None
        return self._images[row]

    def _on_current_item_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        del previous
        if current is None or not self._images:
            self._clear_preview()
            self._reset_combos_to_defaults()
            return
        row = self.imageListWidget.row(current)
        if row < 0 or row >= len(self._images):
            self._clear_preview()
            self._reset_combos_to_defaults()
            return
        path = self._images[row]
        self._load_preview(path)
        self._load_labels_for_image(path)

    def _clear_preview(self) -> None:
        self.imagePreviewLabel.setPixmap(QPixmap())
        self.imagePreviewLabel.setText("미리보기")

    @staticmethod
    def _scale_pixmap_pixel_art(pix: QPixmap, max_w: int, max_h: int) -> QPixmap:
        """Nearest-neighbor scale; integer upscale for small sprites so pixels stay crisp."""
        w, h = pix.width(), pix.height()
        if w <= 0 or h <= 0:
            return pix
        max_w = max(1, max_w)
        max_h = max(1, max_h)
        scale_up = min(max_w // w, max_h // h, 48)
        if scale_up >= 1:
            nw, nh = w * scale_up, h * scale_up
            return pix.scaled(
                QSize(nw, nh),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        return pix.scaled(
            QSize(max_w, max_h),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )

    def _load_preview(self, path: Path) -> None:
        pix = QPixmap(str(path))
        if pix.isNull():
            self.imagePreviewLabel.setPixmap(QPixmap())
            self.imagePreviewLabel.setText("이미지를 불러올 수 없습니다.")
            return
        label = self.imagePreviewLabel
        target = label.size()
        if target.width() <= 0 or target.height() <= 0:
            target = QSize(400, 240)
        scaled = self._scale_pixmap_pixel_art(pix, target.width(), target.height())
        label.setPixmap(scaled)
        label.setText("")

    def _reset_combos_to_defaults(self) -> None:
        defaults = self._schema.default_values()
        self._apply_combo_values(defaults)

    def _apply_combo_values(self, values: dict[str, str]) -> None:
        normalized = normalize_label_values(self._schema, values)
        for combo in self._combos.values():
            combo.blockSignals(True)
        try:
            for dim_id, combo in self._combos.items():
                val = normalized.get(dim_id, "")
                idx = combo.findText(val)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                else:
                    combo.setCurrentIndex(0)
        finally:
            for combo in self._combos.values():
                combo.blockSignals(False)

    def _load_labels_for_image(self, image_path: Path) -> None:
        sidecar = _label_sidecar_path(image_path)
        raw_dims: dict[str, str] = {}
        if sidecar.is_file():
            try:
                raw = json.loads(sidecar.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    raw_dims = parse_label_file(raw)
            except (json.JSONDecodeError, OSError, ValueError):
                raw_dims = {}
        self._apply_combo_values(raw_dims)

    def _on_save_label(self) -> None:
        path = self._current_image_path()
        if path is None:
            return
        values = {dim_id: combo.currentText() for dim_id, combo in self._combos.items()}
        payload = label_file_payload(self._schema, values)
        sidecar = _label_sidecar_path(path)
        sidecar.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        item = self.imageListWidget.currentItem()
        if item is None:
            return
        row = self.imageListWidget.row(item)
        if 0 <= row < len(self._images):
            self._load_preview(self._images[row])
