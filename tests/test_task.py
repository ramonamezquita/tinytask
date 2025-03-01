from tinytask.decorators import task
from tinytask.ops import NOp
from tinytask.task import Signature, Task


def test_signature_composition_1():
    s1 = Signature(lambda x: x + 1, args=(3,))
    s2 = Signature(lambda x: x * 2)
    s3 = s1 | s2
    assert s3().eval().arg == 8


def test_signature_composition_2():
    s1 = Signature(lambda x: x + 1, args=(3,))
    s2 = Signature(lambda x: x * 2)
    s3 = Signature(lambda x: x * 3)
    s4 = s1 | s2 | s3
    assert s4().eval().arg == 24


def test_task_composition():

    @task()
    def initial_value():
        return 10

    @task()
    def double(x):
        return 2 * x

    @task()
    def triple(x):
        return 3 * x

    s1 = initial_value.s()
    s2 = double.s()
    s3 = triple.s()
    s4 = s1 | s2 | s3

    assert s4().eval().arg == 60


def test_task_from_callable():

    @task()
    def x_plus_y(x, y):
        return x + y

    assert isinstance(x_plus_y, Task)
    assert x_plus_y(2, 2) == 4


def test_signature():

    @task()
    def x_plus_y(x, y):
        return x + y

    s = x_plus_y.s((2, 2))

    assert isinstance(s(), NOp)
    assert s().eval().arg == 4
