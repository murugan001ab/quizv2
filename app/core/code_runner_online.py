"""
Runs user-submitted code against the Judge0 API (https://ce.judge0.com)
instead of spawning local subprocesses or using Piston. This is the online 
counterpart to code_runner.py — maintaining the exact same public surface 
(`run_batch`, `Judge0Verdict`, the STATUS_* constants), allowing router code 
to swap between runners seamlessly.

WHY: Offloads compilation and execution entirely to Judge0's hosted engine,
avoiding local binary dependencies (gcc, java, python).

API SETUP: Uses Judge0's submission API with `wait=true` to process submissions 
synchronously in a single HTTP POST request.
"""

import asyncio
import os
import time

import httpx

from app.core.code_runner import (
    STATUS_ACCEPTED,
    STATUS_WRONG_ANSWER,
    STATUS_TIME_LIMIT_EXCEEDED,
    Judge0Verdict,
)
from app.models.problem import Language

JUDGE0_BASE_URL = os.environ.get("JUDGE0_BASE_URL", "https://ce.judge0.com").rstrip("/")

# Judge0 Language IDs mapped from internal Language enum.
# 71 -> Python (3.8.1), 50 -> C (GCC 9.2.0), 62 -> Java (OpenJDK 13.0.1)
# Adjust these IDs based on your specific Judge0 instance runtime catalog.
LANGUAGE_CONFIG: dict[Language, dict] = {
    Language.PYTHON3: {"language_id": 71},
    Language.C: {"language_id": 50},
    Language.JAVA: {"language_id": 62},
}

# Limit concurrency to adhere to target API rate-limits and avoid socket exhaustion
_MAX_CONCURRENT = 5
_sem = asyncio.Semaphore(_MAX_CONCURRENT)

_HTTP_TIMEOUT_S = 30.0


async def _execute_one(
    client: httpx.AsyncClient,
    language_id: int,
    code: str,
    stdin_data: str,
    expected_output: str,
    time_limit_ms: int,
    memory_limit_kb: int,
) -> Judge0Verdict:
    # Convert limits: Judge0 expects cpu_time_limit in seconds (float)
    cpu_time_limit_s = max(1.0, time_limit_ms / 1000.0)

    payload = {
        "language_id": language_id,
        "source_code": code,
        "stdin": stdin_data,
        "cpu_time_limit": cpu_time_limit_s,
        "memory_limit": memory_limit_kb if memory_limit_kb else None,
    }

    url = f"{JUDGE0_BASE_URL}/submissions?wait=true"

    async with _sem:
        start = time.monotonic()
        try:
            resp = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=_HTTP_TIMEOUT_S,
            )
        except httpx.TimeoutException:
            return Judge0Verdict(
                passed=False,
                stdout="",
                stderr="Request to Judge0 timed out",
                status_id=STATUS_TIME_LIMIT_EXCEEDED,
                status_desc="Time Limit Exceeded",
                time_ms=time_limit_ms,
            )
        except httpx.HTTPError as e:
            return Judge0Verdict(
                passed=False,
                stdout="",
                stderr=f"Could not reach Judge0 at {JUDGE0_BASE_URL}: {e}",
                status_id=13,
                status_desc="Internal Error",
                time_ms=None,
            )

        elapsed_ms = int((time.monotonic() - start) * 1000)

        if resp.status_code == 429:
            return Judge0Verdict(
                passed=False,
                stdout="",
                stderr="Rate limited by the Judge0 API — try again shortly",
                status_id=13,
                status_desc="Internal Error",
                time_ms=elapsed_ms,
            )

        try:
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            return Judge0Verdict(
                passed=False,
                stdout="",
                stderr=f"Invalid response from Judge0: {e}",
                status_id=13,
                status_desc="Internal Error",
                time_ms=elapsed_ms,
            )

        # Parse Judge0 standard response fields
        stdout = data.get("stdout") or ""
        stderr = data.get("stderr") or ""
        compile_output = data.get("compile_output") or ""
        
        status = data.get("status", {})
        status_id = status.get("id")
        status_desc = status.get("description", "Unknown Status")

        # Judge0 Execution Time is returned in seconds (string/float)
        execution_time_s = data.get("time")
        if execution_time_s is not None:
            time_ms = int(float(execution_time_s) * 1000)
        else:
            time_ms = elapsed_ms

        # 1) Compilation Error (Judge0 Status ID 6)
        if status_id == 6:
            return Judge0Verdict(
                passed=False,
                stdout=stdout,
                stderr=compile_output or stderr,
                status_id=6,
                status_desc="Compile Error",
                time_ms=time_ms,
            )

        # 2) Time Limit Exceeded (Judge0 Status ID 5)
        if status_id == 5:
            return Judge0Verdict(
                passed=False,
                stdout=stdout,
                stderr=stderr or "Time Limit Exceeded",
                status_id=STATUS_TIME_LIMIT_EXCEEDED,
                status_desc="Time Limit Exceeded",
                time_ms=time_limit_ms,
            )

        # 3) Runtime Errors (Judge0 Status IDs 7, 8, 9, 10, 11, 12)
        if status_id not in (3, None) and status_id != 3:  # 3 == Accepted in Judge0
            return Judge0Verdict(
                passed=False,
                stdout=stdout,
                stderr=stderr or compile_output,
                status_id=status_id or 11,
                status_desc=status_desc,
                time_ms=time_ms,
            )

        # 4) Output Comparison (Judge0 status 3 = Ran to completion)
        passed = stdout.strip() == expected_output.strip()
        return Judge0Verdict(
            passed=passed,
            stdout=stdout,
            stderr=stderr,
            status_id=STATUS_ACCEPTED if passed else STATUS_WRONG_ANSWER,
            status_desc="Accepted" if passed else "Wrong Answer",
            time_ms=time_ms,
        )


async def run_batch(
    code: str,
    language: Language,
    test_cases: list[dict],  # [{"input": str, "expected_output": str, "time_limit_ms": int, "memory_limit_kb": int}]
) -> list[Judge0Verdict]:
    """
    Runs `code` against every test case via Judge0 API (bounded concurrency),
    returning pass/fail + output per test case, in order.
    """
    if language not in LANGUAGE_CONFIG:
        raise ValueError(f"Unsupported language for Judge0 execution: {language}")

    cfg = LANGUAGE_CONFIG[language]

    async with httpx.AsyncClient() as client:
        tasks = [
            _execute_one(
                client=client,
                language_id=cfg["language_id"],
                code=code,
                stdin_data=tc["input"],
                expected_output=tc["expected_output"],
                time_limit_ms=tc.get("time_limit_ms", 2000),
                memory_limit_kb=tc.get("memory_limit_kb", 65536),
            )
            for tc in test_cases
        ]
        return await asyncio.gather(*tasks)