"""Command descriptor and decorator for protocol methods."""

from __future__ import annotations

import types
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, overload

if TYPE_CHECKING:
    from .protocol import HIDProtocol


@dataclass(frozen=True)
class CommandSpec:
    """Metadata for a registered protocol command.

    Attributes:
        name: Method name (set by metaclass).
        opcode: Command byte(s) - single or multiple (e.g. command_class + command_id).
        args: Number of data bytes after the opcode.
        doc: Human-readable description.
        use_feature: True for feature reports (ioctl), False for output reports.
        builder: Custom builder function, or None for auto-generated.
    """

    name: str
    opcode: tuple[int, ...]
    args: int = 0
    doc: str = ""
    use_feature: bool = True
    builder: Callable[..., bytes] | None = None


class command:
    """Declarative command descriptor.

    Can be used as a decorator (custom builder) or as a class attribute
    (auto-generated method).

    Auto-generated (no custom logic needed)::

        class MyProto(HIDProtocol):
            set_led = command(0x01, args=4, doc="Set LED color")

        # Generates: proto.set_led(led_id, r, g, b)
        # Sends:     [report_id, 0x01, led_id, r, g, b, 0x00, ...]

    Custom builder (complex logic)::

        class MyProto(HIDProtocol):
            @command(0x09, doc="Set brightness and speed")
            def brightness_speed(self, brightness: int, speed: int):
                b = max(0, min(10, brightness))
                s = max(0, min(10, speed))
                return self._report(0x09, b, s, 0, 0)

    Args:
        opcode: Command byte.
        args: Number of data bytes (for auto-generated commands).
        doc: Description string.
        feature: If True, feature report. If False, output report.
    """

    def __init__(
        self,
        *opcode: int,
        args: int = 0,
        doc: str = "",
        feature: bool = True,
    ) -> None:
        self.opcode = opcode
        self.args = args
        self.doc = doc
        self.feature = feature
        self._builder: Callable[..., bytes] | None = None
        self._name: str = ""

    def __call__(self, fn: Callable[..., bytes]) -> command:
        """Used as decorator: @command(0x09, doc="...")."""
        self._builder = fn
        self.doc = self.doc or fn.__doc__ or ""
        return self

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    def _to_spec(self, name: str) -> CommandSpec:
        return CommandSpec(
            name=name,
            opcode=self.opcode,
            args=self.args,
            doc=self.doc,
            use_feature=self.feature,
            builder=self._builder,
        )

    def _make_auto_method(self, name: str) -> Callable[..., bytes]:
        """Generate a method that builds a report from opcode(s) + args."""
        opcode = self.opcode

        def auto_method(proto_self: HIDProtocol, *args: int) -> bytes:
            return proto_self._report(*opcode, *args)

        auto_method.__name__ = name
        auto_method.__qualname__ = name
        auto_method.__doc__ = self.doc
        return auto_method

    @overload
    def __get__(self, obj: None, objtype: type) -> command: ...

    @overload
    def __get__(self, obj: Any, objtype: type | None) -> Callable[..., bytes]: ...

    def __get__(self, obj: Any, objtype: type | None = None) -> command | Callable[..., bytes]:
        if obj is None:
            return self
        if self._builder:
            return types.MethodType(self._builder, obj)
        return types.MethodType(self._make_auto_method(self._name), obj)
