"""Key layout dataclass for keyboard protocols."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Key:
    """A key with visual position and LED matrix address.

    Attributes:
        label: Display label on the key.
        x: Visual X position in key units.
        y: Visual Y position in key units.
        w: Width in key units (default 1.0).
        h: Height in key units (default 1.0).
        row: LED matrix row.
        col: LED matrix col (hardware LED ID column).
    """

    label: str
    x: float
    y: float
    w: float = 1.0
    h: float = 1.0
    row: int = -1
    col: int = -1
