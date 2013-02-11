from monads.state.monad import Monad


class StateMonad(Monad):
    def __init__(self, function=lambda x: x):
        self.function = function

    def run(self, state):
        return self.function(state)


class Game(StateMonad):
    def move(self, char):
        def transformer(state):
            on, score = self.function(state)
            if char == 'a' and on:
                return (on, score + 1)
            elif char == 'b' and on:
                return (on, score - 1)
            elif char == 'c':
                return (not on, score)
            else:
                return (on, score)
        return Game(transformer)
