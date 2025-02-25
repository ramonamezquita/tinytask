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


    
if __name__ == "__main__":

    test_call_1()
    test_call_2()
    print("All tests passed!")