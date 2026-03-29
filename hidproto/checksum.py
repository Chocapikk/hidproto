"""Checksum functions for HID protocols."""

from __future__ import annotations


def xor_checksum(data: bytes, start: int = 0, end: int | None = None) -> int:
    """XOR all bytes in data[start:end]. Used by Razer and others.

    Args:
        data: Raw bytes to checksum.
        start: Start index (inclusive).
        end: End index (exclusive). None means len(data).
    """
    crc = 0
    for b in data[start:end]:
        crc ^= b
    return crc


def sum_checksum(data: bytes, start: int = 0, end: int | None = None) -> int:
    """Sum all bytes mod 256. Used by some Corsair/SteelSeries devices.

    Args:
        data: Raw bytes to checksum.
        start: Start index (inclusive).
        end: End index (exclusive). None means len(data).
    """
    return sum(data[start:end]) & 0xFF
