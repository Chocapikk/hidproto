"""Declarative effect definitions for HID devices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .protocol import HIDProtocol


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
        clear_animation: Animation ID used for clearing (default 0x0C).
    """

    name: str
    animation: int | None = None
    color_cmd: str | None = None
    slot_cmd: str | None = None
    directions: tuple[str, ...] = ()
    color_slots: int = 0
    needs_clear: bool = False
    clear_animation: int = 0x0C


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
    )


def _build_clear(proto: HIDProtocol, clear_anim: int) -> list[bytes]:
    """Build clear sequence: animation mode + black on all LEDs."""
    reports: list[bytes] = [proto.animation_mode(clear_anim)]
    for row in range(proto.rows):
        for col in range(proto.cols):
            reports.append(proto.set_led(proto.led_id(row, col), 0, 0, 0))
    return reports


def _build_color(
    proto: HIDProtocol, spec: EffectSpec, colors: list[tuple[int, int, int]]
) -> list[bytes]:
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


def apply_effect(
    proto: HIDProtocol,
    spec: EffectSpec,
    *,
    colors: list[tuple[int, int, int]] | None = None,
    direction: str | None = None,
) -> list[bytes]:
    """Build the full report sequence for an effect.

    Args:
        proto: Protocol instance.
        spec: Effect specification.
        colors: RGB tuples for color slots.
        direction: Direction name for directional effects.

    Returns:
        Ordered list of reports to send.
    """
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
