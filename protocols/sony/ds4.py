"""Sony DualShock 4 gamepad - USB 64-byte reports, RGB lightbar.

Protocol reference: OpenRGB SonyDS4Controller.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class SonyDS4Protocol(HIDProtocol):
    """Sony DS4 USB - [0x05, 0x04, 0x00, ..., R, G, B at bytes 6-8]."""

    vendor_id = 0x054C
    product_id = 0x09CC  # DS4 V2
    report_id = 0x00
    report_size = 64
    rows, cols = 1, 1
    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        buf = bytearray(self.report_size)
        buf[0] = 0x05
        buf[1] = 0x04
        for i, b in enumerate(data):
            if 6 + i < self.report_size:
                buf[6 + i] = b
        return bytes(buf)

    set_color = command(args=3, feature=False, doc="Set lightbar RGB")

    # fmt: off
    effects = {
        "red":   effect("red",   steps=(step("set_color", 0xFF, 0x00, 0x00, use_feature=False),)),
        "green": effect("green", steps=(step("set_color", 0x00, 0xFF, 0x00, use_feature=False),)),
        "blue":  effect("blue",  steps=(step("set_color", 0x00, 0x00, 0xFF, use_feature=False),)),
        "off":   effect("off",   steps=(step("set_color", 0x00, 0x00, 0x00, use_feature=False),)),
    }
    # fmt: on


SonyDS4 = HIDDevice.for_protocol(SonyDS4Protocol)
