"""Low-level hidraw transport for Linux.

Provides direct access to HID devices via /dev/hidraw* using ioctl
for feature reports and read/write for input/output reports.
"""

from __future__ import annotations

import fcntl
import os
import select
from pathlib import Path

# ioctl encoding constants (from <asm-generic/ioctl.h>)
_IOC_WRITE = 1
_IOC_READ = 2
_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS


def _ioc(direction: int, type_: int, nr: int, size: int) -> int:
    return (
        (direction << _IOC_DIRSHIFT)
        | (type_ << _IOC_TYPESHIFT)
        | (nr << _IOC_NRSHIFT)
        | (size << _IOC_SIZESHIFT)
    )


def _hidiocsfeature(length: int) -> int:
    """HIDIOCSFEATURE(len) - send a feature report to the device."""
    return _ioc(_IOC_WRITE | _IOC_READ, ord("H"), 0x06, length)


def _hidiocgfeature(length: int) -> int:
    """HIDIOCGFEATURE(len) - get a feature report from the device."""
    return _ioc(_IOC_WRITE | _IOC_READ, ord("H"), 0x07, length)


class HidrawTransport:
    """Direct hidraw transport using ioctl for feature reports.

    Supports three modes of communication:
    - Feature reports (send_feature_report / get_feature_report) via ioctl
    - Output reports (write) via os.write
    - Input reports (read) via os.read with select timeout

    Example::

        with HidrawTransport("/dev/hidraw0") as t:
            t.send_feature_report(bytes([0xCC, 0x09, 0x0A, 0x05, 0x00, 0x00]))
            response = t.get_feature_report(0xCC, 6)
    """

    def __init__(self, devnode: str | Path) -> None:
        self.devnode = Path(devnode)
        flags = os.O_RDWR
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        self._fd: int | None = os.open(os.fspath(self.devnode), flags)

    def send_feature_report(self, data: bytes) -> int:
        """Send a HID feature report via HIDIOCSFEATURE ioctl.

        Args:
            data: Raw report bytes including the report ID as first byte.

        Returns:
            Number of bytes sent.

        Raises:
            RuntimeError: If the transport is closed.
            OSError: If the ioctl fails.
        """
        if self._fd is None:
            raise RuntimeError("transport is closed")
        buf = bytearray(data)
        fcntl.ioctl(self._fd, _hidiocsfeature(len(buf)), buf, True)
        return len(buf)

    def get_feature_report(self, report_id: int, size: int) -> bytes:
        """Get a HID feature report via HIDIOCGFEATURE ioctl.

        Args:
            report_id: The report ID to request.
            size: Expected report size in bytes.

        Returns:
            Raw report bytes.

        Raises:
            RuntimeError: If the transport is closed.
            OSError: If the ioctl fails.
        """
        if self._fd is None:
            raise RuntimeError("transport is closed")
        buf = bytearray(size)
        buf[0] = report_id
        fcntl.ioctl(self._fd, _hidiocgfeature(size), buf, True)
        return bytes(buf)

    def write(self, data: bytes) -> int:
        """Send an output report via os.write.

        Args:
            data: Raw report bytes.

        Returns:
            Number of bytes written.
        """
        if self._fd is None:
            raise RuntimeError("transport is closed")
        return os.write(self._fd, data)

    def read(self, size: int, timeout_ms: int = 1000) -> bytes:
        """Read an input report with timeout.

        Args:
            size: Maximum number of bytes to read.
            timeout_ms: Timeout in milliseconds. 0 for non-blocking.

        Returns:
            Raw report bytes, or empty bytes on timeout.
        """
        if self._fd is None:
            raise RuntimeError("transport is closed")
        ready, _, _ = select.select([self._fd], [], [], timeout_ms / 1000.0)
        if not ready:
            return b""
        return os.read(self._fd, size)

    def close(self) -> None:
        """Close the hidraw file descriptor."""
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None

    @property
    def closed(self) -> bool:
        """True if the transport has been closed."""
        return self._fd is None

    def __enter__(self) -> HidrawTransport:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
