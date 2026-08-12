from pydantic import BaseModel


class LeetCodeSearchResult(BaseModel):
    """One row in the search dropdown — enough to render + pick, not import."""
    title_slug: str
    title: str
    question_frontend_id: str
    difficulty: str | None = None
    paid_only: bool = False
    topics: list[str] = []


class LeetCodeSearchOut(BaseModel):
    results: list[LeetCodeSearchResult]
    has_more: bool


class LeetCodeStarterCode(BaseModel):
    language: str  # one of our Language enum values: python3 / java / c
    code: str


class LeetCodeExample(BaseModel):
    input: str
    output: str


class LeetCodeImportOut(BaseModel):
    """
    A ready-to-prefill draft for the New Problem form — field names line up
    with ProblemCreate/the frontend form's `form` state so the UI can spread
    this straight in, only `topic_id` still needs picking by the admin.
    """
    title: str
    slug: str
    description: str  # HTML content converted to a plain/markdown-ish text
    constraints: str | None = None  # best-effort split out of the description
    difficulty: str  # "basic" | "intermediate" | "advanced" (already mapped)
    starter_codes: list[LeetCodeStarterCode]  # only python3/java/c snippets, if LeetCode had them
    examples: list[LeetCodeExample]  # best-effort parse of the "Example N:" blocks
    is_paid_only: bool
    source_url: str
