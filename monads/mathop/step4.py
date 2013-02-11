from functools import wraps


##################################################################
# The Monad meta design pattern.

class Monad(object):
    def bind(self, method, args, kwargs):
        return method(self, *args, **kwargs)


def bound(method):
    @wraps(method)
    def bound_method(self, *args, **kwargs):
        result = self.bind(method, args, kwargs)
        assert(isinstance(result, Monad))
        return result
    return bound_method


##################################################################
# The MaybeMonad design pattern,
# an instance of the Monad meta design pattern.

class MaybeMonad(Monad):
    is_nothing = False

    def bind(self, method, args, kwargs):
        if self.is_nothing:
            return self
        else:
            return method(self, *args, **kwargs)


##################################################################
# The MathOp class,
# an instance of the MaybeMonad design pattern,
# in turn an instance of the Monad meta design pattern.

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
