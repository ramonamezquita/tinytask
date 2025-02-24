from typing import Callable

from tinytask.callbacks import Callback
from tinytask.task import Task, task_from_callable


def task(name: str | None = None, callbacks: list[Callback] = ()):
    """Wrap a function into a task.

    Parameters
    ----------
    name : str or None, default=None
        Name of the task. If None, the name will be inferred from the function's
        name and module.

    callbacks : list of Callbacks, default=()
        List of callbacks.
    """

    def decorator(fn: Callable) -> Task:

        task = task_from_callable(fun=fn, name=name)
        task.callbacks = callbacks
        return task

    return decorator
