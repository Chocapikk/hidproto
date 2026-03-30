"""Fnatic Streak keyboard - 65-byte output reports.

Protocol reference: OpenRGB FnaticStreakController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class FnaticStreakProtocol(HIDProtocol):
    vendor_id = 0x2F0E
    product_id = 0x0101  # Full size
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

    direct_data = command(0x00, 0x0F, 0x03, feature=False, args=61, doc="Direct RGB")
    set_effect = command(0x00, feature=False, args=8, doc="Set effect")

    # fmt: off
    effects = {
        "pulse":    effect("pulse",    steps=(step("set_effect", 0x06, 0, 0, 0, 0, 0, 0, 0, use_feature=False),)),
        "wave":     effect("wave",     steps=(step("set_effect", 0x07, 0, 0, 0, 0, 0, 0, 0, use_feature=False),)),
        "reactive": effect("reactive", steps=(step("set_effect", 0x09, 0, 0, 0, 0, 0, 0, 0, use_feature=False),)),
        "ripple":   effect("ripple",   steps=(step("set_effect", 0x0A, 0, 0, 0, 0, 0, 0, 0, use_feature=False),)),
        "rain":     effect("rain",     steps=(step("set_effect", 0x0B, 0, 0, 0, 0, 0, 0, 0, use_feature=False),)),
        "fade":     effect("fade",     steps=(step("set_effect", 0x0D, 0, 0, 0, 0, 0, 0, 0, use_feature=False),)),
    }
    # fmt: on


FnaticStreak = HIDDevice.for_protocol(FnaticStreakProtocol)
