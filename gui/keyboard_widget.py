"""Qt widget that renders a keyboard layout with per-key RGB colors."""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget

from hidproto.layout import Key


class KeyboardWidget(QWidget):
    """Renders a keyboard layout with per-key colors and click support."""

    UNIT = 50
    GAP = 3
    MARGIN = 15
    CORNER_RADIUS = 5

    key_clicked = Signal(int, int)  # row, col

    def __init__(self, layout: list[Key], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = layout
        self._colors: dict[tuple[int, int], QColor] = {}
        self._hover_key: tuple[int, int] | None = None
        self._brightness: float = 1.0  # 0.0 to 1.0
        self._compute_size()
        self.setMinimumSize(self.sizeHint())
        self.setMouseTracking(True)

    def set_brightness(self, value: float) -> None:
        self._brightness = max(0.0, min(1.0, value))
        self.update()

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

    def _key_rect(self, k: Key) -> QRectF:
        px = self.MARGIN + int(k.x * (self.UNIT + self.GAP))
        py = self.MARGIN + int(k.y * (self.UNIT + self.GAP))
        pw = int(k.w * self.UNIT + max(0, k.w - 1) * self.GAP)
        ph = int(k.h * self.UNIT + max(0, k.h - 1) * self.GAP)
        return QRectF(px, py, pw, ph)

    def _key_at(self, x: float, y: float) -> Key | None:
        for k in self._layout:
            if self._key_rect(k).contains(x, y):
                return k
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            k = self._key_at(event.position().x(), event.position().y())
            if k and k.row >= 0:
                self.key_clicked.emit(k.row, k.col)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        k = self._key_at(event.position().x(), event.position().y())
        new_hover = (k.row, k.col) if k and k.row >= 0 else None
        if new_hover != self._hover_key:
            self._hover_key = new_hover
            self.update()

    def leaveEvent(self, event) -> None:
        self._hover_key = None
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        font = QFont("sans-serif", 8)
        font.setWeight(QFont.Weight.Medium)
        p.setFont(font)

        for k in self._layout:
            rect = self._key_rect(k)
            is_hover = self._hover_key == (k.row, k.col) and k.row >= 0

            # Key body
            p.setPen(Qt.NoPen)
            bg = QColor(50, 50, 50) if is_hover else QColor(35, 35, 35)
            p.setBrush(bg)
            p.drawRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)

            # LED glow on borders (scaled by brightness)
            color = self._colors.get((k.row, k.col))
            if color and (color.red() or color.green() or color.blue()):
                br = self._brightness
                scaled = QColor(int(color.red() * br), int(color.green() * br), int(color.blue() * br))
                p.setPen(QPen(scaled, 3))
                p.setBrush(Qt.NoBrush)
                p.setOpacity(0.9 * br)
                p.drawRoundedRect(rect.adjusted(1, 1, -1, -1), self.CORNER_RADIUS, self.CORNER_RADIUS)
                p.setOpacity(0.3 * br)
                p.setPen(QPen(scaled, 6))
                p.drawRoundedRect(rect.adjusted(2, 2, -2, -2), self.CORNER_RADIUS - 1, self.CORNER_RADIUS - 1)
                p.setOpacity(1.0)

            # Border
            if not (color and (color.red() or color.green() or color.blue())):
                border_color = QColor(100, 100, 100) if is_hover else QColor(55, 55, 55)
                p.setPen(QPen(border_color, 1.5 if is_hover else 1))
                p.setBrush(Qt.NoBrush)
                p.drawRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)

            # Label
            label_color = QColor(220, 220, 220) if is_hover else QColor(180, 180, 180)
            p.setPen(label_color)
            p.drawText(rect, Qt.AlignCenter, k.label)
