from __future__ import annotations

import inspect
import itertools
from typing import Any, Dict, Type


class Renamable:
    __attribute_names: Dict[str, str]

    def __new__(mcls, cls: Type[Renamable]) -> Type[Renamable]:
        cls = mcls._rename_attributes(cls)
        cls = mcls._add_property(cls)
        return cls

    @classmethod
    def _rename_attributes(mcls, cls: Type[Renamable]) -> Type[Renamable]:
        attributes_names = set(itertools.chain(vars(cls), inspect.get_annotations(cls)))
        cls.__attribute_names = {
            name: name for name in attributes_names if not name.startswith("_")
        }
        return cls

    @classmethod
    def _add_property(mcls, cls: Type[Renamable]) -> Type[Renamable]:
        """Add a property that acts as an alias via the current name."""

        @property
        def base_property(derived_self):
            public_properties: Dict[str, property] = {}
            for name in cls.__attribute_names:
                public_properties[name] = mcls._make_property(derived_self, name, settable=True)
            return type(cls.__name__, (), public_properties)()

        def lookup_variable(self: Renamable, name: str) -> str:
            while name in self.__attribute_names and self.__attribute_names[name] != name:
                name = self.__attribute_names[name]
            return name

        setattr(cls, cls.__name__, base_property)
        setattr(cls, "_lookup_variable", lookup_variable)
        return cls

    @classmethod
    def _make_property(mcls, derived_self: Renamable, name: str, settable: bool = True) -> property:
        """Make a property to get attributes from the root."""

        def getter(self: object) -> Any:
            derived_self._lookup_variable(name)
            return getattr(derived_self, name)

        def setter(self: object, value: Any):
            derived_self._lookup_variable(name)
            return setattr(derived_self, name, value)

        if settable:
            return property(getter, setter)
        else:
            return property(getter)
