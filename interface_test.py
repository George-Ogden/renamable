from dataclasses import dataclass

from interface import Add


@dataclass
class Box(Add):
    value: int


@dataclass
class Currency(Add["amount"]):
    amount: int


def test_box_add():
    a = Box(10)
    b = Box(20)
    c = a + b
    assert c == Box(30)
    assert c.value == 30
    assert c.Add.value == 30


def test_currency_add():
    a = Currency(10)
    b = Currency(20)
    c = a + b
    assert c == Currency(30)
    assert c.amount == 30


def test_box_overwrite():
    box = Box(10)
    box.Add.value = 30
    assert box.Add.value == 30
    assert box.value == 30


def test_currency():
    currency = Currency(10)
    currency.Add.value = 40
    assert currency.Add.value == 40
    assert currency.amount == 40
