"""hidproto GUI - keyboard RGB controller with visual layout."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
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
from hidproto.registry import discover

from .keyboard_widget import KeyboardWidget
from .layouts import ANSI_FULL


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("hidproto")
        self.setStyleSheet("QMainWindow { background-color: #1a1a1a; }")

        self._protocols = discover()
        self._device: HIDDevice | None = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Keyboard widget
        self._kb_widget = KeyboardWidget(ANSI_FULL)
        root.addWidget(self._kb_widget)

        # Controls
        controls = QHBoxLayout()
        root.addLayout(controls)

        # Device selector
        self._device_combo = QComboBox()
        self._device_combo.addItems(sorted(self._protocols.keys()))
        self._device_combo.setStyleSheet("color: white; background: #333; padding: 4px;")
        controls.addWidget(QLabel("Device:", styleSheet="color: #aaa;"))
        controls.addWidget(self._device_combo)

        # Connect button
        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setStyleSheet("color: white; background: #444; padding: 6px 12px;")
        self._connect_btn.clicked.connect(self._on_connect)
        controls.addWidget(self._connect_btn)

        # Effect selector
        self._effect_combo = QComboBox()
        self._effect_combo.setStyleSheet("color: white; background: #333; padding: 4px;")
        controls.addWidget(QLabel("Effect:", styleSheet="color: #aaa;"))
        controls.addWidget(self._effect_combo)

        # Apply button
        self._apply_btn = QPushButton("Apply")
        self._apply_btn.setStyleSheet("color: white; background: #555; padding: 6px 12px;")
        self._apply_btn.clicked.connect(self._on_apply)
        controls.addWidget(self._apply_btn)

        # Brightness slider
        controls.addWidget(QLabel("Brightness:", styleSheet="color: #aaa;"))
        self._brightness = QSlider(Qt.Horizontal)
        self._brightness.setRange(0, 10)
        self._brightness.setValue(8)
        self._brightness.setMaximumWidth(120)
        controls.addWidget(self._brightness)

        # Speed slider
        controls.addWidget(QLabel("Speed:", styleSheet="color: #aaa;"))
        self._speed = QSlider(Qt.Horizontal)
        self._speed.setRange(0, 10)
        self._speed.setValue(5)
        self._speed.setMaximumWidth(120)
        controls.addWidget(self._speed)

        # Status bar
        self.statusBar().setStyleSheet("color: #888;")
        self.statusBar().showMessage("Select a device and click Connect")

        self.resize(self._kb_widget.sizeHint().width() + 30, self._kb_widget.sizeHint().height() + 120)

    def _on_connect(self) -> None:
        name = self._device_combo.currentText()
        proto_cls = self._protocols.get(name)
        if not proto_cls:
            return

        try:
            self._device = HIDDevice.for_protocol(proto_cls)()
            self.statusBar().showMessage(f"Connected: {name}")
            self._connect_btn.setText("Connected")
            self._connect_btn.setStyleSheet("color: white; background: #2a6; padding: 6px 12px;")

            # Populate effects
            self._effect_combo.clear()
            effects = getattr(proto_cls, "effects", {})
            self._effect_combo.addItems(sorted(effects.keys()))
        except Exception as e:
            self.statusBar().showMessage(f"Error: {e}")

    def _on_apply(self) -> None:
        if not self._device:
            self.statusBar().showMessage("Not connected")
            return

        effect = self._effect_combo.currentText()
        if not effect:
            return

        try:
            self._device.brightness(self._brightness.value())
            self._device.speed(self._speed.value())
            self._device.effect(effect)
            self.statusBar().showMessage(f"Applied: {effect}")

            # Visual feedback: color the keyboard widget
            self._kb_widget.set_all_colors(QColor(100, 200, 255))
        except Exception as e:
            self.statusBar().showMessage(f"Error: {e}")

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
