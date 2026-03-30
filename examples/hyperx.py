"""HyperX Alloy Elite RGB keyboard - 65-byte feature reports, hardware modes.

Protocol reference: OpenRGB HyperXAlloyEliteController.

Usage::

    from examples.hyperx import HyperX

    with HyperX() as kb:
        kb.effect("wave", direction="right")
        kb.effect("static")
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step

_DIRECTIONS = ("right", "left", "up", "down", "in", "out")


class HyperXProtocol(HIDProtocol):
    """HyperX Alloy Elite RGB - 65-byte feature reports.

    Packet structure: [0x00, packet_id, ...data..., zero-padded to 65 bytes]
    """

    vendor_id = 0x0951
    product_id = 0x16BE  # Alloy Elite RGB
    report_id = 0x00
    report_size = 65
    rows = 6
    cols = 22

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    directions = _DIRECTIONS

    def _report(self, *data: int) -> bytes:
        """65-byte feature report, zero-padded."""
        buf = bytearray(self.report_size)
        for i, b in enumerate(data):
            if i < self.report_size:
                buf[i] = b
        return bytes(buf)

    # Commands
    # Set effect: [0x00, 0x02, mode, direction, speed, color_mode, R1, G1, B1, R2, G2, B2]
    set_effect = command(0x00, 0x02, args=10, doc="Set hardware effect")
    # Set color:  [0x00, 0x06, ...color data...]
    set_color = command(0x00, 0x06, args=62, doc="Set profile colors")
    # Direct:     [0x00, 0x16, ...per-key data...]
    direct_ctrl = command(0x00, 0x16, args=62, doc="Direct per-key control")

    # Effects
    # set_effect args: [mode, direction, speed, color_mode, R1, G1, B1, R2, G2, B2]
    effects = {
        "wave": effect(
            "wave",
            steps=(step("set_effect", 0x00, 0x00, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),),
            directions=True,
        ),
        "wave_right": effect(
            "wave_right", steps=(step("set_effect", 0x00, 0x00, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),)
        ),
        "wave_left": effect(
            "wave_left", steps=(step("set_effect", 0x00, 0x01, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),)
        ),
        "wave_up": effect(
            "wave_up", steps=(step("set_effect", 0x00, 0x02, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),)
        ),
        "wave_down": effect(
            "wave_down", steps=(step("set_effect", 0x00, 0x03, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),)
        ),
        "static": effect(
            "static", steps=(step("set_effect", 0x01, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00),)
        ),
        "static_dual": effect(
            "static_dual", steps=(step("set_effect", 0x01, 0x00, 0x00, 0x01, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xFF),)
        ),
        "breathing": effect(
            "breathing", steps=(step("set_effect", 0x02, 0x00, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),)
        ),
    }


HyperX = HIDDevice.for_protocol(HyperXProtocol)


if __name__ == "__main__":
    print("HyperX protocol - report verification (no device needed)")
    print()

    proto = HyperXProtocol.__new__(HyperXProtocol)
    proto.report_id = 0x00
    proto.report_size = 65
    proto._seq = 0

    # Wave right: [0x00, 0x02, 0x00, 0x00, 0x05, 0x02, ...]
    report = proto.set_effect(0x00, 0x00, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
    print(f"Wave right: {report[:12].hex()} (len={len(report)})")
    assert report[1] == 0x02  # packet_id
    assert report[2] == 0x00  # mode = wave
    assert report[3] == 0x00  # direction = right
    assert len(report) == 65

    # Static red: [0x00, 0x02, 0x01, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, ...]
    report = proto.set_effect(0x01, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00)
    print(f"Static red: {report[:12].hex()} (len={len(report)})")
    assert report[2] == 0x01  # mode = static
    assert report[6] == 0xFF  # R

    print()
    print("All verified.")
    print()

    print("Effects:")
    for name, spec in HyperXProtocol.effects.items():
        from hidproto.effect import resolve_directions

        dirs = resolve_directions(proto, spec)
        extra = f"  directions: {', '.join(dirs)}" if dirs else ""
        print(f"  {name:16s}  {len(spec.steps)} steps{extra}")
