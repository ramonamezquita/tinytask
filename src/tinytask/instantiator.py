from __future__ import annotations

import inspect
import pydoc
from typing import Any, Iterable, Type, TypedDict


class GenericObject(TypedDict):
    """Represents a generic object.

    Parameters
    ----------
    clspath : str
       Path to object class.

    kwargs : dict, str -> str
        Object key word arguments.

    key : str or None, default=None
        Object identifier.
    """

    clspath: str
    kwargs: dict[str, str]
    key: str | None


def map_to_instances(
    objects: list[GenericObject],
    context: dict[str, Any] = None,
    return_dict: bool = False,
) -> Iterable[Any]:
    """Maps object definitions to corresponding instances.

    This function takes a list of object definitions, each specifying the class
    path (`clspath`) and keyword arguments (`kwargs`) for instantiating the
    object. It then creates instances of the specified classes by using the
    `Instantiator` class to handle the instantiation..

    Parameters
    ----------
    objects : list[GenericObject]
        A list of object definitions, where each definition is a dictionary containing:
        - `clspath`: The path to the class to instantiate.
        - `kwargs`: A dictionary of keyword arguments to pass during instantiation.

    context : dict[str, Any], optional
        An optional context dictionary that can be passed to the `Instantiator`
        for additional initialization parameters.

    Returns
    -------
    instances : map object
        Map of instantiated objects.
    """
    instantiator = Instantiator(context)

    if return_dict:

        for o in objects:
            if "key" not in o:
                raise ValueError(
                    "`return_dict=True` only works if all object "
                    "have a not None `key` value"
                )

        return {
            o["key"]: instantiator.instantiate(
                o["clspath"], context=o["kwargs"]
            )
            for o in objects
        }

    return map(
        lambda o: instantiator.instantiate(o["clspath"], context=o["kwargs"]),
        objects,
    )


class InitArgsGetter:
    """Infers __init__ parameters.

    Parameters
    ----------
    context : dict, str -> Any
        Context dictionary from which __init__ args will be inferred.
    """

    def __init__(self, context: dict[str, Any]):
        self.context = context

    def get(
        self, cls: Type[Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Infers __init__ parameters for type `cls`.

        Parameters
        ----------
        cls : Type[Any]
            Class whose __init__ parameters will be obtained base on the context.

        context : dict, str -> Any
            Additional context args from which also infer __init__ args.

        Returns
        -------
        initargs : dict
        """
        init_signature = self._get_init_signature(cls)
        initargs = self._get_initargs(init_signature, context=context)
        return initargs

    def _get_init_signature(self, cls: Type[Any]) -> inspect.Signature:
        """Retrieves __init__ signature from ``cls``.

        Parameters
        ----------
        cls : class

        Returns
        -------
        Signature
        """
        init = getattr(cls.__init__, "deprecated_original", cls.__init__)
        return inspect.signature(init)

    def _get_initargs(
        self, init_signature, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Returns init kwargs inferred from context."""
        if context is None:
            context = {}

        context = {**self.context, **context}
        return {
            k: v for k, v in context.items() if k in init_signature.parameters
        }


class Instantiator:
    """Generic object instantiator.

    Parameters
    ----------
    context : dict, str -> Any
        Context dictionary from which __init__ args will be inferred.
    """

    def __init__(self, context: dict[str, Any] | None = None) -> None:
        self.context = context or {}

        self._initargs_getter = InitArgsGetter(self.context)

    def instantiate(
        self, clspath: str, context: dict[str, Any] | None = None
    ) -> Any:
        """Instantiates type located at `clspath`.

        Parameters
        ----------
        clspath : str
            Path, in dot notation format, of the class to instantiate.

        context : dict, str -> Any
            Additional context args from which also infer __init__ args.


        Returns
        -------
        object: Any
        """
        cls = pydoc.locate(clspath)
        initargs = self.get_initargs(cls, context)
        return cls(**initargs)

    def get_initargs(
        self, cls: Type[Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Infers __init__ parameters for type `cls`.

        Parameters
        ----------
        cls : Type[Any]
            Class whose __init__ parameters will be obtained based on the context.

        context : dict, str -> Any
            Additional context args from which also infer __init__ args.

        Returns
        -------
        initargs : dict, str -> Any
        """
        return self._initargs_getter.get(cls, context=context)
