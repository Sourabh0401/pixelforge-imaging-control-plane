from __future__ import annotations

import pathlib
import sys
import unittest
from trace import Trace, _find_executable_linenos


ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))


def run() -> int:
    tracer = Trace(count=True, trace=False)

    def _run_suite():
        suite = unittest.defaultTestLoader.discover(str(TESTS))
        return unittest.TextTestRunner(verbosity=0).run(suite)

    result = tracer.runfunc(_run_suite)
    if not result.wasSuccessful():
        return 1
    counts = tracer.results().counts
    total_lines = 0
    hit_lines = 0
    for path in SRC.rglob("*.py"):
        # Use Python's executable line table instead of "all non-empty lines".
        # Large metadata modules in this repo contain many literal continuation
        # lines that are not independent executable statements and should not
        # count against the coverage gate.
        executable = set(_find_executable_linenos(str(path)).keys())
        executed = {line for (filename, line), count in counts.items() if pathlib.Path(filename) == path and count > 0}
        total_lines += len(executable)
        hit_lines += sum(1 for line in executable if line in executed)
    percent = round((hit_lines / total_lines * 100.0) if total_lines else 0.0, 2)
    print(f"coverage: {percent}%")
    return 0 if percent >= 80.0 else 2


if __name__ == "__main__":
    raise SystemExit(run())
