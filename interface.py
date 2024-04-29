from __future__ import annotations

from typing import Dict, Self, Tuple, Type, Union


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


def InterfaceMeta(cls_name, cls_parents, cls_attrs):
    # * Make any annotations or defined variables public.
    # Assume all methods have annotations.
    public_attributes = (
        []
        if not "__annotations__" in cls_attrs
        else list(
            attribute
            for attribute in cls_attrs["__annotations__"].keys()
            if not attribute.startswith("_")
        )
    )
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

    def __class_getitem__(cls, alternative_names: Union[str, Tuple[str, ...]]) -> Type[Self]:
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
            f"{cls.__name__}",
            cls.__bases__,
            attributes,
        )

    cls_attrs[cls_name] = base_property
    cls_attrs["__class_getitem__"] = __class_getitem__
    return type(cls_name, cls_parents, cls_attrs)


class Add(metaclass=InterfaceMeta):
    value: int

    def __add__(self, other: Add) -> Self:
        return type(self)(self.Add.value + other.Add.value)
