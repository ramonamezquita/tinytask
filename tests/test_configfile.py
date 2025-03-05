import pytest

from tinytask.configfile import ConfigFile

CONFIG = """
args:
  msg: "hello, world!"

tasks:
  sum:
    args:
      x: 10
      y: 20

  mul:
    args:
      x: 30
      y: 40

  print:
    args:
      msg: ${msg}
"""


@pytest.fixture
def config_path(tmp_path) -> str:
    p = tmp_path / "config.yaml"
    p.write_text(CONFIG, encoding="utf-8")
    return p.as_posix()


def test_load_from_yaml(config_path: str):
    ConfigFile.from_yaml(config_path.removesuffix(".yaml"))


def test_load_from_yaml(config_path: str):
    expected = {
        "sum": {"x": 10, "y": 20},
        "mul": {"x": 30, "y": 40},
        "print": {"msg": "hello, world!"},
    }

    config = ConfigFile.from_yaml(config_path.removesuffix(".yaml"))
    task_args = config.get_task_args()

    assert task_args == expected
