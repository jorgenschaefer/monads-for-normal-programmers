class MathOp(object):
    def __init__(self, value=None, is_nan=False):
        self.value = value
        self.is_nan = is_nan

    def __repr__(self):
        if self.is_nan:
            return "<MathOp NaN>"
        else:
            return "<MathOp {}>".format(self.value)

    def div(self, denum):
        if self.is_nan:
            return self
        elif denum == 0:
            return MathOp(is_nan=True)
        else:
            return MathOp(self.value / denum)

    def mul(self, multiplicand):
        if self.is_nan:
            return self
        else:
            return MathOp(self.value * multiplicand)

    def add(self, multiplicand):
        if self.is_nan:
            return self
        else:
            return MathOp(self.value + multiplicand)

    def sub(self, multiplicand):
        if self.is_nan:
            return self
        else:
            return MathOp(self.value - multiplicand)
