#!/usr/bin/env python3
"""Parse OpenRGB KeyboardLayoutManager.cpp and generate Python layout data.

Usage:
    python tools/parse_klm.py /path/to/OpenRGB/KeyboardLayoutManager/KeyboardLayoutManager.cpp

Outputs gui/layouts_generated.py with all keyboard zones and regional overlays.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Key name to short label mapping
KEY_LABELS = {
    "KEY_EN_ESCAPE": "Esc",
    "KEY_EN_F1": "F1",
    "KEY_EN_F2": "F2",
    "KEY_EN_F3": "F3",
    "KEY_EN_F4": "F4",
    "KEY_EN_F5": "F5",
    "KEY_EN_F6": "F6",
    "KEY_EN_F7": "F7",
    "KEY_EN_F8": "F8",
    "KEY_EN_F9": "F9",
    "KEY_EN_F10": "F10",
    "KEY_EN_F11": "F11",
    "KEY_EN_F12": "F12",
    "KEY_EN_BACK_TICK": "`",
    "KEY_EN_1": "1",
    "KEY_EN_2": "2",
    "KEY_EN_3": "3",
    "KEY_EN_4": "4",
    "KEY_EN_5": "5",
    "KEY_EN_6": "6",
    "KEY_EN_7": "7",
    "KEY_EN_8": "8",
    "KEY_EN_9": "9",
    "KEY_EN_0": "0",
    "KEY_EN_MINUS": "-",
    "KEY_EN_EQUALS": "=",
    "KEY_EN_BACKSPACE": "Bksp",
    "KEY_EN_TAB": "Tab",
    "KEY_EN_Q": "Q",
    "KEY_EN_W": "W",
    "KEY_EN_E": "E",
    "KEY_EN_R": "R",
    "KEY_EN_T": "T",
    "KEY_EN_Y": "Y",
    "KEY_EN_U": "U",
    "KEY_EN_I": "I",
    "KEY_EN_O": "O",
    "KEY_EN_P": "P",
    "KEY_EN_LEFT_BRACKET": "[",
    "KEY_EN_RIGHT_BRACKET": "]",
    "KEY_EN_ANSI_BACK_SLASH": "\\",
    "KEY_EN_CAPS_LOCK": "Caps",
    "KEY_EN_A": "A",
    "KEY_EN_S": "S",
    "KEY_EN_D": "D",
    "KEY_EN_F": "F",
    "KEY_EN_G": "G",
    "KEY_EN_H": "H",
    "KEY_EN_J": "J",
    "KEY_EN_K": "K",
    "KEY_EN_L": "L",
    "KEY_EN_SEMICOLON": ";",
    "KEY_EN_QUOTE": "'",
    "KEY_EN_POUND": "#",
    "KEY_EN_ANSI_ENTER": "Enter",
    "KEY_EN_LEFT_SHIFT": "Shift",
    "KEY_EN_ISO_BACK_SLASH": "\\",
    "KEY_EN_Z": "Z",
    "KEY_EN_X": "X",
    "KEY_EN_C": "C",
    "KEY_EN_V": "V",
    "KEY_EN_B": "B",
    "KEY_EN_N": "N",
    "KEY_EN_M": "M",
    "KEY_EN_COMMA": ",",
    "KEY_EN_PERIOD": ".",
    "KEY_EN_FORWARD_SLASH": "/",
    "KEY_EN_RIGHT_SHIFT": "Shift",
    "KEY_EN_LEFT_CONTROL": "Ctrl",
    "KEY_EN_LEFT_WINDOWS": "Win",
    "KEY_EN_LEFT_ALT": "Alt",
    "KEY_EN_SPACE": "Space",
    "KEY_EN_RIGHT_ALT": "Alt",
    "KEY_EN_RIGHT_FUNCTION": "Fn",
    "KEY_EN_MENU": "Menu",
    "KEY_EN_RIGHT_CONTROL": "Ctrl",
    "KEY_EN_PRINT_SCREEN": "PrtSc",
    "KEY_EN_SCROLL_LOCK": "ScrLk",
    "KEY_EN_PAUSE_BREAK": "Pause",
    "KEY_EN_INSERT": "Ins",
    "KEY_EN_HOME": "Home",
    "KEY_EN_PAGE_UP": "PgUp",
    "KEY_EN_DELETE": "Del",
    "KEY_EN_END": "End",
    "KEY_EN_PAGE_DOWN": "PgDn",
    "KEY_EN_UP_ARROW": "Up",
    "KEY_EN_LEFT_ARROW": "Left",
    "KEY_EN_DOWN_ARROW": "Down",
    "KEY_EN_RIGHT_ARROW": "Right",
    "KEY_EN_NUMPAD_LOCK": "Num",
    "KEY_EN_NUMPAD_DIVIDE": "/",
    "KEY_EN_NUMPAD_TIMES": "*",
    "KEY_EN_NUMPAD_MINUS": "-",
    "KEY_EN_NUMPAD_7": "7",
    "KEY_EN_NUMPAD_8": "8",
    "KEY_EN_NUMPAD_9": "9",
    "KEY_EN_NUMPAD_PLUS": "+",
    "KEY_EN_NUMPAD_4": "4",
    "KEY_EN_NUMPAD_5": "5",
    "KEY_EN_NUMPAD_6": "6",
    "KEY_EN_NUMPAD_1": "1",
    "KEY_EN_NUMPAD_2": "2",
    "KEY_EN_NUMPAD_3": "3",
    "KEY_EN_NUMPAD_ENTER": "Ent",
    "KEY_EN_NUMPAD_0": "0",
    "KEY_EN_NUMPAD_PERIOD": ".",
    "KEY_EN_UNUSED": "",
}

# Pattern to match keyboard_led entries
LED_PATTERN = re.compile(
    r"\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,"
    r"\s*(KEY_\w+)\s*,\s*(KEY_\w+)\s*,\s*KEYBOARD_OPCODE_(\w+)"
)

# Pattern to match zone/overlay variable names
ZONE_PATTERN = re.compile(r"static\s+const\s+std::vector<keyboard_led>\s+(\w+)\s*=")


def parse_zone(text: str, start: int) -> list[dict]:
    """Parse a keyboard_led vector from its opening brace to closing };."""
    keys = []
    brace_start = text.index("{", start)

    # Find the matching closing };
    depth = 0
    end = brace_start
    for i in range(brace_start, len(text)):
        if text[i] == "{":
            depth += 1
        if text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    block = text[brace_start : end + 1]

    for match in LED_PATTERN.finditer(block):
        name = match.group(5)
        label = KEY_LABELS.get(name, name.replace("KEY_EN_", "").replace("_", " ").title())

        keys.append(
            {
                "zone": int(match.group(1)),
                "row": int(match.group(2)),
                "col": int(match.group(3)),
                "value": int(match.group(4)),
                "name": name,
                "alt_name": match.group(6),
                "label": label,
                "opcode": match.group(7),
            }
        )

    return keys


def parse_klm(cpp_path: str) -> dict[str, list[dict]]:
    """Parse all zones from KeyboardLayoutManager.cpp."""
    text = Path(cpp_path).read_text()
    zones = {}

    for match in ZONE_PATTERN.finditer(text):
        zone_name = match.group(1)
        keys = parse_zone(text, match.end())
        if keys:
            zones[zone_name] = keys

    return zones


def generate_python(zones: dict[str, list[dict]]) -> str:
    """Generate Python layout data from parsed zones."""
    lines = [
        '"""Auto-generated keyboard layouts from OpenRGB KeyboardLayoutManager."""',
        "",
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "",
        "",
        "@dataclass(frozen=True)",
        "class Key:",
        '    """A key in the keyboard layout."""',
        "    label: str",
        "    row: int",
        "    col: int",
        "    name: str",
        "",
        "",
    ]

    for zone_name, keys in zones.items():
        lines.append(f"{zone_name.upper()}: list[Key] = [")
        for k in keys:
            if k["label"]:
                label = k["label"].replace("\\", "\\\\")
                lines.append(f'    Key("{label}", {k["row"]}, {k["col"]}, "{k["name"]}"),')
        lines.append("]")
        lines.append("")

    # Composite layouts
    lines.append("")
    lines.append("# Composite layouts")
    lines.append("FULL = KEYBOARD_ZONE_FN_ROW + KEYBOARD_ZONE_MAIN + KEYBOARD_ZONE_EXTRAS + KEYBOARD_ZONE_NUMPAD")
    lines.append("TKL = KEYBOARD_ZONE_FN_ROW + KEYBOARD_ZONE_MAIN + KEYBOARD_ZONE_EXTRAS")
    lines.append("SEVENTY_FIVE = KEYBOARD_ZONE_FN_ROW + KEYBOARD_ZONE_MAIN")
    lines.append("SIXTY = KEYBOARD_ZONE_MAIN")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <KeyboardLayoutManager.cpp>")
        sys.exit(1)

    zones = parse_klm(sys.argv[1])

    print(f"Parsed {len(zones)} zones:")
    for name, keys in zones.items():
        print(f"  {name}: {len(keys)} keys")

    output = generate_python(zones)
    out_path = Path(__file__).parent.parent / "gui" / "layouts_generated.py"
    out_path.write_text(output)
    print(f"\nGenerated: {out_path}")
