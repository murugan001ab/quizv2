"""
Post-solve discussion room.

Gated by solve status: a user must have at least one ACCEPTED submission
for a problem before they can read, post, comment, or like in its
discussion room.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.problem import Problem, Submission, SubmissionStatus
from app.models.discussion import (
    DiscussionPost,
    DiscussionComment,
    DiscussionPostLike,
    DiscussionCommentLike,
)
from app.schemas.discussion import (
    DiscussionPostCreate,
    DiscussionCommentCreate,
    DiscussionPostOut,
    DiscussionCommentOut,
    LikeToggleOut,
)

router = APIRouter(tags=["discussion"])


async def _has_solved(db: AsyncSession, user: User, problem_id: int) -> bool:
    result = await db.execute(
        select(Submission.id).where(
            Submission.user_id == user.id,
            Submission.problem_id == problem_id,
            Submission.status == SubmissionStatus.ACCEPTED,
        ).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def _require_solved(db: AsyncSession, user: User, problem_id: int):
    problem = (
        await db.execute(select(Problem).where(Problem.id == problem_id))
    ).scalar_one_or_none()
    if not problem:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Problem not found")
    if not await _has_solved(db, user, problem_id):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Solve this problem first to unlock its discussion room",
        )
    return problem


def _serialize_post(post: DiscussionPost, user_id: int) -> DiscussionPostOut:
    return DiscussionPostOut(
        id=post.id,
        uuid=post.uuid,
        content=post.content,
        created_at=post.created_at,
        user=post.user,
        likes_count=len(post.likes),
        liked_by_me=any(l.user_id == user_id for l in post.likes),
        is_mine=post.user_id == user_id,
        comments=[_serialize_comment(c, user_id) for c in post.comments],
    )


def _serialize_comment(comment: DiscussionComment, user_id: int) -> DiscussionCommentOut:
    return DiscussionCommentOut(
        id=comment.id,
        content=comment.content,
        created_at=comment.created_at,
        user=comment.user,
        likes_count=len(comment.likes),
        liked_by_me=any(l.user_id == user_id for l in comment.likes),
        is_mine=comment.user_id == user_id,
    )


# ---------- Posts (scoped to a problem) ----------

@router.get("/problems/{problem_id}/discussion", response_model=list[DiscussionPostOut])
async def list_discussion(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _require_solved(db, user, problem_id)

    result = await db.execute(
        select(DiscussionPost)
        .where(DiscussionPost.problem_id == problem_id)
        .options(
            selectinload(DiscussionPost.user),
            selectinload(DiscussionPost.likes),
            selectinload(DiscussionPost.comments).selectinload(DiscussionComment.user),
            selectinload(DiscussionPost.comments).selectinload(DiscussionComment.likes),
        )
        .order_by(DiscussionPost.created_at.desc())
    )
    posts = result.scalars().all()
    return [_serialize_post(p, user.id) for p in posts]


@router.post("/problems/{problem_id}/discussion", response_model=DiscussionPostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    problem_id: int,
    body: DiscussionPostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _require_solved(db, user, problem_id)

    post = DiscussionPost(problem_id=problem_id, user_id=user.id, content=body.content)
    db.add(post)
    await db.commit()

    result = await db.execute(
        select(DiscussionPost)
        .where(DiscussionPost.id == post.id)
        .options(
            selectinload(DiscussionPost.user),
            selectinload(DiscussionPost.likes),
            selectinload(DiscussionPost.comments).selectinload(DiscussionComment.user),
            selectinload(DiscussionPost.comments).selectinload(DiscussionComment.likes),
        )
    )
    post = result.scalar_one()
    return _serialize_post(post, user.id)


@router.delete("/discussion/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = (
        await db.execute(select(DiscussionPost).where(DiscussionPost.id == post_id))
    ).scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    if post.user_id != user.id and not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your post")
    await db.delete(post)
    await db.commit()


@router.post("/discussion/posts/{post_id}/like", response_model=LikeToggleOut)
async def toggle_post_like(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = (
        await db.execute(select(DiscussionPost).where(DiscussionPost.id == post_id))
    ).scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    await _require_solved(db, user, post.problem_id)

    existing = (
        await db.execute(
            select(DiscussionPostLike).filter_by(post_id=post_id, user_id=user.id)
        )
    ).scalar_one_or_none()

    if existing:
        await db.delete(existing)
        liked = False
    else:
        db.add(DiscussionPostLike(post_id=post_id, user_id=user.id))
        liked = True
    await db.commit()

    count = (
        await db.execute(
            select(func.count()).select_from(DiscussionPostLike).where(DiscussionPostLike.post_id == post_id)
        )
    ).scalar_one()
    return LikeToggleOut(liked=liked, likes_count=count)


# ---------- Comments ----------

@router.post("/discussion/posts/{post_id}/comments", response_model=DiscussionCommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    body: DiscussionCommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = (
        await db.execute(select(DiscussionPost).where(DiscussionPost.id == post_id))
    ).scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    await _require_solved(db, user, post.problem_id)

    comment = DiscussionComment(post_id=post_id, user_id=user.id, content=body.content)
    db.add(comment)
    await db.commit()

    result = await db.execute(
        select(DiscussionComment)
        .where(DiscussionComment.id == comment.id)
        .options(selectinload(DiscussionComment.user), selectinload(DiscussionComment.likes))
    )
    comment = result.scalar_one()
    return _serialize_comment(comment, user.id)


@router.delete("/discussion/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    comment = (
        await db.execute(select(DiscussionComment).where(DiscussionComment.id == comment_id))
    ).scalar_one_or_none()
    if not comment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")
    if comment.user_id != user.id and not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your comment")
    await db.delete(comment)
    await db.commit()


@router.post("/discussion/comments/{comment_id}/like", response_model=LikeToggleOut)
async def toggle_comment_like(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    comment = (
        await db.execute(select(DiscussionComment).where(DiscussionComment.id == comment_id))
    ).scalar_one_or_none()
    if not comment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")

    post = (
        await db.execute(select(DiscussionPost).where(DiscussionPost.id == comment.post_id))
    ).scalar_one()
    await _require_solved(db, user, post.problem_id)

    existing = (
        await db.execute(
            select(DiscussionCommentLike).filter_by(comment_id=comment_id, user_id=user.id)
        )
    ).scalar_one_or_none()

    if existing:
        await db.delete(existing)
        liked = False
    else:
        db.add(DiscussionCommentLike(comment_id=comment_id, user_id=user.id))
        liked = True
    await db.commit()

    count = (
        await db.execute(
            select(func.count()).select_from(DiscussionCommentLike).where(DiscussionCommentLike.comment_id == comment_id)
        )
    ).scalar_one()
    return LikeToggleOut(liked=liked, likes_count=count)
