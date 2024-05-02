from typing import Callable, Optional

import pytest

from interface import InterfaceMeta, Specification


def test_empty_specification():
    with pytest.raises(TypeError):

        class EmptyInterface(metaclass=InterfaceMeta): ...


def test_specification_with_definition():
    with pytest.raises(TypeError):

        class InterfaceWithError(metaclass=InterfaceMeta):
            a: int = 5


def test_specification_without_declaration():
    with pytest.raises(ValueError):

        class InterfaceWithError(metaclass=InterfaceMeta):
            a = 5


def test_specification_with_duplicate():
    with pytest.raises(TypeError):

        class DuplicateInterface(metaclass=InterfaceMeta):
            foo: Callable

            def foo(self): ...


def test_specification_repr():
    class TestInterface(metaclass=InterfaceMeta):
        a: int
        b: str

        def method(self, x: int, y: str):
            pass

    spec = Specification.from_cls(TestInterface)
    assert (
        str(spec) == "TestInterface: Interface\n- a: int\n- b: str\n- method(self, x: int, y: str)"
    )


def test_specification_variables():
    class TestInterface:
        attribute1: int
        attribute2: Optional[str]

    spec = Specification.from_cls(TestInterface)
    assert len(spec.variables) == 2
    assert len(spec.methods) == 0
    assert "attribute1" in spec.variables
    assert "attribute2" in spec.variables
    assert spec.variables["attribute1"] == int
    assert spec.variables["attribute2"] == Optional[str]


def test_specification_methods():
    class TestInterface:
        def method1(self, x: int, y: str):
            pass

        def method2(self):
            pass

    spec = Specification.from_cls(TestInterface)
    assert len(spec.variables) == 0
    assert len(spec.methods) == 2
    assert "method1" in spec.methods
    assert "method2" in spec.methods
    assert str(spec.methods["method1"]) == "(self, x: int, y: str)"
    assert str(spec.methods["method2"]) == "(self)"


def test_registration():
    class TestInterface(metaclass=InterfaceMeta):
        x: int

    class TestImplementation1(TestInterface):
        x = 1

    class TestImplementation2(TestInterface):
        x: int = 2

    implementations = TestInterface.list_implementations()
    assert len(implementations) == 2
    assert set(implementations) == set((TestImplementation1, TestImplementation2))


def test_access_to_implementations():
    class TestInterface(metaclass=InterfaceMeta):
        x: int

    class TestImplementation1(TestInterface):
        x = 1

    class TestImplementation2(TestInterface):
        x: int = 2

    assert TestInterface.TestImplementation1.x == 1
    assert TestInterface.TestImplementation2.x == 2
