from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable


def gen_default_name(fun: Callable) -> str:
    """Generates default name from the given function."""
    name = fun.__name__
    module_name = fun.__module__
    return ".".join([module_name, name])


class Registry(dict):
    """Generic objects registry."""

    def __init__(
        self, prefix: str | None = None, exception: Exception = KeyError
    ):
        self.prefix = prefix or ""
        self.exception = exception

    def __missing__(self, key: str):
        self.raise_exception(key)

    def __call__(self, name: str | None = None) -> None:
        return self.register(name)

    def raise_exception(self, key: str):
        raise self.exception(key)

    def register(self, name: str | None = None) -> Callable:
        """Registers functions in the internal registry.

        Use it as decorator to register objects in the internal registry.

        Example
        -------
        registry = Registry()

        @registry()
            def foo():
                ...

        Parameters
        ----------
        name : str, default = None
            Name under which to store the function object.

        Returns
        -------
        inner : Callable
            Actual decorator that registers objects to the internal registry
            under the given name.
        """

        def inner(fun: Callable) -> Callable:
            name_ = name or gen_default_name(fun)
            self[self.prefix + name_] = fun
            return fun

        return inner

    def unregister(self, name: str) -> None:
        """Unregisters a function by name.

        Parameters
        ----------
        name : str
            Name of the function object to unregister

        Raises
        ------
        KeyError
        """
        try:
            self.pop(name)
        except KeyError:
            self.raise_exception(name)

    def merge(self, other: Registry | dict[str, Any]) -> None:
        """Merges another registry into this one.

        Parameters
        ----------
        other : Registry
            Another registry instance to merge.

        Raises
        ------
        ValueError
            If there are duplicate keys between the registries.
        """
        duplicates = set(self.keys()) & set(other.keys())
        if duplicates:
            raise ValueError(f"Duplicate keys found: {duplicates}")

        self.update(other)


class DictRegistry:
    def __init__(self):
        self._root = OrderedDict()

    @property
    def root(self):
        return self._root

    def add_dict(self, id_: str, dct: dict[str, Any]) -> None:
        """Adds a dictionary to the storage."""
        self._root[id_] = dct

    def get(self, id_: str) -> dict[str, Any] | None:
        """Retrieves a dictionary by its ID."""
        return self._root.get(id_)

    def clear(self) -> None:
        """Removes all stored dictionaries."""
        self._root.clear()

    def exists(self, id_: str) -> bool:
        """Checks if a dictionary with the given ID exists."""
        return id_ in self._root

    def get_last(self) -> tuple[str, dict]:
        k = next(reversed(self.root))
        v = self.root[k]
        return k, v

    def get_flattened(self) -> dict[str, Any]:
        """Returns all nested dict values in a single dict with keys prefixed
        by their dict ID."""
        flattened = {}
        for id_, dct in self._root.items():
            for key, value in dct.items():
                flattened[f"{id_}.{key}"] = value
        return flattened
