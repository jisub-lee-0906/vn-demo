#!/usr/bin/env python3
"""Tiny stdlib test runner for this repo's documentation/script contract tests."""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "tests"


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    failures: list[str] = []
    test_files = sorted(TEST_DIR.glob("test_*.py"))
    if not test_files:
        print("No tests found")
        return 1

    total = 0
    for path in test_files:
        module = load_module(path)
        for name, fn in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            total += 1
            try:
                fn()
                print(f"PASS {path.name}::{name}")
            except Exception as exc:  # noqa: BLE001 - tiny runner reports any test failure.
                failures.append(f"FAIL {path.name}::{name}: {type(exc).__name__}: {exc}")
                print(failures[-1])

    print(f"\n{total - len(failures)} passed, {len(failures)} failed, {total} total")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
