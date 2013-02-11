# functools.wraps is a simple wrapper that copies docstrings and names
# from a wrapped method to the wrapper. This is not as important in
# this example code, but quite useful to get a hang of. If you are
# confused about it, you can simply ignore this in the following code.

from functools import wraps


def mathop(method):
    @wraps(method)
    def math_method(self, *args, **kwargs):
        if self.is_nan:
            return self
        else:
            return method(self, *args, **kwargs)
    return math_method


class MathOp(object):
    def __init__(self, value=None, is_nan=False):
        self.value = value
        self.is_nan = is_nan

    def __repr__(self):
        if self.is_nan:
            return "<MathOp NaN>"
        else:
            return "<MathOp {}>".format(self.value)

    @mathop
    def div(self, denum):
        if denum == 0:
            return MathOp(is_nan=True)
        else:
            return MathOp(self.value / denum)

    @mathop
    def mul(self, multiplicand):
        return MathOp(self.value * multiplicand)

    @mathop
    def add(self, addend):
        return MathOp(self.value + addend)

    @mathop
    def sub(self, subtrahend):
        return MathOp(self.value - subtrahend)
