"""Device discovery via /sys/class/hidraw.

Scans sysfs to find HID devices by vendor/product ID without
requiring any external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DeviceInfo:
    """Information about a discovered HID device.

    Attributes:
        devnode: Path to the /dev/hidraw* device node.
        vendor_id: USB vendor ID.
        product_id: USB product ID.
        name: Human-readable device name from HID_NAME.
    """

    devnode: Path
    vendor_id: int
    product_id: int
    name: str = ""

    def __str__(self) -> str:
        return f"{self.devnode} [{self.vendor_id:04x}:{self.product_id:04x}] {self.name}"


def _parse_uevent(uevent_path: Path) -> dict[str, str]:
    """Parse a kernel uevent file into a key-value dict."""
    result: dict[str, str] = {}
    try:
        text = uevent_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return result
    for line in text.splitlines():
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def _parse_hid_id(hid_id: str) -> tuple[int, int] | None:
    """Parse HID_ID 'bus:vid:pid' into (vendor_id, product_id)."""
    parts = hid_id.split(":")
    if len(parts) != 3:
        return None
    try:
        return int(parts[1], 16), int(parts[2], 16)
    except ValueError:
        return None


def list_devices(
    sysfs_root: Path = Path("/sys/class/hidraw"),
    dev_root: Path = Path("/dev"),
) -> list[DeviceInfo]:
    """List all HID devices visible in sysfs.

    Args:
        sysfs_root: Path to /sys/class/hidraw.
        dev_root: Path to /dev (for constructing device node paths).

    Returns:
        List of DeviceInfo for each discovered device.
    """
    if not sysfs_root.exists():
        return []

    devices: list[DeviceInfo] = []
    for entry in sorted(sysfs_root.glob("hidraw*"), key=lambda p: p.name):
        uevent = entry / "device" / "uevent"
        if not uevent.exists():
            continue
        data = _parse_uevent(uevent)
        parsed = _parse_hid_id(data.get("HID_ID", ""))
        if not parsed:
            continue
        vid, pid = parsed
        devices.append(
            DeviceInfo(
                devnode=dev_root / entry.name,
                vendor_id=vid,
                product_id=pid,
                name=data.get("HID_NAME", ""),
            )
        )
    return devices


def find_device(
    vendor_id: int,
    product_id: int,
    sysfs_root: Path = Path("/sys/class/hidraw"),
    dev_root: Path = Path("/dev"),
) -> DeviceInfo | None:
    """Find the first HID device matching a vendor/product ID pair.

    Args:
        vendor_id: USB vendor ID to match.
        product_id: USB product ID to match.
        sysfs_root: Path to /sys/class/hidraw.
        dev_root: Path to /dev.

    Returns:
        DeviceInfo if found, None otherwise.
    """
    for dev in list_devices(sysfs_root, dev_root):
        if dev.vendor_id == vendor_id and dev.product_id == product_id:
            return dev
    return None
