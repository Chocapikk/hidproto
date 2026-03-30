"""ITE 8291 rev3 keyboard RGB - 8-byte control transfers, row-based colors.

Different transport than ITE 8910 (USB control transfer vs hidraw feature report)
but same DSL. Demonstrates hidproto with palette colors, directions, and
per-row bulk writes.

Protocol reference: https://github.com/pobrn/ite8291r3-ctl

Usage::

    from examples.ite8291 import ITE8291

    with ITE8291() as kb:
        kb.effect("wave", direction="right", brightness=25, speed=5)
"""

from hidproto import HIDDevice, HIDProtocol, command, effect

_DIRECTIONS = ("none", "right", "left", "up", "down")
_COLORS = ("none", "red", "orange", "yellow", "green", "blue", "teal", "purple", "random")


class ITE8291Protocol(HIDProtocol):
    """ITE 8291 rev3 - 8-byte control transfers, 6x21 matrix.

    Commands are sent as USB HID SET_REPORT class requests (not hidraw feature
    reports). The report is 8 bytes, zero-padded, no report ID prefix.
    Per-key colors are sent row-by-row on the OUT endpoint (65 bytes per row).
    """

    vendor_id = 0x048D
    product_id = 0x600B
    report_id = 0x00
    report_size = 8
    rows = 6
    cols = 21

    preset_base = 0x00
    custom_base = 0x00
    color_custom = 0x00

    # Directions (index = firmware value)
    directions = _DIRECTIONS
    # Palette colors (index = firmware value)
    palette_colors = _COLORS

    def _report(self, *data: int) -> bytes:
        """8-byte report, no report ID, zero-padded."""
        payload = bytes(data)
        pad = self.report_size - len(payload)
        if pad > 0:
            payload += b"\x00" * pad
        return payload[: self.report_size]

    # Commands
    # SET_EFFECT: [8, control, effect, speed, brightness, color, direction/reactive, save]
    set_effect_cmd = command(8, args=7, doc="Set effect")
    set_brightness = command(9, args=2, doc="Set brightness")
    set_palette_color = command(20, args=4, doc="Set palette color")
    set_row_index = command(22, 0x00, args=1, doc="Set row index for bulk write")
    get_fw_version = command(128, doc="Get firmware version")
    get_effect_cmd = command(136, doc="Get current effect")

    # Effects
    effects = {
        "breathing": effect("breathing", color_cmd="set_effect_cmd", color_slots=1),
        "wave": effect("wave", color_cmd="set_effect_cmd", color_slots=1, directions=_DIRECTIONS),
        "random": effect("random", color_cmd="set_effect_cmd", color_slots=1),
        "rainbow": effect("rainbow", color_cmd="set_effect_cmd"),
        "ripple": effect("ripple", color_cmd="set_effect_cmd", color_slots=1),
        "marquee": effect("marquee", color_cmd="set_effect_cmd"),
        "raindrop": effect("raindrop", color_cmd="set_effect_cmd", color_slots=1),
        "aurora": effect("aurora", color_cmd="set_effect_cmd", color_slots=1),
        "fireworks": effect("fireworks", color_cmd="set_effect_cmd", color_slots=1),
    }

    # Effect IDs (firmware values)
    effect_ids = {
        "breathing": 0x02,
        "wave": 0x03,
        "random": 0x04,
        "rainbow": 0x05,
        "ripple": 0x06,
        "marquee": 0x09,
        "raindrop": 0x0A,
        "aurora": 0x0E,
        "fireworks": 0x11,
    }


class ITE8291(HIDDevice):
    """High-level ITE 8291 keyboard interface."""

    proto: ITE8291Protocol

    def __init__(self, **kwargs: object) -> None:
        proto = ITE8291Protocol(**kwargs)
        super().__init__(proto)
        self.proto = proto

    def effect(
        self,
        name: str,
        *,
        speed: int = 5,
        brightness: int = 25,
        color: int = 8,
        direction: str = "right",
        save: bool = False,
        **_kwargs: object,
    ) -> None:
        """Apply a named effect.

        Args:
            name: Effect name (breathing, wave, random, rainbow, etc).
            speed: Animation speed (0-10).
            brightness: Brightness (0-50).
            color: Palette color index (0-8). 8 = random.
            direction: Direction name (none, right, left, up, down).
            save: Persist to firmware.
        """
        effect_id = self.proto.effect_ids.get(name)
        if effect_id is None:
            raise ValueError(f"Unknown effect: {name}. Valid: {', '.join(self.proto.effect_ids)}")

        dir_idx = 0
        if direction in self.proto.directions:
            dir_idx = self.proto.directions.index(direction)

        self.proto._send(self.proto.set_effect_cmd(0x02, effect_id, speed, brightness, color, dir_idx, int(save)))

    def brightness(self, value: int) -> None:
        self.proto._send(self.proto.set_brightness(0x02, value))

    def turn_off(self) -> None:
        self.proto._send(self.proto.set_effect_cmd(0x01, 0, 0, 0, 0, 0, 0))


if __name__ == "__main__":
    print("ITE 8291 protocol - report verification (no device needed)")
    print()

    proto = ITE8291Protocol.__new__(ITE8291Protocol)
    proto.report_id = 0x00
    proto.report_size = 8
    proto._seq = 0

    # Set effect: breathing, speed=5, brightness=25, color=random(8)
    report = proto.set_effect_cmd(0x02, 0x02, 5, 25, 8, 0, 0)
    print(f"Breathing:  {report.hex()}")
    assert report == bytes([8, 0x02, 0x02, 5, 25, 8, 0, 0])

    # Set effect: wave right, speed=5, brightness=25
    report = proto.set_effect_cmd(0x02, 0x03, 5, 25, 0, 1, 0)
    print(f"Wave right: {report.hex()}")
    assert report == bytes([8, 0x02, 0x03, 5, 25, 0, 1, 0])

    # Set brightness to 30
    report = proto.set_brightness(0x02, 30)
    print(f"Bright 30:  {report.hex()}")
    assert report == bytes([9, 0x02, 30, 0, 0, 0, 0, 0])

    # Turn off
    report = proto.set_effect_cmd(0x01, 0, 0, 0, 0, 0, 0)
    print(f"Turn off:   {report.hex()}")
    assert report == bytes([8, 0x01, 0, 0, 0, 0, 0, 0])

    print()
    print("All verified.")
    print()

    print("Effects:")
    for name in ITE8291Protocol.effect_ids:
        print(f"  {name}")
