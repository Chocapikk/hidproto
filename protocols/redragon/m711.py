"""Redragon mouse - 16-byte feature reports.

Protocol reference: OpenRGB RedragonController.
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class RedragonMouseProtocol(HIDProtocol):
    """Redragon mouse - 16-byte feature reports."""

    vendor_id = 0x04D9
    product_id = 0xFC30  # M711
    report_id = 0x02
    report_size = 16
    rows = 1
    cols = 1

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    apply = command(0xF1, 0x02, 0x04, args=4, doc="Apply settings")
    write = command(0xF3, args=12, doc="Write data")

    # fmt: off
    effects = {
        "wave":      effect("wave",      steps=(step("apply", 0x00, 0x00, 0x00, 0x00),)),
        "breathing": effect("breathing", steps=(step("apply", 0x04, 0x00, 0x00, 0x00),)),
        "static":    effect("static",    steps=(step("apply", 0x02, 0x00, 0x00, 0x00),)),
        "rainbow":   effect("rainbow",   steps=(step("apply", 0x08, 0x00, 0x00, 0x00),)),
        "flashing":  effect("flashing",  steps=(step("apply", 0x10, 0x00, 0x00, 0x00),)),
    }
    # fmt: on


RedragonMouse = HIDDevice.for_protocol(RedragonMouseProtocol)
