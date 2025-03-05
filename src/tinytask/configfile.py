from __future__ import annotations

from types import SimpleNamespace

from tinytask import fileloaders


class ConfigFile:
    """Manage and validate configuration files.

    The configuration file should define tasks in the following format:

    ```yaml
    tasks:
      task_name:
        args:
          arg1: value1
          arg2: value2
    [...]
    ```
    """

    def __init__(self, data: dict) -> None:
        self._data = SimpleNamespace(**data)

    @property
    def tasks(self) -> dict[str, dict]:
        return self._data.tasks

    def get_task_args(self) -> dict[str, dict]:
        task_args = {}

        for task_name, task_config in self.tasks.items():
            task_args[task_name] = task_config["args"]

        return task_args

    def validate(self, validators) -> None:
        pass

    @classmethod
    def from_yaml(cls, filepath: str) -> ConfigFile:
        data = fileloaders.yaml.load_and_substitute(filepath)
        return cls(data=data)
