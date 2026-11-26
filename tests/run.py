#!/usr/bin/env python3
"""Test runner for lunsoc (pass, fail, generics, modules, std, self-host, CLI)."""

from __future__ import annotations

import os
from pathlib import Path
import shlex
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


def parse_directives(path: Path) -> dict[str, str]:
    directives: dict[str, str] = {}
    for line in path.read_text().splitlines():
        if not line.startswith("//"):
            break
        body = line[2:].strip()
        if ":" in body:
            k, v = body.split(":", 1)
            directives[k.strip()] = v.strip()
    return directives


def collect_run_tests() -> list[Path]:
    files: list[Path] = []
    files.extend(sorted((ROOT / "tests" / "pass").glob("*.lunso")))
    for sub in ("generics", "modules"):
        entry = ROOT / "tests" / sub / "main.lunso"
        if entry.is_file():
            files.append(entry)
    files.extend(sorted((ROOT / "tests" / "std").glob("*.lunso")))
    return files


def main() -> int:
    boot = find_boot()
    diff_count = 0

    pass_files = sorted((ROOT / "tests" / "pass").glob("*.lunso"))
    if boot is not None:
        for sample in pass_files:
            if "// lunsoc-only" in sample.read_text():
                continue
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
        for idx, sample in enumerate(collect_run_tests()):
            dirs = parse_directives(sample)
            if "expect-exit" not in dirs and "expect-stdout" not in dirs:
                continue
            expected_rc = int(dirs.get("expect-exit", "0"))
            out_bin = Path(tmpdir) / f"test_{idx}_{sample.stem}"
            res = subprocess.run([str(LUNSOC), "--build", str(sample), "-o", str(out_bin)], cwd=ROOT, text=True, capture_output=True, check=False)
            if res.returncode != 0:
                print(f"--build failed on {sample}: rc {res.returncode}\nstderr: {res.stderr}", file=sys.stderr)
                return 1
            extra_args = shlex.split(dirs["args"]) if "args" in dirs else []
            run_res = subprocess.run([str(out_bin), *extra_args], cwd=tmpdir, text=True, capture_output=True, check=False)
            if run_res.returncode != expected_rc:
                print(f"runtime exit mismatch on {sample}: {run_res.returncode} vs {expected_rc}", file=sys.stderr)
                return 1
            if "expect-stdout" in dirs:
                expected_out = dirs["expect-stdout"].replace("\\n", "\n")
                if run_res.stdout != expected_out:
                    print(f"runtime stdout mismatch on {sample}: {run_res.stdout!r} vs {expected_out!r}", file=sys.stderr)
                    return 1
            built_count += 1

        fail_files = sorted((ROOT / "tests" / "fail").glob("*.lunso"))
        fail_count = 0
        for sample in fail_files:
            dirs = parse_directives(sample)
            mode = dirs.get("mode", "check")
            flags = [] if mode == "tokens" else ["--parse"] if mode == "parse" else ["--check"]
            res = subprocess.run([str(LUNSOC), *flags, str(sample)], cwd=ROOT, text=True, capture_output=True, check=False)
            if res.returncode == 0:
                print(f"expected failure on {sample.name}, got rc 0", file=sys.stderr)
                return 1
            exp_err = dirs.get("expect-stderr", "")
            if exp_err and exp_err not in res.stderr:
                print(f"stderr mismatch on {sample.name}: expected {exp_err!r}, got:\n{res.stderr}", file=sys.stderr)
                return 1
            fail_count += 1

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
        cli_run_file = ROOT / "tests" / "pass" / "cli_run.lunso"
        run_res = subprocess.run([str(stage2), "--run", str(cli_run_file), "--", "arg1"], cwd=ROOT, check=False)
        if run_res.returncode != 42:
            print(f"CLI --run check failed: {run_res.returncode} vs 42", file=sys.stderr)
            return 1

    print(
        f"OK ({diff_count} differential checks, {built_count} --build+run checks, "
        f"{fail_count} negative checks, self-host 3-stage + CLI OK)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
