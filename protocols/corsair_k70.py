"""Corsair Peripheral keyboard protocol - 65-byte output reports, hardware modes.

Demonstrates multi-step effects with the step() builder. Each hardware
mode requires a sequence: brightness -> header -> stream config. This is
defined declaratively in the effects dict.

Protocol reference: OpenRGB CorsairPeripheralController.

Usage::

    from examples.corsair import Corsair

    with Corsair() as kb:
        kb.effect("rainbow_wave", brightness=0x03, speed=0x02)
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class CorsairK70Protocol(HIDProtocol):
    """Corsair Peripheral - 65-byte output reports via hid_write."""

    vendor_id = 0x1B1C
    product_id = 0x1B2D  # K70 RGB, override per device
    report_id = 0x00
    report_size = 65
    rows = 7
    cols = 22

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    def _report(self, *data: int) -> bytes:
        """65-byte output report, zero-padded."""
        buf = bytearray(self.report_size)
        for i, b in enumerate(data):
            if i < self.report_size:
                buf[i] = b
        return bytes(buf)

    # Commands (all output reports)
    lighting_control = command(0x00, 0x07, 0x05, 0x01, feature=False, args=1, doc="Lighting control mode")
    set_brightness = command(0x00, 0x07, 0x05, 0x02, feature=False, args=1, doc="Set brightness (0-3)")
    special_function = command(0x00, 0x07, 0x04, 0x02, feature=False, doc="Special function control")

    # Mode header: "lght_00.d"
    mode_header = command(
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
        feature=False,
        doc="Mode header (lght_00.d)",
    )

    # Stream mode config: [0x00, 0x7F, packet_id, data_sz, 0x00, mode, speed, random, direction, ...]
    stream_config = command(0x00, 0x7F, 0x01, 0x0D, 0x00, feature=False, args=8, doc="Stream mode config")

    # Effects (multi-step: brightness -> header -> stream config)
    effects = {
        "color_shift": effect(
            "color_shift",
            steps=(
                step("set_brightness", 0x03, use_feature=False),
                step("mode_header", use_feature=False),
                step("stream_config", 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),
            ),
        ),
        "color_pulse": effect(
            "color_pulse",
            steps=(
                step("set_brightness", 0x03, use_feature=False),
                step("mode_header", use_feature=False),
                step("stream_config", 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),
            ),
        ),
        "rainbow_wave": effect(
            "rainbow_wave",
            steps=(
                step("set_brightness", 0x03, use_feature=False),
                step("mode_header", use_feature=False),
                step("stream_config", 0x03, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),
            ),
        ),
        "color_wave": effect(
            "color_wave",
            steps=(
                step("set_brightness", 0x03, use_feature=False),
                step("mode_header", use_feature=False),
                step("stream_config", 0x04, 0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, use_feature=False),
            ),
        ),
        "rain": effect(
            "rain",
            steps=(
                step("set_brightness", 0x03, use_feature=False),
                step("mode_header", use_feature=False),
                step("stream_config", 0x06, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),
            ),
        ),
        "spiral": effect(
            "spiral",
            steps=(
                step("set_brightness", 0x03, use_feature=False),
                step("mode_header", use_feature=False),
                step("stream_config", 0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),
            ),
        ),
        "visor": effect(
            "visor",
            steps=(
                step("set_brightness", 0x03, use_feature=False),
                step("mode_header", use_feature=False),
                step("stream_config", 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, use_feature=False),
            ),
        ),
    }


CorsairK70 = HIDDevice.for_protocol(CorsairK70Protocol)


if __name__ == "__main__":
    print("Corsair protocol - report verification (no device needed)")
    print()

    proto = CorsairK70Protocol.__new__(CorsairK70Protocol)
    proto.report_id = 0x00
    proto.report_size = 65
    proto._seq = 0

    # Lighting control
    report = proto.lighting_control(0x02)
    print(f"SW mode:    {report[:8].hex()} (len={len(report)})")
    assert report[1] == 0x07

    # Mode header
    report = proto.mode_header()
    print(f"Header:     {report[:15].hex()} (len={len(report)})")
    assert report[5] == 0x6C  # 'l'
    assert report[9] == 0x5F  # '_'

    # Stream config for rainbow_wave (mode=0x03, speed=0x02)
    report = proto.stream_config(0x03, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
    print(f"Rainbow:    {report[:13].hex()} (len={len(report)})")
    assert report[1] == 0x7F
    assert report[5] == 0x03  # mode
    assert report[6] == 0x02  # speed

    print()
    print("All verified.")
    print()

    print("Commands:")
    for name, spec in CorsairK70Protocol.list_commands().items():
        feat = "feature" if spec.use_feature else "output"
        print(f"  {name:20s}  [{feat}]  {spec.doc}")

    print()
    print("Effects (multi-step):")
    for name, spec in CorsairK70Protocol.effects.items():
        print(f"  {name:20s}  {len(spec.steps)} steps")
