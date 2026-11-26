#!/usr/bin/env python3
"""Differential and unit tests for lunsoc."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
LUNSOC = ROOT / "build" / "lunsoc"
BOOT = ROOT.parent / "lunso-boot" / "build" / "lunso"


def main() -> int:
    samples = [
        ROOT / "src" / "lexer.lunso",
        ROOT / "src" / "main.lunso",
    ]
    for sample in samples:
        got = subprocess.run([str(LUNSOC), str(sample)], text=True, capture_output=True, check=False)
        exp = subprocess.run([str(BOOT), str(sample)], text=True, capture_output=True, check=False)
        if got.returncode != exp.returncode or got.stdout != exp.stdout:
            print(f"mismatch on {sample.name}: rc {got.returncode} vs {exp.returncode}", file=sys.stderr)
            return 1
    print(f"OK ({len(samples)} differential lexer checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
