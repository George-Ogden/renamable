from __future__ import annotations

from typing import Self


class Add:
    value: int

    def __add__(self, other: Add) -> Self:
        return type(self)(self.value + other.value)
