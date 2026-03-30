"""ITE 8291 rev3 keyboard RGB - 8-byte control transfers, 9 effects.

Protocol reference: https://github.com/pobrn/ite8291r3-ctl

Usage::

    from examples.ite8291 import ITE8291

    with ITE8291() as kb:
        kb.effect("wave")
        kb.effect("breathing")
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step

_DIRECTIONS = ("none", "right", "left", "up", "down")


class ITE8291Protocol(HIDProtocol):
    """ITE 8291 rev3 - 8-byte control transfers, 6x21 matrix.

    Commands are 8 bytes, no report ID. Per-key colors use bulk OUT endpoint.
    SET_EFFECT: [8, control, effect, speed, brightness, color, direction, save]
    """

    vendor_id    = 0x048D
    product_id   = 0x600B
    report_id    = 0x00
    report_size  = 8
    rows         = 6
    cols         = 21

    preset_base  = 0x00
    custom_base  = 0x00
    color_custom = 0x00

    directions = _DIRECTIONS

    def _report(self, *data: int) -> bytes:
        """8-byte report, no report ID, zero-padded."""
        payload = bytes(data)
        pad = self.report_size - len(payload)
        if pad > 0:
            payload += b"\x00" * pad
        return payload[: self.report_size]

    # Commands
    # SET_EFFECT: [8, control, effect, speed, brightness, color, direction, save]
    set_effect_cmd    = command(8, args=7, doc="Set effect")
    set_brightness    = command(9, args=2, doc="Set brightness")
    set_palette_color = command(20, args=4, doc="Set palette color")
    set_row_index     = command(22, 0x00, args=1, doc="Set row index")
    get_fw_version    = command(128, doc="Get firmware version")
    get_effect_cmd    = command(136, doc="Get current effect")

    # Effects
    # set_effect_cmd args: [control, effect_id, speed, brightness, color, direction, save]
    # Default: control=0x02, speed=5, brightness=25, color=8(random), direction=1(right), save=0
    effects = {
        "breathing": effect("breathing", steps=(
            step("set_effect_cmd", 0x02, 0x02, 5, 25, 8, 0, 0),
        )),
        "wave": effect("wave", steps=(
            step("set_effect_cmd", 0x02, 0x03, 5, 25, 0, 1, 0),
        ), directions=_DIRECTIONS),
        "random": effect("random", steps=(
            step("set_effect_cmd", 0x02, 0x04, 5, 25, 8, 0, 0),
        )),
        "rainbow": effect("rainbow", steps=(
            step("set_effect_cmd", 0x02, 0x05, 0, 25, 0, 0, 0),
        )),
        "ripple": effect("ripple", steps=(
            step("set_effect_cmd", 0x02, 0x06, 5, 25, 8, 0, 0),
        )),
        "marquee": effect("marquee", steps=(
            step("set_effect_cmd", 0x02, 0x09, 5, 25, 0, 0, 0),
        )),
        "raindrop": effect("raindrop", steps=(
            step("set_effect_cmd", 0x02, 0x0A, 5, 25, 8, 0, 0),
        )),
        "aurora": effect("aurora", steps=(
            step("set_effect_cmd", 0x02, 0x0E, 5, 25, 8, 0, 0),
        )),
        "fireworks": effect("fireworks", steps=(
            step("set_effect_cmd", 0x02, 0x11, 5, 25, 8, 0, 0),
        )),
        "off": effect("off", steps=(
            step("set_effect_cmd", 0x01, 0, 0, 0, 0, 0, 0),
        )),
    }


ITE8291 = HIDDevice.for_protocol(ITE8291Protocol)


if __name__ == "__main__":
    print("ITE 8291 protocol - report verification (no device needed)")
    print()

    proto = ITE8291Protocol.__new__(ITE8291Protocol)
    proto.report_id = 0x00
    proto.report_size = 8
    proto._seq = 0

    # Breathing: [8, 0x02, 0x02, 5, 25, 8, 0, 0]
    report = proto.set_effect_cmd(0x02, 0x02, 5, 25, 8, 0, 0)
    print(f"Breathing:  {report.hex()}")
    assert report == bytes([8, 0x02, 0x02, 5, 25, 8, 0, 0])

    # Wave right: [8, 0x02, 0x03, 5, 25, 0, 1, 0]
    report = proto.set_effect_cmd(0x02, 0x03, 5, 25, 0, 1, 0)
    print(f"Wave right: {report.hex()}")
    assert report == bytes([8, 0x02, 0x03, 5, 25, 0, 1, 0])

    # Off: [8, 0x01, 0, 0, 0, 0, 0, 0]
    report = proto.set_effect_cmd(0x01, 0, 0, 0, 0, 0, 0)
    print(f"Off:        {report.hex()}")
    assert report == bytes([8, 0x01, 0, 0, 0, 0, 0, 0])

    print()
    print("All verified.")
    print()

    print("Effects:")
    for name, spec in ITE8291Protocol.effects.items():
        extra = f"  directions: {', '.join(spec.directions)}" if spec.directions else ""
        print(f"  {name:12s}  {len(spec.steps)} steps{extra}")
