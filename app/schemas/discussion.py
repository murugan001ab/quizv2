from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DiscussionAuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    username: str
    profile_url: str | None = None


class DiscussionPostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class DiscussionCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class DiscussionCommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    created_at: datetime
    user: DiscussionAuthorOut
    likes_count: int = 0
    liked_by_me: bool = False
    is_mine: bool = False


class DiscussionPostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uuid: str
    content: str
    created_at: datetime
    user: DiscussionAuthorOut
    likes_count: int = 0
    liked_by_me: bool = False
    is_mine: bool = False
    comments: list[DiscussionCommentOut] = []


class LikeToggleOut(BaseModel):
    liked: bool
    likes_count: int
