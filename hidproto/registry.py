"""Protocol registry with auto-discovery and entry point support."""

from __future__ import annotations

import importlib
import importlib.metadata
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .protocol import HIDProtocol

ENTRY_POINT_GROUP = "hidproto.protocols"

_registry: dict[str, type[HIDProtocol]] | None = None


def _scan_builtin() -> dict[str, type[HIDProtocol]]:
    """Auto-discover builtin protocols from protocols/<vendor>/<device>.py."""
    from .protocol import HIDProtocol as BaseProto

    found: dict[str, type[HIDProtocol]] = {}
    proto_root = Path(__file__).parent.parent / "protocols"

    if not proto_root.exists():
        return found

    sys.path.insert(0, str(proto_root.parent))

    for f in sorted(proto_root.glob("**/*.py")):
        if f.name.startswith("_"):
            continue
        vendor = f.parent.name
        if vendor == "protocols":
            continue

        try:
            mod = importlib.import_module(f"protocols.{vendor}.{f.stem}")
        except Exception:
            continue

        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and issubclass(obj, BaseProto) and obj is not BaseProto:
                name = f.stem if f.stem.startswith(vendor) else f"{vendor}_{f.stem}"
                found[name] = obj
                break

    return found


def _scan_entry_points() -> dict[str, type[HIDProtocol]]:
    """Discover third-party protocols via entry points.

    Third-party packages register in their pyproject.toml::

        [project.entry-points."hidproto.protocols"]
        my_device = "my_package:MyProtocol"
    """
    found: dict[str, type[HIDProtocol]] = {}
    eps = importlib.metadata.entry_points()
    group = eps.select(group=ENTRY_POINT_GROUP) if hasattr(eps, "select") else eps.get(ENTRY_POINT_GROUP, [])

    for ep in group:
        try:
            found[ep.name] = ep.load()
        except Exception:
            continue

    return found


def discover() -> dict[str, type[HIDProtocol]]:
    """Discover all protocols: builtin + entry points.

    Results are cached after first call.
    """
    global _registry
    if _registry is not None:
        return _registry

    _registry = {}
    _registry.update(_scan_builtin())
    _registry.update(_scan_entry_points())
    return _registry


def register(name: str, cls: type[HIDProtocol]) -> None:
    """Manually register a protocol."""
    global _registry
    if _registry is None:
        _registry = {}
    _registry[name] = cls


def get(name: str) -> type[HIDProtocol] | None:
    """Get a protocol by name."""
    return discover().get(name)


def names() -> list[str]:
    """List all protocol names."""
    return sorted(discover().keys())
