"""
Inspired by celery.canvas and celery.task
"""

from __future__ import annotations

from typing import Any, Callable, Sequence

from tinytask.callbacks import Callback, check_is_callback


def check_is_task(o: object) -> None:
    if not isinstance(o, Task):
        raise TypeError(f"Expected a Task instance, got {type(o).__name__}.")


def gen_task_name(name: str, module_name: str) -> str:
    return ".".join([module_name, name])


def make_tracer(task: Task) -> Callable:
    """Returns tracer to handle task execution, notifications, and error handling."""

    def tracer(args: tuple = (), kwargs: dict | None = None) -> Any:
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
            # Run the task
            retval = task(*args, **kwargs)
        except Exception as exc:
            # Notify task failure
            task.notify("on_failure", task_id=task_id, exc=exc)
            raise RuntimeError(f"Task {task_id} failed.") from exc

        # Notify task success
        task.notify("on_success", task_id=task_id, retval=retval)
        return retval

    return tracer


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
    """Placeholder for task and its parameters.

    Parameters
    ----------
    name : Task
        Task instance to run.

    args : tuple, default=()
        Task positional arguments.

    kwargs : dict, default=None
        Task key-word arguments.
    """

    def __init__(
        self,
        task: Task,
        args: tuple = (),
        kwargs: dict | None = None,
    ):

        self.task = task
        self.args = args
        self.kwargs = kwargs or {}

    def __call__(self):
        return self.task(*self.args, **self.kwargs)

    def trace(self):
        return self.task.trace(args=self.args, kwargs=self.kwargs)

    def insert_arg(self, value: Any) -> None:
        """Inserts `arg` at beggining of `args` attribute.

        Parameters
        ----------
        value : Any
            Value to insert.
        """
        self.args = (value,) + self.args

    def insert_kwarg(
        self, key: str, value: Any, overwrite: bool = True
    ) -> None:
        """Updates kwargs with the given key:value.

        Set `overwrite=False` to preserve existing values
        """
        if overwrite or key not in self.kwargs:
            self.kwargs[key] = value


class Task:
    """Task base class."""

    def __init__(self, name: str):
        self.name = name
        self._callbacks: Sequence[Callback] = ()

    def run(self, *args, **kwargs):
        """The body of the task executed by workers."""
        raise NotImplementedError("Tasks must define the `run` method.")

    def trace(self, args: tuple = (), kwargs: dict | None = None) -> Any:
        """Runs the task using a tracer object.

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

    def s(self, *args, **kwargs) -> Signature:
        return Signature(task=self, args=args, kwargs=kwargs)

    def notify(self, method_name: str, **kwargs) -> None:
        for cb in self._callbacks:
            getattr(cb, method_name)(**kwargs)

    @property
    def callbacks(self) -> Sequence[Callback]:
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value: Sequence[Callback]) -> None:
        for cb in value:
            check_is_callback(cb)
        self._callbacks = value

    def set_callbacks(self, callbacks: Sequence[Callback]):
        self.callbacks = callbacks
        return self
