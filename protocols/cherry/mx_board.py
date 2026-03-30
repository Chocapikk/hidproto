"""Cherry keyboard - 64-byte reports with 16-bit checksum.

Protocol reference: OpenRGB CherryKeyboardController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class CherryKeyboardProtocol(HIDProtocol):
    """Cherry keyboard - 64-byte reports, checksum at bytes 1-2."""

    vendor_id = 0x046A
    product_id = 0x00AB  # MX Board 1.0
    report_id = 0x00
    report_size = 64
    rows = 6
    keyboard_size = "full"
    cols = 22

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        """64-byte report: [0x04, csum_L, csum_H, cmd, ...data...]."""
        buf = bytearray(self.report_size)
        buf[0] = 0x04
        for i, b in enumerate(data):
            if 3 + i < self.report_size:
                buf[3 + i] = b
        # 16-bit checksum over bytes 3..63
        csum = sum(buf[3:]) & 0xFFFF
        buf[1] = csum & 0xFF
        buf[2] = (csum >> 8) & 0xFF
        return bytes(buf)

    begin = command(0x01, doc="Begin transaction")
    end = command(0x02, doc="End transaction")
    set_param = command(0x06, args=10, doc="Set parameter")
    set_colors = command(0x0B, args=59, doc="Write color data")

    # fmt: off
    # set_param args: [param_type, mode, speed, brightness, direction, R, G, B, R2, G2]
    effects = {
        "wave":      effect("wave",      steps=(step("begin"), step("set_param", 0x01, 0x00, 0x05, 0x05, 0x00, 0, 0, 0, 0, 0), step("end"),)),
        "spectrum":  effect("spectrum",  steps=(step("begin"), step("set_param", 0x01, 0x01, 0x05, 0x05, 0x00, 0, 0, 0, 0, 0), step("end"),)),
        "breathing": effect("breathing", steps=(step("begin"), step("set_param", 0x01, 0x02, 0x05, 0x05, 0x00, 0xFF, 0, 0, 0, 0), step("end"),)),
        "static":    effect("static",    steps=(step("begin"), step("set_param", 0x01, 0x03, 0x00, 0x05, 0x00, 0xFF, 0, 0, 0, 0), step("end"),)),
        "radar":     effect("radar",     steps=(step("begin"), step("set_param", 0x01, 0x04, 0x05, 0x05, 0x00, 0, 0, 0, 0, 0), step("end"),)),
        "fire":      effect("fire",      steps=(step("begin"), step("set_param", 0x01, 0x06, 0x05, 0x05, 0x00, 0xFF, 0, 0, 0, 0), step("end"),)),
        "stars":     effect("stars",     steps=(step("begin"), step("set_param", 0x01, 0x07, 0x05, 0x05, 0x00, 0, 0, 0, 0, 0), step("end"),)),
        "rain":      effect("rain",      steps=(step("begin"), step("set_param", 0x01, 0x0B, 0x05, 0x05, 0x00, 0, 0, 0, 0, 0), step("end"),)),
    }
    # fmt: on


CherryKeyboard = HIDDevice.for_protocol(CherryKeyboardProtocol)
