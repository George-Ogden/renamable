from dataclasses import dataclass

from interface import Add


@dataclass
class Box(Add):
    value: int


@dataclass
class Currency(Add["amount"]):
    amount: int


def test_box():
    a = Box(10)
    b = Box(20)
    c = a + b
    assert c == Box(30)
    assert c.value == 30
    assert c.Add.value == 30


def test_currency():
    a = Currency(10)
    b = Currency(20)
    c = a + b
    assert c == Currency(30)
    assert c.amount == 30
