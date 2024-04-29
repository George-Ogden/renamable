from __future__ import annotations

from typing import Self, Type


class AddInterface:
    _alternative_name: str = "value"

    def __class_getitem__(cls, alternative_name: str) -> Type[Self]:
        return type(
            f"{cls.__name__}",
            cls.__bases__,
            dict(cls.__dict__) | dict(_alternative_name=alternative_name),
        )


def AddMeta(cls_name, cls_parents, cls_attrs):
    @property
    def base_property(base_self) -> Add:
        def value_getter(self) -> int:
            return getattr(base_self, base_self._alternative_name)

        def value_setter(self, value) -> int:
            return setattr(base_self, base_self._alternative_name, value)

        return type(cls_name, (), {"value": property(value_getter, value_setter)})()

    return type(cls_name, cls_parents + (AddInterface,), cls_attrs | {"Add": base_property})


class Add(metaclass=AddMeta):
    value: int

    def __add__(self, other: Add) -> Self:
        return type(self)(self.Add.value + other.Add.value)
