from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator

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
    # None/empty => every language code_runner supports is offered to the user.
    # One entry => that language is pinned; the frontend hides the picker.
    # 2+ entries => user picks among just these.
    allowed_languages: list[Language] | None = None
    # Which of allowed_languages (or, if that's unset, which overall language)
    # is preselected when a problem allows more than one.
    default_language: Language | None = None
    test_cases: list[TestCaseCreate] = []

    @model_validator(mode="after")
    def _default_language_must_be_allowed(self):
        if (
            self.default_language is not None
            and self.allowed_languages
            and self.default_language not in self.allowed_languages
        ):
            raise ValueError("default_language must be one of allowed_languages")
        return self


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
    allowed_languages: list[Language] | None = None
    default_language: Language | None = None

    @model_validator(mode="after")
    def _default_language_must_be_allowed(self):
        if (
            self.default_language is not None
            and self.allowed_languages
            and self.default_language not in self.allowed_languages
        ):
            raise ValueError("default_language must be one of allowed_languages")
        return self


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
    # Computed from Problem.allowed_languages/default_language (see the model
    # properties of the same name) — tells the frontend which languages to
    # offer and which to preselect, without it needing to reimplement the
    # "admin pinned one language" vs "user picks" logic itself.
    available_languages: list[Language]
    is_single_language: bool
    effective_default_language: Language


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
    allowed_languages: list[Language] | None
    default_language: Language | None
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
