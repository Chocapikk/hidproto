"""Razer keyboard protocol - XOR checksum, transaction IDs, 90-byte reports.

Demonstrates hidproto with a complex protocol: custom _report() override
with checksum, transaction ID, and command class/ID encoding.
Same declarative syntax as ITE 8910, just a different report builder.

Usage::

    from examples.razer import Razer

    with Razer() as kb:
        kb.brightness(255)
        kb.effect("static", color=(255, 0, 0))
"""

from hidproto import HIDDevice, HIDProtocol, command, xor_checksum


class RazerProtocol(HIDProtocol):
    """Razer HID protocol - 90-byte feature reports with XOR checksum.

    Report layout:
    [report_id, status, transaction_id, remaining_hi, remaining_lo,
     protocol_type, data_size, command_class, command_id, args[80], crc, reserved]
    """

    vendor_id = 0x1532
    product_id = 0x0000  # override per device
    report_id = 0x00
    report_size = 90
    rows = 6
    cols = 22

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00
    transaction_id = 0x1F

    def _report(self, *data: int) -> bytes:
        """Build a Razer report: [header, command_class, command_id, args..., crc, reserved].

        First two bytes of data are command_class and command_id.
        Remaining bytes are arguments. Checksum is XOR of bytes 3..88.
        """
        buf = bytearray(self.report_size)
        buf[0] = self.report_id
        buf[1] = 0x00  # status
        buf[2] = self.transaction_id

        # data[0] = command_class, data[1] = command_id, rest = args
        if len(data) >= 2:
            buf[7] = data[0]  # command_class
            buf[8] = data[1]  # command_id
            args = data[2:]
            buf[6] = len(args)  # data_size
            for i, a in enumerate(args):
                if 9 + i < 89:
                    buf[9 + i] = a

        buf[88] = xor_checksum(bytes(buf), 3, 88)
        return bytes(buf)

    # Commands (declarative, same syntax as ITE 8910)
    #
    # The first two values in command() are command_class and command_id.
    # args= is the number of additional argument bytes.
    # _report() handles the rest: header, checksum, padding.

    static_extended = command(0x0F, 0x02, args=9, doc="Static color")
    wave_extended = command(0x0F, 0x02, args=6, doc="Wave effect")
    breathing_random = command(0x0F, 0x02, args=3, doc="Breathing random")
    spectrum_extended = command(0x0F, 0x02, args=3, doc="Spectrum cycle")
    none_extended = command(0x0F, 0x02, args=3, doc="Off")
    brightness_cmd = command(0x0F, 0x04, args=3, doc="Set brightness")


class Razer(HIDDevice):
    """High-level Razer keyboard interface."""

    proto: RazerProtocol

    def __init__(self, **kwargs: object) -> None:
        proto = RazerProtocol(**kwargs)
        super().__init__(proto)
        self.proto = proto
        self._storage = 0x05
        self._led_id = 0x00

    def brightness(self, value: int) -> None:
        report = self.proto.brightness_cmd(self._storage, self._led_id, value)
        self.send_if_changed("brightness", report)

    def effect(
        self,
        name: str,
        *,
        color: tuple[int, int, int] | None = None,
        direction: int = 0x01,
    ) -> None:
        s, led = self._storage, self._led_id
        r, g, b = color if color else (255, 255, 255)

        dispatch = {
            "static": lambda: self.proto.static_extended(s, led, 0x01, 0, 0, 0x01, r, g, b),
            "wave": lambda: self.proto.wave_extended(s, led, 0x04, 0, 0, direction),
            "breathing": lambda: self.proto.breathing_random(s, led, 0x02),
            "spectrum": lambda: self.proto.spectrum_extended(s, led, 0x03),
            "off": lambda: self.proto.none_extended(s, led, 0x00),
        }

        builder = dispatch.get(name)
        if not builder:
            raise ValueError(f"Unknown effect: {name}. Valid: {', '.join(dispatch)}")
        self.proto._send(builder())


if __name__ == "__main__":
    print("Razer protocol - report verification (no device needed)")
    print()

    proto = RazerProtocol.__new__(RazerProtocol)
    proto.report_id = 0x00
    proto.report_size = 90
    proto.transaction_id = 0x1F
    proto._seq = 0

    # Static red
    report = proto.static_extended(0x05, 0x00, 0x01, 0x00, 0x00, 0x01, 0xFF, 0x00, 0x00)
    print(f"Static red:     {report[:15].hex()} ... crc={report[88]:02x}")
    assert report[88] == xor_checksum(report, 3, 88)
    assert report[7] == 0x0F
    assert report[8] == 0x02

    # Brightness 200
    report = proto.brightness_cmd(0x05, 0x00, 0xC8)
    print(f"Brightness 200: {report[:15].hex()} ... crc={report[88]:02x}")
    assert report[88] == xor_checksum(report, 3, 88)
    assert report[7] == 0x0F
    assert report[8] == 0x04

    print()
    print("All checksums verified.")
    print()

    print("Commands:")
    for name, spec in RazerProtocol.list_commands().items():
        print(f"  {name}: opcode={tuple(hex(x) for x in spec.opcode)} - {spec.doc}")
