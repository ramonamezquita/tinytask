from tinytask.ops import NOp, Ops, recursive_eval


def test_call_1():
    two = NOp(Ops.CONST, arg=2)
    three = NOp(Ops.CONST, arg=3)
    sum = NOp(Ops.CALL, lambda x, y: x + y, src=[two, three])
    n = recursive_eval(sum)
    assert n.arg == 5


def test_call_2():
    two = NOp(Ops.CONST, arg=2)
    three = NOp(Ops.CONST, arg=3)
    sum = NOp(Ops.CALL, lambda x, y: x + y, src=[two, three])
    mul = NOp(Ops.CALL, lambda x, y: x * y, src=[sum, sum])
    n = recursive_eval(mul)
    assert n.arg == 25


def test_call_is_special_case_of_compose():
    double = NOp(Ops.CALL, arg=lambda x: 2 * x)
    n = NOp(Ops.COMPOSE, arg=(5,), src=[double])
    n = recursive_eval(n)
    assert n.arg == 10


def test_compose_1():

    double = NOp(Ops.CALL, lambda x: 2 * x)
    triple = NOp(Ops.CALL, lambda x: 3 * x)
    double_then_triple = NOp(Ops.COMPOSE, arg=10, src=[double, triple])
    n = recursive_eval(double_then_triple)
    assert n.arg == 60
