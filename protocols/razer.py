"""Razer keyboard protocol - XOR checksum, transaction IDs, 90-byte reports.

Same declarative syntax as all other examples. Custom _report() override
handles the Razer-specific header and XOR checksum. Effects use step()
for multi-command sequences.

Protocol reference: OpenRazer / OpenRGB RazerController.

Usage::

    from examples.razer import Razer

    with Razer() as kb:
        kb.effect("static")
        kb.effect("wave")
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step, xor_checksum


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

    # Storage + LED defaults baked into commands
    storage = 0x05
    led_id = 0x00

    def _report(self, *data: int) -> bytes:
        """Build a Razer report with XOR checksum.

        data = (command_class, command_id, *args)
        """
        buf = bytearray(self.report_size)
        buf[0] = self.report_id
        buf[2] = self.transaction_id

        if len(data) >= 2:
            buf[7] = data[0]
            buf[8] = data[1]
            args = data[2:]
            buf[6] = len(args)
            for i, a in enumerate(args):
                if 9 + i < 89:
                    buf[9 + i] = a

        buf[88] = xor_checksum(bytes(buf), 3, 88)
        return bytes(buf)

    # Commands
    # static: class=0x0F, id=0x02, args=[storage, led, 0x01, 0, 0, 0x01, R, G, B]
    static_extended = command(0x0F, 0x02, args=9, doc="Static color")
    # wave: class=0x0F, id=0x02, args=[storage, led, 0x04, 0, 0, direction]
    wave_extended = command(0x0F, 0x02, args=6, doc="Wave effect")
    # breathing: class=0x0F, id=0x02, args=[storage, led, 0x02]
    breathing_random = command(0x0F, 0x02, args=3, doc="Breathing random")
    # spectrum: class=0x0F, id=0x02, args=[storage, led, 0x03]
    spectrum_extended = command(0x0F, 0x02, args=3, doc="Spectrum cycle")
    # off: class=0x0F, id=0x02, args=[storage, led, 0x00]
    none_extended = command(0x0F, 0x02, args=3, doc="Off")
    # brightness: class=0x0F, id=0x04, args=[storage, led, brightness]
    brightness_cmd = command(0x0F, 0x04, args=3, doc="Set brightness")

    # Effects (single-step, args include storage + led_id)
    effects = {
        "static": effect(
            "static", steps=(step("static_extended", 0x05, 0x00, 0x01, 0x00, 0x00, 0x01, 0xFF, 0xFF, 0xFF),)
        ),
        "wave": effect("wave", steps=(step("wave_extended", 0x05, 0x00, 0x04, 0x00, 0x00, 0x01),)),
        "breathing": effect("breathing", steps=(step("breathing_random", 0x05, 0x00, 0x02),)),
        "spectrum": effect("spectrum", steps=(step("spectrum_extended", 0x05, 0x00, 0x03),)),
        "off": effect("off", steps=(step("none_extended", 0x05, 0x00, 0x00),)),
    }


Razer = HIDDevice.for_protocol(RazerProtocol)


if __name__ == "__main__":
    print("Razer protocol - report verification (no device needed)")
    print()

    proto = RazerProtocol.__new__(RazerProtocol)
    proto.report_id = 0x00
    proto.report_size = 90
    proto.transaction_id = 0x1F
    proto._seq = 0

    # Static white (default)
    report = proto.static_extended(0x05, 0x00, 0x01, 0x00, 0x00, 0x01, 0xFF, 0xFF, 0xFF)
    print(f"Static white:   {report[:15].hex()} ... crc={report[88]:02x}")
    assert report[88] == xor_checksum(report, 3, 88)

    # Wave direction 1
    report = proto.wave_extended(0x05, 0x00, 0x04, 0x00, 0x00, 0x01)
    print(f"Wave dir=1:     {report[:15].hex()} ... crc={report[88]:02x}")
    assert report[88] == xor_checksum(report, 3, 88)

    # Brightness 200
    report = proto.brightness_cmd(0x05, 0x00, 0xC8)
    print(f"Brightness 200: {report[:15].hex()} ... crc={report[88]:02x}")
    assert report[88] == xor_checksum(report, 3, 88)

    print()
    print("All checksums verified.")
    print()

    print("Commands:")
    for name, spec in RazerProtocol.list_commands().items():
        print(f"  {name}: opcode={tuple(hex(x) for x in spec.opcode)} - {spec.doc}")

    print()
    print("Effects:")
    for name, spec in RazerProtocol.effects.items():
        print(f"  {name}: {len(spec.steps)} steps")
