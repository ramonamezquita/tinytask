from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable


class Ops(Enum):
    VOID = auto()
    CONST = auto()
    CALL = auto()
    OR = auto()


# fmt: off
def void(arg: tuple, src: list[NOp]): return None
def const(arg: tuple, src: list[NOp]) -> NOp: return NOp(Ops.VOID)
def call(arg: tuple, src: list[NOp]) -> NOp: return NOp(Ops.CONST, arg(*(s.arg for s in src)))

_OP_TO_FXN = {
    Ops.VOID: void,
    Ops.CONST: const,
    Ops.CALL: call
}
# fmt: on


@dataclass
class LazyCallable:
    """Placeholder for a callable and its parameters.

    Parameters
    ----------
    fxn : Callable
        Callable.

    args : tuple, default=()
        Task positional arguments.

    kwargs : dict, default=None
        Task key-word arguments.
    """

    fxn: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)

    def __post_init__(self):
        # Ensure args is always a tuple
        if not isinstance(self.args, (tuple, list)):
            self.args = (self.args,) if self.args else ()

    def __call__(self, *args) -> Any:
        args = args + self.args
        return self.fxn(*args, **self.kwargs)


def recursive_eval(n: NOp) -> NOp:

    if n.is_leaf():
        return n

    new_src = [recursive_eval(src) for src in n.src]
    new_n = NOp(n.op, n.arg, new_src)
    return new_n.eval()


@dataclass
class NOp:
    """Represents a Node Operation in a computation tree.

    Allows callables to be combined algebraically into a graph where operations
    (like OR) define how they interact.

    Parameters
    ----------
    op : Ops
        The operation type (e.g., CONST, OR).
    arg : tuple, default=()
        Optional arguments for the operation.
    src : list[NOp] or None, default=None
        List of source/input nodes.
    """

    op: Ops
    arg: tuple = ()
    src: list[NOp] | None = None

    def is_leaf(self) -> bool:
        return self.src is None or not self.src

    def eval(self) -> NOp:
        return _OP_TO_FXN[self.op](self.arg, self.src)
