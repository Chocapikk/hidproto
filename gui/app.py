"""hidproto GUI - keyboard RGB controller with per-key editing."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from hidproto.device import HIDDevice
from hidproto.discovery import list_devices
from hidproto.registry import discover

from .keyboard_widget import KeyboardWidget
from .layouts import LAYOUTS


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("hidproto")
        self.setStyleSheet("QMainWindow { background-color: #1a1a1a; }")

        self._protocols = discover()
        self._device: HIDDevice | None = None
        self._current_color = QColor(255, 0, 0)
        self._proto_cls: type | None = None
        self._in_direct_mode = False

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Keyboard widget (replaced on connect with device-specific layout)
        self._root = root
        self._kb_widget = KeyboardWidget(LAYOUTS["full"])
        self._kb_widget.key_clicked.connect(self._on_key_clicked)
        root.insertWidget(0, self._kb_widget)

        # Controls row 1
        row1 = QHBoxLayout()
        root.addLayout(row1)

        # Device info
        self._device_label = QLabel("Detecting...")
        self._device_label.setStyleSheet("color: #aaa; font-size: 11px;")
        row1.addWidget(self._device_label)

        row1.addStretch()

        # Color picker button
        self._color_btn = QPushButton()
        self._color_btn.setFixedSize(30, 30)
        self._update_color_btn()
        self._color_btn.clicked.connect(self._on_color_pick)
        row1.addWidget(QLabel("Color:", styleSheet="color: #aaa;"))
        row1.addWidget(self._color_btn)

        # Fill all button
        fill_btn = QPushButton("Fill All")
        fill_btn.setStyleSheet("color: white; background: #444; padding: 4px 10px;")
        fill_btn.clicked.connect(self._on_fill_all)
        row1.addWidget(fill_btn)

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("color: white; background: #444; padding: 4px 10px;")
        clear_btn.clicked.connect(self._on_clear)
        row1.addWidget(clear_btn)

        # Controls row 2
        row2 = QHBoxLayout()
        root.addLayout(row2)

        # Effect selector
        row2.addWidget(QLabel("Effect:", styleSheet="color: #aaa;"))
        self._effect_combo = QComboBox()
        self._effect_combo.setStyleSheet("color: white; background: #333; padding: 4px;")
        self._effect_combo.currentTextChanged.connect(self._on_effect_changed)
        row2.addWidget(self._effect_combo)

        row2.addStretch()

        # Brightness
        row2.addWidget(QLabel("Brightness:", styleSheet="color: #aaa;"))
        self._brightness = QSlider(Qt.Horizontal)
        self._brightness.setRange(0, 10)
        self._brightness.setValue(8)
        self._brightness.setMaximumWidth(120)
        self._brightness.valueChanged.connect(self._on_brightness_changed)
        row2.addWidget(self._brightness)
        self._brightness_label = QLabel("8")
        self._brightness_label.setStyleSheet("color: #ccc; min-width: 20px;")
        row2.addWidget(self._brightness_label)

        # Speed
        row2.addWidget(QLabel("Speed:", styleSheet="color: #aaa;"))
        self._speed = QSlider(Qt.Horizontal)
        self._speed.setRange(0, 10)
        self._speed.setValue(5)
        self._speed.setMaximumWidth(120)
        self._speed.valueChanged.connect(self._on_speed_changed)
        row2.addWidget(self._speed)
        self._speed_label = QLabel("5")
        self._speed_label.setStyleSheet("color: #ccc; min-width: 20px;")
        row2.addWidget(self._speed_label)

        # Status bar
        self.statusBar().setStyleSheet("color: #888;")

        self.resize(self._kb_widget.sizeHint().width() + 30, self._kb_widget.sizeHint().height() + 150)

        self._auto_connect()

    def _auto_connect(self) -> None:
        connected_devices = list_devices()
        for name, proto_cls in self._protocols.items():
            for dev in connected_devices:
                if dev.vendor_id == proto_cls.vendor_id and dev.product_id == proto_cls.product_id:
                    try:
                        self._device = HIDDevice.for_protocol(proto_cls)()
                        self._proto_cls = proto_cls
                        self._device_label.setText(f"{name} ({dev.name})")
                        self._device_label.setStyleSheet("color: #2a6; font-size: 11px;")
                        self.statusBar().showMessage(f"Connected: {name}")

                        # Swap keyboard layout
                        kb_size = getattr(proto_cls, "keyboard_size", "full")
                        layout = LAYOUTS.get(kb_size, LAYOUTS["full"])
                        old = self._kb_widget
                        self._kb_widget = KeyboardWidget(layout)
                        self._kb_widget.key_clicked.connect(self._on_key_clicked)
                        self._root.replaceWidget(old, self._kb_widget)
                        old.deleteLater()
                        self.resize(self._kb_widget.sizeHint().width() + 30, self._kb_widget.sizeHint().height() + 150)

                        effects = getattr(proto_cls, "effects", {})
                        self._effect_combo.blockSignals(True)
                        self._effect_combo.clear()
                        self._effect_combo.addItems(sorted(effects.keys()))
                        self._effect_combo.blockSignals(False)
                        return
                    except Exception:
                        continue

        self._device_label.setText("No device found")
        self._device_label.setStyleSheet("color: #a44; font-size: 11px;")

    def _update_color_btn(self) -> None:
        c = self._current_color
        self._color_btn.setStyleSheet(
            f"background: rgb({c.red()},{c.green()},{c.blue()}); border: 2px solid #666; border-radius: 4px;"
        )

    def _on_color_pick(self) -> None:
        color = QColorDialog.getColor(self._current_color, self, "Pick LED Color")
        if color.isValid():
            self._current_color = color
            self._update_color_btn()

    def _ensure_direct_mode(self) -> None:
        if self._in_direct_mode or not self._device:
            return
        try:
            self._device.effect("direct")
            self._device.brightness(self._brightness.value())
            self._in_direct_mode = True
            self._effect_combo.blockSignals(True)
            idx = self._effect_combo.findText("direct")
            if idx >= 0:
                self._effect_combo.setCurrentIndex(idx)
            self._effect_combo.blockSignals(False)
        except Exception:
            pass

    def _on_key_clicked(self, row: int, col: int) -> None:
        current = self._kb_widget._colors.get((row, col))
        is_active = current and (current.red() or current.green() or current.blue())

        if is_active and current == self._current_color:
            self._kb_widget.set_key_color(row, col, QColor(0, 0, 0))
            if self._device:
                self._ensure_direct_mode()
                try:
                    self._device.set_key(row, col, 0, 0, 0)
                except Exception:
                    pass
            self.statusBar().showMessage(f"Key ({row},{col}) off")
            return

        self._kb_widget.set_key_color(row, col, self._current_color)
        if self._device:
            self._ensure_direct_mode()
            try:
                self._device.set_key(
                    row, col, self._current_color.red(), self._current_color.green(), self._current_color.blue()
                )
            except Exception:
                pass
        self.statusBar().showMessage(
            f"Key ({row},{col}) = #{self._current_color.red():02x}"
            f"{self._current_color.green():02x}{self._current_color.blue():02x}"
        )

    def _on_fill_all(self) -> None:
        self._kb_widget.set_all_colors(self._current_color)
        if self._device:
            try:
                # Send direct mode + all keys
                self._device.effect("direct")
                for k in self._kb_widget._layout:
                    if k.row >= 0:
                        self._device.set_key(
                            k.row,
                            k.col,
                            self._current_color.red(),
                            self._current_color.green(),
                            self._current_color.blue(),
                        )
            except Exception:
                pass
        self.statusBar().showMessage("Filled all keys")

    def _on_clear(self) -> None:
        self._kb_widget.clear_colors()
        if self._device:
            try:
                self._device.effect("off")
            except Exception:
                pass
        self.statusBar().showMessage("Cleared")

    def _on_effect_changed(self, effect: str) -> None:
        if not self._device or not effect:
            return
        self._in_direct_mode = effect == "direct"
        try:
            self._device.brightness(self._brightness.value())
            self._device.speed(self._speed.value())
            self._device.effect(effect)
            self.statusBar().showMessage(f"Effect: {effect}")
        except Exception as e:
            self.statusBar().showMessage(f"Error: {e}")

    def _on_brightness_changed(self, value: int) -> None:
        self._brightness_label.setText(str(value))
        self._kb_widget.set_brightness(value / 10.0)
        if self._device:
            try:
                self._device.brightness(value)
            except Exception:
                pass

    def _on_speed_changed(self, value: int) -> None:
        self._speed_label.setText(str(value))
        if self._device:
            try:
                self._device.speed(value)
            except Exception:
                pass

    def closeEvent(self, event) -> None:
        if self._device:
            self._device.close()
        event.accept()


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
