"""CoolerMaster keyboard - 65-byte output reports, V2 protocol.

Protocol reference: OpenRGB CMKeyboardController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class CoolerMasterKeyboardProtocol(HIDProtocol):
    """CoolerMaster keyboard - 65-byte hid_write."""

    vendor_id = 0x2516
    product_id = 0x003B  # MasterKeys Pro L
    report_id = 0x00
    report_size = 65
    rows = 7
    cols = 22

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        buf = bytearray(self.report_size)
        for i, b in enumerate(data):
            if i < self.report_size:
                buf[i] = b
        return bytes(buf)

    set_mode = command(0x41, feature=False, args=1, doc="Set control mode")
    set_effect = command(0x51, 0x2C, 0x00, 0x00, feature=False, args=8, doc="Set effect")
    direct_ctrl = command(0xC0, feature=False, args=63, doc="Direct LED data")

    # fmt: off
    effects = {
        "direct":    effect("direct",    steps=(step("set_mode", 0x80, use_feature=False),)),
        "static":    effect("static",    steps=(step("set_effect", 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),)),
        "breathing": effect("breathing", steps=(step("set_effect", 0x01, 0x00, 0xFF, 0x00, 0x00, 0x04, 0x00, 0x00, use_feature=False),)),
        "cycle":     effect("cycle",     steps=(step("set_effect", 0x02, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, use_feature=False),)),
        "wave":      effect("wave",      steps=(step("set_effect", 0x03, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, use_feature=False),)),
        "ripple":    effect("ripple",    steps=(step("set_effect", 0x04, 0x00, 0xFF, 0x00, 0x00, 0x04, 0x00, 0x00, use_feature=False),)),
        "snake":     effect("snake",     steps=(step("set_effect", 0x08, 0x00, 0xFF, 0x00, 0x00, 0x04, 0x00, 0x00, use_feature=False),)),
        "reactive":  effect("reactive",  steps=(step("set_effect", 0x09, 0x00, 0xFF, 0x00, 0x00, 0x04, 0x00, 0x00, use_feature=False),)),
        "stars":     effect("stars",     steps=(step("set_effect", 0x07, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, use_feature=False),)),
    }
    # fmt: on


CoolerMasterKeyboard = HIDDevice.for_protocol(CoolerMasterKeyboardProtocol)
