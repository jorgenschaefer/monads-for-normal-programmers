from functools import wraps


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
