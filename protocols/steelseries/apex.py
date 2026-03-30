"""SteelSeries Apex keyboard protocol - 65/643-byte feature reports.

Protocol reference: OpenRGB SteelSeriesApexController.

Usage::

    from examples.steelseries import SteelSeries

    with SteelSeries() as kb:
        kb.effect("direct")
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class SteelSeriesApexProtocol(HIDProtocol):
    """SteelSeries Apex - 65-byte feature reports (643 for direct mode).

    Packets: [0x00, packet_id, ...data..., zero-padded]
    """

    vendor_id = 0x1038
    product_id = 0x1610  # Apex Pro
    report_id = 0x00
    report_size = 65
    rows = 6
    keyboard_size = "full"
    cols = 22

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        """65-byte feature report, zero-padded."""
        buf = bytearray(self.report_size)
        for i, b in enumerate(data):
            if i < self.report_size:
                buf[i] = b
        return bytes(buf)

    # Commands
    # Direct init: [0x00, 0x3A, ...] (or 0x40 for 2023 models)
    direct_init = command(0x00, 0x3A, doc="Direct mode init")
    # Select profile: [0x00, 0x89, profile_id]
    select_profile = command(0x00, 0x89, args=1, doc="Select profile")
    # Get serial: [0x00, 0xFF]
    get_serial = command(0x00, 0xFF, feature=False, doc="Get serial number")
    # Get firmware: [0x00, 0x90]
    get_firmware = command(0x00, 0x90, feature=False, doc="Get firmware version")

    # Effects
    effects = {
        "direct": effect("direct", steps=(step("direct_init"),)),
        "profile_1": effect("profile_1", steps=(step("select_profile", 0x01),)),
        "profile_2": effect("profile_2", steps=(step("select_profile", 0x02),)),
        "profile_3": effect("profile_3", steps=(step("select_profile", 0x03),)),
    }


SteelSeriesApex = HIDDevice.for_protocol(SteelSeriesApexProtocol)


if __name__ == "__main__":
    print("SteelSeries protocol - report verification (no device needed)")
    print()

    proto = SteelSeriesApexProtocol.__new__(SteelSeriesApexProtocol)
    proto.report_id = 0x00
    proto.report_size = 65
    proto._seq = 0

    # Direct init
    report = proto.direct_init()
    print(f"Direct init:  {report[:8].hex()} (len={len(report)})")
    assert report[1] == 0x3A
    assert len(report) == 65

    # Select profile 1
    report = proto.select_profile(0x01)
    print(f"Profile 1:    {report[:8].hex()} (len={len(report)})")
    assert report[1] == 0x89
    assert report[2] == 0x01

    # Get serial
    report = proto.get_serial()
    print(f"Get serial:   {report[:8].hex()} (len={len(report)})")
    assert report[1] == 0xFF

    print()
    print("All verified.")
    print()

    print("Commands:")
    for name, spec in SteelSeriesApexProtocol.list_commands().items():
        feat = "feature" if spec.use_feature else "output"
        print(f"  {name:16s}  [{feat}]  {spec.doc}")

    print()
    print("Effects:")
    for name, spec in SteelSeriesApexProtocol.effects.items():
        print(f"  {name:12s}  {len(spec.steps)} steps")
