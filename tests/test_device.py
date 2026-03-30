"""Tests for HIDDevice wrapper."""

from __future__ import annotations

from hidproto import HIDDevice, command, effect

from .test_command import FakeProto, FakeTransport


class EffectProto(FakeProto):
    rows = 2
    cols = 2
    preset_base = 0x71
    custom_base = 0xA1
    color_custom = 0xAA

    animation_mode = command(0x00, args=1)
    set_led = command(0x01, args=4)
    brightness_speed = command(0x09, args=4)
    color_cmd = command(0x0A, args=4)
    slot_cmd = command(0x15, args=4)

    effects = dict(
        off=effect("off", animation=0x0C, needs_clear=True),
        simple=effect("simple", animation=0x02),
        colored=effect("colored", color_cmd="color_cmd", color_slots=1),
        slotted=effect("slotted", animation=0x04, slot_cmd="slot_cmd", color_slots=2),
        directed=effect("directed", animation=0x04, slot_cmd="slot_cmd", directions=("up", "down")),
    )


def _device() -> tuple[HIDDevice, FakeTransport]:
    transport = FakeTransport()
    proto = EffectProto(transport=transport)
    return HIDDevice(proto), transport


def test_brightness_sends_report() -> None:
    dev, transport = _device()
    dev.brightness(8)
    assert len(transport.sent) == 1
    assert transport.sent[0][2] == 8


def test_brightness_cached() -> None:
    dev, transport = _device()
    dev.brightness(8)
    dev.brightness(8)
    assert len(transport.sent) == 1


def test_speed_sends_report() -> None:
    dev, transport = _device()
    dev.speed(5)
    assert len(transport.sent) == 1


def test_invalidate_clears_cache() -> None:
    dev, transport = _device()
    dev.brightness(8)
    dev.invalidate()
    dev.brightness(8)
    assert len(transport.sent) == 2


def test_effect_simple() -> None:
    dev, transport = _device()
    dev.effect("simple")
    assert any(b[1] == 0x00 and b[2] == 0x02 for b in transport.sent)


def test_effect_colored_with_color() -> None:
    dev, transport = _device()
    dev.effect("colored", color=(255, 0, 0))
    assert any(b[1] == 0x0A and b[2] == 0xAA for b in transport.sent)


def test_effect_colored_random() -> None:
    dev, transport = _device()
    dev.effect("colored")
    assert any(b[1] == 0x0A and b[2] == 0x00 for b in transport.sent)


def test_effect_directed_preset() -> None:
    dev, transport = _device()
    dev.effect("directed", direction="down")
    assert any(b[1] == 0x15 and b[2] == 0x72 for b in transport.sent)


def test_effect_directed_custom() -> None:
    dev, transport = _device()
    dev.effect("directed", direction="up", color=(0, 255, 0))
    assert any(b[1] == 0x15 and b[2] == 0xA1 for b in transport.sent)


def test_effect_slotted_dual_color() -> None:
    dev, transport = _device()
    dev.effect("slotted", color=(255, 0, 0), color2=(0, 0, 255))
    slot_reports = [b for b in transport.sent if b[1] == 0x15]
    assert len(slot_reports) == 2
    assert slot_reports[0][2] == 0xA1
    assert slot_reports[1][2] == 0xA2


def test_effect_off_clears_leds() -> None:
    dev, transport = _device()
    dev.effect("off")
    clear_reports = [b for b in transport.sent if b[1] == 0x01]
    assert len(clear_reports) == 4  # 2x2 matrix


def test_effect_unknown_raises() -> None:
    dev, _ = _device()
    try:
        dev.effect("nonexistent")
        assert False, "should have raised"
    except ValueError:
        pass


def test_for_protocol() -> None:
    BoundDev = HIDDevice.for_protocol(EffectProto)
    assert BoundDev.__name__ == "EffectProto"


def test_batch() -> None:
    dev, transport = _device()
    reports = [b"\xaa\x01\x00\x00\x00\x00", b"\xaa\x01\x01\x00\x00\x00"]
    dev.batch(reports)
    assert len(transport.sent) == 2


def test_context_manager() -> None:
    transport = FakeTransport()
    proto = EffectProto(transport=transport)
    with HIDDevice(proto) as dev:
        dev.brightness(5)
    assert len(transport.sent) == 1
