from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.problem import Difficulty, Language, SubmissionStatus


# ---------- Topic ----------
class TopicCreate(BaseModel):
    name: str
    slug: str
    order_index: int = 0


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    order_index: int


# ---------- Test case ----------
class TestCaseCreate(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False
    order_index: int = 0
    points: int = 1


class TestCaseUpdate(BaseModel):
    input: str | None = None
    expected_output: str | None = None
    is_hidden: bool | None = None
    order_index: int | None = None
    points: int | None = None


class TestCaseAdminOut(BaseModel):
    """Full detail — admin only, includes hidden cases + expected output."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    input: str
    expected_output: str
    is_hidden: bool
    order_index: int
    points: int


class TestCasePublicOut(BaseModel):
    """What a user sees on the problem page — visible cases only, no id leakage needed."""
    model_config = ConfigDict(from_attributes=True)
    input: str
    expected_output: str


# ---------- Problem ----------
class ProblemCreate(BaseModel):
    title: str
    slug: str
    description: str
    constraints: str | None = None
    starter_code: str | None = None
    difficulty: Difficulty = Difficulty.BASIC
    topic_id: int
    time_limit_ms: int = 2000
    memory_limit_kb: int = 65536
    access_password: str | None = Field(
        default=None, description="Plaintext; hashed before storage. Omit for an open problem."
    )
    test_cases: list[TestCaseCreate] = []


class ProblemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    constraints: str | None = None
    starter_code: str | None = None
    difficulty: Difficulty | None = None
    topic_id: int | None = None
    time_limit_ms: int | None = None
    memory_limit_kb: int | None = None
    is_active: bool | None = None
    access_password: str | None = None
    clear_password: bool = False  # explicit flag to remove password gate


class ProblemListItem(BaseModel):
    """Card/table row for the browse page — no description body, no test cases."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    difficulty: Difficulty
    topic: TopicOut
    is_locked: bool
    is_active: bool
    solved: bool = False


class ProblemDetailOut(BaseModel):
    """Full problem page for a user who has access (or it's unlocked)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    description: str
    constraints: str | None
    starter_code: str | None
    difficulty: Difficulty
    topic: TopicOut
    time_limit_ms: int
    memory_limit_kb: int
    is_locked: bool
    visible_test_cases: list[TestCasePublicOut]
    solved: bool = False
    saved_code: str | None = None
    saved_language: Language | None = None
    saved_at: datetime | None = None


class ProblemAdminOut(BaseModel):
    """Admin view — includes all test cases, hidden included."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    description: str
    constraints: str | None
    starter_code: str | None
    difficulty: Difficulty
    topic: TopicOut
    time_limit_ms: int
    memory_limit_kb: int
    is_locked: bool
    is_active: bool
    created_at: datetime
    test_cases: list[TestCaseAdminOut]


class UnlockRequest(BaseModel):
    password: str


# ---------- Saved code (per user, per problem) ----------
class SaveCodeRequest(BaseModel):
    code: str
    language: Language = Language.PYTHON3


class SavedCodeOut(BaseModel):
    code: str
    language: Language
    saved_at: datetime


# ---------- Run / Submit ----------
class RunRequest(BaseModel):
    code: str
    language: Language = Language.PYTHON3


class SubmitRequest(BaseModel):
    code: str
    language: Language = Language.PYTHON3


class TestCaseResultOut(BaseModel):
    is_hidden: bool
    passed: bool
    time_ms: int | None = None
    # For visible cases we return stdout/expected for debugging.
    # For hidden cases these are omitted entirely (see judge0 service).
    stdout: str | None = None
    expected: str | None = None
    stderr: str | None = None


class RunResultOut(BaseModel):
    status: SubmissionStatus
    results: list[TestCaseResultOut]


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uuid: str
    problem_id: int
    language: Language
    status: SubmissionStatus
    score: int
    max_score: int
    runtime_ms: int | None
    created_at: datetime


class SubmissionDetailOut(SubmissionOut):
    code: str
    results: list[TestCaseResultOut]
