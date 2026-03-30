"""Keyboard layout definitions for the GUI renderer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Key:
    """A visual key on the keyboard layout."""

    label: str
    x: float  # position in key units
    y: float
    w: float = 1.0  # width in key units
    h: float = 1.0
    row: int = -1  # LED matrix row (-1 = no LED)
    col: int = -1  # LED matrix col


# ANSI full-size layout (6 rows, matches ITE 8910 / standard 104-key)
ANSI_FULL: list[Key] = [
    # Row 0: Function row
    Key("Esc", 0, 0, row=0, col=0),
    Key("F1", 2, 0, row=0, col=1),
    Key("F2", 3, 0, row=0, col=2),
    Key("F3", 4, 0, row=0, col=3),
    Key("F4", 5, 0, row=0, col=4),
    Key("F5", 6.5, 0, row=0, col=5),
    Key("F6", 7.5, 0, row=0, col=6),
    Key("F7", 8.5, 0, row=0, col=7),
    Key("F8", 9.5, 0, row=0, col=8),
    Key("F9", 11, 0, row=0, col=9),
    Key("F10", 12, 0, row=0, col=10),
    Key("F11", 13, 0, row=0, col=11),
    Key("F12", 14, 0, row=0, col=12),
    Key("PrtSc", 15.25, 0, row=0, col=13),
    Key("Ins", 16.25, 0, row=0, col=14),
    Key("Del", 17.25, 0, row=0, col=15),
    # Row 1: Number row
    Key("`", 0, 1.25, row=1, col=0),
    Key("1", 1, 1.25, row=1, col=1),
    Key("2", 2, 1.25, row=1, col=2),
    Key("3", 3, 1.25, row=1, col=3),
    Key("4", 4, 1.25, row=1, col=4),
    Key("5", 5, 1.25, row=1, col=5),
    Key("6", 6, 1.25, row=1, col=6),
    Key("7", 7, 1.25, row=1, col=7),
    Key("8", 8, 1.25, row=1, col=8),
    Key("9", 9, 1.25, row=1, col=9),
    Key("0", 10, 1.25, row=1, col=10),
    Key("-", 11, 1.25, row=1, col=11),
    Key("=", 12, 1.25, row=1, col=12),
    Key("Bksp", 13, 1.25, 2, row=1, col=13),
    Key("Home", 15.25, 1.25, row=1, col=15),
    # Row 2: QWERTY
    Key("Tab", 0, 2.25, 1.5, row=2, col=0),
    Key("Q", 1.5, 2.25, row=2, col=1),
    Key("W", 2.5, 2.25, row=2, col=2),
    Key("E", 3.5, 2.25, row=2, col=3),
    Key("R", 4.5, 2.25, row=2, col=4),
    Key("T", 5.5, 2.25, row=2, col=5),
    Key("Y", 6.5, 2.25, row=2, col=6),
    Key("U", 7.5, 2.25, row=2, col=7),
    Key("I", 8.5, 2.25, row=2, col=8),
    Key("O", 9.5, 2.25, row=2, col=9),
    Key("P", 10.5, 2.25, row=2, col=10),
    Key("[", 11.5, 2.25, row=2, col=11),
    Key("]", 12.5, 2.25, row=2, col=12),
    Key("\\", 13.5, 2.25, 1.5, row=2, col=13),
    Key("PgUp", 15.25, 2.25, row=2, col=15),
    # Row 3: Home row
    Key("Caps", 0, 3.25, 1.75, row=3, col=0),
    Key("A", 1.75, 3.25, row=3, col=1),
    Key("S", 2.75, 3.25, row=3, col=2),
    Key("D", 3.75, 3.25, row=3, col=3),
    Key("F", 4.75, 3.25, row=3, col=4),
    Key("G", 5.75, 3.25, row=3, col=5),
    Key("H", 6.75, 3.25, row=3, col=6),
    Key("J", 7.75, 3.25, row=3, col=7),
    Key("K", 8.75, 3.25, row=3, col=8),
    Key("L", 9.75, 3.25, row=3, col=9),
    Key(";", 10.75, 3.25, row=3, col=10),
    Key("'", 11.75, 3.25, row=3, col=11),
    Key("Enter", 12.75, 3.25, 2.25, row=3, col=12),
    Key("PgDn", 15.25, 3.25, row=3, col=15),
    # Row 4: Shift row
    Key("Shift", 0, 4.25, 2.25, row=4, col=0),
    Key("Z", 2.25, 4.25, row=4, col=2),
    Key("X", 3.25, 4.25, row=4, col=3),
    Key("C", 4.25, 4.25, row=4, col=4),
    Key("V", 5.25, 4.25, row=4, col=5),
    Key("B", 6.25, 4.25, row=4, col=6),
    Key("N", 7.25, 4.25, row=4, col=7),
    Key("M", 8.25, 4.25, row=4, col=8),
    Key(",", 9.25, 4.25, row=4, col=9),
    Key(".", 10.25, 4.25, row=4, col=10),
    Key("/", 11.25, 4.25, row=4, col=11),
    Key("Shift", 12.25, 4.25, 1.75, row=4, col=12),
    Key("Up", 14.25, 4.25, row=4, col=14),
    Key("End", 15.25, 4.25, row=4, col=15),
    # Row 5: Bottom row
    Key("Ctrl", 0, 5.25, 1.25, row=5, col=0),
    Key("Fn", 1.25, 5.25, row=5, col=1),
    Key("Win", 2.25, 5.25, 1.25, row=5, col=2),
    Key("Alt", 3.5, 5.25, 1.25, row=5, col=3),
    Key("Space", 4.75, 5.25, 6.25, row=5, col=4),
    Key("Alt", 11, 5.25, row=5, col=10),
    Key("Ctrl", 12, 5.25, row=5, col=11),
    Key("Left", 13.25, 5.25, row=5, col=13),
    Key("Down", 14.25, 5.25, row=5, col=14),
    Key("Right", 15.25, 5.25, row=5, col=15),
]

LAYOUTS: dict[str, list[Key]] = {
    "ansi_full": ANSI_FULL,
}
