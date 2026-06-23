"""
Safe scientific-expression evaluation engine for the TI-84 CE+ emulator.

The engine never calls Python's built-in ``eval`` on user text directly.
Instead the expression is parsed into an AST and only a whitelisted set of
node types, function names and constants are permitted.  This keeps the
"calculator" surface area safe even though the separate Python-programming
mode deliberately runs arbitrary code.
"""

from __future__ import annotations

import ast
import math
import operator
from typing import Any, Callable, Dict


class CalculatorError(Exception):
    """Raised for any user-facing evaluation problem (bad syntax, math domain)."""


# --- angle handling ---------------------------------------------------------

DEG = "DEG"
RAD = "RAD"


class Engine:
    """Stateful scientific calculator engine.

    Holds the angle mode (degrees/radians), the last answer (``Ans``) and the
    A-Z memory registers that the TI-84 exposes.
    """

    # Binary operators that the AST evaluator understands.
    _BIN_OPS: Dict[type, Callable[[Any, Any], Any]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    _UNARY_OPS: Dict[type, Callable[[Any], Any]] = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def __init__(self, angle_mode: str = DEG) -> None:
        self.angle_mode = angle_mode
        self.ans: float = 0.0
        self.memory: Dict[str, float] = {chr(c): 0.0 for c in range(ord("A"), ord("Z") + 1)}
        self._functions = self._build_functions()
        self._constants = self._build_constants()

    # -- public API ----------------------------------------------------------

    def set_angle_mode(self, mode: str) -> None:
        if mode not in (DEG, RAD):
            raise ValueError(f"Unknown angle mode: {mode!r}")
        self.angle_mode = mode

    def evaluate(self, expression: str) -> float:
        """Evaluate a calculator expression and update ``Ans``."""
        result = self.eval_no_store(expression)
        self.ans = result
        return result

    def eval_no_store(self, expression: str) -> float:
        """Evaluate without updating ``Ans`` (used for graphing many points)."""
        expression = self._normalize(expression)
        if not expression.strip():
            raise CalculatorError("Empty expression")
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise CalculatorError("Syntax error") from exc
        try:
            value = self._eval_node(tree.body)
        except CalculatorError:
            raise
        except ZeroDivisionError as exc:
            raise CalculatorError("Divide by 0") from exc
        except (ValueError, OverflowError) as exc:
            raise CalculatorError(f"Math error: {exc}") from exc
        return value

    def eval_function(self, expression: str, x: float) -> float:
        """Evaluate ``expression`` treating the name ``X`` (or ``x``) as ``x``."""
        old = self.memory.get("X", 0.0)
        try:
            self.memory["X"] = x
            return self.eval_no_store(expression)
        finally:
            self.memory["X"] = old

    # -- expression normalisation -------------------------------------------

    @staticmethod
    def _normalize(expression: str) -> str:
        """Translate calculator glyphs into Python-parseable syntax."""
        replacements = {
            "×": "*",   # ×
            "÷": "/",   # ÷
            "−": "-",   # − (unicode minus)
            "π": "pi",  # π
            "τ": "tau",  # τ
            "φ": "phi",  # φ
            "√": "sqrt",  # √ -> sqrt (expects following parens)
            "^": "**",
            "²": "**2",  # ²
            "³": "**3",  # ³
            "⁻¹": "**-1",  # ⁻¹
            "E": "e_const_marker",  # protect scientific E handled below
        }
        text = expression
        # Handle scientific notation "1.2E3" before generic E replacement.
        text = text.replace("e_const_marker", "E")
        for src, dst in replacements.items():
            if src == "E":
                continue
            text = text.replace(src, dst)
        return text

    # -- AST evaluation ------------------------------------------------------

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise CalculatorError("Invalid constant")
        if isinstance(node, ast.BinOp):
            op = self._BIN_OPS.get(type(node.op))
            if op is None:
                raise CalculatorError("Unsupported operator")
            return op(self._eval_node(node.left), self._eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            op = self._UNARY_OPS.get(type(node.op))
            if op is None:
                raise CalculatorError("Unsupported unary operator")
            return op(self._eval_node(node.operand))
        if isinstance(node, ast.Name):
            return self._resolve_name(node.id)
        if isinstance(node, ast.Call):
            return self._eval_call(node)
        raise CalculatorError("Unsupported expression element")

    def _resolve_name(self, name: str) -> float:
        if name in self._constants:
            return self._constants[name]
        if name == "Ans":
            return self.ans
        upper = name.upper()
        if upper in self.memory:
            return self.memory[upper]
        raise CalculatorError(f"Unknown name: {name}")

    def _eval_call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise CalculatorError("Invalid function call")
        fname = node.func.id
        func = self._functions.get(fname)
        if func is None:
            raise CalculatorError(f"Unknown function: {fname}")
        args = [self._eval_node(a) for a in node.args]
        return func(*args)

    # -- function / constant tables -----------------------------------------

    def _to_radians(self, x: float) -> float:
        return math.radians(x) if self.angle_mode == DEG else x

    def _from_radians(self, x: float) -> float:
        return math.degrees(x) if self.angle_mode == DEG else x

    def _build_functions(self) -> Dict[str, Callable[..., float]]:
        def safe_log(x: float, base: float = 10.0) -> float:
            return math.log(x, base)

        return {
            # Trigonometry (respect angle mode).
            "sin": lambda x: math.sin(self._to_radians(x)),
            "cos": lambda x: math.cos(self._to_radians(x)),
            "tan": lambda x: math.tan(self._to_radians(x)),
            "asin": lambda x: self._from_radians(math.asin(x)),
            "acos": lambda x: self._from_radians(math.acos(x)),
            "atan": lambda x: self._from_radians(math.atan(x)),
            "atan2": lambda y, x: self._from_radians(math.atan2(y, x)),
            # Hyperbolic.
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "asinh": math.asinh,
            "acosh": math.acosh,
            "atanh": math.atanh,
            # Logs / exponentials.
            "ln": math.log,
            "log": safe_log,
            "exp": math.exp,
            # Powers and roots.
            "sqrt": math.sqrt,
            "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
            "pow": math.pow,
            "nroot": lambda n, x: math.copysign(abs(x) ** (1 / n), x),
            # Misc.
            "abs": abs,
            "fabs": math.fabs,
            "floor": math.floor,
            "ceil": math.ceil,
            "round": round,
            "trunc": math.trunc,
            "factorial": lambda x: float(math.factorial(int(x))),
            "gcd": lambda a, b: float(math.gcd(int(a), int(b))),
            "mod": math.fmod,
            "sign": lambda x: float((x > 0) - (x < 0)),
            "max": max,
            "min": min,
            "deg": math.degrees,
            "rad": math.radians,
            "hypot": math.hypot,
        }

    def _build_constants(self) -> Dict[str, float]:
        return {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "phi": (1 + math.sqrt(5)) / 2,
        }
