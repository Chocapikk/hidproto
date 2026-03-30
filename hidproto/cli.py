"""CLI for hidproto - control HID devices from the terminal."""

from __future__ import annotations

import click

from .device import HIDDevice
from .discovery import list_devices
from .effect import resolve_directions
from .protocol import HIDProtocol
from .registry import discover

PROTOCOLS = discover()


@click.group()
def cli() -> None:
    """hidproto - Control HID devices from the terminal."""


@cli.command()
def devices() -> None:
    """List connected HID devices."""
    devs = list_devices()
    if not devs:
        click.echo("No HID devices found.")
        return
    for d in devs:
        click.echo(d)


@cli.command()
@click.argument("protocol", type=click.Choice(list(PROTOCOLS)))
def info(protocol: str) -> None:
    """Show protocol info: effects, commands, constants."""
    proto_cls = PROTOCOLS[protocol]

    click.echo(f"Protocol: {protocol}")
    click.echo(f"  VID:PID     {proto_cls.vendor_id:04x}:{proto_cls.product_id:04x}")
    click.echo(f"  Report ID   0x{proto_cls.report_id:02X}")
    click.echo(f"  Report size {proto_cls.report_size} bytes")
    click.echo(f"  Matrix      {proto_cls.rows}x{proto_cls.cols}")
    click.echo()

    cmds = proto_cls.list_commands()
    if cmds:
        click.echo("Commands:")
        for name, spec in cmds.items():
            opcode = ", ".join(f"0x{o:02X}" for o in spec.opcode)
            click.echo(f"  {name:20s}  [{opcode}]  {spec.doc}")
        click.echo()

    effects = getattr(proto_cls, "effects", {})
    if effects:
        click.echo("Effects:")
        for name, spec in effects.items():
            parts = []
            # Need a dummy proto for resolve_directions
            dirs = resolve_directions(proto_cls, spec)
            if dirs:
                parts.append(f"directions: {', '.join(dirs)}")
            if spec.color_slots:
                parts.append(f"colors: {spec.color_slots}")
            if spec.needs_clear:
                parts.append("clears LEDs")
            extra = f"  ({', '.join(parts)})" if parts else ""
            click.echo(f"  {name:20s}{extra}")


def _make_protocol_group(proto_name: str, proto_cls: type[HIDProtocol]) -> click.Group:
    """Dynamically create a click group for a protocol with effect subcommands."""
    effects = getattr(proto_cls, "effects", {})

    @click.group(name=proto_name, help=f"Control {proto_name} device")
    def proto_group() -> None:
        pass

    # brightness command
    @proto_group.command()
    @click.argument("value", type=click.IntRange(0, 10))
    def brightness(value: int) -> None:
        """Set brightness (0-10)."""
        with HIDDevice.for_protocol(proto_cls)() as dev:
            dev.brightness(value)
            click.echo(f"Brightness: {value}")

    # speed command
    @proto_group.command()
    @click.argument("value", type=click.IntRange(0, 10))
    def speed(value: int) -> None:
        """Set speed (0-10)."""
        with HIDDevice.for_protocol(proto_cls)() as dev:
            dev.speed(value)
            click.echo(f"Speed: {value}")

    # effect commands
    for effect_name, spec in effects.items():
        _register_effect(proto_group, proto_cls, effect_name, spec)

    return proto_group


def _register_effect(
    group: click.Group,
    proto_cls: type[HIDProtocol],
    effect_name: str,
    spec: object,
) -> None:
    """Register a single effect as a click subcommand."""

    params: list[click.Parameter] = []

    dirs = resolve_directions(proto_cls, spec)

    if dirs:
        params.append(
            click.Option(
                ["--direction", "-d"],
                type=click.Choice(list(dirs)),
                default=dirs[0],
                help="Direction",
                show_default=True,
            )
        )

    if spec.color_slots >= 1:
        params.append(
            click.Option(
                ["--color", "-c"],
                type=str,
                default=None,
                help="Color (hex RGB, e.g. ff0000)",
            )
        )

    if spec.color_slots >= 2:
        params.append(
            click.Option(
                ["--color2"],
                type=str,
                default=None,
                help="Second color (hex RGB)",
            )
        )

    params.append(click.Option(["--brightness", "-b"], type=click.IntRange(0, 10), default=None, help="Brightness"))
    params.append(click.Option(["--speed", "-s"], type=click.IntRange(0, 10), default=None, help="Speed"))

    def callback(**kwargs: object) -> None:
        effect_kwargs: dict[str, object] = {}

        color_str = kwargs.get("color")
        if color_str:
            rgb = int(str(color_str), 16)
            effect_kwargs["color"] = ((rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF)

        color2_str = kwargs.get("color2")
        if color2_str:
            rgb = int(str(color2_str), 16)
            effect_kwargs["color2"] = ((rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF)

        direction = kwargs.get("direction")
        if direction:
            effect_kwargs["direction"] = direction

        with HIDDevice.for_protocol(proto_cls)() as dev:
            br = kwargs.get("brightness")
            if br is not None:
                dev.brightness(int(br))
            sp = kwargs.get("speed")
            if sp is not None:
                dev.speed(int(sp))
            dev.effect(effect_name, **effect_kwargs)
            click.echo(f"{effect_name} applied")

    cmd = click.Command(
        name=effect_name,
        callback=callback,
        params=params,
        help=f"Apply {effect_name} effect",
    )
    group.add_command(cmd)


# Register all protocols as subcommands
for _name, _cls in PROTOCOLS.items():
    if hasattr(_cls, "effects"):
        cli.add_command(_make_protocol_group(_name, _cls))


def main() -> None:
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
