from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from tinytask.callbacks import Callback, check_is_callback
from tinytask.ops import NOp, Ops, recursive_eval


def check_is_task(o: object) -> None:
    if not isinstance(o, Task):
        raise TypeError(f"Expected a Task instance, got {type(o).__name__}.")


def gen_task_name(name: str, module_name: str) -> str:
    return ".".join([module_name, name])


def make_tracer(task: Task) -> Callable:
    """Returns tracer to handle task execution, notifications, and error handling."""

    def trace(args: tuple = (), kwargs: dict | None = None) -> Any:
        """Executes the task while managing notifications and errors.

        Parameters
        ----------
        args : tuple, default=()
            Positional arguments for the task.

        kwargs : dict, default=None
            Keyword arguments for the task.

        Returns
        -------
        Any
            The return value from the task's `run` method.

        Raises
        ------
        Exception
            Propagates exceptions raised by the task's `run` method after
            notifying on failure.
        """
        kwargs = kwargs or {}
        task_id = task.name

        # Notify task begin
        task.notify("on_begin", task_id=task_id)

        try:
            retval = task(*args, **kwargs)
        except Exception as exc:
            # Notify task failure
            task.notify("on_failure", task_id=task_id, exc=exc)
            raise RuntimeError(f"Task {task_id} failed. Reason: {exc}") from exc

        # Notify task success
        task.notify("on_success", task_id=task_id, retval=retval)
        return retval

    return trace


def task_from_callable(
    fun: Callable[..., Any], name: str | None = None
) -> Task:
    """Factory function for :class:`Task` from arbitrary callables.

    Parameters
    ----------
    fun : Callable
        Function to convert to a :class:`Task` object.

    name : str or None, default=None
        Task name. If None, the name is inferred from function's name and
        module.
    """

    name = name or gen_task_name(fun.__name__, fun.__module__)

    class TaskWrapper(Task):

        def __init__(self):
            super().__init__(name=name)

        def run(self, *args, **kwargs):
            return fun(*args, **kwargs)

    return TaskWrapper()


class Signature:

    def __init__(
        self,
        fxn: Callable[..., Any] = None,
        args: tuple = (),
        kwargs: dict | None = None,
        n: NOp | None = None,
    ):
        self.fxn = fxn
        self.args = tuple(args) if isinstance(args, (tuple, list)) else (args,)
        self.kwargs = kwargs or {}
        self.n = n

    @property
    def node(self) -> NOp:

        def wrapper(*args) -> Any:
            return self.fxn(*(args + self.args), **self.kwargs)

        return self.n or NOp(Ops.CALL, wrapper)

    def __call__(self):
        return recursive_eval(self.node)

    def __or__(self, other: Signature) -> Signature:
        """Implements function composition using the `|` operator."""
        if not isinstance(other, Signature):
            raise TypeError(
                f"Cannot compose Signature with {type(other).__name__}"
            )

        n = NOp(Ops.COMPOSE, src=[self.node, other.node])
        return Signature(n=n)


@dataclass
class Task:
    """Task base class."""

    def __init__(
        self,
        name: str | None = None,
        callbacks: list[Callback] = (),
    ):
        self.name = name
        self.callbacks = callbacks

    @classmethod
    def from_callable(cls, fun: Callable[..., Any], name: str | None = None):
        return task_from_callable(fun, name)

    def run(self, *args, **kwargs):
        """The body of the task executed by workers."""
        raise NotImplementedError("Tasks must define the `run` method.")

    def s(self, args: tuple = (), kwargs: dict | None = None) -> Signature:
        return Signature(self.apply, args, kwargs)

    def apply(self, *args, **kwargs) -> Any:
        """Runs the task.

        Parameters
        ----------
        args : tuple
            Positional arguments for the task.

        kwargs : dict
            Keyword arguments for the task.

        Returns
        -------
        Any
            The return value from the task's execution.
        """
        return make_tracer(self)(args=args, kwargs=kwargs)

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def notify(self, method_name: str, **kwargs) -> None:
        for cb in self._callbacks:
            getattr(cb, method_name)(**kwargs)

    @property
    def callbacks(self) -> list[Callback]:
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value) -> None:
        for cb in value:
            check_is_callback(cb)
        self._callbacks = value

    def set_callbacks(self, callbacks):
        self.callbacks = callbacks
        return self
