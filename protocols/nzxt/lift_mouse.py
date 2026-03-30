"""NZXT Lift mouse - 64-byte output reports.

Protocol reference: OpenRGB NZXTMouseController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class NZXTLiftProtocol(HIDProtocol):
    vendor_id = 0x1E71
    product_id = 0x2100
    report_id = 0x00
    report_size = 64
    rows, cols = 1, 5
    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        """[0x43, 0xAE, ...data]."""
        buf = bytearray(self.report_size)
        buf[0] = 0x43
        buf[1] = 0xAE
        for i, b in enumerate(data):
            if 2 + i < self.report_size:
                buf[2 + i] = b
        return bytes(buf)

    set_direct = command(0x00, 0x10, 0x02, 0x3F, args=20, doc="Direct LED control")

    effects = {
        "direct": effect("direct", steps=(step("set_direct"),)),
    }


NZXTLift = HIDDevice.for_protocol(NZXTLiftProtocol)
