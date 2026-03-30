"""Logitech HID++ (FAP) protocol - short (7B) and long (20B) messages.

Logitech uses a feature-based protocol where each capability has a
"feature page" (e.g. 0x8070 for RGB) and commands are dispatched via
feature index + command ID. Two report formats: short (0x10, 7B) and
long (0x11, 20B).

Protocol reference: OpenRGB LogitechG815ProtocolCommon, libratbag.

Usage::

    from examples.logitech import Logitech

    with Logitech() as kb:
        kb.effect("spectrum")
        kb.effect("breathing")
"""

from hidproto import HIDDevice, HIDProtocol, command, effect, step


class LogitechG815Protocol(HIDProtocol):
    """Logitech HID++ FAP protocol.

    Short message: [0x10, device_index, feature_index, command, data[3]]  (7 bytes)
    Long message:  [0x11, device_index, feature_index, command, data[16]] (20 bytes)
    """

    vendor_id      = 0x046D
    product_id     = 0xC339  # G815 RGB, override per device
    report_id      = 0x11    # long message by default
    report_size    = 20
    rows           = 6
    cols           = 22

    preset_base    = 0x00
    custom_base    = 0x00
    color_custom   = 0x00

    device_index   = 0xFF

    # RGB effects feature page index (device-specific, queried at runtime)
    # For static definitions we use a placeholder
    rgb_feature_idx = 0x0E

    # Mode IDs
    mode_off       = 0x0000
    mode_on        = 0x0001
    mode_spectrum  = 0x0003
    mode_wave      = 0x0004
    mode_star      = 0x0005
    mode_breathing = 0x000A
    mode_ripple    = 0x000B
    mode_custom    = 0x000C

    def _report(self, *data: int) -> bytes:
        """Build a Logitech long FAP message (20 bytes)."""
        buf = bytearray(self.report_size)
        buf[0] = self.report_id
        buf[1] = self.device_index
        for i, b in enumerate(data):
            if 2 + i < self.report_size:
                buf[2 + i] = b
        return bytes(buf)

    def _short_report(self, *data: int) -> bytes:
        """Build a Logitech short FAP message (7 bytes)."""
        buf = bytearray(7)
        buf[0] = 0x10
        buf[1] = self.device_index
        for i, b in enumerate(data):
            if 2 + i < 7:
                buf[2 + i] = b
        return bytes(buf)

    # Commands
    # Root: query feature index
    # [feature_idx=0x00, cmd=0x01, feature_page_hi, feature_page_lo]
    get_feature_index  = command(0x00, 0x01, args=2, doc="Query feature index")
    # Set mode: [rgb_feature_idx, 0x30, zone, mode_hi, mode_lo, ...]
    set_mode           = command(args=16, doc="Set RGB mode")
    # Direct mode control: [rgb_feature_idx, 0x50, enable]
    set_direct         = command(args=3, doc="Enable/disable direct mode")

    # Effects
    # set_mode args: [feat_idx, cmd, zone, 0, mode_hi, mode_lo, speed, R, G, B, brightness, ...]
    # fmt: off
    effects = {
        "off":       effect("off",       steps=(step("set_mode", 0x0E, 0x30, 0, 0, 0x00, 0, 0x00, 0,    0, 0, 0,    0, 0, 0, 0, 0),)),
        "static":    effect("static",    steps=(step("set_mode", 0x0E, 0x30, 0, 0, 0x01, 0, 0x00, 0xFF, 0, 0, 0x64, 0, 0, 0, 0, 0),)),
        "spectrum":  effect("spectrum",  steps=(step("set_mode", 0x0E, 0x30, 0, 0, 0x03, 0, 0x64, 0,    0, 0, 0,    0, 0, 0, 0, 0),)),
        "wave":      effect("wave",      steps=(step("set_mode", 0x0E, 0x30, 0, 0, 0x04, 0, 0x64, 0,    0, 0, 0,    0, 0, 0, 0, 0),)),
        "breathing": effect("breathing", steps=(step("set_mode", 0x0E, 0x30, 0, 0, 0x0A, 0, 0x64, 0xFF, 0, 0, 0,    0, 0, 0, 0, 0),)),
        "ripple":    effect("ripple",    steps=(step("set_mode", 0x0E, 0x30, 0, 0, 0x0B, 0, 0x64, 0,    0, 0, 0,    0, 0, 0, 0, 0),)),
    }
    # fmt: on


LogitechG815 = HIDDevice.for_protocol(LogitechG815Protocol)


if __name__ == "__main__":
    print("Logitech HID++ protocol - report verification (no device needed)")
    print()

    proto = LogitechG815Protocol.__new__(LogitechG815Protocol)
    proto.report_id = 0x11
    proto.report_size = 20
    proto.device_index = 0xFF
    proto._seq = 0

    # Set mode: spectrum cycle
    report = proto.set_mode(
        0x0E, 0x30, 0x00, 0x00, 0x03, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    )
    print(f"Spectrum:   {report.hex()} (len={len(report)})")
    assert report[0] == 0x11  # long message
    assert report[1] == 0xFF  # device index
    assert report[2] == 0x0E  # feature index
    assert report[3] == 0x30  # set mode command
    assert len(report) == 20

    # Feature query
    report = proto.get_feature_index(0x80, 0x70)
    print(f"Query 8070: {report.hex()} (len={len(report)})")
    assert report[2] == 0x00  # root feature index
    assert report[3] == 0x01  # get feature command
    assert report[4] == 0x80  # page hi
    assert report[5] == 0x70  # page lo

    print()
    print("All verified.")
    print()

    print("Effects:")
    for name, spec in LogitechG815Protocol.effects.items():
        print(f"  {name:12s}  {len(spec.steps)} steps")
