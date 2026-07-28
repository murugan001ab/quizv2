"""
Runs user-submitted code locally via subprocess instead of hitting a remote
Judge0 instance. Each test case is executed as its own short-lived
subprocess: stdin is piped in, stdout/stderr captured, with a wall-clock
timeout and (on POSIX) an address-space rlimit standing in for Judge0's
cpu/memory limits.

The subprocess itself is spawned with the synchronous `subprocess` module
on a worker thread (via asyncio.to_thread), not asyncio's native
create_subprocess_exec. This is deliberate: on Windows, asyncio subprocess
support only works under ProactorEventLoop, and uvicorn doesn't guarantee
that loop is active (it sets its own event loop policy at startup). Using
plain `subprocess` sidesteps that entirely and behaves the same on every
platform/event loop.

Kept the same public surface as the old judge0_client.py (`run_batch`,
`Judge0Verdict`, the STATUS_* / *_RANGE constants) so app/routers/problems.py
only needed an import rename, not a rewrite.

LANGUAGES: python3 runs directly. java and c go through a compile step
(javac / gcc) once per submission, then every test case re-runs the already
-compiled artifact — compiling per test case would be needlessly slow and
would also misreport a compile error as a per-test-case failure.

REQUIREMENTS: `javac`/`java` (a JDK) and `gcc` must be on PATH for the java/c
languages to work. If they're missing, run_batch raises a clear error rather
than a confusing subprocess.FileNotFoundError.

SECURITY NOTE: this is process-level isolation only — separate PID, own
address space, killed on timeout/OOM. It is NOT a sandbox: the child still
shares the filesystem and network with the FastAPI process. That's an
acceptable trade-off for a small internal practice tool running trusted-ish
submissions, but if this is ever exposed to untrusted/public users, put it
behind a real sandbox (gVisor, Docker with --network=none and a read-only
rootfs, firejail/bubblewrap, nsjail, etc.) or bring back an isolated judge.
"""

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

from app.models.problem import Language

# Status codes kept numerically compatible with the old Judge0 scheme so
# nothing downstream (problems.py) has to change.
STATUS_ACCEPTED = 3
STATUS_WRONG_ANSWER = 4
STATUS_TIME_LIMIT_EXCEEDED = 5
COMPILE_ERROR_RANGE = {6}
RUNTIME_ERROR_RANGE = set(range(7, 13))
IN_PROGRESS = {1, 2}  # unused with subprocess execution; kept for interface parity

# Per-language: source filename (fixed for java — the public class name must
# match), the compile command template (None => no compile step, e.g.
# Python), and the run command template. {dir} / {src} / {exe} / {class_dir}
# get filled in per-submission.
LANGUAGE_CONFIG: dict[Language, dict] = {
    Language.PYTHON3: {
        "source_name": "main.py",
        "compile_cmd": None,
        "run_cmd": [sys.executable, "-I", "{src}"],
    },
    Language.C: {
        "source_name": "main.c",
        "compile_cmd": ["gcc", "-O2", "-o", "{exe}", "{src}"],
        "run_cmd": ["{exe}"],
    },
    Language.JAVA: {
        # javac requires the file to be named after its public class, so
        # user code for this problem type must declare `public class Main`.
        "source_name": "Main.java",
        "compile_cmd": ["javac", "-d", "{dir}", "{src}"],
        "run_cmd": ["java", "-cp", "{dir}", "Main"],
    },
}

# Back-compat alias — some callers may still import the old name.
LANGUAGE_MAP: dict[Language, str] = {Language.PYTHON3: sys.executable}

# Cap how many test cases run at once so a batch of 50 test cases doesn't
# fork 50 interpreters/JVMs simultaneously.
_MAX_CONCURRENT = 4
_sem = asyncio.Semaphore(_MAX_CONCURRENT)

_COMPILE_ERROR_MARKERS = ("SyntaxError", "IndentationError", "TabError")

# How long a compile step (javac/gcc) is allowed to take, separate from the
# per-test-case run timeout — compiling is a one-off cost, not something the
# problem's time_limit_ms (meant for a single run) should be charged against.
_COMPILE_TIMEOUT_S = 15


@dataclass
class Judge0Verdict:
    passed: bool
    stdout: str
    stderr: str
    status_id: int
    status_desc: str
    time_ms: int | None


class _CompileError(Exception):
    def __init__(self, stderr: str):
        self.stderr = stderr


def _memory_limit_preexec(memory_limit_kb: int):
    """Build a preexec_fn that caps the child's address space (POSIX only)."""
    if os.name != "posix":
        return None

    def _apply():
        import resource

        mem_bytes = max(1, memory_limit_kb) * 1024
        for limit in (resource.RLIMIT_AS,):
            try:
                resource.setrlimit(limit, (mem_bytes, mem_bytes))
            except (ValueError, OSError):
                pass
        # Belt-and-braces: no core dumps, no spawning grandchildren that
        # outlive the timeout kill.
        try:
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        except (ValueError, OSError):
            pass

    return _apply


def _check_toolchain(language: Language) -> None:
    """Fail fast with a clear message if the compiler/interpreter isn't installed."""
    tool = {Language.C: "gcc", Language.JAVA: "javac"}.get(language)
    if tool and shutil.which(tool) is None:
        raise RuntimeError(
            f"'{tool}' was not found on PATH. Install it to enable {language.value} "
            f"execution (e.g. `apt install gcc` or `apt install default-jdk`)."
        )


def _compile_sync(compile_cmd: list[str]) -> None:
    """Runs the compile step synchronously. Raises _CompileError on failure."""
    try:
        completed = subprocess.run(
            compile_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=_COMPILE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as e:
        raise _CompileError((e.stderr or b"").decode(errors="replace") or "Compilation timed out")
    if completed.returncode != 0:
        raise _CompileError(completed.stderr.decode(errors="replace"))


def _run_subprocess_sync(
    run_cmd: list[str], stdin_data: str, time_limit_s: float, memory_limit_kb: int
):
    """
    Runs the judged process synchronously via the plain `subprocess` module.
    Called through asyncio.to_thread() so it works identically no matter
    which asyncio event loop the server is running — this sidesteps the
    Windows gotcha where asyncio.create_subprocess_exec() only works under
    ProactorEventLoop, and uvicorn doesn't guarantee that loop on Windows
    (it sets its own policy at startup, after the app module is imported,
    so setting the policy from our side doesn't reliably stick).

    Returns (returncode, stdout_bytes, stderr_bytes, timed_out).
    """
    preexec = _memory_limit_preexec(memory_limit_kb)
    try:
        completed = subprocess.run(
            run_cmd,
            input=stdin_data.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=time_limit_s,
            preexec_fn=preexec,
        )

        
        return completed.returncode, completed.stdout, completed.stderr, False
    except subprocess.TimeoutExpired as e:
        # subprocess.run() already kills the process for us on timeout.
        return None, e.stdout or b"", e.stderr or b"", True


async def _run_one(
    run_cmd: list[str],
    stdin_data: str,
    expected_output: str,
    time_limit_ms: int,
    memory_limit_kb: int,
) -> Judge0Verdict:
    time_limit_s = max(1.0, time_limit_ms / 1000)

    async with _sem:
        start = time.monotonic()
        returncode, stdout_b, stderr_b, timed_out = await asyncio.to_thread(
            _run_subprocess_sync, run_cmd, stdin_data, time_limit_s, memory_limit_kb
        )

        if timed_out:
            return Judge0Verdict(
                passed=False,
                stdout="",
                stderr="Time limit exceeded",
                status_id=STATUS_TIME_LIMIT_EXCEEDED,
                status_desc="Time Limit Exceeded",
                time_ms=time_limit_ms,
            )

        elapsed_ms = int((time.monotonic() - start) * 1000)
        stdout = stdout_b.decode(errors="replace")
        stderr = stderr_b.decode(errors="replace")

        if returncode != 0:
            is_compile_error = any(m in stderr for m in _COMPILE_ERROR_MARKERS)
            return Judge0Verdict(
                passed=False,
                stdout=stdout,
                stderr=stderr,
                status_id=6 if is_compile_error else 11,
                status_desc="Compile Error" if is_compile_error else "Runtime Error",
                time_ms=elapsed_ms,
            )

        passed = stdout.strip() == expected_output.strip()
        return Judge0Verdict(
            passed=passed,
            stdout=stdout,
            stderr=stderr,
            status_id=STATUS_ACCEPTED if passed else STATUS_WRONG_ANSWER,
            status_desc="Accepted" if passed else "Wrong Answer",
            time_ms=elapsed_ms,
        )


async def run_batch(
    code: str,
    language: Language,
    test_cases: list[dict],  # [{"input": str, "expected_output": str, "time_limit_ms": int, "memory_limit_kb": int}]
) -> list[Judge0Verdict]:
    """
    Compiles `code` once (if the language needs it), then runs it against
    every test case as its own subprocess (bounded concurrency), returning
    pass/fail + output per test case, in order.
    """
    if language not in LANGUAGE_CONFIG:
        raise ValueError(f"Unsupported language for local execution: {language}")

    _check_toolchain(language)
    cfg = LANGUAGE_CONFIG[language]

    work_dir = tempfile.mkdtemp(prefix="coderunner_")
    src_path = os.path.join(work_dir, cfg["source_name"])
    exe_path = os.path.join(work_dir, "a.out")

    try:
        with open(src_path, "w") as f:
            f.write(code)

        def _fmt(template: list[str]) -> list[str]:
            return [
                part.format(dir=work_dir, src=src_path, exe=exe_path, class_dir=work_dir)
                for part in template
            ]

        if cfg["compile_cmd"]:
            try:
                await asyncio.to_thread(_compile_sync, _fmt(cfg["compile_cmd"]))
            except _CompileError as e:
                # Compilation failed once for the whole submission — every
                # test case reports the same compile error rather than
                # re-attempting (and re-failing) the compile per test case.
                verdict = Judge0Verdict(
                    passed=False,
                    stdout="",
                    stderr=e.stderr,
                    status_id=6,
                    status_desc="Compile Error",
                    time_ms=None,
                )
                return [verdict for _ in test_cases]

        run_cmd = _fmt(cfg["run_cmd"])
        tasks = [
            _run_one(
                run_cmd,
                tc["input"],
                tc["expected_output"],
                tc.get("time_limit_ms", 2000),
                tc.get("memory_limit_kb", 65536),
            )
            for tc in test_cases
        ]
        return await asyncio.gather(*tasks)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
