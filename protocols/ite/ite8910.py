"""ITE 8910 keyboard RGB - fully declarative protocol definition.

Usage::

    from protocols.ite.ite8910 import ITE8910

    with ITE8910() as kb:
        kb.brightness(8)
        kb.speed(5)
        kb.effect("wave", direction="right", color=(255, 0, 0))
"""

from hidproto import HIDDevice, HIDProtocol, Key, command, effect

_WAVE = ("up_left", "up_right", "down_left", "down_right", "up", "down", "left", "right")
_SNAKE = ("up_left", "up_right", "down_left", "down_right")

# fmt: off
# LED ID = ((row & 7) << 5) | col. From ClevoKeyboardDevices.cpp.
_KEYS = (
    # Row 0: F-key row
    Key("Esc",  0,    0,         row=0, col=0x00),
    Key("F1",   2,    0,         row=0, col=0x01),
    Key("F2",   3,    0,         row=0, col=0x02),
    Key("F3",   4,    0,         row=0, col=0x03),
    Key("F4",   5,    0,         row=0, col=0x04),
    Key("F5",   6.5,  0,         row=0, col=0x05),
    Key("F6",   7.5,  0,         row=0, col=0x06),
    Key("F7",   8.5,  0,         row=0, col=0x07),
    Key("F8",   9.5,  0,         row=0, col=0x08),
    Key("F9",   11,   0,         row=0, col=0x09),
    Key("F10",  12,   0,         row=0, col=0x0A),
    Key("F11",  13,   0,         row=0, col=0x0B),
    Key("F12",  14,   0,         row=0, col=0x0C),
    Key("PrtSc",15.5, 0,         row=0, col=0x0D),
    Key("Ins",  16.5, 0,         row=0, col=0x0E),
    Key("Del",  17.5, 0,         row=0, col=0x0F),
    # Row 1: Number row + numpad
    Key("`",    0,    1.5,       row=1, col=0x00),
    Key("1",    1,    1.5,       row=1, col=0x01),
    Key("2",    2,    1.5,       row=1, col=0x02),
    Key("3",    3,    1.5,       row=1, col=0x03),
    Key("4",    4,    1.5,       row=1, col=0x04),
    Key("5",    5,    1.5,       row=1, col=0x05),
    Key("6",    6,    1.5,       row=1, col=0x06),
    Key("7",    7,    1.5,       row=1, col=0x07),
    Key("8",    8,    1.5,       row=1, col=0x08),
    Key("9",    9,    1.5,       row=1, col=0x09),
    Key("0",    10,   1.5,       row=1, col=0x0A),
    Key("-",    11,   1.5,       row=1, col=0x0B),
    Key("=",    12,   1.5,       row=1, col=0x0D),
    Key("Bksp", 13,  1.5, 2,    row=1, col=0x0E),
    Key("Home", 15.5, 1.5,      row=0, col=0x10),
    Key("PgUp", 16.5, 1.5,      row=0, col=0x12),
    Key("Num",  19,   1.5,      row=1, col=0x10),
    Key("/",    20,   1.5,      row=1, col=0x11),
    Key("*",    21,   1.5,      row=1, col=0x12),
    Key("-",    22,   1.5,      row=1, col=0x13),
    # Row 2: QWERTY + numpad
    Key("Tab",  0,    2.5, 1.5, row=2, col=0x00),
    Key("Q",    1.5,  2.5,      row=2, col=0x02),
    Key("W",    2.5,  2.5,      row=2, col=0x03),
    Key("E",    3.5,  2.5,      row=2, col=0x04),
    Key("R",    4.5,  2.5,      row=2, col=0x05),
    Key("T",    5.5,  2.5,      row=2, col=0x06),
    Key("Y",    6.5,  2.5,      row=2, col=0x07),
    Key("U",    7.5,  2.5,      row=2, col=0x08),
    Key("I",    8.5,  2.5,      row=2, col=0x09),
    Key("O",    9.5,  2.5,      row=2, col=0x0A),
    Key("P",    10.5, 2.5,      row=2, col=0x0B),
    Key("[",    11.5, 2.5,      row=2, col=0x0C),
    Key("]",    12.5, 2.5,      row=2, col=0x0D),
    Key("\\",   13.5, 2.5, 1.5, row=2, col=0x0E),
    Key("Del",  15.5, 2.5,      row=0, col=0x0F),
    Key("End",  16.5, 2.5,      row=0, col=0x11),
    Key("PgDn", 17.5, 2.5,      row=0, col=0x13),
    Key("7",    19,   2.5,      row=2, col=0x10),
    Key("8",    20,   2.5,      row=2, col=0x11),
    Key("9",    21,   2.5,      row=2, col=0x12),
    Key("+",    22,   2.5,      row=2, col=0x13),
    # Row 3: Home row + numpad
    Key("Caps", 0,    3.5, 1.75,row=3, col=0x00),
    Key("A",    1.75, 3.5,      row=3, col=0x02),
    Key("S",    2.75, 3.5,      row=3, col=0x03),
    Key("D",    3.75, 3.5,      row=3, col=0x04),
    Key("F",    4.75, 3.5,      row=3, col=0x05),
    Key("G",    5.75, 3.5,      row=3, col=0x06),
    Key("H",    6.75, 3.5,      row=3, col=0x07),
    Key("J",    7.75, 3.5,      row=3, col=0x08),
    Key("K",    8.75, 3.5,      row=3, col=0x09),
    Key("L",    9.75, 3.5,      row=3, col=0x0A),
    Key(";",    10.75,3.5,      row=3, col=0x0B),
    Key("'",    11.75,3.5,      row=3, col=0x0C),
    Key("Enter",12.75,3.5, 2.25,row=3, col=0x0E),
    Key("4",    19,   3.5,      row=3, col=0x10),
    Key("5",    20,   3.5,      row=3, col=0x11),
    Key("6",    21,   3.5,      row=3, col=0x12),
    # Row 4: Shift row + numpad
    Key("Shift",0,    4.5, 2.25,row=4, col=0x00),
    Key("Z",    2.25, 4.5,      row=4, col=0x03),
    Key("X",    3.25, 4.5,      row=4, col=0x04),
    Key("C",    4.25, 4.5,      row=4, col=0x05),
    Key("V",    5.25, 4.5,      row=4, col=0x06),
    Key("B",    6.25, 4.5,      row=4, col=0x07),
    Key("N",    7.25, 4.5,      row=4, col=0x08),
    Key("M",    8.25, 4.5,      row=4, col=0x09),
    Key(",",    9.25, 4.5,      row=4, col=0x0A),
    Key(".",    10.25,4.5,      row=4, col=0x0B),
    Key("/",    11.25,4.5,      row=4, col=0x0C),
    Key("Shift",12.25,4.5, 2.75,row=4, col=0x0D),
    Key("Up",   16.5, 4.5,      row=4, col=0x0F),
    Key("1",    19,   4.5,      row=4, col=0x10),
    Key("2",    20,   4.5,      row=4, col=0x11),
    Key("3",    21,   4.5,      row=4, col=0x12),
    Key("Ent",  22,   4.5,      row=4, col=0x13),
    # Row 5: Bottom row + numpad
    Key("Ctrl", 0,    5.5, 1.25,row=5, col=0x00),
    Key("Fn",   1.25, 5.5,      row=5, col=0x02),
    Key("Win",  2.25, 5.5, 1.25,row=5, col=0x03),
    Key("Alt",  3.5,  5.5, 1.25,row=5, col=0x04),
    Key("Space",4.75, 5.5, 6.25,row=5, col=0x05),
    Key("Alt",  11,   5.5, 1.25,row=5, col=0x0A),
    Key("Menu", 12.25,5.5, 1.25,row=5, col=0x0B),
    Key("Ctrl", 13.5, 5.5, 1.25,row=5, col=0x0C),
    Key("Left", 15.5, 5.5,      row=5, col=0x0E),
    Key("Down", 16.5, 5.5,      row=5, col=0x0F),
    Key("Right",17.5, 5.5,      row=5, col=0x10),
    Key("0",    19,   5.5, 2,   row=5, col=0x11),
    Key(".",    21,   5.5,      row=5, col=0x12),
)
# fmt: on


class ITE8910Protocol(HIDProtocol):
    """ITE 8910 - 6-byte HID feature reports [CC, cmd, d0, d1, d2, d3]."""

    vendor_id = 0x048D
    product_id = 0x8910
    report_id = 0xCC
    report_size = 6
    rows, cols = 6, 20
    keyboard_size = "full"
    keys = _KEYS

    preset_base = 0x71
    custom_base = 0xA1
    color_custom = 0xAA

    animation_mode = command(0x00, args=1)
    set_led = command(0x01, args=4)
    brightness_speed = command(0x09, args=4)
    breathing_cmd = command(0x0A, args=4)
    flashing_cmd = command(0x0B, args=4)
    wave_slot = command(0x15, args=4)
    snake_slot = command(0x16, args=4)
    scan_slot = command(0x17, args=4)
    random_color_cmd = command(0x18, args=4)

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
