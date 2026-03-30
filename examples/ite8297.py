"""ITE 8297 keyboard RGB - uniform color only.

The simplest possible hidproto protocol: one command, one report.
Demonstrates that the same DSL scales from trivial (ITE 8297)
to complex (Razer 90-byte + checksum) protocols.

Usage::

    from examples.ite8297 import ITE8297

    with ITE8297() as kb:
        kb.set_color(255, 0, 0)      # red
        kb.set_color(0, 0, 0)        # off
"""

from hidproto import HIDDevice, HIDProtocol, command


class ITE8297Protocol(HIDProtocol):
    """ITE 8297 - 64-byte HID feature reports, uniform color only."""

    vendor_id    = 0x048D
    product_id   = 0x8297
    report_id    = 0xCC
    report_size  = 64

    # [CC, B0, 01, 01, R, G, B, 0x00...]
    set_color_cmd = command(0xB0, 0x01, 0x01, args=3, doc="Uniform RGB color")


ITE8297 = HIDDevice.for_protocol(ITE8297Protocol)


if __name__ == "__main__":
    print("ITE 8297 protocol - report verification (no device needed)")
    print()

    proto = ITE8297Protocol.__new__(ITE8297Protocol)
    proto.report_id = 0xCC
    proto.report_size = 64
    proto._seq = 0

    report = proto.set_color_cmd(255, 0, 0)
    print(f"Red:   {report[:8].hex()} (len={len(report)})")
    assert report[0] == 0xCC
    assert report[1] == 0xB0
    assert report[2] == 0x01
    assert report[3] == 0x01
    assert report[4] == 0xFF
    assert report[5] == 0x00
    assert report[6] == 0x00
    assert len(report) == 64

    report = proto.set_color_cmd(0, 255, 0)
    print(f"Green: {report[:8].hex()} (len={len(report)})")

    report = proto.set_color_cmd(0, 0, 0)
    print(f"Off:   {report[:8].hex()} (len={len(report)})")

    print()
    print("All verified.")
