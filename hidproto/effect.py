"""Declarative effect definitions for HID devices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .protocol import HIDProtocol


@dataclass(frozen=True)
class Step:
    """A single step in a multi-step effect sequence.

    Attributes:
        cmd: Command method name on the protocol.
        args: Fixed args to pass. Use None as placeholder for runtime values.
        use_feature: If False, use _write instead of _send.
    """

    cmd: str
    args: tuple[int, ...] = ()
    use_feature: bool = True


@dataclass(frozen=True)
class EffectSpec:
    """Declarative effect definition.

    Attributes:
        name: Effect name.
        animation: Animation mode ID to send, or None.
        color_cmd: Command name for color/random slot.
        slot_cmd: Command name for directional slot.
        directions: Valid direction names, or empty.
        color_slots: Number of color slots (0, 1, or 2).
        needs_clear: Send clear animation + black to all LEDs first.
        clear_animation: Animation ID used for clearing.
        steps: Ordered list of Steps for multi-step effects.
    """

    name: str
    animation: int | None = None
    color_cmd: str | None = None
    slot_cmd: str | None = None
    directions: tuple[str, ...] = ()
    color_slots: int = 0
    needs_clear: bool = False
    clear_animation: int = 0x0C
    steps: tuple[Step, ...] = ()


def step(cmd: str, *args: int, use_feature: bool = True) -> Step:
    """Create a step in a multi-step effect."""
    return Step(cmd=cmd, args=args, use_feature=use_feature)


def effect(
    name: str,
    *,
    animation: int | None = None,
    color_cmd: str | None = None,
    slot_cmd: str | None = None,
    directions: tuple[str, ...] = (),
    color_slots: int = 0,
    needs_clear: bool = False,
    clear_animation: int = 0x0C,
    steps: tuple[Step, ...] = (),
) -> EffectSpec:
    """Create a declarative effect definition."""
    return EffectSpec(
        name=name,
        animation=animation,
        color_cmd=color_cmd,
        slot_cmd=slot_cmd,
        directions=directions,
        color_slots=color_slots,
        needs_clear=needs_clear,
        clear_animation=clear_animation,
        steps=steps,
    )


def _build_clear(proto: HIDProtocol, clear_anim: int) -> list[bytes]:
    """Build clear sequence: animation mode + black on all LEDs."""
    reports: list[bytes] = [proto.animation_mode(clear_anim)]
    for row in range(proto.rows):
        for col in range(proto.cols):
            reports.append(proto.set_led(proto.led_id(row, col), 0, 0, 0))
    return reports


def _build_color(proto: HIDProtocol, spec: EffectSpec, colors: list[tuple[int, int, int]]) -> list[bytes]:
    """Build color/random reports for non-directional effects."""
    cmd = getattr(proto, spec.color_cmd)
    if colors:
        return [cmd(proto.color_custom, *colors[0])]
    if spec.color_slots > 0:
        return [cmd(0x00, 0, 0, 0)]
    return []


def _build_slots(
    proto: HIDProtocol,
    spec: EffectSpec,
    colors: list[tuple[int, int, int]],
    direction: str | None,
) -> list[bytes]:
    """Build directional or multi-slot reports."""
    cmd = getattr(proto, spec.slot_cmd)

    if spec.directions:
        dir_name = direction if direction else spec.directions[0]
        color = colors[0] if colors else None
        return [cmd(*proto.dir_slot(dir_name, spec.directions, color))]

    reports: list[bytes] = []
    for i, c in enumerate(colors[: spec.color_slots]):
        reports.append(cmd(proto.custom_base + i, *c))
    return reports


def _build_steps(proto: HIDProtocol, spec: EffectSpec) -> list[tuple[bytes, bool]]:
    """Build reports from multi-step sequence.

    Returns list of (report, use_feature) tuples.
    """
    results: list[tuple[bytes, bool]] = []
    for s in spec.steps:
        cmd = getattr(proto, s.cmd)
        report = cmd(*s.args)
        results.append((report, s.use_feature))
    return results


def apply_effect(
    proto: HIDProtocol,
    spec: EffectSpec,
    *,
    colors: list[tuple[int, int, int]] | None = None,
    direction: str | None = None,
) -> list[bytes]:
    """Build the full report sequence for an effect.

    For multi-step effects (spec.steps), returns reports from the step
    sequence. For simple effects, builds from animation/color/slot/clear.

    Args:
        proto: Protocol instance.
        spec: Effect specification.
        colors: RGB tuples for color slots.
        direction: Direction name for directional effects.

    Returns:
        Ordered list of reports to send.
    """
    # Multi-step effects: execute steps in order
    if spec.steps:
        results = _build_steps(proto, spec)
        # For now, return just the bytes (caller handles feature vs write)
        return [r for r, _ in results]

    reports: list[bytes] = []
    colors = colors or []

    if spec.needs_clear:
        reports.extend(_build_clear(proto, spec.clear_animation))

    if spec.animation is not None:
        reports.append(proto.animation_mode(spec.animation))

    if spec.color_cmd and not spec.slot_cmd:
        reports.extend(_build_color(proto, spec, colors))

    if spec.slot_cmd:
        reports.extend(_build_slots(proto, spec, colors, direction))

    return reports
