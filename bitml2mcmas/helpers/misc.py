"""Miscellaneous helper functions."""

import inspect
import os
from collections import Counter, deque
from collections.abc import Collection, Sequence
from enum import Enum
from pathlib import Path
from typing import AbstractSet, Any

ROOT_PATH = Path(os.path.dirname(inspect.getfile(inspect.currentframe()))).parent  # type: ignore[arg-type]


def assert_(condition: bool, message: str = "") -> None:
    """User-defined assert.

    This function is useful to avoid the use of the built-in assert statement, which is removed
        when the code is compiled in optimized mode. For more information, see
        https://bandit.readthedocs.io/en/1.7.5/plugins/b101_assert_used.html
    """
    check(condition, message=message, exception_cls=AssertionError)


def check(
    condition: bool, message: str = "", exception_cls: type[Exception] = AssertionError
) -> None:
    """Check a condition, and if false, raise exception."""
    if not condition:
        raise exception_cls(message)


def find_repeated(collection: Collection) -> Sequence:
    return tuple([item for item, count in Counter(collection).items() if count > 1])


def sequence_like(v: Any) -> bool:
    return type(v) in (list, tuple, set, frozenset, deque)


class CaseNotHandledError(Exception):
    def __init__(self, func_name: str, arg: Any) -> None:
        self._func_name = func_name
        self._arg = arg
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        return f"function {self._func_name} cannot handle argument {self._arg!r} of type {type(self._arg)!r}"


class ExtendedEnum(Enum):
    @classmethod
    def values(cls) -> AbstractSet:
        return {c.value for c in cls}
