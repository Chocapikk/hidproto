"""Wooting keyboard - 8-byte feature reports with magic bytes.

Protocol reference: OpenRGB WootingKeyboardController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class WootingProtocol(HIDProtocol):
    """Wooting - 8-byte feature reports with 0xD0DA magic."""

    vendor_id = 0x31E3
    product_id = 0x1300  # 60HE
    report_id = 0x00
    report_size = 8
    rows = 6
    cols = 22

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        """8-byte report: [0x00, 0xD0, 0xDA, cmd, p3, p2, p1, p0]."""
        buf = bytearray(self.report_size)
        buf[0] = 0x00
        buf[1] = 0xD0
        buf[2] = 0xDA
        for i, b in enumerate(data):
            if 3 + i < self.report_size:
                buf[3 + i] = b
        return bytes(buf)

    # Commands (after magic, just cmd + params)
    single_color = command(30, doc="Single color command")
    single_reset = command(31, doc="Single reset command")
    reset_all = command(32, doc="Reset all LEDs")
    color_init = command(33, doc="Color init")
    raw_colors = command(11, doc="Raw colors report")

    # Effects
    effects = {
        "reset": effect("reset", steps=(step("reset_all"),)),
        "init": effect("init", steps=(step("color_init"),)),
    }


Wooting = HIDDevice.for_protocol(WootingProtocol)
