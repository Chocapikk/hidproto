"""Corsair Peripheral keyboard protocol - 65-byte output reports, hardware modes.

Demonstrates hidproto with output reports (hid_write) instead of feature
reports, multi-step mode setup, and string literals in packets ("lght_00.d").

Protocol reference: OpenRGB CorsairPeripheralController.

Usage::

    from examples.corsair import Corsair

    with Corsair() as kb:
        kb.effect("wave", direction=0x01, speed=0x02, brightness=0x03)
"""

from hidproto import HIDDevice, HIDProtocol, command


class CorsairProtocol(HIDProtocol):
    """Corsair Peripheral - 65-byte output reports via hid_write.

    Commands:
    - WRITE (0x07): control packets (brightness, lighting control, firmware info)
    - STREAM (0x7F): streaming data (mode config, per-key colors)
    """

    vendor_id = 0x1B1C
    product_id = 0x1B2D  # K70 RGB, override per device
    report_id = 0x00
    report_size = 65
    rows = 7
    cols = 22

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    # Mode IDs
    mode_direct = 0xFF
    mode_color_shift = 0x00
    mode_color_pulse = 0x01
    mode_spiral = 0x02
    mode_rainbow_wave = 0x03
    mode_color_wave = 0x04
    mode_visor = 0x05
    mode_rain = 0x06
    mode_type_key = 0x08
    mode_type_ripple = 0x09

    def _report(self, *data: int) -> bytes:
        """65-byte output report, zero-padded, no report ID prefix in data."""
        buf = bytearray(self.report_size)
        for i, b in enumerate(data):
            if i < self.report_size:
                buf[i] = b
        return bytes(buf)

    # Commands (all use hid_write, feature=False)
    lighting_control = command(0x00, 0x07, 0x05, 0x01, feature=False, args=1, doc="Lighting control mode")
    set_brightness = command(0x00, 0x07, 0x05, 0x02, feature=False, args=1, doc="Set brightness (0-3)")
    special_function = command(0x00, 0x07, 0x04, 0x02, feature=False, doc="Special function control")
    stream_mode = command(0x00, 0x7F, feature=False, args=12, doc="Stream mode config")

    # Effects
    effects = {}  # Corsair modes are complex, handled in device layer


class Corsair(HIDDevice):
    """High-level Corsair keyboard interface."""

    proto: CorsairProtocol

    def __init__(self, **kwargs: object) -> None:
        proto = CorsairProtocol(**kwargs)
        super().__init__(proto)
        self.proto = proto

    def switch_to_software(self) -> None:
        """Switch to software lighting control."""
        self.proto._write(self.proto.lighting_control(0x02))

    def switch_to_hardware(self) -> None:
        """Switch to hardware lighting control."""
        self.proto._write(self.proto.lighting_control(0x01))

    def brightness(self, value: int) -> None:
        """Set brightness (0-3)."""
        report = self.proto.set_brightness(max(0, min(3, value)))
        self.send_if_changed("brightness", report)

    def effect(
        self,
        name: str,
        *,
        speed: int = 0x02,
        direction: int = 0x00,
        brightness: int = 0x03,
        color: tuple[int, int, int] | None = None,
        random_color: bool = False,
    ) -> None:
        """Apply a hardware effect."""
        modes = {
            "color_shift": self.proto.mode_color_shift,
            "color_pulse": self.proto.mode_color_pulse,
            "spiral": self.proto.mode_spiral,
            "rainbow_wave": self.proto.mode_rainbow_wave,
            "color_wave": self.proto.mode_color_wave,
            "visor": self.proto.mode_visor,
            "rain": self.proto.mode_rain,
            "type_key": self.proto.mode_type_key,
            "type_ripple": self.proto.mode_type_ripple,
        }

        mode_id = modes.get(name)
        if mode_id is None:
            raise ValueError(f"Unknown effect: {name}. Valid: {', '.join(modes)}")

        # Set brightness
        self.proto._write(self.proto.set_brightness(brightness))

        # Send "lght_00.d" header
        header = self.proto._report(
            0x00,
            0x07,
            0x17,
            0x05,
            0x00,
            0x6C,
            0x67,
            0x68,
            0x74,
            0x5F,  # "lght_"
            0x30,
            0x30,
            0x2E,
            0x64,  # "00.d"
        )
        self.proto._write(header)

        # Stream mode config
        speed_offset = 0x04 if mode_id == self.proto.mode_type_key else 0x01
        config = bytearray(12)
        config[0] = mode_id
        config[3] = direction
        config[speed_offset] = speed
        if random_color:
            config[2] = 0x01

        if color:
            config[5] = color[0]
            config[6] = color[1]
            config[7] = color[2]

        report = self.proto._report(0x00, 0x7F, 0x01, 0x0D, 0x00, *config)
        self.proto._write(report)


if __name__ == "__main__":
    print("Corsair protocol - report verification (no device needed)")
    print()

    proto = CorsairProtocol.__new__(CorsairProtocol)
    proto.report_id = 0x00
    proto.report_size = 65
    proto._seq = 0

    # Lighting control (software mode)
    report = proto.lighting_control(0x02)
    print(f"SW mode:    {report[:8].hex()} (len={len(report)})")
    assert len(report) == 65
    assert report[1] == 0x07
    assert report[2] == 0x05
    assert report[3] == 0x01
    assert report[4] == 0x02

    # Set brightness
    report = proto.set_brightness(0x03)
    print(f"Bright 3:   {report[:8].hex()} (len={len(report)})")
    assert report[1] == 0x07
    assert report[4] == 0x03

    print()
    print("All verified.")
    print()

    print("Commands:")
    for name, spec in CorsairProtocol.list_commands().items():
        feat = "feature" if spec.use_feature else "output"
        print(f"  {name:20s}  [{feat}]  {spec.doc}")
