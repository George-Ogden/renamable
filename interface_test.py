from dataclasses import dataclass

from interface import Add


@dataclass
class Currency(Add):
    amount: int

    @property
    def value(self) -> int:
        return self.amount

    @value.setter
    def value(self, value: int):
        self.amount = value


def test_currency():
    a = Currency(10)
    b = Currency(20)
    c = a + b
    assert c == Currency(30)
