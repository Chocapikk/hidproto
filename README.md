# hidproto

[![PyPI](https://img.shields.io/pypi/v/hidproto)](https://pypi.org/project/hidproto/)
[![Python](https://img.shields.io/pypi/pyversions/hidproto)](https://pypi.org/project/hidproto/)
[![License](https://img.shields.io/github/license/Chocapikk/hidproto)](LICENSE.md)
[![Tests](https://img.shields.io/github/actions/workflow/status/Chocapikk/hidproto/tests.yml?label=tests)](https://github.com/Chocapikk/hidproto/actions)

A Python DSL for HID device protocols on Linux. Define commands and effects as pure data, the runtime handles transport, discovery, checksums, and state tracking.

## Why

Every HID device project (OpenRGB, keyRGB, rivalcfg, openrazer) rewrites the same boilerplate: open hidraw, build reports, send ioctl, manage state. hidproto lets you define a protocol in ~50 lines of pure data and get a working device driver.

## Install

```bash
pip install hidproto
```

Or from source:

```bash
git clone https://github.com/Chocapikk/hidproto
cd hidproto
pip install -e .
```

## Quick start

```python
from hidproto import HIDDevice, HIDProtocol, command, effect

class MyKeyboard(HIDProtocol):
    vendor_id    = 0x048D
    product_id   = 0x8910
    report_id    = 0xCC
    report_size  = 6
    rows         = 6
    cols         = 20
    preset_base  = 0x71
    custom_base  = 0xA1
    color_custom = 0xAA

    animation_mode   = command(0x00, args=1, doc="Animation mode")
    set_led          = command(0x01, args=4, doc="Per-key color")
    brightness_speed = command(0x09, args=4, doc="Brightness + speed")
    wave_slot        = command(0x15, args=4, doc="Wave slot")

    effects = {
        "off":  effect("off",  animation=0x0C, needs_clear=True),
        "wave": effect("wave", animation=0x04, slot_cmd="wave_slot",
                        directions=("up", "down", "left", "right")),
    }

Keyboard = HIDDevice.for_protocol(MyKeyboard)

with Keyboard() as kb:
    kb.brightness(8)
    kb.speed(5)
    kb.effect("wave", direction="right", color=(255, 0, 0))
```

That's it. No boilerplate, no subclassing, no transport code.

## Features

**Protocol definition** - `command()` descriptor auto-generates report builders from opcode + arg count. No methods to write.

**Effect dispatch** - `effect()` declaratively maps names to animation modes, color slots, directional slots. One `kb.effect("wave", direction="right")` call handles everything.

**Device discovery** - auto-finds devices via `/sys/class/hidraw` by VID/PID.

**Transport** - hidraw ioctl for feature reports, `os.write` for output reports, `select` for reads with timeout.

**State caching** - `send_if_changed()` skips redundant HID sends. `invalidate()` forces resync (suspend/resume).

**Checksums** - `xor_checksum()`, `sum_checksum()`, and `_with_checksum()` for protocols that need them (Razer, Corsair).

**Sequence numbers** - `_next_seq()` for transactional protocols (Logitech, Corsair).

**CLI** - `hidproto` command with auto-generated subcommands per protocol. Each effect gets its own `--help` with only the relevant options.

## CLI

```bash
hidproto devices                                    # list connected HID devices
hidproto info ite8910                               # show commands, effects, matrix size
hidproto ite8910 wave -d right -b 8 -s 5            # wave rainbow, right, brightness 8
hidproto ite8910 wave -d left -c ff0000             # wave red, left
hidproto ite8910 breathing -c 00ff00 -b 8           # breathing green
hidproto ite8910 scan -c ff0000 --color2 0000ff     # scan red + blue
hidproto ite8910 snake -d down_right -c 0000ff      # snake blue, diagonal
hidproto ite8910 off                                # turn off
hidproto ite8910 brightness 8                       # set brightness only
hidproto ite8910 speed 5                            # set speed only
```

Options are generated from the protocol definition. `wave --help` shows `--direction` with valid choices, `scan --help` shows `--color` and `--color2`, `spectrum_cycle --help` shows only brightness/speed.

## Architecture

```
hidproto/
  cli.py         Click CLI with auto-generated subcommands
  command.py     CommandSpec + @command descriptor
  effect.py      EffectSpec + declarative effect dispatch
  protocol.py    HIDProtocol base class (report building, transport)
  device.py      HIDDevice wrapper (effects, caching, brightness/speed)
  transport.py   HidrawTransport (ioctl, read, write)
  discovery.py   sysfs device discovery
  checksum.py    xor/sum checksum helpers
```

## Examples

See `examples/ite8910.py` for a complete ITE 8910 keyboard RGB implementation: 9 commands, 11 effects, 8 wave directions, 4 snake diagonals, per-key color. All in ~70 lines of data.

## License

MIT
