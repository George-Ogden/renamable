from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Dict, Self, Tuple, Type


@dataclass(repr=False)
class Specification:
    name: str
    variables: Dict[str, Type[Any]]
    methods: Dict[str, inspect.Signature]

    def __repr__(self) -> str:
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

    def __new__(
        mcls: Type[Self],
        name: str,
        bases: Tuple[Type[Any], ...],
        namespace: Dict[str, Any],
        /,
        **kwargs: Dict[str, Any],
    ) -> Self:
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        specification = Specification.from_cls(cls)
        cls.__specification = specification
        return cls

    def __repr__(cls) -> str:
        return repr(cls.__specification)
