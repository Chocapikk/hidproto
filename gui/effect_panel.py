"""Dynamic effect controls panel - auto-generated from EffectSpec."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from hidproto.effect import EffectSpec, resolve_directions


class EffectPanel(QWidget):
    """Dynamic controls for an effect: colors, direction, auto-generated."""

    apply_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._spec: EffectSpec | None = None
        self._proto_cls: type | None = None
        self._dir_combo: QComboBox | None = None
        self._color_btns: list[QPushButton] = []
        self._colors: list[QColor] = []

    def configure(self, spec: EffectSpec, proto_cls: type) -> None:
        """Rebuild controls for a new effect."""
        self._spec = spec
        self._proto_cls = proto_cls

        # Clear old widgets
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._dir_combo = None
        self._color_btns = []
        self._colors = []

        # Directions
        dirs = resolve_directions(proto_cls, spec)
        if dirs:
            self._layout.addWidget(QLabel("Direction:", styleSheet="color: #aaa;"))
            self._dir_combo = QComboBox()
            self._dir_combo.setStyleSheet("color: white; background: #333; padding: 4px;")
            self._dir_combo.addItems(list(dirs))
            self._dir_combo.currentTextChanged.connect(lambda _: self.apply_requested.emit())
            self._layout.addWidget(self._dir_combo)

        # Color slots
        for i in range(spec.color_slots):
            default = QColor(255, 0, 0) if i == 0 else QColor(0, 0, 255)
            self._colors.append(default)

            label = f"Color {i + 1}:" if spec.color_slots > 1 else "Color:"
            self._layout.addWidget(QLabel(label, styleSheet="color: #aaa;"))

            btn = QPushButton()
            btn.setFixedSize(30, 30)
            self._set_btn_color(btn, default)
            idx = i
            btn.clicked.connect(lambda checked=False, ci=idx: self._pick_color(ci))
            self._color_btns.append(btn)
            self._layout.addWidget(btn)

    def _set_btn_color(self, btn: QPushButton, color: QColor) -> None:
        btn.setStyleSheet(
            f"background: rgb({color.red()},{color.green()},{color.blue()}); "
            f"border: 2px solid #666; border-radius: 4px;"
        )

    def _pick_color(self, index: int) -> None:
        color = QColorDialog.getColor(self._colors[index], self, f"Pick Color {index + 1}")
        if color.isValid():
            self._colors[index] = color
            self._set_btn_color(self._color_btns[index], color)
            self.apply_requested.emit()

    def get_direction(self) -> str | None:
        if self._dir_combo:
            return self._dir_combo.currentText()
        return None

    def get_colors(self) -> list[tuple[int, int, int]]:
        return [(c.red(), c.green(), c.blue()) for c in self._colors]

    def get_effect_kwargs(self) -> dict:
        """Build kwargs for HIDDevice.effect()."""
        kwargs: dict = {}
        direction = self.get_direction()
        if direction:
            kwargs["direction"] = direction
        colors = self.get_colors()
        if len(colors) >= 1:
            kwargs["color"] = colors[0]
        if len(colors) >= 2:
            kwargs["color2"] = colors[1]
        return kwargs
