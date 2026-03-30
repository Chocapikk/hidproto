"""Cross-platform transport using the hidapi library.

Works on Linux, Windows, and macOS. Requires ``pip install hidapi``.
Falls back to hidraw transport on Linux if hidapi is not installed.
"""

from __future__ import annotations

try:
    import hid
except ImportError:
    hid = None  # type: ignore[assignment]


class HidapiTransport:
    """Cross-platform HID transport using hidapi (cython-hidapi).

    Supports feature reports, output reports, and input reports
    on Linux, Windows, and macOS.

    Example::

        transport = HidapiTransport(0x048D, 0x8910)
        transport.send_feature_report(bytes([0xCC, 0x09, 0x0A, 0x05, 0x00, 0x00]))
        transport.close()
    """

    def __init__(self, vid: int = 0, pid: int = 0, path: bytes | None = None) -> None:
        if hid is None:
            raise ImportError("hidapi not installed. Run: pip install hidapi")

        self._dev = hid.device()

        if path:
            self._dev.open_path(path)
        elif vid and pid:
            self._dev.open(vid, pid)

    def send_feature_report(self, data: bytes) -> int:
        """Send a HID feature report."""
        return self._dev.send_feature_report(list(data))

    def get_feature_report(self, report_id: int, size: int) -> bytes:
        """Get a HID feature report."""
        return bytes(self._dev.get_feature_report(report_id, size))

    def write(self, data: bytes) -> int:
        """Send an output report."""
        return self._dev.write(list(data))

    def read(self, size: int, timeout_ms: int = 1000) -> bytes:
        """Read an input report with timeout."""
        self._dev.set_nonblocking(True)
        result = self._dev.read(size, timeout_ms)
        if not result:
            return b""
        return bytes(result)

    def close(self) -> None:
        """Close the HID device."""
        try:
            self._dev.close()
        except Exception:
            pass

    @property
    def closed(self) -> bool:
        """Always False until close() is called (hidapi has no closed check)."""
        return False

    def __enter__(self) -> HidapiTransport:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
