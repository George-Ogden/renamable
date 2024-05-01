from dataclasses import dataclass

from interface import Add, Boxed, Option


@dataclass
class Box(Add["value"]):
    value: int


@dataclass
class Currency(Add["amount"]):
    amount: int


@dataclass
class Integer(Boxed[int]["value"]):
    value: int


OptInt = Option[int]


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


def test_currency_overwrite():
    currency = Currency(10)
    currency.Add.value = 40
    assert currency.Add.value == 40
    assert currency.amount == 40


def test_integer_map():
    x = Integer(10)
    y = x.map(lambda x: x * 2)
    assert y == Integer(20)
    assert y.value == 20


def test_optint_present_map():
    x = OptInt(10)
    y = x.map(lambda x: x * 2)
    assert y == OptInt(20)
    assert y.optional_value == 20


def test_optint_absent_map():
    x = OptInt()
    y = x.map(lambda x: x * 2)
    assert y == OptInt()
    assert y.optional_value is None


def test_integer_overwrite():
    x = Integer(10)
    x.Boxed.value = 40
    assert x.Boxed.value == 40
    assert x.value == 40


def test_optint_overwrite():
    x = OptInt(10)
    x.Boxed.value = 40
    assert x.Boxed.value == 40
    assert x.optional_value == 40


def test_integer_indirect_map():
    x = Integer(10)
    y = x.Functor.map(lambda x: x * 2)
    assert y == Integer(20)
    assert y.value == 20


def test_optint_present_indirect_map():
    x = OptInt(10)
    y = x.Functor.map(lambda x: x * 2)
    assert y == OptInt(20)
    assert y.optional_value == 20


def test_optint_absent_indirect_map():
    x = OptInt()
    y = x.Functor.map(lambda x: x * 2)
    assert y == OptInt()
    assert y.optional_value is None
