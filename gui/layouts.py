"""Keyboard layout definitions with visual positions.

Each Key has a visual position (x, y in key units) and a LED matrix
position (row, col for the protocol). Layouts are built from the
KLM-style data with standard keyboard spacing rules applied.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Key:
    """A visual key on the keyboard layout."""

    label: str
    x: float
    y: float
    w: float = 1.0
    h: float = 1.0
    row: int = -1
    col: int = -1
    led_value: int = -1


# Standard key widths (ANSI)
_WIDTHS = {
    "Bksp": 2,
    "Tab": 1.5,
    "\\": 1.5,
    "Caps": 1.75,
    "Enter": 2.25,
    "LShift": 2.25,
    "RShift": 2.75,
    "LCtrl": 1.25,
    "Fn": 1,
    "Win": 1.25,
    "LAlt": 1.25,
    "Space": 6.25,
    "RAlt": 1.25,
    "Menu": 1.25,
    "RCtrl": 1.25,
}


def _build_full_layout(values: list[int] | None = None) -> list[Key]:
    """Build a full-size ANSI keyboard layout with visual positions.

    If values is provided, maps LED values from the protocol's value array.
    """
    keys: list[Key] = []
    v = values or []
    vi = 0

    def _val() -> int:
        nonlocal vi
        if vi < len(v):
            val = v[vi]
            vi += 1
            return val
        vi += 1
        return -1

    def _add(label: str, x: float, y: float, w: float = 1.0, row: int = -1, col: int = -1) -> None:
        led = _val()
        keys.append(Key(label, x, y, w, row=row, col=col, led_value=led))

    # Row 0: Function row
    _add("Esc", 0, 0, row=0, col=0)
    _add("F1", 2, 0, row=0, col=1)
    _add("F2", 3, 0, row=0, col=2)
    _add("F3", 4, 0, row=0, col=3)
    _add("F4", 5, 0, row=0, col=4)
    _add("F5", 6.5, 0, row=0, col=5)
    _add("F6", 7.5, 0, row=0, col=6)
    _add("F7", 8.5, 0, row=0, col=7)
    _add("F8", 9.5, 0, row=0, col=8)
    _add("F9", 11, 0, row=0, col=9)
    _add("F10", 12, 0, row=0, col=10)
    _add("F11", 13, 0, row=0, col=11)
    _add("F12", 14, 0, row=0, col=12)
    _add("PrtSc", 15.5, 0, row=0, col=13)
    _add("ScrLk", 16.5, 0, row=0, col=14)
    _add("Pause", 17.5, 0, row=0, col=15)

    # Row 1: Number row
    y = 1.5
    _add("`", 0, y, row=1, col=0)
    for i, l in enumerate("1234567890"):
        _add(l, 1 + i, y, row=1, col=1 + i)
    _add("-", 11, y, row=1, col=11)
    _add("=", 12, y, row=1, col=12)
    _add("Bksp", 13, y, 2, row=1, col=13)
    _add("Ins", 15.5, y, row=1, col=14)
    _add("Home", 16.5, y, row=1, col=15)
    _add("PgUp", 17.5, y, row=1, col=16)
    _add("Num", 19, y, row=1, col=17)
    _add("/", 20, y, row=1, col=18)
    _add("*", 21, y, row=1, col=19)
    _add("-", 22, y, row=1, col=20)

    # Row 2: QWERTY
    y = 2.5
    _add("Tab", 0, y, 1.5, row=2, col=0)
    for i, l in enumerate("QWERTYUIOP"):
        _add(l, 1.5 + i, y, row=2, col=1 + i)
    _add("[", 11.5, y, row=2, col=11)
    _add("]", 12.5, y, row=2, col=12)
    _add("\\", 13.5, y, 1.5, row=2, col=13)
    _add("Del", 15.5, y, row=2, col=14)
    _add("End", 16.5, y, row=2, col=15)
    _add("PgDn", 17.5, y, row=2, col=16)
    _add("7", 19, y, row=2, col=17)
    _add("8", 20, y, row=2, col=18)
    _add("9", 21, y, row=2, col=19)
    _add("+", 22, y, row=2, col=20)

    # Row 3: Home row
    y = 3.5
    _add("Caps", 0, y, 1.75, row=3, col=0)
    for i, l in enumerate("ASDFGHJKL"):
        _add(l, 1.75 + i, y, row=3, col=1 + i)
    _add(";", 10.75, y, row=3, col=10)
    _add("'", 11.75, y, row=3, col=11)
    _add("#", 12.75, y, row=3, col=12)
    _add("Enter", 13.75, y, 2.25, row=3, col=13)
    _add("4", 19, y, row=3, col=17)
    _add("5", 20, y, row=3, col=18)
    _add("6", 21, y, row=3, col=19)

    # Row 4: Shift row
    y = 4.5
    _add("Shift", 0, y, 2.25, row=4, col=0)
    _add("\\", 2.25, y, row=4, col=1)  # ISO backslash
    for i, l in enumerate("ZXCVBNM"):
        _add(l, 3.25 + i, y, row=4, col=2 + i)
    _add(",", 10.25, y, row=4, col=9)
    _add(".", 11.25, y, row=4, col=10)
    _add("/", 12.25, y, row=4, col=11)
    _add("Shift", 13.25, y, 2.75, row=4, col=13)
    _add("Up", 16.5, y, row=4, col=15)
    _add("1", 19, y, row=4, col=17)
    _add("2", 20, y, row=4, col=18)
    _add("3", 21, y, row=4, col=19)
    _add("Ent", 22, y, row=4, col=20)

    # Row 5: Bottom row
    y = 5.5
    _add("Ctrl", 0, y, 1.25, row=5, col=0)
    _add("Fn", 1.25, y, row=5, col=1)
    _add("Win", 2.25, y, 1.25, row=5, col=2)
    _add("Alt", 3.5, y, 1.25, row=5, col=3)
    _add("Space", 4.75, y, 6.25, row=5, col=6)
    _add("Alt", 11, y, 1.25, row=5, col=10)
    _add("Menu", 12.25, y, 1.25, row=5, col=11)
    _add("Ctrl", 13.5, y, 1.25, row=5, col=13)
    _add("Left", 15.5, y, row=5, col=14)
    _add("Down", 16.5, y, row=5, col=15)
    _add("Right", 17.5, y, row=5, col=16)
    _add("0", 19, y, 2, row=5, col=18)
    _add(".", 21, y, row=5, col=19)

    return keys


def _build_tkl_layout() -> list[Key]:
    """TKL layout - full without numpad."""
    return [k for k in _build_full_layout() if k.x < 18.5]


def _build_sixty_layout() -> list[Key]:
    """60% layout - main block only."""
    return [k for k in _build_full_layout() if k.x < 15.5 and k.y >= 1.5]


LAYOUTS: dict[str, list[Key]] = {
    "full": _build_full_layout(),
    "tkl": _build_tkl_layout(),
    "sixty": _build_sixty_layout(),
}
