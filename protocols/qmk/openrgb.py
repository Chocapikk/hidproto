"""QMK OpenRGB protocol - 65-byte reports, universal keyboard firmware.

Protocol reference: OpenRGB QMKOpenRGBController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class QMKOpenRGBProtocol(HIDProtocol):
    """QMK OpenRGB - 65-byte reports, detected by usage page 0xFF60."""

    vendor_id = 0x0000  # device-specific
    product_id = 0x0000  # device-specific
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

    get_protocol = command(0x00, 0x01, feature=False, doc="Get protocol version")
    get_qmk_ver = command(0x00, 0x02, feature=False, doc="Get QMK version")
    get_device = command(0x00, 0x03, feature=False, doc="Get device info")
    get_mode = command(0x00, 0x04, feature=False, args=1, doc="Get mode info")
    get_leds = command(0x00, 0x05, feature=False, args=1, doc="Get LED info")
    get_modes = command(0x00, 0x06, feature=False, doc="Get enabled modes")
    set_mode = command(0x00, 0x08, feature=False, args=7, doc="Set mode")
    set_single_led = command(0x00, 0x09, feature=False, args=4, doc="Direct set single LED")
    set_leds = command(0x00, 0x0A, feature=False, args=62, doc="Direct set LEDs batch")

    # fmt: off
    # set_mode args: [mode_id, speed, H, S, V, 0, 0]
    effects = {
        "direct":      effect("direct",      steps=(step("set_mode", 0x01, 0x7F, 0x00, 0xFF, 0xFF, 0, 0, use_feature=False),)),
        "solid":       effect("solid",       steps=(step("set_mode", 0x02, 0x7F, 0x00, 0xFF, 0xFF, 0, 0, use_feature=False),)),
        "breathing":   effect("breathing",   steps=(step("set_mode", 0x05, 0x7F, 0x00, 0xFF, 0xFF, 0, 0, use_feature=False),)),
        "rainbow":     effect("rainbow",     steps=(step("set_mode", 0x06, 0x7F, 0x00, 0xFF, 0xFF, 0, 0, use_feature=False),)),
        "swirl":       effect("swirl",       steps=(step("set_mode", 0x0D, 0x7F, 0x00, 0xFF, 0xFF, 0, 0, use_feature=False),)),
        "snake":       effect("snake",       steps=(step("set_mode", 0x15, 0x7F, 0x00, 0xFF, 0xFF, 0, 0, use_feature=False),)),
        "knight":      effect("knight",      steps=(step("set_mode", 0x16, 0x7F, 0x00, 0xFF, 0xFF, 0, 0, use_feature=False),)),
        "splash":      effect("splash",      steps=(step("set_mode", 0x1A, 0x7F, 0x00, 0xFF, 0xFF, 0, 0, use_feature=False),)),
    }
    # fmt: on


QMKOpenRGB = HIDDevice.for_protocol(QMKOpenRGBProtocol)
