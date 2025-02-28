from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from functools import reduce


# --- Operation Types ---
class Ops(Enum):
    VOID = auto()
    CONST = auto()
    CALL = auto()
    COMPOSE = auto()


#  --- Operation Functions ---


def void(arg: tuple, src: list[NOp]):
    return None


def const(arg: tuple, src: list[NOp]) -> NOp:
    return NOp(Ops.VOID)


def call(arg: tuple, src: list[NOp]) -> NOp:
    retval = arg(*(s.arg for s in src))
    return NOp(Ops.CALL if callable(retval) else Ops.CONST, retval)


def compose(arg: tuple, src: list[NOp]) -> NOp:
    initial_value = arg

    def wrapper(x, y):
        x = tuple(x) if isinstance(x, (tuple, list)) else (x,)
        return y(*x)

    retval = reduce(wrapper, (s.arg for s in src), initial_value)
    return NOp(Ops.CONST, retval)


# --- Operation Mapping ---
_OP_TO_FXN = {
    Ops.VOID: void,
    Ops.CONST: const,
    Ops.CALL: call,
    Ops.COMPOSE: compose,
}


def recursive_eval(n: NOp) -> NOp:
    """Bottom-up evaluation."""

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
    src: list[NOp] | None = ()

    def is_leaf(self) -> bool:
        return self.src is None or not self.src

    def eval(self) -> NOp:
        return _OP_TO_FXN[self.op](self.arg, self.src)
