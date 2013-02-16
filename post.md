Title: Monads for Normal Programmers (part 2)

The [first part of this series][part1] generated a lot of responses,
both very positive ones and very negative ones. I’m quite happy to
accept that I just don’t understand monads very well, but so far, no
one was able to convince me of that. One of the negative responses
claimed it was not possible to actually implement monadic structures
using my (simple) definition, which I took as meaning that the idea I
was trying to convey was not very clear.

[part1]: http://blog.jorgenschaefer.de/2013/01/monads-for-normal-programmers.html

This second part of the series will show an application of the
explanation I gave in the first part. I’ll start with a concrete
problem and implement it in Python, slowly building up to the ideas
encapsulated within monads. I assume you to have a good understanding
of Python to be able to focus on the new concepts introduced.

<!--more-->

**Please Note:** This article is not going to help you one bit if you
are trying to understand monads in Haskell. The intended audience is
software engineers wondering what this concept of monads is useful for
in other languages, especially dynamically typed ones. Chances are
that if you are trying to learn Haskell, this will do the opposite of
helping. Haskell has very different needs from other languages, and
uses monads very differently than I do here. Trying to apply things
you learn in other languages to Haskell usually is a recipe for
disaster.

Quick summary of the differences for functional programming
enthusiasts which happen to come across this for some reason or other:
We use methods instead of functions, so you need to subclass a monad
to be able to bind new functions to it. This also means that you can
not have a chain of applications without having a monadic value first.
Also, we do not differentiate between the monadic value and the value
stored within, as without static type systems, the difference is
mostly irrelevant.


## Source Code

I put the source code used below in a repository on github for easier
use.

[https://github.com/jorgenschaefer/monads-for-normal-programmers](https://github.com/jorgenschaefer/monads-for-normal-programmers)


# Finding Monads

Let’s start with a concrete problem. What I would like is a class
which encapsulates chained mathematical operations.

    >>> MathOp(5)
    <MathOp 5>
    >>> MathOp(5).mul(2)
    <MathOp 10>
    >>> MathOp(5).mul(2).add(17)
    <MathOp 27>
    >>> MathOp(5).mul(2).add(17).sub(4)
    <MathOp 23>

So far, so simple, but let’s add a twist. If there is a `div(0)`
anywhere in the chain, we don’t want to raise an exception, but to
have the whole chain return a `NaN`.

    >>> MathOp(5).div(0)
    <MathOp NaN>
    >>> MathOp(5).div(0).mul(2)
    <MathOp NaN>
    >>> MathOp(5).div(0).mul(2).add(17)
    <MathOp NaN>
    >>> MathOp(5).div(0).mul(2).add(17).sub(4)
    <MathOp NaN>


## Step 1: Trivial Implementation

The first implementation of this is straightforward and simple.

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

## Step 2: Bind

When you look at that code, you will notice that all the methods
implementing math operations share the same test for `is_nan`. This
repetitive code could be abstracted out into a common pattern, maybe
using a [decorator](http://www.python.org/dev/peps/pep-0318/).

    def mathop(method):
        @wraps(method)
        def math_method(self, *args, **kwargs):
            if self.is_nan:
                return self
            else:
                return method(self, *args, **kwargs)
        return math_method

This lets us write the class a bit more succinctly:

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

This common pattern is called *bind* in monad theory. If you remember
my last article, I noted that bind is *method application*. This here
now is the implementation of that idea. Bind influences how methods
are applied.

To make the idea more general, we could define a bind method in our
class and make our decorator call that instead.

    def bound(method):
        @wraps(method)
        def bound_method(self, *args, **kwargs):
            return self.bind(method, args, kwargs)
        return bound_method

By defining the `bind` magic in the class itself, we can re-use this
decorator in different subclasses.

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

This is the main part of the monad design pattern: We can abstract
away some specifics related to method application by using a decorator
that calls the bind method for us first.

Admittedly, the name bind is terrible, but it’s what the monad theory
uses. Use something more intuitive when you actually use this pattern.

*Note: It is possible to use metaclasses to make all methods of a
class use bind by default. This then requires a decorator for methods
that should not be passed through bind. It also adds a lot of magic
which I do not think helps understanding at all.*


## Step 3: Maybe Monad

You can probably see that what we implemented here is again an example
of a generic pattern: A chain of operations continues until a “bad”
value happens, then all following operations just pass on the bad
value. This is useful for mathematical operations, but it could be
useful for other things, too, if throwing an exception is not a
sensible solution. Some languages even implement exceptions using this
pattern.

This generic pattern is called the *maybe monad*.

    class MaybeMonad(object):
        is_nothing = False

        def bind(self, method, args, kwargs):
            if self.is_nothing:
                return self
            else:
                return method(self, *args, **kwargs)

We can subclass this to implement our math operation. As the
`is_nothing` field is now available on the class level, we can simply
define our `NaN` value as a subclass of `MathOp`. This would be a good
place for a singleton, but that’s a bit outside of the topic of this
article.

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


## Step 4: Monads!

So our `MathOp` class is an instance of a generic design pattern,
called the *Maybe Monad*. The same design pattern can be used for
other purposes.

A step further though, the *Maybe Monad* is itself an instance of an
even more generic design pattern. This more generic design pattern is
about the ability to chain method calls, and to override what method
application does, exactly. This more general design pattern is, as you
likely guessed, the *Monad*.

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

This example code for `bound` enforces that the result of bind
actually is a monad itself. That’s not something we need to do in a
dynamically typed language like Python, but it highlights one of the
theoretical requirements of monads.

We can now use this meta-pattern to define our `MaybeMonad`.

    class MaybeMonad(Monad):
        is_nothing = False

        def bind(self, method, args, kwargs):
            if self.is_nothing:
                return self
            else:
                return method(self, *args, **kwargs)

And in turn, we can use this `MaybeMonad` pattern to define the
`MathOp` class.

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


## Conclusions

In a sense, we have now created an abstraction tower.

The term *monad* refers to a very generic pattern about objects whose
methods return monadic objects so that method calls can be chained,
together with a generic way with which the application of those
methods can be influenced.

Using this general pattern, we can define more specific patterns that
use the general pattern for more specific purposes. The *Maybe Monad*
is one example of this, but there are many others. These are still
patterns, not concrete, useful classes, though.

We then can take this monadic pattern and create a specific class
which implements this pattern and finally have something useful.

Monads are *meta patterns* for specific monadic structures, which are
*patterns* for actually useful classes.

And just like with other design patterns, the important part is not
that you create the full abstraction tower in your code, it’s that you
use the pattern. A class that implements a singleton is still a
singleton, even if it does not inherit from a singleton abstract
class. A factory method is still a factory method, even if it does not
implement an abstract factory method interface.

This is especially true for dynamically-typed languages, and probably
the greatest source of confusion for people coming from the statically
typed world. Python objects do not need a rigid type hierarchy and
type checks to implement patterns that require careful consideration
for the type system in other languages.

The first implementation we used here is still monadic, even though we
did not make bind explicit. It’s useful to see that there is a common
pattern there, but it’s not necessary to actually make this pattern
explicit in your code. If you have your software engineer hat on, your
goal is to create programs that solve problems, and this is the most
important thing you care about.

On the other hand, if you are wearing your computer scientist hat,
your focus is on analyzing the patterns in programs first, and solving
real-world problems only second. This is where it becomes important to
split up those patterns, to make sure you know exactly what you are
talking about and how the different concepts interact.


# State Monad

Let’s add some complexity. The *state monad* is a design pattern where
you use method chaining to create a computation. The resulting
computation then can be run against various inputs (initial states).
This is a very handy pattern for all sorts of tasks, like creating a
pattern matcher from a pattern specification or pre-computing a
composable sequence of actions.

The basic idea is that we define methods in our monad instances that
add computations. At the end, we call the accumulated function with an
initial state. That state then is passed through the accumulated
computation.

Our goal is a simple game (courtesy of
[haskell.org](http://www.haskell.org/haskellwiki/State_Monad#Complete_and_Concrete_Example_1)).
This game is played in moves. Each move is either an *a*, a *b*, or a
*c*. If the game is on, an *a* will add one point and *b* will deduce
one point. If the game is off, neither one does anything. A *c* will
toggle the game between on and off. The game starts in the off state.

    >>> start_state = (False, 0)
    >>> Game().move('a').move('b').run(start_state)
    (False, 0)
    >>> game = Game().move('c').move('a')
    >>> game.run(start_state)
    (True, 1)
    >>> game.move('b').move('c').move('a').run(start_state)
    (False, 0)

We can start by defining a very skeleton `StateMonad` class. We want
to store a computation (function), and when we’re done building the
computation, we want to run that computation on a start state.

    class StateMonad(Monad):
        def __init__(self, function=lambda x: x):
            self.function = function

        def run(self, state):
            return self.function(state)

This isn’t too exciting yet. The default computation even is a real
no-op, simply returning what we pass in. But we’re still looking for
this generic pattern, not so much writing it down right away.

The first attempt below defines a method in `move`, which represents
the computation which we simply accumulate during the chaining
process. Once the game is done, we simply `run` the resulting game by
applying the function to the initial state.

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

Each computation calls the former computation (`self.function`), and
adds something to its result.

The pattern you can see here is the nested method. On the first pass,
when the methods are chained, only `move` is called, passing in the
`char` parameter. On the second pass, when the resulting game function
is applied to the initial state, the inner `transformer` function is
called and actually does the state transition. This is a perfectly
fine solution for us, and probably all you’ll ever use in Python when
you use this kind of pattern, but as we’re looking at formalizing
design patterns, we can try and abstract this further.

The following `bind` implementation captures the pattern we
established above, making the code a bit cleaner:

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

So far, so good. For a general pattern, though, it would be really
nice if our `move` method could return a whole series of transitions,
not just a single new state. But if this method can return a chained
game, then we need a state to run that returned value on.

        def bind(self, method, args, kwargs):
            def transformer(old_state):
                current_state = self.run(old_state)
                new_game = method(self, current_state,
                                  *args, **kwargs)
                new_state = new_game.run(???)
                return new_state
            return Game(transformer)

The ??? there can be solved by having `run` return two values, a value
and a state. The value is passed to the method, and the state to the
run method of the response of the game.

        def bind(self, method, args, kwargs):
            def transformer(old_state):
                value, current_state = self.run(old_state)
                new_game = method(self, value, *args, **kwargs)
                new_value, new_state = new_game.run(current_state)
                return new_value, new_state
            return Game(transformer)

So a run of a chained game now returns two values. The first value is
passed to the next method, while the second value is passed to the
composed state transition functions we create within those methods.

This requires some changes. First, we change `run` so it returns only
the first of the tuple returned, because that’s the actual value. Then
we define a `_run` internal method that returns the tuple for internal
use (in `bind`).

    def run(self, state):
        return self.get().function(state)[0]

    def _run(self, state):
        return self.function(state)

This change has another effect, which is much more useful in languages
without implicit state transitions. We can completely ignore the
current state in our (bound) methods and simply pass a value to the
next method. Alternatively, we can grab the current state and modify
it. The ability to grab the current state and pass it to the next
method as a value, or to store a value as the state, and also the
ability to modify the state using a function, are generic methods we
can use in all instances of this pattern.

The `get` method will simply discard the value it got from the last
computation and pass the current state as the value (argument) to the
next method.

    @bound
    def get(self, value):
        cls = type(self)
        return cls(lambda state: (state, state))

The `put` method will take an extra argument, the `new_state`, and
inject this as the new state in the computation, leaving the original
value intact. (Some implementations overwrite the value with some
useless value; it doesn’t matter.)

    @bound
    def put(self, value, new_state):
        cls = type(self)
        return cls(lambda state: (value, new_state))

To modify a state, we just take the last state and pass it through a
function. This is very much like put.

    @bound
    def modify(self, value, fun):
        cls = type(self)
        return cls(lambda state: (value, fun(state)))

For ultimate abstraction, we can implement `modify` using `get` and
`put`. Using existing functionality is conceptually cleaner, albeit
possibly not more readable. Note that we define a helper function.
`get` passes the state as a value to the next function, where we then
modify it, and pass it to put to store it back as the state.

    @bound
    def modify(self, value, fun):
        cls = type(self)
        return cls().get()._modify(fun)

    @bound
    def _modify(self, value, fun):
        "Modify the current state."
        cls = type(self)
        return cls().put(fun(value))

This leaves us with a new definition of the `StateMonad`.

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

The `move` definition in `Game` needs to be changed so it returns a
chain of state changes instead of simply the next state.

    class Game(StateMonad):
        @bound
        def move(self, char):
            if char == 'a':
                return Game().modify(
                    lambda (on, score): ((on, score + 1)
                                         if on else (on, score)))
            elif char == 'b':
                return Game().modify(
                    lambda (on, score): ((on, score - 1)
                                         if on else (on, score)))
            elif char == 'c':
                return Game().modify(
                    lambda (on, score): (not on, score))
            else:
                return Game().modify(
                    lambda (on, score): (on, score))

But wait a moment. Now that we can return state transitions, the no-op
action at the end could be a simple empty game. And actually, the
values `move` returns do not depend at all on the arguments to move
anymore. That means we can abstract them out of the method and into
global or class variables.

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

This works.

    >>> Game().move('a').move('a').move('a').get().result((False, 0))
    (False, 0)
    >>> Game().move('c').move('a').move('a').get().result((False, 0))
    (True, 2)

What we have done in the last step is to create the state change
transitions for the computation separately from creating the
computation itself.

And this is the very abstract idea of the state monad.

This final implementation is so abstract that it’s unlikely to be used
as is for any actual programs (in Python), but the idea of the pattern
is very useful. And seeing the common operations used for this pattern
is helpful in identifying when and how to use it for your programs to
solve problems.
