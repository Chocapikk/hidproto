"""Keyboard layout definitions with visual positions and correct LED IDs.

LED IDs for ITE 8910: ((row & 7) << 5) | col
The col values are NOT sequential - some positions are skipped.
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


def _ite8910_full() -> list[Key]:
    """ITE 8910 full layout with correct LED IDs from clevo_829x_full_values.

    LED ID = ((row & 7) << 5) | col. Values from ClevoKeyboardDevices.cpp.
    """
    # fmt: off
    return [
        # Row 0 (row=0): ESC F1-F12 PrtSc
        # LED IDs: 0x00 0x01 0x02 0x03 0x04 0x05 0x06 0x07 0x08 0x09 0x0A 0x0B 0x0C 0x0D
        Key("Esc",  0,    0,      row=0, col=0x00),
        Key("F1",   2,    0,      row=0, col=0x01),
        Key("F2",   3,    0,      row=0, col=0x02),
        Key("F3",   4,    0,      row=0, col=0x03),
        Key("F4",   5,    0,      row=0, col=0x04),
        Key("F5",   6.5,  0,      row=0, col=0x05),
        Key("F6",   7.5,  0,      row=0, col=0x06),
        Key("F7",   8.5,  0,      row=0, col=0x07),
        Key("F8",   9.5,  0,      row=0, col=0x08),
        Key("F9",   11,   0,      row=0, col=0x09),
        Key("F10",  12,   0,      row=0, col=0x0A),
        Key("F11",  13,   0,      row=0, col=0x0B),
        Key("F12",  14,   0,      row=0, col=0x0C),
        Key("PrtSc",15.5, 0,      row=0, col=0x0D),
        Key("Ins",  16.5, 0,      row=0, col=0x0E),
        Key("Del",  17.5, 0,      row=0, col=0x0F),

        # Row 1 (row=1): ` 1-0 - = Bksp  Ins Home PgUp  Num / * -
        # LED IDs: 0x20-0x2E then nav 0x0E 0x10 0x12 then numpad 0x30-0x33
        Key("`",    0,    1.5,     row=1, col=0x00),
        Key("1",    1,    1.5,     row=1, col=0x01),
        Key("2",    2,    1.5,     row=1, col=0x02),
        Key("3",    3,    1.5,     row=1, col=0x03),
        Key("4",    4,    1.5,     row=1, col=0x04),
        Key("5",    5,    1.5,     row=1, col=0x05),
        Key("6",    6,    1.5,     row=1, col=0x06),
        Key("7",    7,    1.5,     row=1, col=0x07),
        Key("8",    8,    1.5,     row=1, col=0x08),
        Key("9",    9,    1.5,     row=1, col=0x09),
        Key("0",    10,   1.5,     row=1, col=0x0A),
        Key("-",    11,   1.5,     row=1, col=0x0B),
        Key("=",    12,   1.5,     row=1, col=0x0D),
        Key("Bksp", 13,  1.5, 2,  row=1, col=0x0E),
        Key("Home", 15.5, 1.5,    row=0, col=0x10),
        Key("PgUp", 16.5, 1.5,    row=0, col=0x12),
        Key("Num",  18,   1.5,    row=1, col=0x10),
        Key("/",    19,   1.5,    row=1, col=0x11),
        Key("*",    20,   1.5,    row=1, col=0x12),
        Key("-",    21,   1.5,    row=1, col=0x13),

        # Row 2 (row=2): Tab Q-P [ ] \  Del End PgDn  7 8 9 +
        # LED IDs: 0x40 0x42-0x4E then nav 0x0F 0x11 0x13 then numpad 0x50-0x53
        Key("Tab",  0,    2.5, 1.5, row=2, col=0x00),
        Key("Q",    1.5,  2.5,     row=2, col=0x02),
        Key("W",    2.5,  2.5,     row=2, col=0x03),
        Key("E",    3.5,  2.5,     row=2, col=0x04),
        Key("R",    4.5,  2.5,     row=2, col=0x05),
        Key("T",    5.5,  2.5,     row=2, col=0x06),
        Key("Y",    6.5,  2.5,     row=2, col=0x07),
        Key("U",    7.5,  2.5,     row=2, col=0x08),
        Key("I",    8.5,  2.5,     row=2, col=0x09),
        Key("O",    9.5,  2.5,     row=2, col=0x0A),
        Key("P",    10.5, 2.5,     row=2, col=0x0B),
        Key("[",    11.5, 2.5,     row=2, col=0x0C),
        Key("]",    12.5, 2.5,     row=2, col=0x0D),
        Key("\\",   13.5, 2.5, 1.5, row=2, col=0x0E),
        Key("Del",  15.5, 2.5,    row=0, col=0x0F),
        Key("End",  16.5, 2.5,    row=0, col=0x11),
        Key("PgDn", 17.5, 2.5,    row=0, col=0x13),
        Key("7",    18,   2.5,    row=2, col=0x10),
        Key("8",    19,   2.5,    row=2, col=0x11),
        Key("9",    20,   2.5,    row=2, col=0x12),
        Key("+",    21,   2.5,    row=2, col=0x13),

        # Row 3 (row=3): Caps A-L ; ' Enter  4 5 6
        # LED IDs: 0x60 0x62-0x6E then numpad 0x70-0x72
        Key("Caps", 0,    3.5, 1.75, row=3, col=0x00),
        Key("A",    1.75, 3.5,     row=3, col=0x02),
        Key("S",    2.75, 3.5,     row=3, col=0x03),
        Key("D",    3.75, 3.5,     row=3, col=0x04),
        Key("F",    4.75, 3.5,     row=3, col=0x05),
        Key("G",    5.75, 3.5,     row=3, col=0x06),
        Key("H",    6.75, 3.5,     row=3, col=0x07),
        Key("J",    7.75, 3.5,     row=3, col=0x08),
        Key("K",    8.75, 3.5,     row=3, col=0x09),
        Key("L",    9.75, 3.5,     row=3, col=0x0A),
        Key(";",    10.75,3.5,     row=3, col=0x0B),
        Key("'",    11.75,3.5,     row=3, col=0x0C),
        Key("Enter",12.75,3.5, 2.25, row=3, col=0x0E),
        Key("4",    18,   3.5,    row=3, col=0x10),
        Key("5",    19,   3.5,    row=3, col=0x11),
        Key("6",    20,   3.5,    row=3, col=0x12),

        # Row 4 (row=4): Shift Z-/ Shift Up  1 2 3 Enter
        # LED IDs: 0x80 0x83-0x8D 0x8F then numpad 0x90-0x93
        Key("Shift",0,    4.5, 2.25, row=4, col=0x00),
        Key("Z",    2.25, 4.5,     row=4, col=0x03),
        Key("X",    3.25, 4.5,     row=4, col=0x04),
        Key("C",    4.25, 4.5,     row=4, col=0x05),
        Key("V",    5.25, 4.5,     row=4, col=0x06),
        Key("B",    6.25, 4.5,     row=4, col=0x07),
        Key("N",    7.25, 4.5,     row=4, col=0x08),
        Key("M",    8.25, 4.5,     row=4, col=0x09),
        Key(",",    9.25, 4.5,     row=4, col=0x0A),
        Key(".",    10.25,4.5,     row=4, col=0x0B),
        Key("/",    11.25,4.5,     row=4, col=0x0C),
        Key("Shift",12.25,4.5, 2.75, row=4, col=0x0D),
        Key("Up",   16.5, 4.5,    row=4, col=0x0F),
        Key("1",    18,   4.5,    row=4, col=0x10),
        Key("2",    19,   4.5,    row=4, col=0x11),
        Key("3",    20,   4.5,    row=4, col=0x12),
        Key("Ent",  21,   4.5,    row=4, col=0x13),

        # Row 5 (row=5): Ctrl Fn Win Alt Space RAlt Menu RCtrl Left Down Right 0 .
        # LED IDs: 0xA0 0xA2-0xAC 0xAE-0xB2
        Key("Ctrl", 0,    5.5, 1.25, row=5, col=0x00),
        Key("Fn",   1.25, 5.5,     row=5, col=0x02),
        Key("Win",  2.25, 5.5, 1.25, row=5, col=0x03),
        Key("Alt",  3.5,  5.5, 1.25, row=5, col=0x04),
        Key("Space",4.75, 5.5, 6.25, row=5, col=0x05),
        Key("Alt",  11,   5.5, 1.25, row=5, col=0x0A),
        Key("Menu", 12.25,5.5, 1.25, row=5, col=0x0B),
        Key("Ctrl", 13.5, 5.5, 1.25, row=5, col=0x0C),
        Key("Left", 15.5, 5.5,    row=5, col=0x0E),
        Key("Down", 16.5, 5.5,    row=5, col=0x0F),
        Key("Right",17.5, 5.5,    row=5, col=0x10),
        Key("0",    18,   5.5, 2,  row=5, col=0x11),
        Key(".",    20,   5.5,    row=5, col=0x12),
    ]
    # fmt: on


def _build_tkl() -> list[Key]:
    return [k for k in _ite8910_full() if k.x < 18]


def _build_sixty() -> list[Key]:
    return [k for k in _ite8910_full() if k.x < 15.5 and k.y >= 1.5]


LAYOUTS: dict[str, list[Key]] = {
    "full": _ite8910_full(),
    "tkl": _build_tkl(),
    "sixty": _build_sixty(),
}
