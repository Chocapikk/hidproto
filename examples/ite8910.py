"""ITE 8910 keyboard RGB - fully declarative protocol definition.

Usage::

    from examples.ite8910 import ITE8910

    with ITE8910() as kb:
        kb.brightness(8)
        kb.speed(5)
        kb.effect("wave", direction="right", color=(255, 0, 0))
"""

from hidproto import HIDDevice, HIDProtocol, command, effect

_WAVE = ("up_left", "up_right", "down_left", "down_right", "up", "down", "left", "right")
_SNAKE = ("up_left", "up_right", "down_left", "down_right")


class ITE8910Protocol(HIDProtocol):
    """ITE 8910 - 6-byte HID feature reports [CC, cmd, d0, d1, d2, d3]."""

    # Device
    vendor_id = 0x048D
    product_id = 0x8910
    report_id = 0xCC
    report_size = 6
    rows, cols = 6, 20

    # Slot encoding
    preset_base = 0x71
    custom_base = 0xA1
    color_custom = 0xAA

    # Commands
    animation_mode = command(0x00, args=1)
    set_led = command(0x01, args=4)
    brightness_speed = command(0x09, args=4)
    breathing_cmd = command(0x0A, args=4)
    flashing_cmd = command(0x0B, args=4)
    wave_slot = command(0x15, args=4)
    snake_slot = command(0x16, args=4)
    scan_slot = command(0x17, args=4)
    random_color_cmd = command(0x18, args=4)

    # Effects
    effects = {
        "off": effect("off", animation=0x0C, needs_clear=True),
        "direct": effect("direct", needs_clear=True),
        "spectrum_cycle": effect("spectrum_cycle", animation=0x02),
        "rainbow_wave": effect("rainbow_wave", animation=0x04),
        "breathing": effect("breathing", color_cmd="breathing_cmd", color_slots=1),
        "flashing": effect("flashing", color_cmd="flashing_cmd", color_slots=1),
        "random": effect("random", animation=0x09),
        "random_color": effect("random_color", animation=0x09, slot_cmd="random_color_cmd", color_slots=1),
        "scan": effect("scan", animation=0x0A, slot_cmd="scan_slot", color_slots=2),
        "wave": effect("wave", animation=0x04, slot_cmd="wave_slot", directions=_WAVE),
        "snake": effect("snake", animation=0x0B, slot_cmd="snake_slot", directions=_SNAKE),
    }


ITE8910 = HIDDevice.for_protocol(ITE8910Protocol)


if __name__ == "__main__":
    import time

    with ITE8910() as kb:
        kb.brightness(8)
        kb.speed(5)

        for name, args in [
            ("wave", {"direction": "right"}),
            ("wave", {"direction": "left", "color": (255, 0, 0)}),
            ("breathing", {"color": (0, 255, 0)}),
            ("snake", {"direction": "down_right", "color": (0, 0, 255)}),
            ("scan", {"color": (255, 0, 0), "color2": (0, 0, 255)}),
            ("off", {}),
        ]:
            print(f"{name} {args}")
            kb.effect(name, **args)
            time.sleep(3)
