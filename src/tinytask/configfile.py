from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from graphlib import TopologicalSorter
from types import SimpleNamespace
from typing import Any

from tinytask import fileloaders
from tinytask.task import Signature, check_is_task


@dataclass
class TaskDefinition:
    """Represents a task configuration."""

    pyfunc: str
    args: dict[str, Any] | None = None
    depends_on: list[str] = ()


def _resolve_task(taskdef: TaskDefinition, namespace: Any) -> Signature:
    """Resolve and validate a task based on its definition and the provided
    namespace.

    Parameters
    ----------
    taskdef : TaskDefinition
        The TaskDefinition object containing the task's configuration.

    namespace : Any
        The namespace containing the Python functions or tasks referenced in the
        task definitions.

    Returns:
    -------
    task : Task
        The resolved and validated Task object.

    Raises:
    ------
    ValueError
        If the specified 'pyfunc' does not exist in the namespace or is not
        callable.
    """
    if not hasattr(namespace, taskdef.pyfunc):
        raise ValueError(
            f"pyfunc `{taskdef.pyfunc}` does not exist in namespace."
        )

    task = getattr(namespace, taskdef.pyfunc)
    check_is_task(task)
    return task.s(**taskdef.args)


class TasksConfigFile:
    """Manage and validate task configuration files for workflow orchestration.

    This class handles the parsing, validation, and resolution of task
    configurations defined in YAML files. It supports dependency management
    between tasks and provides methods to generate executable task signatures
    in the correct order.

    The configuration file should define tasks in the following format:

    ```yaml
    tasks:
      task_name:
        pyfunc: function_name  # Optional, defaults to task_name
        args:                  # Optional, defaults to empty dict
          param1: value1
          param2: value2
        depends_on:           # Optional, defaults to empty tuple
          - other_task_name
    ```

    See Also
    --------
    Signature : Class representing executable task signatures

    """

    def __init__(self, data: dict) -> None:
        self._data = SimpleNamespace(**data)
        self._validate()

    def _validate(self):
        pass

    @cached_property
    def tasks(self) -> dict[str, TaskDefinition]:
        """Parse and return tasks as a dictionary of TaskDefinition objects."""

        return {
            k: TaskDefinition(
                pyfunc=v.get("pyfunc", k),
                args=v.get("args", {}),
                depends_on=v.get("depends_on", ()),
            )
            for k, v in self._data.tasks.items()
        }

    def order(self) -> tuple[str]:
        """Determine the execution order of tasks based on their dependencies.

        This method uses topological sorting to create an execution order where
        all dependencies are executed before their dependent tasks. The tasks
        must form a Directed Acyclic Graph (DAG) - meaning the dependency
        relationships between tasks cannot form any cycles.

        Returns
        -------
        tuple[str]
            Task names ordered according to their dependencies using topological
            sorting. This order ensures that all dependencies are executed
            before dependent tasks.

        Raises
        ------
        graphlib.CycleError
            If there are circular dependencies between tasks.

        Examples
        --------
        Valid DAG (will succeed):
        ```yaml
        tasks:
          task_a:
            pyfunc: func_a
          task_b:
            depends_on: [task_a]
          task_c:
            depends_on: [task_a, task_b]
        ```

        Invalid DAG (will raise CycleError):
        ```yaml
        tasks:
          task_a:
            depends_on: [task_b]
          task_b:
            depends_on: [task_a]
        ```
        """
        graph = {name: t.depends_on for name, t in self.tasks.items()}
        return TopologicalSorter(graph).static_order()

    def resolve(self, namespace: Any) -> dict[str, Signature]:
        """Resolve tasks into :class:`Signature` objects.

        This method creates executable Signature objects for each task by:
        1. Looking up the function in the provided namespace.
        2. Validating the function is callable.
        3. Creating a :class:`Signature` object using the specified arguments
        in the config file.
        4. Ordering tasks according to their dependencies.


        Parameters
        ----------
        namespace : Any
            The namespace containing the Python functions or tasks referenced
            in the task configuration file. Typically, this would be a
            module or an object with the required attributes.

        Returns
        -------
        dict[str, Signature]
            Dictionary of :class:`Signature` objects for the tasks.

        Raises
        ------
        ValueError
            If a `pyfunc` specified in the task definitions does not exist in
            the given namespace or if the resolved function is not callable or
            a valid `Task`.

        Example
        --------
        Given a yaml configuration file with the following task definitions:

        ```
        tasks:
          task1:
            pyfunc: my_function
            args: {param1: value1}
          task2:
            pyfunc: another_function
            args: {param2: value2}
            depends_on:
              - task1
        [...]
        ```

        And a namespace containing `my_function` and `another_function`, this
        method will return `Signature` objects for these tasks.
        """
        return {
            name: _resolve_task(self.tasks[name], namespace)
            for name in self.order()
        }

    @classmethod
    def from_yaml(cls, filepath: str) -> TasksConfigFile:
        data = fileloaders.yaml.load_and_substitute(filepath)
        return cls(data=data)
