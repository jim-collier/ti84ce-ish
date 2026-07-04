"""Security tests for the CALC engine whitelist.

CALC mode must never execute anything outside its whitelist of numeric
operators, math functions and constants. Everything below is either a known
sandbox-escape shape or a language feature the calculator has no business
running; each must come back as a CalculatorError, not a value and not a raw
Python exception.

(PYTHON mode deliberately runs arbitrary code and is out of scope here.)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ti84ce.engine import CalculatorError, Engine  # noqa: E402


class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.eng = Engine()

    def assertRejected(self, expr):
        with self.assertRaises(CalculatorError, msg=f"should reject: {expr!r}"):
            self.eng.evaluate(expr)

    def test_dunder_and_attribute_escapes(self):
        for bad in [
            "().__class__",
            "().__class__.__bases__[0].__subclasses__()",
            "(1).real",
            "(1.0).__add__(2)",
            "''.join",
            "().__class__.__mro__",
        ]:
            self.assertRejected(bad)

    def test_builtin_calls(self):
        for bad in [
            "__import__('os')",
            "open('/etc/passwd')",
            "eval('1+1')",
            "exec('x=1')",
            "compile('1', '', 'eval')",
            "getattr(1, 'real')",
            "globals()",
            "locals()",
            "vars()",
            "dir()",
            "input()",
            "print(1)",
            "exit()",
            "help()",
            "id(1)",
            "type(1)",
            "object()",
            "breakpoint()",
        ]:
            self.assertRejected(bad)

    def test_containers_and_subscripts(self):
        for bad in [
            "[1, 2, 3]",
            "(1, 2)",
            "{1, 2}",
            "{'a': 1}",
            "[1, 2][0]",
            "'abc'[0]",
            "{}['x']",
        ]:
            self.assertRejected(bad)

    def test_comprehensions_and_generators(self):
        for bad in [
            "[x for x in range(3)]",
            "{x for x in range(3)}",
            "{x: x for x in range(3)}",
            "(x for x in range(3))",
            "sum([x for x in range(3)])",
        ]:
            self.assertRejected(bad)

    def test_lambda_and_control_flow(self):
        for bad in [
            "lambda: 1",
            "(lambda x: x)(1)",
            "1 if 2 else 3",
            "1 and 2",
            "1 or 0",
            "not 1",
            "1 < 2",
            "1 == 1",
        ]:
            self.assertRejected(bad)

    def test_non_numeric_literals(self):
        for bad in [
            "'hello'",
            'b"bytes"',
            "True",
            "False",
            "None",
            "f'{1}'",
            "...",
        ]:
            self.assertRejected(bad)

    def test_statements_and_assignment(self):
        # eval mode already forbids statements; make sure they never slip through.
        for bad in [
            "x = 5",
            "import os",
            "(x := 5)",
            "del y",
            "1; 2",
        ]:
            self.assertRejected(bad)

    def test_unknown_names_and_functions(self):
        for bad in [
            "os",
            "sys",
            "system('id')",
            "unknownfunc(2)",
            "sqrt",  # bare function name (no call) is not a value
        ]:
            self.assertRejected(bad)

    def test_whitelisted_still_works(self):
        # Guard against an over-eager lockdown breaking legitimate math.
        self.assertAlmostEqual(self.eng.evaluate("sqrt(2)"), 2 ** 0.5)
        self.assertAlmostEqual(self.eng.evaluate("factorial(5)"), 120)
        self.assertAlmostEqual(self.eng.evaluate("2 + 3 * 4"), 14)
        self.assertAlmostEqual(self.eng.evaluate("pi"), 3.141592653589793)


if __name__ == "__main__":
    unittest.main(verbosity=2)
