"""
Admin CRUD for topics, problems, and test cases.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.core.security import get_admin_user, hash_password
from app.models.user import User
from app.models.problem import Topic, Problem, TestCase
from app.schemas.problem import (
    TopicCreate,
    TopicOut,
    ProblemCreate,
    ProblemUpdate,
    ProblemAdminOut,
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseAdminOut,
)

router = APIRouter(prefix="/admin/problems", tags=["admin-problems"])


# ---------- Topics ----------
@router.post("/topics", response_model=TopicOut)
async def create_topic(
    body: TopicCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_admin_user)
):
    existing = await db.execute(select(Topic).filter_by(slug=body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Slug already exists")
    topic = Topic(**body.model_dump())
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


@router.get("/topics", response_model=list[TopicOut])
async def list_topics(db: AsyncSession = Depends(get_db), _: User = Depends(get_admin_user)):
    result = await db.execute(select(Topic).order_by(Topic.order_index))
    return result.scalars().all()


@router.delete("/topics/{topic_id}", status_code=204)
async def delete_topic(
    topic_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_admin_user)
):
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")
    await db.delete(topic)
    await db.commit()


# ---------- Problems ----------
def _to_admin_out(problem: Problem) -> ProblemAdminOut:
    return ProblemAdminOut(
        id=problem.id,
        title=problem.title,
        slug=problem.slug,
        description=problem.description,
        constraints=problem.constraints,
        starter_code=problem.starter_code,
        difficulty=problem.difficulty,
        topic=problem.topic,
        time_limit_ms=problem.time_limit_ms,
        memory_limit_kb=problem.memory_limit_kb,
        is_locked=problem.is_locked,
        is_active=problem.is_active,
        created_at=problem.created_at,
        test_cases=problem.test_cases,
    )


@router.post("", response_model=ProblemAdminOut)
async def create_problem(
    body: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    existing = await db.execute(select(Problem).filter_by(slug=body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Slug already exists")
    if not await db.get(Topic, body.topic_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid topic_id")

    data = body.model_dump(exclude={"test_cases", "access_password"})
    problem = Problem(
        **data,
        created_by=admin.id,
        access_password_hash=hash_password(body.access_password)
        if body.access_password
        else None,
    )
    db.add(problem)
    await db.flush()  # get problem.id before adding children

    for i, tc in enumerate(body.test_cases):
        db.add(TestCase(problem_id=problem.id, order_index=tc.order_index or i, **tc.model_dump(exclude={"order_index"})))

    await db.commit()
    result = await db.execute(
        select(Problem)
        .options(selectinload(Problem.topic), selectinload(Problem.test_cases))
        .where(Problem.id == problem.id)
    )
    problem = result.scalar_one()
    return _to_admin_out(problem)


@router.get("", response_model=list[ProblemAdminOut])
async def list_problems_admin(
    db: AsyncSession = Depends(get_db), _: User = Depends(get_admin_user)
):
    result = await db.execute(
        select(Problem)
        .options(selectinload(Problem.topic), selectinload(Problem.test_cases))
        .order_by(Problem.id.desc())
    )
    problems = result.scalars().all()
    return [_to_admin_out(p) for p in problems]


@router.get("/{problem_id}", response_model=ProblemAdminOut)
async def get_problem_admin(
    problem_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_admin_user)
):
    result = await db.execute(
        select(Problem)
        .options(selectinload(Problem.topic), selectinload(Problem.test_cases))
        .filter_by(id=problem_id)
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")
    return _to_admin_out(problem)


@router.put("/{problem_id}", response_model=ProblemAdminOut)
async def update_problem(
    problem_id: int,
    body: ProblemUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    result = await db.execute(
        select(Problem).options(selectinload(Problem.test_cases)).filter_by(id=problem_id)
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")

    data = body.model_dump(exclude_unset=True, exclude={"access_password", "clear_password"})
    for k, v in data.items():
        setattr(problem, k, v)

    if body.clear_password:
        problem.access_password_hash = None
    elif body.access_password:
        problem.access_password_hash = hash_password(body.access_password)

    await db.commit()
    result = await db.execute(
        select(Problem)
        .options(selectinload(Problem.topic), selectinload(Problem.test_cases))
        .where(Problem.id == problem_id)
    )
    problem = result.scalar_one()
    return _to_admin_out(problem)


@router.delete("/{problem_id}", status_code=204)
async def delete_problem(
    problem_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_admin_user)
):
    problem = await db.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")
    await db.delete(problem)
    await db.commit()


# ---------- Test cases ----------
@router.post("/{problem_id}/test-cases", response_model=TestCaseAdminOut)
async def add_test_case(
    problem_id: int,
    body: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    if not await db.get(Problem, problem_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")
    tc = TestCase(problem_id=problem_id, **body.model_dump())
    db.add(tc)
    await db.commit()
    await db.refresh(tc)
    return tc


@router.put("/test-cases/{test_case_id}", response_model=TestCaseAdminOut)
async def update_test_case(
    test_case_id: int,
    body: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    tc = await db.get(TestCase, test_case_id)
    if not tc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Test case not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(tc, k, v)
    await db.commit()
    await db.refresh(tc)
    return tc


@router.delete("/test-cases/{test_case_id}", status_code=204)
async def delete_test_case(
    test_case_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_admin_user)
):
    tc = await db.get(TestCase, test_case_id)
    if not tc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Test case not found")
    await db.delete(tc)
    await db.commit()
