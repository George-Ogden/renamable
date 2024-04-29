from __future__ import annotations

from typing import Self, Type


class Interface:
    _alternative_name: str = "value"

    def __class_getitem__(cls, alternative_name: str) -> Type[Self]:
        return type(
            f"{cls.__name__}",
            cls.__bases__,
            dict(cls.__dict__) | dict(_alternative_name=alternative_name),
        )


def AddInterface(cls_name, cls_parents, cls_attrs):
    @property
    def base_property(base_self) -> Add:
        @property
        def value_property(self) -> int:
            return getattr(base_self, base_self._alternative_name)

        return type(cls_name, (), {"value": value_property})()

    return type(cls_name, cls_parents + (Interface,), cls_attrs | {"Add": base_property})


class Add(metaclass=AddInterface):
    value: int

    def __add__(self, other: Add) -> Self:
        return type(self)(self.Add.value + other.Add.value)
