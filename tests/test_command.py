"""Tests for command descriptor."""

from __future__ import annotations

from hidproto import HIDProtocol, command


class FakeProto(HIDProtocol):
    vendor_id = 0x1234
    product_id = 0x5678
    report_id = 0xAA
    report_size = 6

    simple = command(0x01, args=2, doc="Simple cmd")

    @command(0x09, doc="Custom builder")
    def custom(self, a: int, b: int) -> bytes:
        return self._report(0x09, max(0, a), min(255, b), 0, 0)


class FakeTransport:
    def __init__(self) -> None:
        self.sent: list[bytes] = []

    def send_feature_report(self, data: bytes) -> int:
        self.sent.append(bytes(data))
        return len(data)

    def write(self, data: bytes) -> int:
        self.sent.append(bytes(data))
        return len(data)

    def read(self, size: int, timeout_ms: int = 1000) -> bytes:
        return b""

    def get_feature_report(self, report_id: int, size: int) -> bytes:
        return b"\x00" * size

    def close(self) -> None:
        pass


def _proto() -> FakeProto:
    return FakeProto(transport=FakeTransport())


def test_auto_command_builds_report() -> None:
    proto = _proto()
    report = proto.simple(0x10, 0x20)
    assert report == bytes([0xAA, 0x01, 0x10, 0x20, 0x00, 0x00])


def test_auto_command_zero_pads() -> None:
    proto = _proto()
    report = proto.simple(0xFF)
    assert len(report) == 6
    assert report[0] == 0xAA
    assert report[1] == 0x01
    assert report[2] == 0xFF


def test_custom_builder_called() -> None:
    proto = _proto()
    report = proto.custom(8, 5)
    assert report == bytes([0xAA, 0x09, 8, 5, 0x00, 0x00])


def test_custom_builder_clamps() -> None:
    proto = _proto()
    report = proto.custom(-1, 999)
    assert report[2] == 0
    assert report[3] == 255


def test_list_commands() -> None:
    cmds = FakeProto.list_commands()
    assert "simple" in cmds
    assert "custom" in cmds
    assert cmds["simple"].opcode == (0x01,)
    assert cmds["custom"].opcode == (0x09,)


def test_command_doc() -> None:
    cmds = FakeProto.list_commands()
    assert cmds["simple"].doc == "Simple cmd"
    assert cmds["custom"].doc == "Custom builder"
