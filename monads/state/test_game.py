import unittest


class StateTestCase(unittest.TestCase):
    CLASS = None

    def setUp(self):
        if self.CLASS is None:
            raise unittest.SkipTest("Base class not tested")
        self.start_state = (False, 0)

    def test_should_ignore_disabled_game(self):
        self.assertEqual(self.CLASS().move('a').move('b')
                         .run(self.start_state),
                         (False, 0))
        self.assertEqual(self.CLASS().move('a').move('a').move('a')
                         .run(self.start_state),
                         (False, 0))

    def test_should_toggle_active_game(self):
        self.assertEqual(self.CLASS().move('c').move('a')
                         .run(self.start_state),
                         (True, 1))

    def test_should_add_on_a(self):
        self.assertEqual(self.CLASS().move('c').move('a').move('a')
                         .run(self.start_state),
                         (True, 2))

    def test_should_chain_correctly(self):
        game = self.CLASS().move('c').move('a')
        self.assertEqual(game.move('b').move('c').move('a')
                         .run(self.start_state),
                         (False, 0))

    def test_should_have_noop(self):
        game = self.CLASS().move('d')
        self.assertEqual(game.run((True, 1000)),
                         (True, 1000))


from monads.state import state1, state2, state3, state4


class TestState1(StateTestCase):
    CLASS = state1.Game


class TestState2(StateTestCase):
    CLASS = state2.Game


class TestState3(StateTestCase):
    CLASS = state3.Game


class TestState4(StateTestCase):
    CLASS = state4.Game
