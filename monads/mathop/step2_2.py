from functools import wraps


def bound(method):
    @wraps(method)
    def bound_method(self, *args, **kwargs):
        return self.bind(method, args, kwargs)
    return bound_method


class MathOp(object):
    def __init__(self, value=None, is_nan=False):
        self.value = value
        self.is_nan = is_nan

    def __repr__(self):
        if self.is_nan:
            return "<MathOp NaN>"
        else:
            return "<MathOp {}>".format(self.value)

    def bind(self, method, args, kwargs):
        if self.is_nan:
            return self
        else:
            return method(self, *args, **kwargs)

    @bound
    def div(self, denum):
        if denum == 0:
            return MathOp(is_nan=True)
        else:
            return MathOp(self.value / denum)

    @bound
    def mul(self, multiplicand):
        return MathOp(self.value * multiplicand)

    @bound
    def add(self, addend):
        return MathOp(self.value + addend)

    @bound
    def sub(self, subtrahend):
        return MathOp(self.value - subtrahend)
