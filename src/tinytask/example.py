from tinytask.ops import NOp, Ops, recursive_eval

two = NOp(Ops.CONST, arg=2)
three = NOp(Ops.CONST, arg=3)

sum_op = NOp(Ops.CALL, lambda x, y: x + y, src=[two, three])
mul_op = NOp(Ops.CALL, lambda x, y: x * y, src=[sum_op, sum_op])
