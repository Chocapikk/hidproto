"""Anne Pro 2 keyboard - 64-byte output reports with service header.

Protocol reference: OpenRGB AnnePro2Controller.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class AnnePro2Protocol(HIDProtocol):
    """Anne Pro 2 - 64-byte hid_write with service header."""

    vendor_id = 0x04D9
    product_id = 0x8008
    report_id = 0x00
    report_size = 64
    rows = 5
    cols = 14

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        """64-byte report with service header [0x00, 0x7B, 0x10, 0x41]."""
        buf = bytearray(self.report_size)
        buf[0] = 0x00
        buf[1] = 0x7B
        buf[2] = 0x10
        buf[3] = 0x41
        for i, b in enumerate(data):
            if 4 + i < self.report_size:
                buf[4 + i] = b
        return bytes(buf)

    static_msg = command(0x00, 0x00, 0x7D, feature=False, doc="Static color message")
    command_info = command(0x20, 0x03, 0xFF, feature=False, doc="Command info")

    effects = {
        "static": effect("static", steps=(step("static_msg", use_feature=False),)),
    }


AnnePro2 = HIDDevice.for_protocol(AnnePro2Protocol)
