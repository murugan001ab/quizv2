"""
Runs user-submitted code locally via subprocess instead of hitting a remote
Judge0 instance. Each test case is executed as its own short-lived
subprocess: stdin is piped in, stdout/stderr captured, with a wall-clock
timeout and (on POSIX) an address-space rlimit standing in for Judge0's
cpu/memory limits.

Kept the same public surface as the old judge0_client.py (`run_batch`,
`Judge0Verdict`, the STATUS_* / *_RANGE constants) so app/routers/problems.py
only needed an import rename, not a rewrite.

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

LANGUAGE_MAP: dict[Language, str] = {
    Language.PYTHON3: sys.executable,
}

# Cap how many test cases run at once so a batch of 50 test cases doesn't
# fork 50 Python interpreters simultaneously.
_MAX_CONCURRENT = 4
_sem = asyncio.Semaphore(_MAX_CONCURRENT)

_COMPILE_ERROR_MARKERS = ("SyntaxError", "IndentationError", "TabError")


@dataclass
class Judge0Verdict:
    passed: bool
    stdout: str
    stderr: str
    status_id: int
    status_desc: str
    time_ms: int | None


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


async def _run_one(
    code: str,
    stdin_data: str,
    expected_output: str,
    time_limit_ms: int,
    memory_limit_kb: int,
) -> Judge0Verdict:
    time_limit_s = max(1.0, time_limit_ms / 1000)

    fd, script_path = tempfile.mkstemp(suffix=".py")
    with os.fdopen(fd, "w") as f:
        f.write(code)

    async with _sem:
        try:
            start = time.monotonic()
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "-I",  # isolated mode: ignore env/user site-packages
                script_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=_memory_limit_preexec(memory_limit_kb),
            )

            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(input=stdin_data.encode()),
                    timeout=time_limit_s,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
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

            if proc.returncode != 0:
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
        finally:
            try:
                os.unlink(script_path)
            except OSError:
                pass


async def run_batch(
    code: str,
    language: Language,
    test_cases: list[dict],  # [{"input": str, "expected_output": str, "time_limit_ms": int, "memory_limit_kb": int}]
) -> list[Judge0Verdict]:
    """
    Runs `code` against every test case as its own subprocess (bounded
    concurrency), and returns pass/fail + output per test case, in order.
    """
    if language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language for local execution: {language}")

    tasks = [
        _run_one(
            code,
            tc["input"],
            tc["expected_output"],
            tc.get("time_limit_ms", 2000),
            tc.get("memory_limit_kb", 65536),
        )
        for tc in test_cases
    ]
    return await asyncio.gather(*tasks)
