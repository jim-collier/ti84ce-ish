#!/usr/bin/env python3
"""Drive the calculator into a few representative states and grab each window.

Meant to run on a headless X display (see screenshots.bash). Writes full-size
PNGs into the directory given as the first argument. Content is generic on
purpose -- plain math, no names or paths -- so the gallery is shareable.

Capture is done by window id via ImageMagick's `import`, which grabs exactly
the app window (no window manager, no decorations, no desktop bleed).
"""

import contextlib
import io
import math
import os
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))  # the github/ source dir
sys.path.insert(0, SRC)

from ti84ce.app import TI84App  # noqa: E402
from ti84ce.engine import DEG, RAD  # noqa: E402


def pump(app, seconds=0.35):
    """Let Tk lay out and render, without a real mainloop."""
    end = time.time() + seconds
    while time.time() < end:
        app.update_idletasks()
        app.update()
        time.sleep(0.02)


def grab(app, path):
    app.update_idletasks()
    app.update()
    pump(app, 0.3)
    wid = app.winfo_id()
    subprocess.run(["import", "-window", str(wid), path], check=True)


def scene_calc_history(app, calc):
    app._select_tab(0)
    if calc.engine.angle_mode == RAD:
        calc._toggle_angle()  # DEG reads nicer for a demo (sin(30) = 0.5)
    calc._all_clear()
    for expr in ["sin(30)", "log(1000)", "5*factorial(4)", "sqrt(2)+1"]:
        calc.expr.set(expr)
        calc._equals()
    calc.expr.set("2^10")  # a pending entry, not yet evaluated
    calc.entry.icursor("end")


def scene_graph_trig(app, graph):
    app._select_tab(1)
    graph.engine.set_angle_mode(RAD)  # waves, not near-flat degree curves
    labels = ["sin(X)", "cos(X)", "X/3"]
    for var, text in zip(graph.func_vars, labels):
        var.set(text)
    pump(app, 0.3)   # give the canvas a real size first
    graph.plot()


def scene_python_run(app, py):
    app._select_tab(2)
    # The app runs code on a worker thread; without a real mainloop its after()
    # callback can't post back. For a static capture, run it inline and fill the
    # console directly with the same result the user would see.
    code = py.editor.get("1.0", "end")
    buf = io.StringIO()
    env = {"__name__": "__main__", "math": math, "engine": py.engine}
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            exec(compile(code, "<editor>", "exec"), env)
    except Exception:  # noqa: BLE001 - surface user errors just like the app
        buf.write("\n" + traceback.format_exc())
    py.clear_output()
    py._write(buf.getvalue() or "(no output)\n")


def scene_calc_second(app, calc):
    app._select_tab(0)
    calc._set_second(True)  # cyan 2nd-function keypad labels
    calc.expr.set("asin(0.5)")
    calc.entry.icursor("end")


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out_dir, exist_ok=True)

    app = TI84App()
    app.geometry("560x760+0+0")
    app.update_idletasks()
    app.update()

    calc, graph, py = app._tab_frames

    shots = [
        ("01-calc", lambda: scene_calc_history(app, calc)),
        ("02-graph", lambda: scene_graph_trig(app, graph)),
        ("03-python", lambda: scene_python_run(app, py)),
        ("04-calc-2nd", lambda: scene_calc_second(app, calc)),
    ]

    written = []
    for name, setup in shots:
        setup()
        path = os.path.join(out_dir, f"{name}.png")
        grab(app, path)
        written.append(path)
        print(path)

    app.destroy()
    return 0 if len(written) == len(shots) else 1


if __name__ == "__main__":
    raise SystemExit(main())
