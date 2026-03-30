"""Roccat Vulcan keyboard - 65-byte reports, 16-bit checksum.

Protocol reference: OpenRGB RoccatVulcanKeyboardController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class RoccatVulcanProtocol(HIDProtocol):
    """Roccat Vulcan - 65-byte hid_write + feature reports with 16-bit checksum."""

    vendor_id = 0x1E7D
    product_id = 0x307A  # Vulcan 100 Aimo
    report_id = 0x00
    report_size = 65
    rows = 6
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

    # Commands
    direct_ctrl = command(0x00, 0xA1, feature=False, args=62, doc="Direct LED update")
    set_mode = command(0x0D, args=6, doc="Set mode (with checksum)")

    # Effects
    effects = {
        "direct": effect("direct", steps=(step("direct_ctrl"),)),
        "static": effect("static", steps=(step("set_mode", 0x00, 0x00, 0x00, 0x01, 0x45, 0x00),)),
        "wave": effect("wave", steps=(step("set_mode", 0x00, 0x00, 0x00, 0x0A, 0x06, 0x45),)),
    }


RoccatVulcan = HIDDevice.for_protocol(RoccatVulcanProtocol)
