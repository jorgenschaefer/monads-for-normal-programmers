import unittest


class MathopTest(unittest.TestCase):
    CLASS = None

    def setUp(self):
        if self.CLASS is None:
            raise unittest.SkipTest("Base class not tested")

    def test_should_chain_computation(self):
        self.assertEqual(repr(self.CLASS(5)),
                         "<MathOp 5>")
        self.assertEqual(repr(self.CLASS(5).mul(2)),
                         "<MathOp 10>")
        self.assertEqual(repr(self.CLASS(5).mul(2).add(17)),
                         "<MathOp 27>")
        self.assertEqual(repr(self.CLASS(5).mul(2).add(17).sub(4)),
                         "<MathOp 23>")
        self.assertEqual(repr(self.CLASS(5).mul(2).div(2)),
                         "<MathOp 5>")

    def test_should_chain_nan(self):
        self.assertEqual(repr(self.CLASS(5).div(0)),
                         "<MathOp NaN>")
        self.assertEqual(repr(self.CLASS(5).div(0).mul(2)),
                         "<MathOp NaN>")
        self.assertEqual(repr(self.CLASS(5).div(0).mul(2).add(17)),
                         "<MathOp NaN>")
        self.assertEqual(repr(self.CLASS(5).div(0).mul(2).add(17).sub(4)),
                         "<MathOp NaN>")


from monads.mathop import step1, step2_1, step2_2, step3, step4


class TestStep1(MathopTest):
    CLASS = step1.MathOp


class TestStep2_1(MathopTest):
    CLASS = step2_1.MathOp


class TestStep2_2(MathopTest):
    CLASS = step2_2.MathOp


class TestStep3(MathopTest):
    CLASS = step3.MathOp


class TestStep4(MathopTest):
    CLASS = step4.MathOp
