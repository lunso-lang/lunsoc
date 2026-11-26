#!/usr/bin/env python3
"""Tests for lunsoc (with optional differential checks against LUNSO_BOOT)."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
LUNSOC = ROOT / "build" / "lunsoc"


def find_boot() -> Path | None:
    env = os.environ.get("LUNSO_BOOT")
    if env:
        p = Path(env)
        return p if p.is_file() else None
    default = ROOT.parent / "lunso-boot" / "build" / "lunso"
    return default if default.is_file() else None


def find_pass_samples() -> list[Path]:
    local_pass = ROOT / "tests" / "pass"
    if local_pass.is_dir():
        return sorted(local_pass.glob("*.lunso"))
    boot_pass = ROOT.parent / "lunso-boot" / "tests" / "pass"
    if boot_pass.is_dir():
        return sorted(boot_pass.glob("*.lunso"))
    return []


def main() -> int:
    boot = find_boot()
    samples = sorted((ROOT / "src").glob("*.lunso"))
    diff_count = 0

    if boot is not None:
        for sample in samples:
            for extra in ([], ["--parse"]):
                got = subprocess.run([str(LUNSOC), *extra, str(sample)], text=True, capture_output=True, check=False)
                exp = subprocess.run([str(boot), *extra, str(sample)], text=True, capture_output=True, check=False)
                if got.returncode != exp.returncode or got.stdout != exp.stdout:
                    print(
                        f"mismatch on {sample.name} ({extra}): rc {got.returncode} vs {exp.returncode}\n"
                        f"got: {got.stdout!r}\nexp: {exp.stdout!r}\nstderr: {got.stderr}",
                        file=sys.stderr,
                    )
                    return 1
                diff_count += 1

    pass_samples = find_pass_samples()
    if boot is not None:
        for sample in pass_samples:
            for flag in ("--check", "--emit-ir", "--emit-qbe"):
                got = subprocess.run([str(LUNSOC), flag, str(sample)], text=True, capture_output=True, check=False)
                exp = subprocess.run([str(boot), flag, str(sample)], text=True, capture_output=True, check=False)
                if got.returncode != exp.returncode or got.stdout != exp.stdout:
                    print(
                        f"{flag} mismatch on {sample.name}: rc {got.returncode} vs {exp.returncode}\n"
                        f"got:\n{got.stdout}\nexp:\n{exp.stdout}\nstderr: {got.stderr}",
                        file=sys.stderr,
                    )
                    return 1
                diff_count += 1

    built_count = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        for sample in pass_samples:
            text = sample.read_text()
            first = text.splitlines()[0] if text else ""
            if not first.startswith("// expect-exit:"):
                continue
            expected_rc = int(first.split(":", 1)[1].strip())
            out_bin = Path(tmpdir) / sample.stem
            res = subprocess.run([str(LUNSOC), "--build", str(sample), "-o", str(out_bin)], cwd=ROOT, text=True, capture_output=True, check=False)
            if res.returncode != 0:
                print(f"--build failed on {sample.name}: rc {res.returncode}\nstderr: {res.stderr}", file=sys.stderr)
                return 1
            run_res = subprocess.run([str(out_bin)], check=False)
            if run_res.returncode != expected_rc:
                print(f"runtime exit mismatch on {sample.name}: {run_res.returncode} vs {expected_rc}", file=sys.stderr)
                return 1
            built_count += 1

        stage2 = Path(tmpdir) / "lunsoc-stage2"
        stage3 = Path(tmpdir) / "lunsoc-stage3"
        src_main = ROOT / "src" / "main.lunso"
        s2_build = subprocess.run([str(LUNSOC), "--build", str(src_main), "-o", str(stage2)], cwd=ROOT, text=True, capture_output=True, check=False)
        if s2_build.returncode != 0:
            print(f"self-host stage2 build failed: {s2_build.stderr}", file=sys.stderr)
            return 1
        s3_build = subprocess.run([str(stage2), "--build", str(src_main), "-o", str(stage3)], cwd=ROOT, text=True, capture_output=True, check=False)
        if s3_build.returncode != 0:
            print(f"self-host stage3 build failed: {s3_build.stderr}", file=sys.stderr)
            return 1
        q1 = subprocess.run([str(LUNSOC), "--emit-qbe", str(src_main)], cwd=ROOT, capture_output=True, check=False)
        q2 = subprocess.run([str(stage2), "--emit-qbe", str(src_main)], cwd=ROOT, capture_output=True, check=False)
        q3 = subprocess.run([str(stage3), "--emit-qbe", str(src_main)], cwd=ROOT, capture_output=True, check=False)
        if q1.returncode != 0 or q2.returncode != 0 or q3.returncode != 0 or q1.stdout != q2.stdout or q2.stdout != q3.stdout:
            print("self-host QBE IL mismatch between stage1/stage2/stage3", file=sys.stderr)
            return 1

        ver = subprocess.run([str(stage2), "--version"], text=True, capture_output=True, check=False)
        hlp = subprocess.run([str(stage2), "--help"], text=True, capture_output=True, check=False)
        if ver.returncode != 0 or "lunsoc " not in ver.stdout or hlp.returncode != 0 or "--run" not in hlp.stdout:
            print("CLI --version / --help check failed", file=sys.stderr)
            return 1
        hello = Path(tmpdir) / "hello_run.lunso"
        hello.write_text("fun main(): i32 { return 42 }\n")
        run_res = subprocess.run([str(stage2), "--run", str(hello), "--", "arg1"], cwd=ROOT, check=False)
        if run_res.returncode != 42:
            print(f"CLI --run check failed: {run_res.returncode} vs 42", file=sys.stderr)
            return 1

    print(f"OK ({diff_count} differential checks, {built_count} --build+run checks, self-host 3-stage + CLI OK)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
