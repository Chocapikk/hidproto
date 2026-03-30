"""Das Keyboard Q5 - 9-byte feature reports with XOR checksum.

Protocol reference: OpenRGB DasKeyboardController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step, xor_checksum


class DasQ5Protocol(HIDProtocol):
    vendor_id = 0x24F0
    product_id = 0x2020
    report_id = 0x00
    report_size = 9
    rows, cols = 6, 22
    keyboard_size = "full"
    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        """[0xEA, length, ...data, xor_checksum]."""
        buf = bytearray(self.report_size)
        buf[0] = 0xEA
        n = min(len(data), self.report_size - 3)
        buf[1] = n
        for i in range(n):
            buf[2 + i] = data[i]
        buf[2 + n] = xor_checksum(bytes(buf), 0, 2 + n)
        return bytes(buf)

    init_cmd = command(0x02, doc="Initialize")
    color_cmd = command(0x08, args=5, doc="Set key color")
    apply_cmd = command(0x03, doc="Apply changes")

    effects = {
        "apply": effect("apply", steps=(step("init_cmd"), step("apply_cmd"))),
    }


DasQ5 = HIDDevice.for_protocol(DasQ5Protocol)
