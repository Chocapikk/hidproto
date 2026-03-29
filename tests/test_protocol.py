"""Tests for protocol base class."""

from __future__ import annotations

from hidproto import HIDProtocol, command
from hidproto.checksum import sum_checksum, xor_checksum

from .test_command import FakeProto, FakeTransport, _proto


def test_report_with_id() -> None:
    proto = _proto()
    report = proto._report(0x01, 0x02, 0x03)
    assert report == bytes([0xAA, 0x01, 0x02, 0x03, 0x00, 0x00])
    assert len(report) == 6


def test_report_no_id() -> None:
    proto = _proto()
    report = proto._report_no_id(0x01, 0x02)
    assert report == bytes([0x01, 0x02, 0x00, 0x00, 0x00, 0x00])
    assert len(report) == 6


def test_report_truncates() -> None:
    proto = _proto()
    report = proto._report(0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07)
    assert len(report) == 6


def test_next_seq_wraps() -> None:
    proto = _proto()
    for i in range(256):
        assert proto._next_seq() == i
    assert proto._next_seq() == 0


def test_xor_checksum() -> None:
    data = bytes([0x01, 0x02, 0x03, 0x04])
    assert xor_checksum(data) == 0x01 ^ 0x02 ^ 0x03 ^ 0x04


def test_xor_checksum_range() -> None:
    data = bytes([0xFF, 0x01, 0x02, 0x03, 0xFF])
    assert xor_checksum(data, 1, 4) == 0x01 ^ 0x02 ^ 0x03


def test_sum_checksum() -> None:
    data = bytes([0x01, 0x02, 0x03, 0x04])
    assert sum_checksum(data) == 0x0A


def test_sum_checksum_wraps() -> None:
    data = bytes([0xFF, 0x02])
    assert sum_checksum(data) == 0x01


def test_with_checksum() -> None:
    proto = _proto()
    data = bytes([0xAA, 0x01, 0x02, 0x03, 0x00, 0x00])
    result = proto._with_checksum(data, offset=4, start=1, end=4)
    assert result[4] == 0x01 ^ 0x02 ^ 0x03


def test_send_calls_transport() -> None:
    transport = FakeTransport()
    proto = FakeProto(transport=transport)
    report = proto.simple(0x10, 0x20)
    proto._send(report)
    assert len(transport.sent) == 1
    assert transport.sent[0] == report


def test_context_manager() -> None:
    transport = FakeTransport()
    with FakeProto(transport=transport) as proto:
        proto._send(proto.simple(0x01, 0x02))
    assert len(transport.sent) == 1


def test_led_id_default() -> None:
    proto = _proto()
    assert proto.led_id(0, 0) == 0x00
    assert proto.led_id(1, 0) == 0x20
    assert proto.led_id(2, 10) == 0x4A
    assert proto.led_id(5, 19) == 0xB3


def test_dir_slot_preset() -> None:
    proto = _proto()
    proto.preset_base = 0x71
    proto.custom_base = 0xA1
    dirs = ("up", "down", "left", "right")
    slot, r, g, b = proto.dir_slot("down", dirs, None)
    assert slot == 0x72
    assert (r, g, b) == (0, 0, 0)


def test_dir_slot_custom_color() -> None:
    proto = _proto()
    proto.preset_base = 0x71
    proto.custom_base = 0xA1
    dirs = ("up", "down", "left", "right")
    slot, r, g, b = proto.dir_slot("right", dirs, (255, 0, 0))
    assert slot == 0xA4
    assert (r, g, b) == (255, 0, 0)


def test_dir_slot_unknown_defaults_first() -> None:
    proto = _proto()
    proto.preset_base = 0x71
    dirs = ("up", "down")
    slot, _, _, _ = proto.dir_slot("invalid", dirs, None)
    assert slot == 0x71
