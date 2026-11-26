#!/usr/bin/env python3
"""Differential tests for lunsoc against lunso-boot."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
LUNSOC = ROOT / "build" / "lunsoc"
BOOT = ROOT.parent / "lunso-boot" / "build" / "lunso"


def main() -> int:
    samples = sorted((ROOT / "src").glob("*.lunso"))
    for sample in samples:
        for extra in ([], ["--parse"]):
            got = subprocess.run([str(LUNSOC), *extra, str(sample)], text=True, capture_output=True, check=False)
            exp = subprocess.run([str(BOOT), *extra, str(sample)], text=True, capture_output=True, check=False)
            if got.returncode != exp.returncode or got.stdout != exp.stdout:
                print(
                    f"mismatch on {sample.name} ({extra}): rc {got.returncode} vs {exp.returncode}\n"
                    f"got: {got.stdout!r}\nexp: {exp.stdout!r}\nstderr: {got.stderr}",
                    file=sys.stderr,
                )
                return 1
    boot_pass = sorted((ROOT.parent / "lunso-boot" / "tests" / "pass").glob("*.lunso"))
    for sample in boot_pass:
        for flag in ("--check", "--emit-ir"):
            got = subprocess.run([str(LUNSOC), flag, str(sample)], text=True, capture_output=True, check=False)
            exp = subprocess.run([str(BOOT), flag, str(sample)], text=True, capture_output=True, check=False)
            if got.returncode != exp.returncode or got.stdout != exp.stdout:
                print(
                    f"{flag} mismatch on {sample.name}: rc {got.returncode} vs {exp.returncode}\n"
                    f"got:\n{got.stdout}\nexp:\n{exp.stdout}\nstderr: {got.stderr}",
                    file=sys.stderr,
                )
                return 1

    print(f"OK ({len(samples) * 2} lexer+parser checks, {len(boot_pass) * 2} --check/--emit-ir checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
