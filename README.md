# Renamable

## What is a renamable?

### Example Problem

One of the major downsides of inheritance is that the names have to be the same.
Take the `Java.util.ArrayList` as an example.
If I want to append an element to this list, I have to use the `add` method:

```java
ArrayList<String> cars = new ArrayList<String>();
cars.add("Volvo");
```

**`add`** is a bad name.
Even the documentation describes this method as "_Appends the specified element to the end of this list._"
They use the word "append", which is a much better name.
This is a simple example but if `ArrayList` wants to implement the `Collection` interface, it must implement the `add` method.

### Solution

The example above is very simple (maybe too simple) but giving things good names is hard enough.
For a language like Java, it is important that `ArrayList` implements `Collection` for compatibility and interoperability.
But here's an alternative idea: when using an `ArrayList`, use the `append` identifier but when referring to the abstract `Collection`, use the `add` identifier.
Both of these refer to the same method.

```java
// ArrayList
ArrayList<String> carsArrayList = new ArrayList<String>();
carsArrayList.append("Volvo");
// Collection
Collection<String> carsCollection = new ArrayList<String>();
carsCollection.add("Volvo");
```

### Python Version

For Python, this is just a metaprogramming problem.
However, Python doesn't have a rich type system and code might not have any annotations.
So this is the `Renamable` class, my first attempt at solving the problem above.

## Usage

### Method Renaming

Let's define a class `Parent` with a method `parent_method`:

```python
@renamable
class Parent:
    def parent_method(self) -> str:
        return "parent"
```

But in the child, we want to override this.
Without using the renamable, we have to call the method `parent_method`:

```python
class Child(Parent):
    def parent_method(self) -> str:
        return "child"
```

But with the renamable, we can call it anything (including `child_method`):

```python
class Child(Parent[dict(parent_method="child_method")]):
    def child_method(self) -> str:
        return "child"
```

When we want to call the `child_method`, we can do just that:

```python
>>> child = Child()
>>> child.child_method()
"child"
```

And when we don't know whether it's a parent or a child, we can refer to the parent's method:

```python
>>> parent_or_child = parent_or_child_method()
>>> parent_or_child.Parent.parent_method()
"parent" or "child" # depending on the type
```

### Attribute Renaming

This also works with attributes:

```python
from renamable import renamable

@renamable
class NamedItem:
    item: str

class Book(NamedItem[dict(item="title")]):
    def __init__(self, title: str):
        self.title = title

book = Book("Harry Potter")
book.title # "Harry Potter"
book.NamedItem.item # "Harry Potter"
book.item # Error
```

It's worth noting that the last case fails.
That's because you can redefine methods with different names in the child classes.
For example, `ArrayList.add` could be reimplemented to do pointwise addition.

Attributes can also be replaced with constants.

```python
@renamable
class Number:
    value: float

@dataclass
class Pi(Number[dict(value=3.141)]):
    ...

eight = Number(8.0)
eight.value # 8.0

pi = Pi()
pi.value # 3.141
```

Use double quotes for strings:

```python
class WordItem(NamedItem[dict(item="'word'")]):
    ...

WordItem().item # "word"
```

### Generics

Renamable classes also work with generics (python>=3.12):

```python
@renamable
class Optional[T]:
    value: T | None

class PotentialError(Optional[str][dict(value="error")]):
    def __init__(self, error: str | None):
        self.error = error

error = PotentialError("error")
error.error # "error"
error.Optional.value # "error"
```

### Failure Modes

-   Renamable classes cause problems with method resolution order so you won't be able to use `__vars__` on any of the derived classes.
-   Renamable classes are not yet integrated with dataclasses when you use the renaming feature.
    If you only use constant values, you'll be fine.

## Install

```bash
pip install git+https://github.com/George-Ogden/renamable.git
```
