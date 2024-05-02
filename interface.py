from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Self, Tuple, Type


@dataclass(repr=False)
class Specification:
    name: str
    variables: Dict[str, Type[Any]]
    methods: Dict[str, inspect.Signature]

    def __str__(self) -> str:
        heading = f"{self.name}: Interface"
        variables_body = "\n".join(
            f"- {name}: {annotation.__name__}" for name, annotation in self.variables.items()
        )
        if variables_body != "":
            variables_body = "\n" + variables_body
        methods_body = "\n".join(
            f"- {name}{(signature)}" for name, signature in self.methods.items()
        )
        if methods_body != "":
            methods_body = "\n" + methods_body
        return f"{heading}{variables_body}{methods_body}"

    @classmethod
    def from_cls(scls, cls: Type[Any]) -> Specification:
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

        for name in definitions:
            if name in declarations:
                raise TypeError(f"`{name}` has been assigned a value or is declare twice.")
            if not callable(definitions[name]):
                raise ValueError(
                    f"`{name}` detected in {cls.__name__} definition is not a function."
                )

        return Specification(
            name=cls.__name__,
            variables=declarations,
            methods={
                name: inspect.signature(definition) for name, definition in definitions.items()
            },
        )


class InterfaceMeta(type):
    __specification: Specification
    __registry: Dict[str, Type[Self]]
    __interface: Optional[InterfaceMeta] = None

    def __new__(
        mcls: Type[type],
        name: str,
        bases: Tuple[Type[Any], ...],
        namespace: Dict[str, Any],
        /,
        **kwargs: Any,
    ) -> InterfaceMeta:
        cls: InterfaceMeta = super().__new__(mcls, name, bases, namespace, **kwargs)
        if cls.__interface == None:
            specification = Specification.from_cls(cls)
            cls.__specification = specification
            cls.__registry = {}
            cls.__interface = cls
        else:
            cls.__interface.register(cls)
        return cls

    def __str__(cls) -> str:
        return str(cls.__specification)

    def register(self, cls: Self):
        self.__registry[cls.__name__] = cls
        self._add_property(cls)

    def _add_property(self, cls: InterfaceMeta):
        """Add a property that acts as an alias via the interface."""

        @property
        def interface_property(root):
            public_properties: Dict[str, property] = {}
            for name in cls.__specification.variables:
                public_properties[name] = self._make_property(root, name, settable=True)

            for name in cls.__specification.methods:
                public_properties[name] = self._make_property(root, name, settable=False)
            return type(cls.__interface.__name__, (), public_properties)()

        setattr(cls, cls.__interface.__name__, interface_property)

    def _make_property(self, root, name: str, settable: bool = True) -> property:
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
