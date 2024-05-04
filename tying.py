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
        # Add the renames to the class name.
        name_suffix = f'[{",".join(f"{k}={v}" for k,v in alternative_names.items())}]'
        # Copy class.
        cls = type(cls.__name__ + name_suffix, cls.__bases__, dict(cls.__dict__))
        cls._alternative_names = dict(cls._alternative_names)
        cls._renamable_attributes = set(cls._renamable_attributes)

        bases = tuple(
            type(base.__name__, base.__bases__, dict(base.__dict__)) for base in cls.__bases__
        )

        for old_name, new_name in alternative_names.items():
            if old_name not in cls._renamable_attributes:
                raise ValueError(
                    f"`{old_name}` not allowed to be renamed in {cls.__name__} but trying to rename to `{new_name}`"
                )
            # Update name and disallow renaming in the future.
            cls._alternative_names[old_name] = new_name
            cls._renamable_attributes.remove(old_name)
            setattr(cls, new_name, getattr(cls, old_name))

            if hasattr(cls, old_name):
                delattr(cls, old_name)

            # Delete the current method from all bases.
            for base in bases:
                if hasattr(base, old_name):
                    delattr(base, old_name)

        cls = type(cls.__name__, bases, dict(cls.__dict__))

        return cls

    def _lookup_variable(self, name: str) -> str:
        while name in self._alternative_names and self._alternative_names[name] != name:
            name = self._alternative_names[name]
        return name
