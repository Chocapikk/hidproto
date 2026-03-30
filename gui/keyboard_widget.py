"""Qt widget that renders a keyboard layout with per-key RGB colors."""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .layouts import Key


class KeyboardWidget(QWidget):
    """Renders a keyboard layout with per-key colors."""

    UNIT = 50  # pixels per key unit
    GAP = 3  # gap between keys
    MARGIN = 15  # margin around keyboard
    CORNER_RADIUS = 5  # key corner radius

    def __init__(self, layout: list[Key], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = layout
        self._colors: dict[tuple[int, int], QColor] = {}
        self._compute_size()
        self.setMinimumSize(self.sizeHint())

    def _compute_size(self) -> None:
        max_x = 0.0
        max_y = 0.0
        for k in self._layout:
            if k.x + k.w > max_x:
                max_x = k.x + k.w
            if k.y + k.h > max_y:
                max_y = k.y + k.h
        self._width = int(2 * self.MARGIN + max_x * self.UNIT + (max_x - 1) * self.GAP)
        self._height = int(2 * self.MARGIN + max_y * self.UNIT + (max_y - 1) * self.GAP)

    def sizeHint(self):
        from PySide6.QtCore import QSize

        return QSize(self._width, self._height)

    def set_key_color(self, row: int, col: int, color: QColor) -> None:
        self._colors[(row, col)] = color
        self.update()

    def set_all_colors(self, color: QColor) -> None:
        for k in self._layout:
            if k.row >= 0:
                self._colors[(k.row, k.col)] = color
        self.update()

    def clear_colors(self) -> None:
        self._colors.clear()
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        font = QFont("sans-serif", 8)
        font.setWeight(QFont.Weight.Medium)
        p.setFont(font)

        for k in self._layout:
            px = self.MARGIN + int(k.x * (self.UNIT + self.GAP))
            py = self.MARGIN + int(k.y * (self.UNIT + self.GAP))
            pw = int(k.w * self.UNIT + max(0, k.w - 1) * self.GAP)
            ph = int(k.h * self.UNIT + max(0, k.h - 1) * self.GAP)
            rect = QRectF(px, py, pw, ph)

            # Key body
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(35, 35, 35))
            p.drawRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)

            # LED color
            color = self._colors.get((k.row, k.col))
            if color and (color.red() or color.green() or color.blue()):
                p.setBrush(color)
                p.setOpacity(0.8)
                inner = QRectF(px + 3, py + 3, pw - 6, ph - 6)
                p.drawRoundedRect(inner, self.CORNER_RADIUS - 1, self.CORNER_RADIUS - 1)
                p.setOpacity(1.0)

            # Border
            p.setPen(QPen(QColor(55, 55, 55), 1))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)

            # Label
            p.setPen(QColor(180, 180, 180))
            p.drawText(rect, Qt.AlignCenter, k.label)
