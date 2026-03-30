# hidproto

[![PyPI](https://img.shields.io/pypi/v/hidproto)](https://pypi.org/project/hidproto/)
[![Python](https://img.shields.io/pypi/pyversions/hidproto)](https://pypi.org/project/hidproto/)
[![License](https://img.shields.io/github/license/Chocapikk/hidproto)](LICENSE.md)
[![Tests](https://img.shields.io/github/actions/workflow/status/Chocapikk/hidproto/tests.yml?label=tests)](https://github.com/Chocapikk/hidproto/actions)

A Python DSL for HID device protocols. Define commands and effects as pure data, the runtime handles transport, discovery, checksums, and state tracking. Works on Linux, Windows, and macOS.

## Why

Every HID device project (OpenRGB, keyRGB, rivalcfg, openrazer) rewrites the same boilerplate: open device, build reports, send ioctl, manage state. hidproto lets you define a protocol in ~50 lines of pure data and get a working device driver.

Existing Python RGB libraries (PyRGBDev, pychroma, python-rgbkeyboards) all depend on vendor SDKs and only work on Windows. hidproto talks HID directly, no vendor SDK needed.

## Install

```bash
pip install hidproto            # Linux (hidraw, zero deps)
pip install hidproto[hidapi]    # Windows / macOS (cross-platform)
```

## Platform support

| Platform | Transport | Dependencies |
|----------|-----------|-------------|
| Linux | hidraw (native ioctl) | None |
| Windows | hidapi | `pip install hidapi` |
| macOS | hidapi | `pip install hidapi` |

On Linux, hidraw is used by default for zero-dependency operation. On other platforms, the hidapi backend is auto-selected. You can also force hidapi on Linux with `pip install hidproto[hidapi]`.

## Supported devices

25 protocols across 19 vendors, all auto-discovered:

| Vendor | Device | Effects |
|--------|--------|---------|
| Alienware | AW510K | 7 (static, breathing, spectrum, wave, rainbow, scanner, off) |
| ASUS | TUF/ROG keyboards | 9 (static, breathing, wave, ripple, reactive, starry, rain, direct, off) |
| Cherry | MX Board | 8 (wave, spectrum, breathing, static, radar, fire, stars, rain) |
| CoolerMaster | MasterKeys Pro | 9 (direct, static, breathing, cycle, wave, ripple, snake, reactive, stars) |
| Corsair | K70/K95 | 7 (color shift, color pulse, rainbow wave, color wave, rain, spiral, visor) |
| Das | Q5 | XOR checksum protocol |
| Ducky | One 2 RGB | Multi-packet direct mode |
| Fnatic | Streak | 6 (pulse, wave, reactive, ripple, rain, fade) |
| HyperX | Alloy Elite | 8 (wave variants, static, breathing) with 6 directions |
| ITE | 8291 rev3 | 9 (breathing, wave, random, rainbow, ripple, marquee, raindrop, aurora, fireworks) |
| ITE | 8297 | Uniform color |
| ITE | 8910 | 11 (full per-key + animations with 8 wave / 4 snake directions) |
| Keychron | K3 V2 | 7 (static, breathing, spectrum, sparkle, rain, random, off) |
| Logitech | G815 (HID++) | 6 (off, static, spectrum, wave, breathing, ripple) |
| Mountain | Everest | 6 (static, breathing, wave, reactive, tornado, off) |
| MSI | Vigor GK30 | 7 (off, static, breathing, rainbow, meteor, ripple, dimming) |
| NZXT | Lift mouse | Direct LED control |
| Obinslab | Anne Pro 2 | Static mode |
| QMK | OpenRGB firmware | 8 (direct, solid, breathing, rainbow, swirl, snake, knight, splash) |
| Razer | BlackWidow | 5 (static, wave, breathing, spectrum, off) with XOR checksum |
| Redragon | M711 mouse | 5 (wave, breathing, static, rainbow, flashing) |
| Roccat | Vulcan | 3 (direct, static, wave) with 16-bit checksum |
| Sony | DualShock 4 | Lightbar RGB control |
| SteelSeries | Apex Pro | Direct mode + profiles |
| Wooting | 60HE | Magic byte protocol |

Adding a new device is one Python file in `protocols/<vendor>/`. The registry auto-discovers it.

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

No boilerplate, no subclassing, no transport code.

## CLI

```bash
hidproto devices                                    # list connected HID devices
hidproto info ite8910                               # show commands, effects, matrix size
hidproto ite8910 wave -d right -b 8 -s 5            # wave rainbow, right, brightness 8
hidproto ite8910 wave -d left -c ff0000             # wave red, left
hidproto ite8910 breathing -c 00ff00 -b 8           # breathing green
hidproto ite8910 scan -c ff0000 --color2 0000ff     # scan red + blue
hidproto ite8910 off                                # turn off
```

All options are auto-generated from the protocol definition. Each device gets its own subcommands with `--help`.

## Features

- **DSL** - `command()` and `effect()` descriptors generate everything from pure data
- **Multi-step effects** - `step()` chains multiple commands for complex protocols (Corsair, Cherry)
- **Auto-discovery** - protocols registered via entry points or filesystem scan
- **Cross-platform** - hidraw on Linux, hidapi on Windows/macOS
- **Checksums** - XOR (Razer, Das), SUM (Cherry), custom via `_with_checksum()`
- **State caching** - skip redundant sends, invalidate on resume
- **CLI** - Click-based with per-device subcommands

## Architecture

```
hidproto/
  cli.py              Click CLI with auto-generated subcommands
  command.py           CommandSpec + @command descriptor
  effect.py            EffectSpec + step() for multi-step effects
  protocol.py          HIDProtocol base (report building, transport)
  device.py            HIDDevice wrapper (effects, caching, brightness/speed)
  transport.py         HidrawTransport (Linux native)
  transport_hidapi.py  HidapiTransport (cross-platform)
  discovery.py         sysfs device discovery
  registry.py          Auto-discovery + entry point plugin system
  checksum.py          xor/sum checksum helpers

protocols/
  alienware/    asus/       cherry/     coolermaster/
  corsair/      das/        ducky/      fnatic/
  hyperx/       ite/        keychron/   logitech/
  mountain/     msi/        nzxt/       obinslab/
  qmk/          razer/      redragon/   roccat/
  sony/         steelseries/ wooting/
```

## License

MIT
