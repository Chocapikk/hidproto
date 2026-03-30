"""Base protocol class with report building and transport."""

from __future__ import annotations

import sys
from typing import Any, Callable

from .checksum import xor_checksum
from .command import CommandSpec, command
from .discovery import find_device
from .transport import HidrawTransport


class _ProtocolMeta(type):
    """Metaclass that collects command descriptors into a registry."""

    _commands: dict[str, CommandSpec]

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> _ProtocolMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        commands: dict[str, CommandSpec] = {}
        for base in reversed(bases):
            parent_cmds = getattr(base, "_commands", None)
            if parent_cmds:
                commands.update(parent_cmds)
        for attr_name, attr_val in namespace.items():
            if isinstance(attr_val, command):
                attr_val.__set_name__(cls, attr_name)
                commands[attr_name] = attr_val._to_spec(attr_name)
        cls._commands = commands
        return cls


class HIDProtocol(metaclass=_ProtocolMeta):
    """Base class for declarative HID protocols.

    Subclass this and set ``vendor_id``, ``product_id``, ``report_id``,
    and ``report_size``. Define commands with the ``@command`` decorator.

    The protocol auto-discovers the device via sysfs and opens a hidraw
    transport. Pass a ``HidrawTransport`` explicitly for testing or when
    multiple matching devices exist.

    Class attributes:
        vendor_id: USB vendor ID (e.g. ``0x048D``).
        product_id: USB product ID (e.g. ``0x8910``).
        report_id: HID report ID prepended to every report.
        report_size: Total report size in bytes (including report ID).
    """

    vendor_id: int = 0
    product_id: int = 0
    report_id: int = 0
    report_size: int = 8
    rows: int = 0
    cols: int = 0
    preset_base: int = 0x00
    custom_base: int = 0x00
    color_custom: int = 0x00
    keyboard_size: str = "full"
    _commands: dict[str, CommandSpec]

    def __init__(self, transport: object | None = None) -> None:
        self._transport = transport or self._auto_transport()
        self._seq = 0

    @classmethod
    def _auto_transport(cls) -> HidrawTransport:
        """Auto-select transport: hidraw on Linux, hidapi elsewhere."""
        if sys.platform == "linux":
            info = find_device(cls.vendor_id, cls.product_id)
            if info is not None:
                return HidrawTransport(info.devnode)

        # Fallback to hidapi (cross-platform)
        try:
            from .transport_hidapi import HidapiTransport

            return HidapiTransport(cls.vendor_id, cls.product_id)
        except ImportError:
            pass

        raise FileNotFoundError(
            f"No device found for {cls.vendor_id:04x}:{cls.product_id:04x}. "
            f"On non-Linux platforms, install hidapi: pip install hidapi"
        )

    # --- Report building ---

    def _report(self, *data: int) -> bytes:
        """Build a report: [report_id, *data], zero-padded to report_size."""
        payload = bytes((self.report_id, *data))
        pad = self.report_size - len(payload)
        if pad > 0:
            payload += b"\x00" * pad
        return payload[: self.report_size]

    def _report_no_id(self, *data: int) -> bytes:
        """Build a report without report_id prefix, zero-padded."""
        payload = bytes(data)
        pad = self.report_size - len(payload)
        if pad > 0:
            payload += b"\x00" * pad
        return payload[: self.report_size]

    def led_id(self, row: int, col: int) -> int:
        """Encode row/col to LED ID. Default: ((row & 7) << 5) | (col & 0x1F)."""
        return ((row & 0x07) << 5) | (col & 0x1F)

    def dir_slot(
        self,
        direction: str,
        table: tuple[str, ...],
        color: tuple[int, int, int] | None,
    ) -> tuple[int, int, int, int]:
        """Build (slot, r, g, b) for a directional command."""
        idx = table.index(direction) if direction in table else 0
        base = self.custom_base if color else self.preset_base
        rgb = color if color else (0, 0, 0)
        return (base + idx, *rgb)

    def _next_seq(self) -> int:
        """Return the next sequence number (0-255, wrapping)."""
        seq = self._seq
        self._seq = (self._seq + 1) & 0xFF
        return seq

    def _with_checksum(
        self,
        data: bytes,
        offset: int,
        checksum_fn: Callable[[bytes, int, int | None], int] = xor_checksum,
        start: int = 0,
        end: int | None = None,
    ) -> bytes:
        """Insert a computed checksum into the report at the given offset.

        Args:
            data: Raw report bytes.
            offset: Index where the checksum byte will be written.
            checksum_fn: Callable(data, start, end) -> int.
            start: Start of checksum range.
            end: End of checksum range (exclusive). None = len(data).

        Returns:
            New bytes with the checksum inserted.
        """
        buf = bytearray(data)
        buf[offset] = checksum_fn(data, start, end)
        return bytes(buf)

    # --- Transport ---

    def _send(self, report: bytes) -> int:
        """Send a feature report (ioctl HIDIOCSFEATURE)."""
        return self._transport.send_feature_report(report)

    def _write(self, data: bytes) -> int:
        """Send an output report (os.write)."""
        return self._transport.write(data)

    def _read(self, size: int = 0, timeout_ms: int = 1000) -> bytes:
        """Read an input report with timeout."""
        return self._transport.read(size or self.report_size, timeout_ms)

    def _get_feature(self, report_id: int = 0, size: int = 0) -> bytes:
        """Get a feature report from the device."""
        return self._transport.get_feature_report(
            report_id or self.report_id,
            size or self.report_size,
        )

    # --- Lifecycle ---

    def close(self) -> None:
        """Close the underlying transport."""
        self._transport.close()

    def __enter__(self) -> HIDProtocol:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @classmethod
    def list_commands(cls) -> dict[str, CommandSpec]:
        """Return all registered commands for this protocol."""
        return dict(cls._commands)
