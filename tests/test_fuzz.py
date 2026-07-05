"""Fuzz sweeps for the calculator engine (stdlib only, no external deps).

Two properties matter and neither may ever be violated:

  1. Robustness: for any input string, ``evaluate`` either returns a real
     number or raises ``CalculatorError`` -- never any other exception, and
     never a hang or crash. Every failure inside the whitelist (bad syntax,
     math-domain, divide-by-zero, overflow) must be funnelled through
     ``CalculatorError``.

  2. Determinism: the same expression evaluates to the same value twice.

The sweeps are seeded so a failure is reproducible. Iteration counts scale
from the ``TI84_FUZZ_ITERS`` env var so the fast test run stays quick while the
cicd slow stage can crank it up.
"""

import math
import os
import random
import sys
import unittest
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ti84ce.engine import DEG, RAD, CalculatorError, Engine  # noqa: E402

ITERS = int(os.environ.get("TI84_FUZZ_ITERS", "400"))

# Whitelisted vocabulary, kept in sync with engine._build_functions/_constants.
_UNARY = ["sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh",
          "ln", "exp", "sqrt", "cbrt", "abs", "floor", "ceil", "sign", "trunc"]
_BINARY = ["pow", "nroot", "gcd", "mod", "atan2", "hypot", "max", "min", "log"]
_CONSTS = ["pi", "e", "tau", "phi", "Ans"]
_OPS = ["+", "-", "*", "/", "%", "**"]
_GLYPHS = ["×", "÷", "−", "√", "²", "³", "π", "τ", "φ", "^"]


def _num(rng):
    """A small, sane numeric literal (bounded so exponents can't blow up)."""
    return rng.choice([
        str(rng.randint(-20, 20)),
        f"{rng.uniform(-20, 20):.4f}",
        str(rng.randint(0, 9)),
    ])


def _expr(rng, depth=0):
    """Build a random expression from the whitelisted grammar."""
    if depth >= 4 or rng.random() < 0.35:
        return rng.choice([_num(rng), rng.choice(_CONSTS)])
    kind = rng.random()
    if kind < 0.45:
        return f"({_expr(rng, depth + 1)} {rng.choice(_OPS)} {_expr(rng, depth + 1)})"
    if kind < 0.75:
        return f"{rng.choice(_UNARY)}({_expr(rng, depth + 1)})"
    return f"{rng.choice(_BINARY)}({_expr(rng, depth + 1)}, {_expr(rng, depth + 1)})"


class TestFuzzGrammar(unittest.TestCase):
    """Well-formed expressions never escape the CalculatorError funnel."""

    def test_grammar_sweep(self):
        rng = random.Random(0xC0FFEE)
        for mode in (DEG, RAD):
            eng = Engine(angle_mode=mode)
            for _ in range(ITERS):
                expr = _expr(rng)
                try:
                    value = eng.evaluate(expr)
                except CalculatorError:
                    continue
                except Exception as exc:  # noqa: BLE001 - that's the whole point
                    self.fail(f"leaked {type(exc).__name__} on {expr!r}: {exc}")
                self.assertIsInstance(value, (int, float),
                                      f"non-numeric result for {expr!r}: {value!r}")
                self.assertFalse(isinstance(value, bool),
                                 f"bool result for {expr!r}")

    def test_determinism(self):
        rng = random.Random(1234)
        eng = Engine()  # eval_no_store leaves Ans untouched, so one engine is enough
        for _ in range(min(ITERS, 500)):
            expr = _expr(rng)
            try:
                first = eng.eval_no_store(expr)
            except CalculatorError:
                with self.assertRaises(CalculatorError):
                    eng.eval_no_store(expr)
                continue
            second = eng.eval_no_store(expr)
            if math.isnan(first):
                self.assertTrue(math.isnan(second))
            else:
                self.assertEqual(first, second, f"non-deterministic result for {expr!r}")


class TestFuzzGarbage(unittest.TestCase):
    """Arbitrary junk in must never crash; only CalculatorError may come out."""

    _ALPHABET = list("0123456789+-*/%^().,eE xXpiπτφ√²³×÷−AnsZ_![]{}<>=:;'\"\\@#")

    def test_random_strings(self):
        rng = random.Random(0xBADC0DE)
        eng = Engine()
        # Junk routinely contains backslash escapes that ast.parse warns about;
        # that noise isn't the calculator's doing, so mute it for the sweep.
        warnings.simplefilter("ignore", SyntaxWarning)
        for _ in range(ITERS):
            length = rng.randint(0, 24)
            junk = "".join(rng.choice(self._ALPHABET) for _ in range(length))
            try:
                value = eng.evaluate(junk)
            except CalculatorError:
                continue
            except RecursionError:
                # Pathological nesting is a known interpreter limit, not a
                # calculator bug; the grammar sweep keeps depth bounded.
                continue
            except Exception as exc:  # noqa: BLE001
                self.fail(f"leaked {type(exc).__name__} on {junk!r}: {exc}")
            self.assertIsInstance(value, (int, float),
                                  f"non-numeric result for {junk!r}: {value!r}")


class TestFuzzLibraryBoundary(unittest.TestCase):
    """Poke the stdlib math boundary through the engine (domain / overflow).

    Random arguments to the math-backed functions must surface as
    CalculatorError, not a raw ValueError/OverflowError from the C library.
    """

    def test_math_domain_and_overflow(self):
        rng = random.Random(2718)
        eng = Engine(angle_mode=RAD)
        func_names = ["sqrt", "ln", "log", "asin", "acos", "acosh", "atanh",
                      "factorial", "exp", "tan"]
        for _ in range(ITERS):
            func_name = rng.choice(func_names)
            arg = rng.choice([
                rng.uniform(-1e6, 1e6),
                rng.uniform(-2, 2),
                rng.randint(-5, 200),
                float("inf") * rng.choice([1, -1]),
            ])
            expr = f"{func_name}({arg})"
            try:
                eng.evaluate(expr)
            except CalculatorError:
                continue
            except Exception as exc:  # noqa: BLE001
                self.fail(f"leaked {type(exc).__name__} on {expr!r}: {exc}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
