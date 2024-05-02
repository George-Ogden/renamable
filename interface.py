from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Dict, List, Self, Tuple, Type


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
    __is_interface: bool

    def __new__(
        mcls: Type[type],
        name: str,
        bases: Tuple[Type[Any], ...],
        namespace: Dict[str, Any],
        /,
        **kwargs: Dict[str, Any],
    ) -> InterfaceMeta:
        metaclass_bases: Tuple[InterfaceMeta] = tuple(base for base in bases if type(base) == mcls)
        cls: InterfaceMeta = super().__new__(mcls, name, bases, namespace, **kwargs)
        if len(metaclass_bases) > 0:
            # TODO: make these readonly and immutable.
            for base in metaclass_bases:
                if base.__is_interface:
                    base.register(cls)
            cls.__is_interface = False
        else:
            specification = Specification.from_cls(cls)
            cls.__specification = specification
            cls.__registry = {}
            cls.__is_interface = True
        return cls

    def __str__(cls) -> str:
        return str(cls.__specification)

    def register(self, cls: Type[Self]):
        self.__registry[cls.__name__] = cls

    def list_implementations(self) -> List[Type[Self]]:
        return list(self.__registry.values())

    def __getattribute__(self, name: str) -> Any:
        if not name.startswith("_") and name in self.__registry:
            return self.__registry[name]
        return super().__getattribute__(name)
