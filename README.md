# tinytask: minimal task manager

## Computation Graph and Task Execution Framework

This project provides a flexible framework for defining and executing computation graphs using callable operations (`NOp`) and a task execution system (`Task`). The framework supports function composition and task orchestration with callback-based notifications.

## Installation
Clone and install the repository:

```bash
git clone git@github.com:ramonamezquita/tinytask.git
pip install -e .
```


## Task Execution System

### Task decorator

The task decorator `tinytask.decorators.task` allows task creation
from arbitary callables.

```python
from tinytask.decorators import task
from tinytask.task import Task

@task()
def x_plus_y(x, y):
    return x + y

assert isinstance(x_plus_y, Task)
assert x_plus_y(2, 2) == 4
```

