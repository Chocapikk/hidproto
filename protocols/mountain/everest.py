"""Mountain Everest keyboard - 65-byte output reports.

Protocol reference: OpenRGB MountainKeyboardController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class MountainEverestProtocol(HIDProtocol):
    vendor_id = 0x3282
    product_id = 0x0001
    report_id = 0x00
    report_size = 65
    rows, cols = 6, 22
    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        buf = bytearray(self.report_size)
        for i, b in enumerate(data):
            if i < self.report_size:
                buf[i] = b
        return bytes(buf)

    send_cmd = command(0x14, feature=False, args=10, doc="Send command")
    save_cmd = command(0x13, feature=False, doc="Save")
    send_color = command(0x2C, feature=False, args=62, doc="Color data")

    # fmt: off
    effects = {
        "static":    effect("static",    steps=(step("send_cmd", 0x00, 0x00, 0, 0, 0, 0xFF, 0, 0, 0, 0, use_feature=False),)),
        "breathing": effect("breathing", steps=(step("send_cmd", 0x00, 0x01, 5, 0, 0, 0xFF, 0, 0, 0, 0, use_feature=False),)),
        "wave":      effect("wave",      steps=(step("send_cmd", 0x00, 0x04, 5, 0, 0, 0, 0, 0, 0, 0, use_feature=False),)),
        "reactive":  effect("reactive",  steps=(step("send_cmd", 0x00, 0x03, 5, 0, 0, 0xFF, 0, 0, 0, 0, use_feature=False),)),
        "tornado":   effect("tornado",   steps=(step("send_cmd", 0x00, 0x07, 5, 0, 0, 0, 0, 0, 0, 0, use_feature=False),)),
        "off":       effect("off",       steps=(step("send_cmd", 0x00, 0x0C, 0, 0, 0, 0, 0, 0, 0, 0, use_feature=False),)),
    }
    # fmt: on


MountainEverest = HIDDevice.for_protocol(MountainEverestProtocol)
