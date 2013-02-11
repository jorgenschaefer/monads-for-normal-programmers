from monads.state.monad import Monad, bound


class StateMonad(Monad):
    def __init__(self, function=lambda x: x):
        self.function = function

    def run(self, state):
        return self.function(state)


class Game(StateMonad):
    def bind(self, method, args, kwargs):
        def transformer(old_state):
            current_state = self.run(old_state)
            new_state = method(self, current_state,
                               *args, **kwargs)
            return new_state
        return Game(transformer)

    @bound
    def move(self, state, char):
        on, score = state
        if char == 'a' and on:
            return (on, score + 1)
        elif char == 'b' and on:
            return (on, score - 1)
        elif char == 'c':
            return (not on, score)
        else:
            return (on, score)
