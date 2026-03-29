"""Tests for device discovery."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from hidproto.discovery import DeviceInfo, find_device, list_devices


def _mock_sysfs(tmpdir: Path, name: str, hid_id: str, hid_name: str = "") -> None:
    dev_dir = tmpdir / "sys" / name / "device"
    dev_dir.mkdir(parents=True)
    lines = [f"HID_ID={hid_id}"]
    if hid_name:
        lines.append(f"HID_NAME={hid_name}")
    (dev_dir / "uevent").write_text("\n".join(lines))


def test_list_devices_empty() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "sys"
        root.mkdir()
        assert list_devices(sysfs_root=root) == []


def test_list_devices_finds_device() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "sys"
        _mock_sysfs(Path(tmpdir), "hidraw0", "0003:048D:8910", "ITE Device")
        devs = list_devices(sysfs_root=root, dev_root=Path("/dev"))
        assert len(devs) == 1
        assert devs[0].vendor_id == 0x048D
        assert devs[0].product_id == 0x8910
        assert devs[0].name == "ITE Device"


def test_find_device_match() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "sys"
        _mock_sysfs(Path(tmpdir), "hidraw0", "0003:048D:8910")
        _mock_sysfs(Path(tmpdir), "hidraw1", "0003:046D:C52B")
        dev = find_device(0x048D, 0x8910, sysfs_root=root)
        assert dev is not None
        assert dev.product_id == 0x8910


def test_find_device_no_match() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "sys"
        _mock_sysfs(Path(tmpdir), "hidraw0", "0003:046D:C52B")
        dev = find_device(0x048D, 0x8910, sysfs_root=root)
        assert dev is None


def test_device_info_str() -> None:
    info = DeviceInfo(
        devnode=Path("/dev/hidraw0"),
        vendor_id=0x048D,
        product_id=0x8910,
        name="ITE Device",
    )
    s = str(info)
    assert "048d:8910" in s
    assert "ITE Device" in s
