"""Ducky One 2 RGB keyboard - 65-byte multi-packet color protocol.

Protocol reference: OpenRGB DuckyKeyboardController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class DuckyOne2Protocol(HIDProtocol):
    """Ducky One 2 RGB - 65-byte hid_write, 8-packet color sequence."""

    vendor_id = 0x04D9
    product_id = 0x0348  # Shine 7 / One 2 RGB
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
    initialize = command(0x00, 0x41, 0x01, feature=False, doc="Initialize")
    color_init = command(0x00, 0x56, 0x81, feature=False, doc="Color init")
    color_data = command(0x00, 0x56, 0x83, feature=False, args=61, doc="Color data packet")
    terminate = command(0x00, 0x51, 0x28, feature=False, doc="Terminate")

    # Effects
    effects = {
        "direct": effect(
            "direct",
            steps=(
                step("initialize", use_feature=False),
                step("color_init", use_feature=False),
            ),
        ),
    }


DuckyOne2 = HIDDevice.for_protocol(DuckyOne2Protocol)
