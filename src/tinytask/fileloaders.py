import json as _json
import os
import re
from typing import Callable

import yaml as _yaml


def substitute(
    value: str | list | dict, parameters: dict[str, str]
) -> dict[str, str]:

    if isinstance(value, str):
        # Replace placeholders with actual parameter values
        return re.sub(
            r"\${(.*?)}",
            lambda match: parameters.get(match.group(1), match.group(0)),
            value,
        )
    elif isinstance(value, dict):
        # Recursively substitute in dictionaries
        return {k: substitute(v, parameters) for k, v in value.items()}
    elif isinstance(value, list):
        # Recursively substitute in lists
        return [substitute(item, parameters) for item in value]
    else:
        return value


class FileLoader:
    """A class for loading files and optional parameter substitution.

    This class provides functionality to load files with a specific extension
    using a custom loader function. It supports checking file existence,
    loading files with UTF-8 encoding, and parameter substitution in
    loaded data.

    Parameters
    ----------
    loader : Callable
        A function that takes a string payload and returns a dictionary.
        This function is responsible for parsing the file content
        (e.g., json.loads for JSON files).

    ext : str
        The file extension to be appended to the filepath (e.g., '.json', '.yaml').

    open_method : Callable, optional
        The method used to open files. Defaults to built-in `open` function.
        Can be replaced with custom open methods for special file handling.
    """

    def __init__(
        self, loader: Callable, ext: str, open_method: Callable = open
    ):
        self.loader = loader
        self.ext = ext
        self.open_method = open_method

    def exists(self, filepath: str) -> bool:
        """Checks if the file exists.

        Parameters
        ----------
        file_path: str
            The full path to the file to load without the extension.

        Returns
        -------
        True if file path exists, False otherwise.
        """
        return os.path.isfile(filepath + self.ext)

    def _load_file(self, filepath: str) -> dict | None:
        if not self.exists(filepath):
            return

        # By default the file will be opened with locale encoding on Python 3.
        # We specify "utf8" here to ensure the correct behavior.
        full_path = filepath + self.ext
        with self.open_method(full_path, "rb") as fp:
            payload = fp.read().decode("utf-8")

        return self.loader(payload)

    def load(self, filepath: str) -> dict | None:
        """Attempt to load the file path.

        Parameters
        ----------
        file_path: str
            The full path to the file to load without the extension.

        Returns
        -------
        data : dict
            The loaded data if it exists, otherwise None.
        """
        return self._load_file(filepath)

    def load_and_substitute(
        self,
        filepath: str,
        params_key="args",
    ) -> dict | None:
        """Load a file and perform parameter substitution on its contents.

        This method loads a file and looks for a special parameters section
        specified by params_key. If found, it uses these parameters to
        substitute values in the rest of the loaded data.

        Parameters
        ----------
        filepath : str
            The full path to the file to load, without the extension.

        params_key : str, optional
            The dictionary key that contains substitution parameters.
            Defaults to "args".

        Returns
        -------
        dict | None
            The loaded and substituted data dictionary.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.

        Notes
        -----
        - The parameters section is removed from the final output
        - Parameter substitution is performed using an external 'substitute' function
        - If no parameters section is found (params_key doesn't exist),
          returns the data unchanged
        """
        data: dict = self.load(filepath)

        if data is None:
            raise FileNotFoundError(f"File not found: {filepath + self.ext}")

        if params_key not in data:
            return data

        parameters = data.pop(params_key)
        return substitute(data, parameters)


# Singleton instances.
# This instance is meant to be used by users.
# Example:
# >>> from sparkit import load
# >>> load.yaml(...)
yaml = FileLoader(loader=_yaml.safe_load, ext=".yaml", open_method=open)
json = FileLoader(loader=_json.loads, ext=".json", open_method=open)

__all__ = ["json", "yaml"]
