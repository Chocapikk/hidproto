"""MSI Vigor GK30 keyboard - 8-byte feature reports, palette-indexed colors.

Protocol reference: OpenRGB MSIVigorGK30Controller.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class MSIVigorGK30Protocol(HIDProtocol):
    """MSI Vigor GK30 - 8-byte feature reports with palette colors."""

    vendor_id = 0x0DB0
    product_id = 0x0B30
    report_id = 0x07
    report_size = 8
    rows = 1
    cols = 1

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    # [report_id, 0xFF, mode, color_idx, direction, speed, brightness, 0x00]
    set_mode = command(0xFF, args=5, doc="Set mode")

    # fmt: off
    # Effects: set_mode args = [mode, color_idx, direction, speed, brightness]
    effects = {
        "off":       effect("off",       steps=(step("set_mode", 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00),)),
        "static":    effect("static",    steps=(step("set_mode", 0xFF, 0x10, 0x01, 0x00, 0x00, 0x03),)),
        "breathing": effect("breathing", steps=(step("set_mode", 0xFF, 0x20, 0x00, 0x00, 0x02, 0x03),)),
        "rainbow":   effect("rainbow",   steps=(step("set_mode", 0xFF, 0x30, 0x00, 0x00, 0x02, 0x03),)),
        "meteor":    effect("meteor",    steps=(step("set_mode", 0xFF, 0x40, 0x00, 0x00, 0x02, 0x03),)),
        "ripple":    effect("ripple",    steps=(step("set_mode", 0xFF, 0x50, 0x00, 0x00, 0x02, 0x03),)),
        "dimming":   effect("dimming",   steps=(step("set_mode", 0xFF, 0x60, 0x00, 0x00, 0x02, 0x03),)),
    }
    # fmt: on


MSIVigorGK30 = HIDDevice.for_protocol(MSIVigorGK30Protocol)
