from monads.state.monad import Monad, bound


class StateMonad(Monad):
    def __init__(self, function=lambda x: (None, x)):
        self.function = function

    def run(self, state):
        return self.get().function(state)[0]

    def _run(self, state):
        return self.function(state)

    def bind(self, method, args, kwargs):
        def transformer(old_state):
            value, current_state = self._run(old_state)
            computation = method(self, value, *args, **kwargs)
            new_value, new_state = computation._run(current_state)
            return new_value, new_state
        cls = type(self)
        return cls(transformer)

    @bound
    def get(self, value):
        "Pass the current state to the next method."
        cls = type(self)
        return cls(lambda state: (state, state))

    @bound
    def put(self, value, new_state):
        "Set new_state as the current state."
        cls = type(self)
        return cls(lambda state: (value, new_state))

    @bound
    def modify(self, value, fun):
        cls = type(self)
        return cls().get()._modify(fun)

    @bound
    def _modify(self, value, fun):
        "Modify the current state."
        cls = type(self)
        return cls().put(fun(value))


class Game(StateMonad):
    @bound
    def move(self, value, char):
        if char == 'a':
            return ADD
        elif char == 'b':
            return SUB
        elif char == 'c':
            return SWITCH
        else:
            return NOOP

ADD = Game().modify(
    lambda (on, score): ((on, score + 1)
                         if on else (on, score)))
SUB = Game().modify(
    lambda (on, score): ((on, score - 1)
                         if on else (on, score)))
SWITCH = Game().modify(
    lambda (on, score): (not on, score))
NOOP = Game()
