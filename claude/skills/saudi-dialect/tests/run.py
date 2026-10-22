#!/usr/bin/env python3
"""Regression tests for check_egyptian.py.

should_flag.txt : every line must raise at least one ERROR (recall)
should_pass.txt : no line may raise any ERROR (precision)

Usage:
    python3 tests/run.py

Exit code 1 if any case fails. Add a line to the matching file whenever you
find a leak the checker missed, or a correct word it wrongly rejected.
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
CHECKER = HERE.parent / "scripts" / "check_egyptian.py"


def errors_for(line):
    r = subprocess.run(
        [sys.executable, str(CHECKER)],
        input=line, capture_output=True, text=True,
    )
    return [l for l in r.stdout.splitlines() if ": ERROR: " in l]


def lines_of(name):
    for raw in (HERE / name).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            yield line


def check(name, want_errors):
    passed = failed = 0
    for line in lines_of(name):
        errs = errors_for(line)
        if bool(errs) == want_errors:
            passed += 1
        else:
            failed += 1
            if want_errors:
                print(f"MISS  {line}\n      no ERROR raised, but this line is Egyptian")
            else:
                print(f"FALSE {line}")
                for e in errs:
                    print(f"      {e.split(': ', 1)[1]}")
    label = "recall " if want_errors else "precision"
    print(f"{label}: {passed} passed, {failed} failed  ({name})")
    return failed


def main():
    failed = check("should_flag.txt", True)
    print()
    failed += check("should_pass.txt", False)
    print()
    if failed:
        print(f"❌ {failed} case(s) failed.")
    else:
        print("✅ All cases passed.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
