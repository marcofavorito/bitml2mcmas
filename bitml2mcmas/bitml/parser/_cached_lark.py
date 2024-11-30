"""Cache for Lark object."""

from typing import Any

from lark import Lark


class CachedLark:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs

        self._cached_lark: Lark | None = None

    def get_parser(self, force_reload: bool = False) -> Lark:
        if force_reload or self._cached_lark is None:
            self._cached_lark = Lark(*self._args, **self._kwargs)

        return self._cached_lark

    @property
    def parser(self) -> Lark:
        return self.get_parser(force_reload=False)
