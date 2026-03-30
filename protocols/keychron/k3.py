"""Keychron K3 V2 keyboard - 64-byte reports with checksum.

Protocol reference: OpenRGB KeychronKeyboardController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class KeychronK3Protocol(HIDProtocol):
    """Keychron K3 V2 Optical RGB - 64-byte reports."""

    vendor_id = 0x05AC  # Apple VID (Keychron uses it)
    product_id = 0x024F
    report_id = 0x00
    report_size = 64
    rows = 5
    cols = 16

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        """64-byte report with 0x04 header."""
        buf = bytearray(self.report_size)
        buf[0] = 0x04
        for i, b in enumerate(data):
            if 1 + i < self.report_size:
                buf[1 + i] = b
        return bytes(buf)

    led_effect_start = command(0xF0, args=10, doc="Start LED effect")
    turn_on_custom = command(0x18, doc="Turn on customization")
    end_communication = command(0x02, doc="End communication")

    # fmt: off
    # led_effect_start args: [mode, speed, brightness, direction, R, G, B, ...]
    effects = {
        "static":       effect("static",       steps=(step("led_effect_start", 0x01, 0x05, 0x05, 0x00, 0xFF, 0x00, 0x00, 0, 0, 0),)),
        "breathing":    effect("breathing",    steps=(step("led_effect_start", 0x07, 0x05, 0x05, 0x00, 0xFF, 0x00, 0x00, 0, 0, 0),)),
        "spectrum":     effect("spectrum",     steps=(step("led_effect_start", 0x08, 0x05, 0x05, 0x00, 0x00, 0x00, 0x00, 0, 0, 0),)),
        "sparkle":      effect("sparkle",      steps=(step("led_effect_start", 0x04, 0x05, 0x05, 0x00, 0x00, 0x00, 0x00, 0, 0, 0),)),
        "rain":         effect("rain",         steps=(step("led_effect_start", 0x05, 0x05, 0x05, 0x00, 0x00, 0x00, 0x00, 0, 0, 0),)),
        "random":       effect("random",       steps=(step("led_effect_start", 0x06, 0x05, 0x05, 0x00, 0x00, 0x00, 0x00, 0, 0, 0),)),
        "off":          effect("off",          steps=(step("led_effect_start", 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 0, 0),)),
    }
    # fmt: on


KeychronK3 = HIDDevice.for_protocol(KeychronK3Protocol)
