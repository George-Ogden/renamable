from __future__ import annotations

import abc
import itertools
from dataclasses import dataclass
from typing import (
    Callable,
    Dict,
    Generic,
    Optional,
    Self,
    Tuple,
    Type,
    Union,
    _generic_class_getitem,
)


def ImplementationMeta(cls_name, cls_parents, cls_attrs):
    # * Make any annotations or defined variables public.
    # Assume all methods have annotations.
    public_attributes = [
        attribute
        for attribute in cls_attrs.get("__annotations__", {}).keys()
        if not attribute.startswith("_")
    ]

    public_methods = list(
        method
        for method in cls_attrs.keys()
        if not method.startswith("_") and not method in public_attributes
    )

    # Define base property.
    @property
    def base_property(base_self) -> Add:
        # Storage for all public properties.
        public_properties: Dict[str, property] = {}
        for attribute in public_attributes:

            def getter(self) -> int:
                return getattr(base_self, base_self._alternative_names[attribute])

            def setter(self, value) -> int:
                return setattr(base_self, base_self._alternative_names[attribute], value)

            public_properties[attribute] = property(getter, setter)

        for method in public_methods:

            def getter(self) -> int:
                return getattr(base_self, method)

            public_properties[method] = property(getter)

        return type(cls_name, (), public_properties)()

    @classmethod
    def class_getitem(cls, alternative_names: Union[str, Tuple[str, ...]]) -> Type[Self]:
        if not isinstance(alternative_names, tuple):
            alternative_names = (alternative_names,)
        if len(alternative_names) != len(public_attributes):
            raise TypeError("Tried to initialise ...")
        alternative_names = {
            attribute: name for attribute, name in zip(public_attributes, alternative_names)
        }
        attributes = dict(cls.__dict__)
        attributes.pop("__class_getitem__")
        attributes["_alternative_names"] = alternative_names
        return type(
            f"{cls.__name__}[{','.join([str(name) for name in alternative_names.values()])}]",
            cls.__bases__,
            attributes,
        )

    cls_attrs["__class_getitem__"] = class_getitem
    cls_attrs[cls_name] = base_property
    if Generic in cls_parents:
        copied_cls_attrs = dict(cls_attrs)

        def updated_class_getitem(cls, *args, **kwargs):
            type_alias = _generic_class_getitem(cls, *args, **kwargs)
            cls_attrs["__class_getitem__"] = class_getitem
            return type(type_alias.__name__, cls_parents, copied_cls_attrs)

        cls_attrs["__class_getitem__"] = updated_class_getitem

    cls = type(cls_name, cls_parents, cls_attrs)
    return cls


class Add(metaclass=ImplementationMeta):
    value: int

    def __add__(self, other: Add) -> Self:
        return type(self)(self.Add.value + other.Add.value)


class Functor[T](metaclass=ImplementationMeta):
    @abc.abstractmethod
    def map(self, f: Callable[[T], T]) -> Self: ...


class Boxed[T](Functor[T][()], metaclass=ImplementationMeta):
    value: T

    def map(self, f: Callable[[T], T]) -> Self:
        return type(self)(f(self.Boxed.value))


@dataclass
class Option[T](Boxed[T]["optional_value"]):
    optional_value: Optional[T] = None

    def map(self, f: Callable[[T], T]) -> Self:
        if self.optional_value is None:
            return type(self)(None)
        else:
            return Boxed.map(self, f)
