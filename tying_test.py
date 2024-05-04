import pytest

from tying import renamable


def test_single_inheritance():
    @renamable
    class Foo:
        def bar(self) -> str:
            return "bar"

    class FooChild(Foo[dict(bar="bar_child")]):
        def bar_child(self) -> str:
            return "bar_child"

    foo = FooChild()
    assert foo.bar_child() == "bar_child"

    with pytest.raises(AttributeError):
        foo.bar()

    with pytest.raises(AttributeError):
        foo.Foo.bar_child()

    assert foo.Foo.bar() == "bar_child"


def test_multiple_inheritance():
    @renamable
    class Foo:
        def bar(self) -> str:
            return "bar"

    class FooChild(Foo[dict(bar="bar_child")]):
        def bar_child(self) -> str:
            return "bar_child"

    class FooGrandChild(FooChild):
        def bar_child(self) -> str:
            return "bar_child"

    foo = FooGrandChild()
    assert foo.bar_child() == "bar_child"

    with pytest.raises(AttributeError):
        foo.bar()

    with pytest.raises(AttributeError):
        foo.Foo.bar_child()

    assert foo.Foo.bar() == "bar_child"


def test_multiple_inheritance_overwrite_parent():
    @renamable
    class Foo:
        def bar(self) -> str:
            return "bar"

    @renamable
    class FooChild(Foo[dict(bar="bar_child")]):
        def bar_child(self) -> str:
            return "bar_child"

    class FooGrandChild(FooChild[dict(bar_child="bar_grandchild")]):
        def bar_grandchild(self) -> str:
            return "bar_grandchild"

    foo = FooChild()
    with pytest.raises(AttributeError):
        assert foo.bar_grandchild()

    foo.bar_child() == "bar_child"

    with pytest.raises(AttributeError):
        foo.bar()

    with pytest.raises(AttributeError):
        foo.FooChild.bar_grandchild()

    assert foo.FooChild.bar_child() == "bar_child"

    with pytest.raises(AttributeError):
        foo.FooChild.bar()

    with pytest.raises(AttributeError):
        foo.Foo.bar_grandchild()

    with pytest.raises(AttributeError):
        foo.Foo.bar_child()

    assert foo.Foo.bar() == "bar_child"


def test_multiple_inheritance_overwrite_child():
    @renamable
    class Foo:
        def bar(self) -> str:
            return "bar"

    @renamable
    class FooChild(Foo[dict(bar="bar_child")]):
        def bar_child(self) -> str:
            return "bar_child"

    class FooGrandChild(FooChild[dict(bar_child="bar_grandchild")]):
        def bar_grandchild(self) -> str:
            return "bar_grandchild"

    foo = FooGrandChild()
    assert foo.bar_grandchild() == "bar_grandchild"

    with pytest.raises(AttributeError):
        foo.bar_child()

    with pytest.raises(AttributeError):
        foo.bar()

    with pytest.raises(AttributeError):
        foo.FooChild.bar_grandchild()

    assert foo.FooChild.bar_child() == "bar_grandchild"

    with pytest.raises(AttributeError):
        foo.FooChild.bar()

    with pytest.raises(AttributeError):
        foo.Foo.bar_grandchild()

    with pytest.raises(AttributeError):
        foo.Foo.bar_child()

    assert foo.Foo.bar() == "bar_grandchild"


def test_replacement_name():
    @renamable
    class Foo:
        def bar(self) -> str:
            return "foo"

    class FooChild(Foo[dict(bar="bar_child")]):
        def bar(self) -> str:
            return "foo_child"

    foo = FooChild()
    assert foo.bar_child() == "foo"

    foo.bar() == "foo_child"

    with pytest.raises(AttributeError):
        foo.Foo.bar_child()

    assert foo.Foo.bar() == "foo"