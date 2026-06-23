"""Unit tests for the calculator engine (no GUI required)."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ti84ce.engine import DEG, RAD, CalculatorError, Engine  # noqa: E402


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.eng = Engine(angle_mode=DEG)

    def almost(self, expr, expected, places=9):
        self.assertAlmostEqual(self.eng.evaluate(expr), expected, places=places)

    def test_basic_arithmetic(self):
        self.almost("2+3*4", 14)
        self.almost("(2+3)*4", 20)
        self.almost("10/4", 2.5)
        self.almost("2^10", 1024)
        self.almost("7 mod(7,3)" if False else "mod(7,3)", 1)

    def test_glyph_normalisation(self):
        self.almost("6×7", 42)
        self.almost("84÷2", 42)
        self.almost("10−3", 7)
        self.almost("5²", 25)
        self.almost("2³", 8)
        self.almost("√(16)", 4)
        self.almost("2⁻¹", 0.5)

    def test_constants(self):
        self.almost("π", math.pi)
        self.almost("e", math.e)
        self.almost("τ", math.tau)

    def test_trig_degrees(self):
        self.eng.set_angle_mode(DEG)
        self.almost("sin(30)", 0.5)
        self.almost("cos(60)", 0.5)
        self.almost("asin(0.5)", 30)

    def test_trig_radians(self):
        self.eng.set_angle_mode(RAD)
        self.almost("sin(π/6)", 0.5)
        self.almost("cos(0)", 1)

    def test_logs(self):
        self.almost("log(1000)", 3)
        self.almost("ln(e)", 1)
        self.almost("exp(0)", 1)

    def test_factorial_and_roots(self):
        self.almost("factorial(5)", 120)
        self.almost("cbrt(27)", 3)
        self.almost("nroot(3,8)", 2)
        self.almost("hypot(3,4)", 5)

    def test_ans_chaining(self):
        self.eng.evaluate("2+2")
        self.almost("Ans*10", 40)

    def test_function_evaluation_for_graph(self):
        self.eng.set_angle_mode(RAD)
        self.assertAlmostEqual(self.eng.eval_function("X^2", 4), 16)
        self.assertAlmostEqual(self.eng.eval_function("sin(X)", 0), 0)

    def test_errors(self):
        with self.assertRaises(CalculatorError):
            self.eng.evaluate("1/0")
        with self.assertRaises(CalculatorError):
            self.eng.evaluate("2++")
        with self.assertRaises(CalculatorError):
            self.eng.evaluate("__import__('os')")
        with self.assertRaises(CalculatorError):
            self.eng.evaluate("unknownfunc(2)")

    def test_security_no_attribute_access(self):
        # Attribute access / arbitrary calls must be rejected by the whitelist.
        for bad in ["().__class__", "open('x')", "[].append(1)"]:
            with self.assertRaises(CalculatorError):
                self.eng.evaluate(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
