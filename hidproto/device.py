"""High-level device wrapper with effects, caching, and brightness/speed."""

from __future__ import annotations

from typing import Sequence

from .effect import apply_effect
from .protocol import HIDProtocol


class HIDDevice:
    """Generic HID device with declarative effect dispatch.

    Provides brightness, speed, per-key color, and named effects.
    All effect logic is driven by the protocol's ``effects`` dict,
    no subclassing needed for standard devices.

    Example::

        MyKeyboard = HIDDevice.for_protocol(MyProtocol)

        with MyKeyboard() as kb:
            kb.brightness(8)
            kb.effect("wave", direction="right", color=(255, 0, 0))
    """

    def __init__(self, protocol: HIDProtocol) -> None:
        self.protocol = protocol
        self._cache: dict[str, bytes] = {}
        self._brightness = 8
        self._speed = 5
        self._bs_dirty = False

    @classmethod
    def for_protocol(cls, protocol_cls: type[HIDProtocol]) -> type[HIDDevice]:
        """Create a device class bound to a specific protocol.

        Args:
            protocol_cls: The protocol class to bind.

        Returns:
            A new class that auto-instantiates the protocol on init.
        """

        class BoundDevice(cls):  # type: ignore[misc]
            def __init__(self, **kwargs: object) -> None:
                super().__init__(protocol_cls(**kwargs))

        BoundDevice.__name__ = protocol_cls.__name__.replace("Protocol", "")
        BoundDevice.__qualname__ = BoundDevice.__name__
        return BoundDevice

    # --- Brightness / Speed ---

    def _bs_report(self) -> bytes:
        return self.protocol.brightness_speed(self._brightness, self._speed, 0, 0)

    def brightness(self, value: int) -> None:
        """Set brightness (0 to protocol max, typically 10)."""
        target = max(0, min(10, value))
        self._bs_dirty = True
        for i in range(target + 1):
            self._brightness = i
            self.protocol._send(self._bs_report())
        self._cache["bs"] = self._bs_report()

    def speed(self, value: int) -> None:
        """Set animation speed (0 to protocol max, typically 10)."""
        target = max(0, min(10, value))
        self._bs_dirty = True
        for i in range(target + 1):
            self._speed = i
            self.protocol._send(self._bs_report())
        self._cache["bs"] = self._bs_report()

    # --- Per-key ---

    def set_key(self, row: int, col: int, r: int, g: int, b: int) -> None:
        """Set a single key color by row/col."""
        led_id = self.protocol.led_id(row, col)
        self.protocol._send(self.protocol.set_led(led_id, r, g, b))

    # --- Effects ---

    def effect(
        self,
        name: str,
        *,
        color: tuple[int, int, int] | None = None,
        color2: tuple[int, int, int] | None = None,
        direction: str | None = None,
    ) -> None:
        """Apply a named effect from the protocol's effects table.

        Args:
            name: Effect name (e.g. "wave", "breathing", "off").
            color: Primary custom color, or None for random/preset.
            color2: Secondary color (scan dual-band).
            direction: Direction name (wave/snake).
        """
        effects = getattr(self.protocol, "effects", {})
        spec = effects.get(name)
        if not spec:
            raise ValueError(f"Unknown effect: {name}. Valid: {', '.join(effects)}")

        colors: list[tuple[int, int, int]] = []
        if color:
            colors.append(color)
        if color2:
            colors.append(color2)

        reports = apply_effect(self.protocol, spec, colors=colors, direction=direction)
        self.batch(reports)
        self.invalidate()
        self.protocol._send(self._bs_report())

    # --- Cache ---

    def send_if_changed(self, key: str, report: bytes) -> bool:
        """Send a feature report only if it differs from cached value."""
        if self._cache.get(key) == report:
            return False
        self.protocol._send(report)
        self._cache[key] = report
        return True

    def write_if_changed(self, key: str, data: bytes) -> bool:
        """Send an output report only if it differs from cached value."""
        if self._cache.get(key) == data:
            return False
        self.protocol._write(data)
        self._cache[key] = data
        return True

    def invalidate(self) -> None:
        """Clear all cached state."""
        self._cache.clear()

    def batch(self, reports: Sequence[bytes], use_feature: bool = True) -> None:
        """Send multiple reports in sequence."""
        send = (self.protocol._send, self.protocol._write)[not use_feature]
        for report in reports:
            send(report)

    # --- Lifecycle ---

    def close(self) -> None:
        """Close the underlying protocol and transport."""
        self.protocol.close()

    def __enter__(self) -> HIDDevice:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
