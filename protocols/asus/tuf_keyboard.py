"""ASUS TUF / ROG keyboard - 65-byte output reports, per-LED and modes.

Protocol reference: OpenRGB AsusAuraTUFKeyboardController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step

_DIRECTIONS = ("right", "left", "up", "down")


class AsusTUFKeyboardProtocol(HIDProtocol):
    """ASUS TUF/ROG keyboard - 65-byte hid_write, per-LED + hardware modes."""

    vendor_id = 0x0B05
    product_id = 0x1899  # TUF K5 Gaming
    report_id = 0x00
    report_size = 65
    rows = 6
    keyboard_size = "full"
    cols = 22

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    directions = _DIRECTIONS

    def _report(self, *data: int) -> bytes:
        buf = bytearray(self.report_size)
        for i, b in enumerate(data):
            if i < self.report_size:
                buf[i] = b
        return bytes(buf)

    # Commands
    # Mode: [0x00, 0x51, 0x2C, mode, flag, speed, brightness, color_mode, direction, R, G, B]
    set_mode = command(0x00, 0x51, 0x2C, feature=False, args=9, doc="Set mode")
    # Per-LED: [0x00, 0xC0, 0x81, count, 0x00, idx, R, G, B, ...]
    set_led = command(0x00, 0xC0, 0x81, feature=False, args=61, doc="Set LEDs")
    # Save: [0x00, 0x50, 0x55]
    save_mode = command(0x00, 0x50, 0x55, feature=False, doc="Save to firmware")

    # fmt: off
    # Effects: set_mode args = [mode, flag, speed, brightness, color_mode, direction, R, G, B]
    effects = {
        "static":     effect("static",     steps=(step("set_mode", 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0xFF, 0x00, 0x00, use_feature=False),)),
        "breathing":  effect("breathing",  steps=(step("set_mode", 0x01, 0x00, 0x02, 0x04, 0x00, 0x00, 0xFF, 0x00, 0x00, use_feature=False),)),
        "color_cycle":effect("color_cycle",steps=(step("set_mode", 0x02, 0x00, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),)),
        "wave":       effect("wave",       steps=(step("set_mode", 0x04, 0x00, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),), directions=True),
        "ripple":     effect("ripple",     steps=(step("set_mode", 0x05, 0x00, 0x02, 0x04, 0x00, 0x00, 0xFF, 0x00, 0x00, use_feature=False),)),
        "reactive":   effect("reactive",   steps=(step("set_mode", 0x03, 0x00, 0x02, 0x04, 0x00, 0x00, 0xFF, 0x00, 0x00, use_feature=False),)),
        "starry":     effect("starry",     steps=(step("set_mode", 0x06, 0x00, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),)),
        "rain_drop":  effect("rain_drop",  steps=(step("set_mode", 0x09, 0x00, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),)),
        "direct":     effect("direct",     steps=(step("set_mode", 0x0F, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),)),
    }
    # fmt: on


AsusTUFKeyboard = HIDDevice.for_protocol(AsusTUFKeyboardProtocol)
