from functools import wraps


def bound(method):
    @wraps(method)
    def bound_method(self, *args, **kwargs):
        return self.bind(method, args, kwargs)
    return bound_method


class MaybeMonad(object):
    is_nothing = False

    def bind(self, method, args, kwargs):
        if self.is_nothing:
            return self
        else:
            return method(self, *args, **kwargs)


class MathOp(MaybeMonad):
    is_nothing = False

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<MathOp {}>".format(self.value)

    @bound
    def div(self, denum):
        if denum == 0:
            return MathOpNaN()
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


class MathOpNaN(MathOp):
    is_nothing = True

    def __init__(self):
        super(MathOpNaN, self).__init__(None)

    def __repr__(self):
        return "<MathOp NaN>"
