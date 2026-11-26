#!/usr/bin/env python3
"""Differential tests for lunsoc against lunso-boot."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile

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
        for flag in ("--check", "--emit-ir", "--emit-qbe"):
            got = subprocess.run([str(LUNSOC), flag, str(sample)], text=True, capture_output=True, check=False)
            exp = subprocess.run([str(BOOT), flag, str(sample)], text=True, capture_output=True, check=False)
            if got.returncode != exp.returncode or got.stdout != exp.stdout:
                print(
                    f"{flag} mismatch on {sample.name}: rc {got.returncode} vs {exp.returncode}\n"
                    f"got:\n{got.stdout}\nexp:\n{exp.stdout}\nstderr: {got.stderr}",
                    file=sys.stderr,
                )
                return 1

    built_count = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        for sample in boot_pass:
            text = sample.read_text()
            first = text.splitlines()[0] if text else ""
            if not first.startswith("// expect-exit:"):
                continue
            expected_rc = int(first.split(":", 1)[1].strip())
            out_bin = Path(tmpdir) / sample.stem
            res = subprocess.run([str(LUNSOC), "--build", str(sample), "-o", str(out_bin)], text=True, capture_output=True, check=False)
            if res.returncode != 0:
                print(f"--build failed on {sample.name}: rc {res.returncode}\nstderr: {res.stderr}", file=sys.stderr)
                return 1
            run_res = subprocess.run([str(out_bin)], check=False)
            if run_res.returncode != expected_rc:
                print(f"runtime exit mismatch on {sample.name}: {run_res.returncode} vs {expected_rc}", file=sys.stderr)
                return 1
            built_count += 1

    print(f"OK ({len(samples) * 2} lexer+parser checks, {len(boot_pass) * 3} --check/--emit-ir/--emit-qbe checks, {built_count} --build+run checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
