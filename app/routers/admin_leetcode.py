"""
Lets an admin search LeetCode and pull a problem straight into the New
Problem form instead of retyping title/description/starter code by hand.
Two endpoints only — search, and import-by-slug — the actual Problem row
is still created via the normal POST /admin/problems once the admin reviews
and submits the (editable) prefilled form.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import leetcode
from app.core.security import get_admin_user
from app.database import get_db
from app.models.leetcode import LeetCodeProblem
from app.models.problem import Language
from app.models.user import User
from app.schemas.leetcode import (
    LeetCodeExample,
    LeetCodeImportOut,
    LeetCodeSearchOut,
    LeetCodeSearchResult,
    LeetCodeStarterCode,
)

router = APIRouter(prefix="/admin/leetcode", tags=["admin-leetcode"])

_DIFFICULTY_MAP = {"Easy": "basic", "Medium": "intermediate", "Hard": "advanced"}

# LeetCode's codeSnippets langSlug values we can actually use — code_runner
# only judges python3/java/c, so anything else (cpp, javascript, go, ...)
# is dropped rather than offered as a starter code the platform can't run.
_USABLE_LANG_SLUGS = {lang.value for lang in Language}


@router.get("/search", response_model=LeetCodeSearchOut)
async def search_leetcode(
    q: str = Query(..., min_length=1, description="Title text or problem number"),
    limit: int = Query(15, ge=1, le=50),
    _: User = Depends(get_admin_user),
):
    try:
        data = await leetcode.get_problem_page(skip=0, limit=limit, search_keyword=q)
    except Exception as e:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, f"Couldn't reach LeetCode: {e}"
        )

    results = [
        LeetCodeSearchResult(
            title_slug=q_["titleSlug"],
            title=q_["title"],
            question_frontend_id=str(q_["questionFrontendId"]),
            difficulty=q_.get("difficulty"),
            paid_only=q_.get("paidOnly", False),
            topics=[t["name"] for t in (q_.get("topicTags") or [])],
        )
        for q_ in data["questions"]
    ]
    return LeetCodeSearchOut(results=results, has_more=data.get("hasMore", False))


@router.get("/import/{title_slug}", response_model=LeetCodeImportOut)
async def import_leetcode_problem(
    title_slug: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    # Serve from cache if we've already fetched this one before.
    existing = await db.execute(
        select(LeetCodeProblem).filter_by(title_slug=title_slug)
    )
    cached = existing.scalar_one_or_none()

    # The cache only stores raw HTML (content column). html_to_text /
    # extract_examples / split_constraints always run fresh at request time,
    # so fixing those functions is sufficient — no DB flush needed.
    if cached is None:
        try:
            question = await leetcode.get_problem_details(title_slug)
        except LookupError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "LeetCode problem not found")
        except Exception as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY, f"Couldn't reach LeetCode: {e}"
            )

        cached = LeetCodeProblem(
            question_id=int(question["questionFrontendId"]),
            title=question["title"],
            title_slug=question["titleSlug"],
            difficulty=question.get("difficulty"),
            paid_only=question.get("isPaidOnly", False),
            topics=[t["name"] for t in (question.get("topicTags") or [])],
            content=question.get("content"),
            code_snippets=question.get("codeSnippets"),
            example_testcases=question.get("exampleTestcaseList"),
            hints=question.get("hints"),
        )
        db.add(cached)
        await db.commit()
        await db.refresh(cached)

    starter_codes = [
        LeetCodeStarterCode(language=snip["langSlug"], code=snip["code"])
        for snip in (cached.code_snippets or [])
        if snip.get("langSlug") in _USABLE_LANG_SLUGS
    ]

    examples = [
        LeetCodeExample(**ex) for ex in leetcode.extract_examples(cached.content or "")
    ]

    full_text = leetcode.html_to_text(cached.content or "")
    description, constraints = leetcode.split_constraints(full_text)

    return LeetCodeImportOut(
        title=cached.title,
        slug=cached.title_slug,
        description=description,
        constraints=constraints,
        difficulty=_DIFFICULTY_MAP.get(cached.difficulty, "basic"),
        starter_codes=starter_codes,
        examples=examples,
        is_paid_only=cached.paid_only,
        source_url=f"https://leetcode.com/problems/{cached.title_slug}/",
    )
