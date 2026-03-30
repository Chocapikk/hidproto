"""hidproto - A Python DSL for HID device protocols on Linux."""

from .checksum import sum_checksum, xor_checksum
from .command import CommandSpec, command
from .device import HIDDevice
from .discovery import DeviceInfo, find_device, list_devices
from .effect import EffectSpec, Step, apply_effect, effect, step
from .protocol import HIDProtocol
from .registry import discover, get, names, register
from .transport import HidrawTransport

__all__ = [
    "CommandSpec",
    "DeviceInfo",
    "EffectSpec",
    "Step",
    "HIDDevice",
    "HIDProtocol",
    "HidrawTransport",
    "apply_effect",
    "command",
    "effect",
    "step",
    "find_device",
    "list_devices",
    "sum_checksum",
    "discover",
    "get",
    "names",
    "register",
    "xor_checksum",
]
