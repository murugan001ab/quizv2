"""
User-facing endpoints: browse problems, unlock password-gated ones,
run code against visible test cases, submit against all test cases.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.core.security import get_current_user, verify_password
from app.core import code_runner_online
from app.models.user import User
from app.models.problem import (
    Topic,
    Problem,
    TestCase,
    Submission,
    ProblemUnlock,
    SubmissionStatus,
)
from app.models.saved_code import SavedCode
from app.schemas.problem import (
    ProblemListItem,
    ProblemDetailOut,
    UnlockRequest,
    SaveCodeRequest,
    SavedCodeOut,
    RunRequest,
    SubmitRequest,
    RunResultOut,
    TestCaseResultOut,
    SubmissionOut,
    SubmissionDetailOut,
    TopicOut,
)

router = APIRouter(prefix="/problems", tags=["problems"])


async def _has_access(db: AsyncSession, user: User, problem: Problem) -> bool:
    if not problem.is_locked:
        return True
    result = await db.execute(
        select(ProblemUnlock).filter_by(user_id=user.id, problem_id=problem.id)
    )
    return result.scalar_one_or_none() is not None


@router.get("/topics", response_model=list[TopicOut])
async def list_topics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Topic).order_by(Topic.order_index))
    return result.scalars().all()


async def _solved_problem_ids(db: AsyncSession, user: User) -> set[int]:
    """Problem ids the user has at least one ACCEPTED submission for."""
    result = await db.execute(
        select(Submission.problem_id)
        .where(Submission.user_id == user.id, Submission.status == SubmissionStatus.ACCEPTED)
        .distinct()
    )
    return {row[0] for row in result.all()}


@router.get("", response_model=list[ProblemListItem])
async def list_problems(
    topic_id: int | None = None,
    difficulty: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(Problem).options(selectinload(Problem.topic)).where(Problem.is_active == True)
    if topic_id:
        q = q.where(Problem.topic_id == topic_id)
    if difficulty:
        q = q.where(Problem.difficulty == difficulty)
    result = await db.execute(q.order_by(Problem.id))
    problems = result.scalars().all()

    solved_ids = await _solved_problem_ids(db, user)

    return [
        ProblemListItem(
            id=p.id,
            title=p.title,
            slug=p.slug,
            difficulty=p.difficulty,
            topic=p.topic,
            is_locked=p.is_locked,
            is_active=p.is_active,
            solved=p.id in solved_ids,
        )
        for p in problems
    ]


@router.get("/{problem_id}", response_model=ProblemDetailOut)
async def get_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Problem)
        .options(selectinload(Problem.topic), selectinload(Problem.test_cases))
        .where(Problem.id == problem_id, Problem.is_active == True)
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")

    unlocked = await _has_access(db, user, problem)
    visible = [tc for tc in problem.test_cases if not tc.is_hidden] if unlocked else []
    solved_ids = await _solved_problem_ids(db, user)

    saved = None
    if unlocked:
        saved_result = await db.execute(
            select(SavedCode).filter_by(user_id=user.id, problem_id=problem.id)
        )
        saved = saved_result.scalar_one_or_none()

    return ProblemDetailOut(
        id=problem.id,
        title=problem.title,
        slug=problem.slug,
        description=problem.description if unlocked else "🔒 Enter the password to view this problem.",
        constraints=problem.constraints if unlocked else None,
        starter_code=problem.starter_code if unlocked else None,
        difficulty=problem.difficulty,
        topic=problem.topic,
        time_limit_ms=problem.time_limit_ms,
        memory_limit_kb=problem.memory_limit_kb,
        is_locked=problem.is_locked and not unlocked,
        visible_test_cases=visible,
        solved=problem.id in solved_ids,
        saved_code=saved.code if saved else None,
        saved_language=saved.language if saved else None,
        saved_at=saved.updated_at if saved else None,
        available_languages=problem.available_languages,
        is_single_language=problem.is_single_language,
        effective_default_language=problem.effective_default_language,
    )


@router.put("/{problem_id}/save", response_model=SavedCodeOut)
async def save_code(
    problem_id: int,
    body: SaveCodeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upserts the user's saved code for this problem (one slot per user/problem)."""
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem or not problem.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")
    if not await _has_access(db, user, problem):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Unlock this problem first")

    existing = await db.execute(
        select(SavedCode).filter_by(user_id=user.id, problem_id=problem_id)
    )
    saved = existing.scalar_one_or_none()

    print(body.language)
    if saved:
        saved.code = body.code
        saved.language = body.language
    else:
        saved = SavedCode(
            user_id=user.id, problem_id=problem_id, code=body.code, language=body.language
        )
        db.add(saved)
    await db.commit()
    await db.refresh(saved)

    return SavedCodeOut(code=saved.code, language=saved.language, saved_at=saved.updated_at)


@router.post("/{problem_id}/unlock")
async def unlock_problem(
    problem_id: int,
    body: UnlockRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem or not problem.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")
    if not problem.is_locked:
        return {"unlocked": True}

    if not verify_password(body.password, problem.access_password_hash):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Incorrect password")

    existing = await db.execute(
        select(ProblemUnlock).filter_by(user_id=user.id, problem_id=problem.id)
    )
    if existing.scalar_one_or_none() is None:
        db.add(ProblemUnlock(user_id=user.id, problem_id=problem.id))
        await db.commit()
    return {"unlocked": True}


async def _judge(
    db: AsyncSession, problem: Problem, code: str, language, test_cases: list[TestCase]
):
    payload = [
        {
            "input": tc.input,
            "expected_output": tc.expected_output,
            "time_limit_ms": problem.time_limit_ms,
            "memory_limit_kb": problem.memory_limit_kb,
        }
        for tc in test_cases
    ]
    verdicts = await code_runner_online.run_batch(code, language, payload)

    results: list[TestCaseResultOut] = []
    for tc, v in zip(test_cases, verdicts):
        if tc.is_hidden:
            # Never leak hidden input/expected/stdout to the client.
            results.append(
                TestCaseResultOut(is_hidden=True, passed=v.passed, time_ms=v.time_ms)
            )
        else:
            results.append(
                TestCaseResultOut(
                    is_hidden=False,
                    passed=v.passed,
                    time_ms=v.time_ms,
                    stdout=v.stdout,
                    expected=tc.expected_output,
                    stderr=v.stderr or None,
                )
            )
    return results, verdicts


@router.post("/{problem_id}/run", response_model=RunResultOut)
async def run_code(
    problem_id: int,
    body: RunRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Runs against VISIBLE test cases only. Nothing is persisted."""
    result = await db.execute(
        select(Problem).options(selectinload(Problem.test_cases)).where(Problem.id == problem_id)
    )
    problem = result.scalar_one_or_none()
    if not problem or not problem.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")
    if not await _has_access(db, user, problem):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Unlock this problem first")
    if body.language.value not in problem.available_languages:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"This problem only allows: {', '.join(problem.available_languages)}",
        )

    visible_cases = [tc for tc in problem.test_cases if not tc.is_hidden]
    results, verdicts = await _judge(db, problem, body.code, body.language, visible_cases)
    overall = (
        SubmissionStatus.ACCEPTED
        if all(v.passed for v in verdicts)
        else SubmissionStatus.WRONG_ANSWER
    )
    return RunResultOut(status=overall, results=results)


@router.post("/{problem_id}/submit", response_model=SubmissionDetailOut)
async def submit_code(
    problem_id: int,
    body: SubmitRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Runs against ALL test cases (visible + hidden) and persists a Submission."""
    result = await db.execute(
        select(Problem).options(selectinload(Problem.test_cases)).where(Problem.id == problem_id)
    )
    problem = result.scalar_one_or_none()
    if not problem or not problem.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")
    if not await _has_access(db, user, problem):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Unlock this problem first")
    if body.language.value not in problem.available_languages:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"This problem only allows: {', '.join(problem.available_languages)}",
        )

    all_cases = problem.test_cases
    results, verdicts = await _judge(db, problem, body.code, body.language, all_cases)

    passed_count = sum(1 for v in verdicts if v.passed)
    score = sum(tc.points for tc, v in zip(all_cases, verdicts) if v.passed)
    max_score = sum(tc.points for tc in all_cases)

    if passed_count == len(verdicts):
        status_ = SubmissionStatus.ACCEPTED
    elif any(v.status_id in code_runner_online.COMPILE_ERROR_RANGE for v in verdicts):
        status_ = SubmissionStatus.COMPILE_ERROR
    elif any(v.status_id in code_runner_online.RUNTIME_ERROR_RANGE for v in verdicts):
        status_ = SubmissionStatus.RUNTIME_ERROR
    elif any(v.status_id == code_runner_online.STATUS_TIME_LIMIT_EXCEEDED for v in verdicts):
        status_ = SubmissionStatus.TIME_LIMIT_EXCEEDED
    else:
        status_ = SubmissionStatus.WRONG_ANSWER

    submission = Submission(
        user_id=user.id,
        problem_id=problem.id,
        language=body.language,
        code=body.code,
        status=status_,
        score=score,
        max_score=max_score,
        runtime_ms=max((v.time_ms or 0) for v in verdicts) if verdicts else None,
        results=[r.model_dump() for r in results],
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    return SubmissionDetailOut(
        id=submission.id,
        uuid=submission.uuid,
        problem_id=submission.problem_id,
        language=submission.language,
        status=submission.status,
        score=submission.score,
        max_score=submission.max_score,
        runtime_ms=submission.runtime_ms,
        created_at=submission.created_at,
        code=submission.code,
        results=results,
    )


@router.get("/{problem_id}/submissions", response_model=list[SubmissionOut])
async def my_submissions(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Submission)
        .filter_by(problem_id=problem_id, user_id=user.id)
        .order_by(Submission.created_at.desc())
    )
    return result.scalars().all()


@router.get("/submissions/{submission_id}", response_model=SubmissionDetailOut)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Submission).filter_by(id=submission_id, user_id=user.id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submission not found")
    return SubmissionDetailOut(
        id=sub.id,
        uuid=sub.uuid,
        problem_id=sub.problem_id,
        language=sub.language,
        status=sub.status,
        score=sub.score,
        max_score=sub.max_score,
        runtime_ms=sub.runtime_ms,
        created_at=sub.created_at,
        code=sub.code,
        results=[TestCaseResultOut(**r) for r in (sub.results or [])],
    )
