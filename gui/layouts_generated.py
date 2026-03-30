"""Auto-generated keyboard layouts from OpenRGB KeyboardLayoutManager."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Key:
    """A key in the keyboard layout."""
    label: str
    row: int
    col: int
    name: str


KEYBOARD_ZONE_MAIN: list[Key] = [
    Key("`", 1, 0, "KEY_EN_BACK_TICK"),
    Key("1", 1, 1, "KEY_EN_1"),
    Key("2", 1, 2, "KEY_EN_2"),
    Key("3", 1, 3, "KEY_EN_3"),
    Key("4", 1, 4, "KEY_EN_4"),
    Key("5", 1, 5, "KEY_EN_5"),
    Key("6", 1, 6, "KEY_EN_6"),
    Key("7", 1, 7, "KEY_EN_7"),
    Key("8", 1, 8, "KEY_EN_8"),
    Key("9", 1, 9, "KEY_EN_9"),
    Key("0", 1, 10, "KEY_EN_0"),
    Key("-", 1, 11, "KEY_EN_MINUS"),
    Key("=", 1, 12, "KEY_EN_EQUALS"),
    Key("Bksp", 1, 13, "KEY_EN_BACKSPACE"),
    Key("Tab", 2, 0, "KEY_EN_TAB"),
    Key("Q", 2, 1, "KEY_EN_Q"),
    Key("W", 2, 2, "KEY_EN_W"),
    Key("E", 2, 3, "KEY_EN_E"),
    Key("R", 2, 4, "KEY_EN_R"),
    Key("T", 2, 5, "KEY_EN_T"),
    Key("Y", 2, 6, "KEY_EN_Y"),
    Key("U", 2, 7, "KEY_EN_U"),
    Key("I", 2, 8, "KEY_EN_I"),
    Key("O", 2, 9, "KEY_EN_O"),
    Key("P", 2, 10, "KEY_EN_P"),
    Key("[", 2, 11, "KEY_EN_LEFT_BRACKET"),
    Key("]", 2, 12, "KEY_EN_RIGHT_BRACKET"),
    Key("\\", 2, 13, "KEY_EN_ANSI_BACK_SLASH"),
    Key("Caps", 3, 0, "KEY_EN_CAPS_LOCK"),
    Key("A", 3, 1, "KEY_EN_A"),
    Key("S", 3, 2, "KEY_EN_S"),
    Key("D", 3, 3, "KEY_EN_D"),
    Key("F", 3, 4, "KEY_EN_F"),
    Key("G", 3, 5, "KEY_EN_G"),
    Key("H", 3, 6, "KEY_EN_H"),
    Key("J", 3, 7, "KEY_EN_J"),
    Key("K", 3, 8, "KEY_EN_K"),
    Key("L", 3, 9, "KEY_EN_L"),
    Key(";", 3, 10, "KEY_EN_SEMICOLON"),
    Key("'", 3, 11, "KEY_EN_QUOTE"),
    Key("#", 3, 12, "KEY_EN_POUND"),
    Key("Enter", 3, 13, "KEY_EN_ANSI_ENTER"),
    Key("Shift", 4, 0, "KEY_EN_LEFT_SHIFT"),
    Key("\\", 4, 1, "KEY_EN_ISO_BACK_SLASH"),
    Key("Z", 4, 2, "KEY_EN_Z"),
    Key("X", 4, 3, "KEY_EN_X"),
    Key("C", 4, 4, "KEY_EN_C"),
    Key("V", 4, 5, "KEY_EN_V"),
    Key("B", 4, 6, "KEY_EN_B"),
    Key("N", 4, 7, "KEY_EN_N"),
    Key("M", 4, 8, "KEY_EN_M"),
    Key(",", 4, 9, "KEY_EN_COMMA"),
    Key(".", 4, 10, "KEY_EN_PERIOD"),
    Key("/", 4, 11, "KEY_EN_FORWARD_SLASH"),
    Key("Shift", 4, 13, "KEY_EN_RIGHT_SHIFT"),
    Key("Ctrl", 5, 0, "KEY_EN_LEFT_CONTROL"),
    Key("Win", 5, 1, "KEY_EN_LEFT_WINDOWS"),
    Key("Alt", 5, 2, "KEY_EN_LEFT_ALT"),
    Key("Space", 5, 6, "KEY_EN_SPACE"),
    Key("Alt", 5, 10, "KEY_EN_RIGHT_ALT"),
    Key("Fn", 5, 11, "KEY_EN_RIGHT_FUNCTION"),
    Key("Menu", 5, 12, "KEY_EN_MENU"),
    Key("Ctrl", 5, 13, "KEY_EN_RIGHT_CONTROL"),
]

KEYBOARD_ZONE_FN_ROW: list[Key] = [
    Key("Esc", 0, 0, "KEY_EN_ESCAPE"),
    Key("F1", 0, 2, "KEY_EN_F1"),
    Key("F2", 0, 3, "KEY_EN_F2"),
    Key("F3", 0, 4, "KEY_EN_F3"),
    Key("F4", 0, 5, "KEY_EN_F4"),
    Key("F5", 0, 6, "KEY_EN_F5"),
    Key("F6", 0, 7, "KEY_EN_F6"),
    Key("F7", 0, 8, "KEY_EN_F7"),
    Key("F8", 0, 9, "KEY_EN_F8"),
    Key("F9", 0, 10, "KEY_EN_F9"),
    Key("F10", 0, 11, "KEY_EN_F10"),
    Key("F11", 0, 12, "KEY_EN_F11"),
    Key("F12", 0, 13, "KEY_EN_F12"),
]

KEYBOARD_ZONE_EXTRAS: list[Key] = [
    Key("PrtSc", 0, 14, "KEY_EN_PRINT_SCREEN"),
    Key("ScrLk", 0, 15, "KEY_EN_SCROLL_LOCK"),
    Key("Pause", 0, 16, "KEY_EN_PAUSE_BREAK"),
    Key("Ins", 1, 14, "KEY_EN_INSERT"),
    Key("Home", 1, 15, "KEY_EN_HOME"),
    Key("PgUp", 1, 16, "KEY_EN_PAGE_UP"),
    Key("Del", 2, 14, "KEY_EN_DELETE"),
    Key("End", 2, 15, "KEY_EN_END"),
    Key("PgDn", 2, 16, "KEY_EN_PAGE_DOWN"),
    Key("Up", 4, 15, "KEY_EN_UP_ARROW"),
    Key("Left", 5, 14, "KEY_EN_LEFT_ARROW"),
    Key("Down", 5, 15, "KEY_EN_DOWN_ARROW"),
    Key("Right", 5, 16, "KEY_EN_RIGHT_ARROW"),
]

KEYBOARD_ZONE_NUMPAD: list[Key] = [
    Key("Num", 1, 17, "KEY_EN_NUMPAD_LOCK"),
    Key("/", 1, 18, "KEY_EN_NUMPAD_DIVIDE"),
    Key("*", 1, 19, "KEY_EN_NUMPAD_TIMES"),
    Key("-", 1, 20, "KEY_EN_NUMPAD_MINUS"),
    Key("7", 2, 17, "KEY_EN_NUMPAD_7"),
    Key("8", 2, 18, "KEY_EN_NUMPAD_8"),
    Key("9", 2, 19, "KEY_EN_NUMPAD_9"),
    Key("+", 2, 20, "KEY_EN_NUMPAD_PLUS"),
    Key("4", 3, 17, "KEY_EN_NUMPAD_4"),
    Key("5", 3, 18, "KEY_EN_NUMPAD_5"),
    Key("6", 3, 19, "KEY_EN_NUMPAD_6"),
    Key("1", 4, 17, "KEY_EN_NUMPAD_1"),
    Key("2", 4, 18, "KEY_EN_NUMPAD_2"),
    Key("3", 4, 19, "KEY_EN_NUMPAD_3"),
    Key("Ent", 4, 20, "KEY_EN_NUMPAD_ENTER"),
    Key("0", 5, 18, "KEY_EN_NUMPAD_0"),
    Key(".", 5, 19, "KEY_EN_NUMPAD_PERIOD"),
]


# Composite layouts
FULL = KEYBOARD_ZONE_FN_ROW + KEYBOARD_ZONE_MAIN + KEYBOARD_ZONE_EXTRAS + KEYBOARD_ZONE_NUMPAD
TKL = KEYBOARD_ZONE_FN_ROW + KEYBOARD_ZONE_MAIN + KEYBOARD_ZONE_EXTRAS
SEVENTY_FIVE = KEYBOARD_ZONE_FN_ROW + KEYBOARD_ZONE_MAIN
SIXTY = KEYBOARD_ZONE_MAIN
