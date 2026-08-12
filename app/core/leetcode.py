"""
Thin async client for LeetCode's public GraphQL endpoint. Used by
app/routers/admin_leetcode.py to let an admin search LeetCode and import a
problem straight into a New Problem form draft, instead of retyping it by
hand.

Trimmed down from a fuller sync-DB-backed version: this project only needs
on-demand search + single-problem detail, not a full catalog sync, so the
`/sync`-style bulk pagination and the `find_problem_by_number` helper were
dropped. `get_problem_page` and `get_problem_details` are kept close to
their original shape.
"""

import html
import re

import httpx

LEETCODE_URL = "https://leetcode.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com",
}


# ============================================================
# Queries
# ============================================================

PROBLEM_LIST_QUERY = """
query problemsetPanelQuestionList(
    $filters: QuestionFilterInput,
    $searchKeyword: String,
    $sortBy: QuestionSortByInput,
    $categorySlug: String,
    $limit: Int,
    $skip: Int
) {
    problemsetPanelQuestionList(
        filters: $filters
        searchKeyword: $searchKeyword
        sortBy: $sortBy
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip
    ) {
        questions {
            titleSlug
            title
            questionFrontendId
            paidOnly
            difficulty
            topicTags {
                name
                slug
            }
            acRate
        }
        totalLength
        hasMore
    }
}
"""

QUESTION_QUERY = """
query questionDetail($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        title
        titleSlug
        questionFrontendId
        content
        difficulty
        topicTags {
            name
            slug
        }
        isPaidOnly
        hints
        codeSnippets {
            code
            lang
            langSlug
        }
        exampleTestcaseList
        sampleTestCase
    }
}
"""

FILTERS = {
    "filterCombineType": "ALL",
    "statusFilter": {"questionStatuses": [], "operator": "IS"},
    "difficultyFilter": {"difficulties": [], "operator": "IS"},
    "languageFilter": {"languageSlugs": [], "operator": "IS"},
    "topicFilter": {"topicSlugs": [], "operator": "IS"},
    "acceptanceFilter": {},
    "frequencyFilter": {},
    "frontendIdFilter": {},
    "lastSubmittedFilter": {},
    "publishedFilter": {},
    "companyFilter": {"companySlugs": [], "operator": "IS"},
    "positionFilter": {"positionSlugs": [], "operator": "IS"},
    "positionLevelFilter": {"positionLevelSlugs": [], "operator": "IS"},
    "contestPointFilter": {"contestPoints": [], "operator": "IS"},
    "premiumFilter": {"premiumStatus": [], "operator": "IS"},
}


async def graphql_request(query: str, variables: dict, operation_name: str):
    async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
        response = await client.post(
            LEETCODE_URL,
            json={"query": query, "variables": variables, "operationName": operation_name},
        )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(str(data["errors"]))
    return data["data"]


async def get_problem_page(skip: int = 0, limit: int = 20, search_keyword: str = ""):
    """One page of the LeetCode problem catalog, optionally text/number filtered."""
    variables = {
        "skip": skip,
        "limit": limit,
        "categorySlug": "",
        "searchKeyword": search_keyword,
        "filters": FILTERS,
        "sortBy": {"sortField": "CUSTOM", "sortOrder": "ASCENDING"},
    }
    data = await graphql_request(PROBLEM_LIST_QUERY, variables, "problemsetPanelQuestionList")
    return data["problemsetPanelQuestionList"]


async def get_problem_details(title_slug: str):
    """Full problem body (HTML content, code snippets, examples, etc.)."""
    data = await graphql_request(
        QUESTION_QUERY, {"titleSlug": title_slug}, "questionDetail"
    )
    question = data["question"]
    if question is None:
        raise LookupError(f"No LeetCode problem found for slug '{title_slug}'")
    return question


# ============================================================
# HTML content -> plain/markdown-ish text
# ============================================================
# LeetCode's `content` field is a blob of HTML. There's no bs4/html2text
# dependency in this project, so this is a small purpose-built converter —
# good enough for a first-pass problem description an admin then edits by
# hand, not a general-purpose HTML->Markdown library.

_TAG_BLOCK_BREAK = re.compile(r"</(p|div|li|h[1-4])\s*>", re.IGNORECASE)
_TAG_BR = re.compile(r"<br\s*/?>", re.IGNORECASE)
_TAG_LI_OPEN = re.compile(r"<li[^>]*>", re.IGNORECASE)
_TAG_STRONG = re.compile(r"</?(strong|b)[^>]*>", re.IGNORECASE)  # stripped, not converted
_TAG_EM = re.compile(r"</?(em|i)[^>]*>", re.IGNORECASE)
_TAG_CODE_INLINE = re.compile(r"</?code[^>]*>", re.IGNORECASE)
_TAG_SUP = re.compile(r"<sup[^>]*>(.*?)</sup>", re.IGNORECASE | re.DOTALL)
_TAG_ANY = re.compile(r"<[^>]+>")
_BLANK_RUN = re.compile(r"\n{3,}")


def html_to_text(raw_html: str) -> str:
    """Convert LeetCode HTML content to clean plain text.
    Bold/italic/code tags are stripped (not converted to markdown markers)
    so ** and `` never appear in the output.
    """
    if not raw_html:
        return ""
    text = raw_html
    text = _TAG_SUP.sub(r"^\1", text)        # <sup>2</sup> -> ^2
    text = _TAG_STRONG.sub("", text)          # strip bold markers entirely
    text = _TAG_EM.sub("", text)              # strip italic markers entirely
    text = _TAG_CODE_INLINE.sub("", text)     # strip inline code markers
    text = _TAG_LI_OPEN.sub("\n- ", text)
    text = _TAG_BR.sub("\n", text)
    text = _TAG_BLOCK_BREAK.sub("\n\n", text)
    text = _TAG_ANY.sub("", text)             # drop every remaining tag
    text = html.unescape(text)
    text = _BLANK_RUN.sub("\n\n", text)
    return "\n".join(line.rstrip() for line in text.split("\n")).strip()


# ============================================================
# Best-effort "Example N: Input:/Output:" extraction
# ============================================================
# LeetCode renders examples as <pre>Input: ...\nOutput: ...\n[Explanation:
# ...]</pre> blocks inside `content`. This pulls Input/Output pairs out of
# those blocks so the New Problem form can be pre-seeded with test cases —
# imperfect (LeetCode's I/O shorthand, e.g. `nums = [2,7,11,15], target = 9`,
# doesn't always match the stdin format code_runner expects), so these are
# meant as a starting point for the admin to edit, not a final answer.

# Matches a <pre> block (the container LeetCode uses for examples).
_PRE_BLOCK = re.compile(r"<pre[^>]*>(.*?)</pre>", re.IGNORECASE | re.DOTALL)

# Strips any remaining HTML tags inside the pre block before we look for
# Input/Output — LeetCode wraps the labels in <strong> inside the <pre>.
_STRIP_TAGS = re.compile(r"<[^>]+>")

# After stripping tags the format is:
#   Input: x = 123\nOutput: 321\nExplanation: ...
# The input value after the variable assignment ("x = 123" -> "123") is
# extracted by _VAR_ASSIGN so the test case field gets just the bare value.
_INPUT_OUTPUT = re.compile(
    r"Input:\s*(.*?)\s*Output:\s*(.*?)(?:\s*Explanation:.*)?$",
    re.IGNORECASE | re.DOTALL,
)
# "varname = value" or "varname1 = v1, varname2 = v2" -> just the values
_VAR_ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*=")


def _strip_var_names(text: str) -> str:
    """'x = 123' -> '123',  'nums = [1,2], target = 9' -> '[1,2]\n9' (one value per line)."""
    # Split on comma boundaries that separate assignments, then strip each.
    parts = re.split(r",\s*(?=[A-Za-z_][A-Za-z0-9_]*\s*=)", text)
    values = []
    for part in parts:
        v = _VAR_ASSIGN.sub("", part).strip()
        if v:
            values.append(v)
    return "\n".join(values) if values else text.strip()


def extract_examples(raw_html: str) -> list[dict]:
    """Pull Input/Output pairs out of LeetCode <pre> example blocks.

    Works directly on the raw HTML (before html_to_text) so the Input/Output
    labels don't pick up stray ** or `` from the text conversion pass.
    """
    if not raw_html:
        return []
    examples = []
    for block in _PRE_BLOCK.findall(raw_html):
        # Strip all HTML tags (strong, em, code, etc.) and unescape entities
        # so we're left with plain text that looks like:
        #   Input: x = 123\nOutput: 321
        plain = html.unescape(_STRIP_TAGS.sub("", block)).strip()
        m = _INPUT_OUTPUT.search(plain)
        if not m:
            continue
        raw_input = m.group(1).strip()
        raw_output = m.group(2).strip()
        # Strip variable-assignment prefixes if present so the field contains
        # just the bare value(s), one per line.
        inp = _strip_var_names(raw_input) if _VAR_ASSIGN.search(raw_input) else raw_input
        out = _strip_var_names(raw_output) if _VAR_ASSIGN.search(raw_output) else raw_output
        examples.append({"input": inp, "output": out})
    return examples


# ============================================================
# Split a trailing "Constraints:" section out of the description text
# ============================================================
# After html_to_text (which now strips <strong>) the heading is just the
# plain word "Constraints" followed by a newline — no ** markers.

_CONSTRAINTS_HEADING = re.compile(r"\n\s*Constraints\s*\n", re.IGNORECASE)


def split_constraints(description_text: str) -> tuple[str, str | None]:
    """Split the plain-text description at the 'Constraints' heading.

    Returns (description_body, constraints_text_or_None). If the heading
    isn't found the whole text is returned unchanged and constraints is None.
    """
    m = _CONSTRAINTS_HEADING.search(description_text)
    if not m:
        return description_text, None
    before = description_text[: m.start()].strip()
    after = description_text[m.end() :].strip()
    return before, (after or None)
