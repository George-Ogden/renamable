from __future__ import annotations

import inspect
import itertools
from typing import Any, Dict, Type


class Renamable:
    __attribute_names: Dict[str, str]

    def __new__(mcls, cls: Type[Renamable]) -> Type[Renamable]:
        cls = mcls._rename_attributes(cls)
        cls = mcls._add_property(cls)
        cls = mcls._add_class_getitem(cls)
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
            return getattr(derived_self, derived_self._lookup_variable(name))

        def setter(self: object, value: Any):
            return setattr(derived_self, derived_self._lookup_variable(name), value)

        if settable:
            return property(getter, setter)
        else:
            return property(getter)

    @classmethod
    def _add_class_getitem(mcls, cls: Type[Renamable]) -> Type[Renamable]:
        def class_getitem(
            cls: Type[Renamable], alternative_names: Dict[str, Any]
        ) -> Type[Renamable]:
            # Copy class.
            cls = type(cls.__name__, cls.__bases__, dict(cls.__dict__))
            for k, v in alternative_names.items():
                if k not in cls.__attribute_names:
                    raise ValueError(
                        f"`{k}` not found in {cls.__name__} but trying to rename to `{v}`"
                    )
                cls.__attribute_names[k] = v
                setattr(cls, v, getattr(cls, k))
                delattr(cls, k)
            return cls

        cls.__class_getitem__ = class_getitem.__get__(cls)
        return cls
