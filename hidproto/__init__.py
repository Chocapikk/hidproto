"""hidproto - A Python DSL for HID device protocols on Linux."""

from .checksum import sum_checksum, xor_checksum
from .command import CommandSpec, command
from .device import HIDDevice
from .discovery import DeviceInfo, find_device, list_devices
from .effect import EffectSpec, apply_effect, effect
from .protocol import HIDProtocol
from .transport import HidrawTransport

__all__ = [
    "CommandSpec",
    "DeviceInfo",
    "EffectSpec",
    "HIDDevice",
    "HIDProtocol",
    "HidrawTransport",
    "apply_effect",
    "command",
    "effect",
    "find_device",
    "list_devices",
    "sum_checksum",
    "xor_checksum",
]
