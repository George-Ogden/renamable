from dataclasses import dataclass

from interface import Add


@dataclass
class Currency(Add):
    value: int


def test_currency():
    a = Currency(10)
    b = Currency(20)
    c = a + b
    assert c == Currency(30)
