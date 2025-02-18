import logging
from abc import ABC, abstractmethod
from typing import Any


def check_is_callback(o: object) -> None:
    if not isinstance(o, Callback):
        raise TypeError()


class Callback(ABC):
    """Base class for callbacks.

    All custom callbacks should inherit from this class. The subclass
    may override any of the `on_*` methods.

    . note::
        This class should not be used directly. Use derived classes instead.
    """

    @abstractmethod
    def on_begin(self, task_id: str) -> None:
        """Called at the beginning of running."""

    @abstractmethod
    def on_success(self, task_id: str, retval: Any) -> None:
        """Called when task completes successfully."""

    @abstractmethod
    def on_failure(self, task_id: str, exc: Any) -> None:
        """Called when task fails."""


class LoggingCallback(Callback):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def on_begin(self, task_id: str):
        return self.logger.info(f"Starting task: {task_id}")

    def on_success(self, task_id: str, retval: Any):
        self.logger.info(f"Completed task: {task_id} with result: {retval}")

    def on_failure(self, task_id: str, exc: Exception):
        self.logger.error(
            f"Task {task_id} failed with error: {exc}", exc_info=True
        )
