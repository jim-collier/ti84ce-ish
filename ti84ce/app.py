"""
TI-84 CE+ style scientific calculator with a built-in Python environment.

Pure standard-library Tkinter GUI, so it runs unmodified on Linux, Windows
and macOS with no third-party dependencies.

Three modes, switched with the tabs across the top:

* CALC   - scientific calculator with a TI-style keypad and entry history.
* GRAPH  - plot up to three Y= functions on a Cartesian canvas.
* PYTHON - a small code editor + console that executes real Python.
"""

from __future__ import annotations

import contextlib
import io
import math
import platform
import threading
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from .engine import DEG, RAD, CalculatorError, Engine

# --- TI-84 CE inspired palette ---------------------------------------------
BG = "#1c2127"          # dark slate body
PANEL = "#2b313b"       # panel background
SCREEN_BG = "#c7d4b8"   # classic greenish LCD
SCREEN_FG = "#10140d"   # dark ink on the LCD
ACCENT = "#3b82f6"      # TI blue accent
NUM_BG = "#3a4150"      # number keys
FUNC_BG = "#2f3542"     # function keys
OP_BG = "#444c5e"       # operator keys
SECOND_FG = "#7dd3fc"   # cyan "2nd" labels
KEY_FG = "#f5f7fa"


class CalculatorFrame(ttk.Frame):
    """Scientific calculator: LCD-style screen plus a TI keypad."""

    def __init__(self, master: tk.Widget, engine: Engine) -> None:
        super().__init__(master, style="Body.TFrame")
        self.engine = engine
        self.second = False  # whether the "2nd" modifier is active
        self.expr = tk.StringVar(value="")
        self._build_screen()
        self._build_keypad()

    # -- screen --------------------------------------------------------------

    def _build_screen(self) -> None:
        screen = tk.Frame(self, bg=SCREEN_BG, bd=0, highlightthickness=2,
                          highlightbackground="#5a6b48")
        screen.pack(fill="x", padx=12, pady=(12, 8))

        self.history = tk.Text(screen, height=6, bg=SCREEN_BG, fg=SCREEN_FG,
                               bd=0, font=("Courier New", 13), state="disabled",
                               highlightthickness=0, wrap="word")
        self.history.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        self.entry = tk.Entry(screen, textvariable=self.expr, bg=SCREEN_BG,
                              fg=SCREEN_FG, bd=0, font=("Courier New", 20),
                              insertbackground=SCREEN_FG, justify="right",
                              highlightthickness=0)
        self.entry.pack(fill="x", padx=8, pady=(0, 8))
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self._equals())
        self.entry.bind("<KP_Enter>", lambda e: self._equals())

        status = tk.Frame(self, bg=BG)
        status.pack(fill="x", padx=12)
        self.mode_label = tk.Label(status, text=self.engine.angle_mode, bg=BG,
                                   fg=SECOND_FG, font=("Courier New", 10, "bold"))
        self.mode_label.pack(side="right")
        self.second_label = tk.Label(status, text="", bg=BG, fg=SECOND_FG,
                                     font=("Courier New", 10, "bold"))
        self.second_label.pack(side="left")

    # -- keypad --------------------------------------------------------------

    def _build_keypad(self) -> None:
        pad = ttk.Frame(self, style="Body.TFrame")
        pad.pack(fill="both", expand=True, padx=10, pady=10)

        # Each spec: (primary label, primary action, 2nd label, 2nd action, bg)
        # An action that is a str is inserted into the entry; a callable runs.
        rows = [
            [("2nd", self._toggle_second, None, None, FUNC_BG),
             (self._mode_text(), self._toggle_angle, None, None, FUNC_BG),
             ("DEL", self._delete, None, None, FUNC_BG),
             ("CLEAR", self._clear, "AC", self._all_clear, FUNC_BG),
             ("Ans", "Ans", None, None, FUNC_BG)],

            [("x²", "²", "x³", "³", FUNC_BG),
             ("x^y", "^", None, None, FUNC_BG),
             ("√", "√(", "∛", "cbrt(", FUNC_BG),
             ("x⁻¹", "⁻¹", None, None, FUNC_BG),
             ("n!", "factorial(", None, None, FUNC_BG)],

            [("sin", "sin(", "sin⁻¹", "asin(", FUNC_BG),
             ("cos", "cos(", "cos⁻¹", "acos(", FUNC_BG),
             ("tan", "tan(", "tan⁻¹", "atan(", FUNC_BG),
             ("π", "π", "τ", "tau", FUNC_BG),
             ("e", "e", "φ", "phi", FUNC_BG)],

            [("ln", "ln(", "eˣ", "exp(", FUNC_BG),
             ("log", "log(", "10ˣ", "10^", FUNC_BG),
             ("(", "(", None, None, FUNC_BG),
             (")", ")", None, None, FUNC_BG),
             (",", ",", None, None, FUNC_BG)],

            [("7", "7", None, None, NUM_BG),
             ("8", "8", None, None, NUM_BG),
             ("9", "9", None, None, NUM_BG),
             ("÷", "÷", "mod", "mod(", OP_BG),
             ("EE", "E", None, None, OP_BG)],

            [("4", "4", None, None, NUM_BG),
             ("5", "5", None, None, NUM_BG),
             ("6", "6", None, None, NUM_BG),
             ("×", "×", None, None, OP_BG),
             ("hyp", "hypot(", None, None, OP_BG)],

            [("1", "1", None, None, NUM_BG),
             ("2", "2", None, None, NUM_BG),
             ("3", "3", None, None, NUM_BG),
             ("−", "−", None, None, OP_BG),
             ("abs", "abs(", None, None, OP_BG)],

            [("0", "0", None, None, NUM_BG),
             (".", ".", None, None, NUM_BG),
             ("(-)", "-", None, None, NUM_BG),
             ("+", "+", None, None, OP_BG),
             ("=", self._equals, None, None, ACCENT)],
        ]

        for r, row in enumerate(rows):
            pad.rowconfigure(r, weight=1)
            for c, spec in enumerate(row):
                pad.columnconfigure(c, weight=1)
                self._make_key(pad, r, c, spec)

    def _make_key(self, parent, r, c, spec) -> None:
        label, action, second_label, second_action, bg = spec
        btn = tk.Button(parent, text=label, bg=bg, fg=KEY_FG, bd=0,
                        activebackground=ACCENT, activeforeground="white",
                        font=("Helvetica", 13, "bold"), relief="flat",
                        highlightthickness=0, cursor="hand2")
        btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3, ipady=6)
        btn._spec = spec  # stash for 2nd-mode relabeling
        btn.configure(command=lambda b=btn: self._press(b))

    def _press(self, btn: tk.Button) -> None:
        label, action, second_label, second_action, _ = btn._spec
        use_second = self.second and second_action is not None
        chosen = second_action if use_second else action
        # Toggling 2nd / angle should not itself be reset by _press.
        if callable(chosen):
            chosen()
        else:
            self._insert(chosen)
        # Any non-modifier key consumes the 2nd modifier.
        if chosen not in (self._toggle_second,) and self.second and action is not self._toggle_second:
            self._set_second(False)

    # -- entry editing -------------------------------------------------------

    def _insert(self, text: str) -> None:
        pos = self.entry.index(tk.INSERT)
        self.entry.insert(pos, text)
        self.entry.focus_set()

    def _delete(self) -> None:
        pos = self.entry.index(tk.INSERT)
        if pos > 0:
            self.entry.delete(pos - 1)
        self.entry.focus_set()

    def _clear(self) -> None:
        self.expr.set("")
        self.entry.focus_set()

    def _all_clear(self) -> None:
        self._clear()
        self.history.configure(state="normal")
        self.history.delete("1.0", "end")
        self.history.configure(state="disabled")

    # -- modifiers -----------------------------------------------------------

    def _toggle_second(self) -> None:
        self._set_second(not self.second)

    def _set_second(self, value: bool) -> None:
        self.second = value
        self.second_label.configure(text="2nd" if value else "")
        for child in self._iter_buttons():
            spec = getattr(child, "_spec", None)
            if not spec:
                continue
            label, _, second_label, second_action, _ = spec
            if value and second_label:
                child.configure(text=second_label, fg=SECOND_FG)
            else:
                child.configure(text=label, fg=KEY_FG)

    def _iter_buttons(self):
        for child in self.winfo_children():
            yield from self._walk(child)

    def _walk(self, widget):
        if isinstance(widget, tk.Button):
            yield widget
        for sub in widget.winfo_children():
            yield from self._walk(sub)

    def _mode_text(self) -> str:
        return self.engine.angle_mode

    def _toggle_angle(self) -> None:
        new = RAD if self.engine.angle_mode == DEG else DEG
        self.engine.set_angle_mode(new)
        self.mode_label.configure(text=new)
        for child in self._iter_buttons():
            spec = getattr(child, "_spec", None)
            if spec and spec[1] is self._toggle_angle:
                child.configure(text=new)

    # -- evaluation ----------------------------------------------------------

    def _equals(self) -> None:
        expression = self.expr.get().strip()
        if not expression:
            return
        try:
            result = self.engine.evaluate(expression)
        except CalculatorError as exc:
            self._append_history(expression, f"ERROR: {exc}")
            return
        self._append_history(expression, self._format(result))
        self.expr.set(self._format(result))
        self.entry.icursor("end")

    @staticmethod
    def _format(value: float) -> str:
        if isinstance(value, float):
            if value == int(value) and abs(value) < 1e16:
                return str(int(value))
            return f"{value:.10g}"
        return str(value)

    def _append_history(self, expression: str, result: str) -> None:
        self.history.configure(state="normal")
        self.history.insert("end", f"{expression}\n")
        self.history.insert("end", f"   = {result}\n")
        self.history.see("end")
        self.history.configure(state="disabled")


class GraphFrame(ttk.Frame):
    """Cartesian function plotter drawn directly on a Tk canvas."""

    COLORS = ["#1d4ed8", "#dc2626", "#059669"]

    def __init__(self, master: tk.Widget, engine: Engine) -> None:
        super().__init__(master, style="Body.TFrame")
        self.engine = engine
        self.func_vars = []
        self.win = {}
        self._build_controls()
        self._build_canvas()
        self.after(200, self.plot)

    def _build_controls(self) -> None:
        bar = ttk.Frame(self, style="Panel.TFrame")
        bar.pack(fill="x", padx=10, pady=(10, 4))

        funcs = ttk.Frame(bar, style="Panel.TFrame")
        funcs.pack(side="left", fill="x", expand=True)
        defaults = ["sin(X)", "", ""]
        for i in range(3):
            row = ttk.Frame(funcs, style="Panel.TFrame")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"Y{i+1}=", bg=PANEL, fg=self.COLORS[i],
                     font=("Courier New", 12, "bold"), width=4).pack(side="left")
            var = tk.StringVar(value=defaults[i])
            ent = tk.Entry(row, textvariable=var, bg=SCREEN_BG, fg=SCREEN_FG,
                           insertbackground=SCREEN_FG, font=("Courier New", 12),
                           width=24)
            ent.pack(side="left", fill="x", expand=True)
            ent.bind("<Return>", lambda e: self.plot())
            self.func_vars.append(var)

        window = ttk.Frame(bar, style="Panel.TFrame")
        window.pack(side="left", padx=(16, 0))
        for label, key, default in [("Xmin", "xmin", "-10"), ("Xmax", "xmax", "10"),
                                    ("Ymin", "ymin", "-10"), ("Ymax", "ymax", "10")]:
            row = ttk.Frame(window, style="Panel.TFrame")
            row.pack(fill="x", pady=1)
            tk.Label(row, text=label, bg=PANEL, fg=KEY_FG, width=5,
                     font=("Courier New", 10), anchor="w").pack(side="left")
            var = tk.StringVar(value=default)
            tk.Entry(row, textvariable=var, width=7, bg=SCREEN_BG, fg=SCREEN_FG,
                     font=("Courier New", 10)).pack(side="left")
            self.win[key] = var

        tk.Button(bar, text="GRAPH", bg=ACCENT, fg="white", bd=0,
                  font=("Helvetica", 12, "bold"), cursor="hand2",
                  activebackground="#2563eb", command=self.plot).pack(
            side="right", padx=8, ipadx=10, ipady=8)

    def _build_canvas(self) -> None:
        self.canvas = tk.Canvas(self, bg=SCREEN_BG, highlightthickness=2,
                                highlightbackground="#5a6b48")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", lambda e: self.plot())

    def _read_window(self):
        try:
            xmin = float(self.win["xmin"].get())
            xmax = float(self.win["xmax"].get())
            ymin = float(self.win["ymin"].get())
            ymax = float(self.win["ymax"].get())
        except ValueError:
            return None
        if xmax <= xmin or ymax <= ymin:
            return None
        return xmin, xmax, ymin, ymax

    def plot(self) -> None:
        self.canvas.delete("all")
        bounds = self._read_window()
        if not bounds:
            return
        xmin, xmax, ymin, ymax = bounds
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        def sx(x):
            return (x - xmin) / (xmax - xmin) * w

        def sy(y):
            return h - (y - ymin) / (ymax - ymin) * h

        self._draw_grid(w, h, xmin, xmax, ymin, ymax, sx, sy)

        for i, var in enumerate(self.func_vars):
            expr = var.get().strip()
            if not expr:
                continue
            self._plot_one(expr, self.COLORS[i], w, sx, sy, ymin, ymax)

    def _draw_grid(self, w, h, xmin, xmax, ymin, ymax, sx, sy) -> None:
        grid = "#a7b795"
        axis = "#3a4a2c"
        step_x = self._nice_step((xmax - xmin) / 10)
        step_y = self._nice_step((ymax - ymin) / 10)
        x = math.ceil(xmin / step_x) * step_x
        while x <= xmax:
            px = sx(x)
            self.canvas.create_line(px, 0, px, h, fill=grid)
            x += step_x
        y = math.ceil(ymin / step_y) * step_y
        while y <= ymax:
            py = sy(y)
            self.canvas.create_line(0, py, w, py, fill=grid)
            y += step_y
        if xmin <= 0 <= xmax:
            self.canvas.create_line(sx(0), 0, sx(0), h, fill=axis, width=2)
        if ymin <= 0 <= ymax:
            self.canvas.create_line(0, sy(0), w, sy(0), fill=axis, width=2)

    @staticmethod
    def _nice_step(raw: float) -> float:
        if raw <= 0:
            return 1.0
        mag = 10 ** math.floor(math.log10(raw))
        for mult in (1, 2, 5, 10):
            if raw <= mult * mag:
                return mult * mag
        return 10 * mag

    def _plot_one(self, expr, color, w, sx, sy, ymin, ymax) -> None:
        samples = max(200, int(w))
        bounds = self._read_window()
        xmin, xmax = bounds[0], bounds[1]
        prev = None
        segment = []
        for i in range(samples + 1):
            x = xmin + (xmax - xmin) * i / samples
            try:
                y = self.engine.eval_function(expr, x)
            except (CalculatorError, ValueError, ZeroDivisionError, OverflowError):
                y = None
            if y is None or not math.isfinite(y) or y < ymin - 1e6 or y > ymax + 1e6:
                if len(segment) > 1:
                    self.canvas.create_line(segment, fill=color, width=2, smooth=True)
                segment = []
                continue
            segment.extend((sx(x), sy(y)))
        if len(segment) > 2:
            self.canvas.create_line(segment, fill=color, width=2, smooth=True)


class PythonFrame(ttk.Frame):
    """A minimal editor + console that executes real Python code."""

    STARTER = (
        "# TI-84 CE+ Python environment\n"
        "# 'math' is already imported. print() shows in the console below.\n\n"
        "import math\n\n"
        "for n in range(1, 6):\n"
        "    print(n, math.factorial(n))\n\n"
        "print('sqrt(2) =', math.sqrt(2))\n"
    )

    def __init__(self, master: tk.Widget, engine: Engine) -> None:
        super().__init__(master, style="Body.TFrame")
        self.engine = engine
        self._build()

    def _build(self) -> None:
        toolbar = ttk.Frame(self, style="Panel.TFrame")
        toolbar.pack(fill="x", padx=10, pady=(10, 0))
        tk.Label(toolbar, text="PYTHON  editor.py", bg=PANEL, fg=KEY_FG,
                 font=("Courier New", 11, "bold")).pack(side="left", padx=6)
        tk.Button(toolbar, text="▶ RUN  (F5)", bg=ACCENT, fg="white", bd=0,
                  font=("Helvetica", 11, "bold"), cursor="hand2",
                  activebackground="#2563eb", command=self.run).pack(
            side="right", padx=4, ipadx=8, ipady=4)
        tk.Button(toolbar, text="Clear out", bg=FUNC_BG, fg=KEY_FG, bd=0,
                  font=("Helvetica", 11), cursor="hand2",
                  command=self.clear_output).pack(side="right", padx=4, ipadx=6, ipady=4)

        paned = ttk.Panedwindow(self, orient="vertical")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        self.editor = tk.Text(paned, bg="#0f1318", fg="#e6edf3", insertbackground="white",
                              font=("Courier New", 13), undo=True, wrap="none",
                              highlightthickness=0, bd=0)
        self.editor.insert("1.0", self.STARTER)
        paned.add(self.editor, weight=3)

        self.output = tk.Text(paned, bg="#05080b", fg="#8ef0a0", state="disabled",
                              font=("Courier New", 12), height=8, wrap="word",
                              highlightthickness=0, bd=0)
        paned.add(self.output, weight=2)

        self.editor.bind("<F5>", lambda e: (self.run(), "break"))
        self.editor.bind("<Control-Return>", lambda e: (self.run(), "break"))

    def clear_output(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def run(self) -> None:
        code = self.editor.get("1.0", "end")
        self.clear_output()
        self._write(">>> running...\n")
        thread = threading.Thread(target=self._execute, args=(code,), daemon=True)
        thread.start()

    def _execute(self, code: str) -> None:
        buffer = io.StringIO()
        env = {
            "__name__": "__main__",
            "math": math,
            "engine": self.engine,
        }
        try:
            compiled = compile(code, "<editor>", "exec")
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                exec(compiled, env)
        except Exception as exc:  # noqa: BLE001 - surface any user error to the console
            import traceback
            buffer.write("\n" + traceback.format_exc())
        text = buffer.getvalue()
        self.after(0, lambda: self._finish(text))

    def _finish(self, text: str) -> None:
        self.clear_output()
        self._write(text if text.strip() else "(no output)\n")

    def _write(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")


class TI84App(tk.Tk):
    """Top-level window hosting the three calculator modes."""

    def __init__(self) -> None:
        super().__init__()
        self.title("TI-84 CE+  ·  Scientific + Python")
        self.geometry("560x760")
        self.minsize(480, 640)
        self.configure(bg=BG)
        # The real TI-84 Plus CE ships in RADIAN mode by default.
        self.engine = Engine(angle_mode=RAD)
        self._configure_style()
        self._build()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        with contextlib.suppress(tk.TclError):
            style.theme_use("clam")
        style.configure("Body.TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)

    def _build(self) -> None:
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(header, text="TI-84 CE+", bg=BG, fg=ACCENT,
                 font=("Helvetica", 18, "bold")).pack(side="left")
        tk.Label(header, text="Scientific · Graphing · Python",
                 bg=BG, fg="#8b94a3", font=("Helvetica", 10)).pack(side="left", padx=10)

        # Custom tab bar. ttk.Notebook's themed tabs render the *selected* tab a
        # different size from the others (the clam theme shrinks it), so we build
        # the tab bar from plain flat buttons that expand to identical widths and
        # never overlap -- the same button style used by the keypad.
        tabbar = tk.Frame(self, bg=BG)
        tabbar.pack(fill="x", padx=8, pady=(8, 0))

        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=8, pady=8)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self._tab_buttons = []
        self._tab_frames = []
        specs = [("CALC", CalculatorFrame), ("GRAPH", GraphFrame), ("PYTHON", PythonFrame)]
        for i, (name, cls) in enumerate(specs):
            frame = cls(container, self.engine)
            frame.grid(row=0, column=0, sticky="nsew")  # stacked; raised on select
            self._tab_frames.append(frame)
            btn = tk.Button(tabbar, text=name, bg=FUNC_BG, fg=KEY_FG, bd=0,
                            font=("Helvetica", 12, "bold"), relief="flat",
                            activebackground=ACCENT, activeforeground="white",
                            cursor="hand2",
                            command=lambda idx=i: self._select_tab(idx))
            btn.pack(side="left", expand=True, fill="both",
                     padx=(0 if i == 0 else 2, 0), ipady=10)
            self._tab_buttons.append(btn)
        self._select_tab(0)

        footer = tk.Label(self, text=f"Python {platform.python_version()} · {platform.system()}",
                          bg=BG, fg="#5b6472", font=("Helvetica", 9))
        footer.pack(side="bottom", pady=(0, 4))

    def _select_tab(self, index: int) -> None:
        for i, (btn, frame) in enumerate(zip(self._tab_buttons, self._tab_frames)):
            active = i == index
            btn.configure(bg=ACCENT if active else FUNC_BG,
                          fg="white" if active else KEY_FG)
            if active:
                frame.tkraise()


def main() -> None:
    app = TI84App()
    app.mainloop()


if __name__ == "__main__":
    main()
