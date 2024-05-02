from __future__ import annotations

import enum
import inspect
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Self, Tuple, Type


class InterfaceLevel(enum.Enum):
    INTERFACE = enum.auto()
    IMPLEMENTATION = enum.auto()
    USAGE = enum.auto()


@dataclass
class Specification:
    name: str
    variables: Dict[str, Type[Any]]
    methods: Dict[str, inspect.Signature]

    @classmethod
    def from_cls(scls, cls: Type[Any], strict=True) -> Specification:
        declarations = {
            name: declaration
            for name, declaration in inspect.get_annotations(cls).items()
            if not name.startswith("_")
        }
        definitions = {
            name: definition for name, definition in vars(cls).items() if not name.startswith("_")
        }

        if len(declarations) + len(definitions) == 0:
            raise TypeError(f"`{cls.__name__}` defines an empty interface.")

        for name in list(definitions.keys()):
            if name in declarations:
                if strict:
                    raise TypeError(f"`{name}` has been assigned a value or is declare twice.")
                else:
                    definitions.pop(name)
                    continue
            if not callable(definitions[name]):
                if strict:
                    raise ValueError(
                        f"`{name}` detected in {cls.__name__} definition is not a function."
                    )
                else:
                    if name not in declarations:
                        declarations[name] = type(name)
                    definitions.pop(name)

        return Specification(
            name=cls.__name__,
            variables=declarations,
            methods={
                name: inspect.signature(definition) for name, definition in definitions.items()
            },
        )

    def __ior__(self, other: Specification) -> Specification:
        if not isinstance(other, Specification):
            return NotImplemented
        assert len(set(self.variables).intersection(set(other.methods))) == 0
        assert len(set(self.methods).intersection(set(other.variables))) == 0
        for name, signature in other.methods.items():
            self.methods[name] = signature
        for name, type_hint in other.variables.items():
            self.variables[name] = type_hint
        return self


class InterfaceMeta(type):
    __specification: Specification
    __registry: Dict[str, Type[Self]]
    __interface: Optional[InterfaceMeta] = None
    __level: InterfaceLevel

    def __new__(
        mcls: Type[type],
        name: str,
        bases: Tuple[Type[Any], ...],
        namespace: Dict[str, Any],
        /,
        **kwargs: Any,
    ) -> InterfaceMeta:
        cls: InterfaceMeta = super().__new__(mcls, name, bases, namespace)
        if cls.__interface == None:
            # This creates a new interface.
            specification = Specification.from_cls(cls, strict=True)
            cls.__specification = specification
            cls.__registry = {}
            cls.__interface = cls
            cls.__level = InterfaceLevel.INTERFACE
        else:
            match cls.__level:
                # Decrease the level and register only implementations.
                case InterfaceLevel.INTERFACE:
                    additional_specification = Specification.from_cls(cls, strict=False)
                    cls.__specification |= additional_specification
                    cls.__interface._register(cls)
                    cls.__level = InterfaceLevel.IMPLEMENTATION
                case InterfaceLevel.IMPLEMENTATION | InterfaceLevel.USAGE:
                    cls.__level = InterfaceLevel.USAGE
            mcls._add_property(cls)
        return cls

    def _register(self, cls: Self):
        self.__registry[cls.__name__] = cls

    def _add_property(cls: InterfaceMeta):
        """Add a property that acts as an alias via the interface."""

        @property
        def interface_property(root):
            public_properties: Dict[str, property] = {}
            for name in cls.__specification.variables:
                public_properties[name] = InterfaceMeta._make_property(root, name, settable=True)

            for name in cls.__specification.methods:
                public_properties[name] = InterfaceMeta._make_property(root, name, settable=False)
            return type(cls.__interface.__name__, (), public_properties)()

        setattr(cls, cls.__interface.__name__, interface_property)

    def _make_property(root, name: str, settable: bool = True) -> property:
        """Make a property to get attributes from the root."""

        def getter(self) -> Any:
            return getattr(root, name)

        def setter(self, value: Any):
            return setattr(root, name, value)

        if settable:
            return property(getter, setter)
        else:
            return property(getter)

    def list_implementations(self) -> List[Self]:
        return list(self.__registry.values())

    def __getattribute__(self, name: str) -> Any:
        if not name.startswith("_") and name in self.__registry:
            return self.__registry[name]
        return super().__getattribute__(name)
