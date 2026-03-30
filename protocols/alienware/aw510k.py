"""Alienware AW510K keyboard - 65-byte reports.

Protocol reference: OpenRGB AlienwareAW510KController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class AlienwareAW510KProtocol(HIDProtocol):
    vendor_id = 0x04F2
    product_id = 0x1830
    report_id = 0x00
    report_size = 65
    rows, cols = 6, 22
    keyboard_size = "full"
    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        buf = bytearray(self.report_size)
        for i, b in enumerate(data):
            if i < self.report_size:
                buf[i] = b
        return bytes(buf)

    initialize = command(0x00, 0x0E, doc="Initialize")
    commit = command(0x00, 0x05, doc="Commit")
    set_mode = command(0x00, 0x01, args=10, doc="Set mode")

    # fmt: off
    effects = {
        "off":       effect("off",       steps=(step("set_mode", 0x00, 0, 0, 0, 0, 0, 0, 0, 0, 0),)),
        "static":    effect("static",    steps=(step("set_mode", 0x13, 0, 0, 0, 0xFF, 0, 0, 0, 0, 0),)),
        "breathing": effect("breathing", steps=(step("set_mode", 0x07, 0, 5, 0, 0xFF, 0, 0, 0, 0, 0),)),
        "spectrum":  effect("spectrum",  steps=(step("set_mode", 0x08, 0, 5, 0, 0, 0, 0, 0, 0, 0),)),
        "wave":      effect("wave",      steps=(step("set_mode", 0x0F, 0, 5, 0, 0, 0, 0, 0, 0, 0),)),
        "rainbow":   effect("rainbow",   steps=(step("set_mode", 0x10, 0, 5, 0, 0, 0, 0, 0, 0, 0),)),
        "scanner":   effect("scanner",   steps=(step("set_mode", 0x11, 0, 5, 0, 0xFF, 0, 0, 0, 0, 0),)),
    }
    # fmt: on


AlienwareAW510K = HIDDevice.for_protocol(AlienwareAW510KProtocol)
