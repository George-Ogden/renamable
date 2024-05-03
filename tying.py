from __future__ import annotations

import inspect
import itertools
from typing import Any, ClassVar, Dict, Set, Type


class renamable:
    """Decorator to make a class renamable."""

    def __new__(mcls, cls: Type[Renamable]) -> Type[Renamable]:
        if not Renamable in cls.mro():
            bases = cls.__bases__
            if bases == (object,):
                bases = ()
            cls = type(
                cls.__name__,
                bases + (Renamable,),
                dict(cls.__dict__),
            )
        cls = mcls._rename_attributes(cls)
        cls = mcls._add_property(cls)
        return cls

    @classmethod
    def _rename_attributes(mcls, cls: Type[Renamable]) -> Type[Renamable]:
        attributes_names = set(itertools.chain(vars(cls), inspect.get_annotations(cls)))
        cls._renamable_attributes = {name for name in attributes_names if not name.startswith("_")}
        return cls

    @classmethod
    def _add_property(mcls, cls: Type[Renamable]) -> Type[Renamable]:
        """Add a property that acts as an alias via the current name."""

        @property
        def base_property(derived_self):
            public_properties: Dict[str, property] = {}
            for name in cls._renamable_attributes:
                public_properties[name] = mcls._make_property(derived_self, name, settable=True)
            return type(cls.__name__, (), public_properties)()

        setattr(cls, cls.__name__, base_property)
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


class Renamable:
    _alternative_names: ClassVar[Dict[str, str]] = dict()
    _renamable_attributes: ClassVar[Set[str]] = set()

    def __class_getitem__(
        cls: Type[Renamable], alternative_names: Dict[str, Any]
    ) -> Type[Renamable]:
        # Copy class.
        name_suffix = f'[{",".join(f"{k}={v}" for k,v in alternative_names.items())}]'
        cls = type(cls.__name__ + name_suffix, cls.__bases__, dict(cls.__dict__))
        cls._alternative_names = dict(cls._alternative_names)
        cls._renamable_attributes = set(cls._renamable_attributes)

        for k, v in alternative_names.items():
            if k not in cls._renamable_attributes:
                raise ValueError(
                    f"`{k}` not allowed to be renamed in {cls.__name__} but trying to rename to `{v}`"
                )
            cls._alternative_names[k] = v
            cls._renamable_attributes.remove(k)
            setattr(cls, v, getattr(cls, k))
            delattr(cls, k)
        return cls

    def _lookup_variable(self, name: str) -> str:
        while name in self._alternative_names and self._alternative_names[name] != name:
            name = self._alternative_names[name]
        return name
