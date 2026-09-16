from pydantic import BaseModel
from app.models.tool_spec import Role, RiskLevel, ToolSpec

class WebSearchInput(BaseModel):
    query: str
    max_results: int = 5

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str

class WebSearchOutput(BaseModel):
    results: list[SearchResult]

_MOCK_RESULTS = [
    SearchResult(
        title="Mock result 1",
        url="https://example.com/1",
        snippet="This is the 1st mock search result."
    ),
    SearchResult(
        title="Mock result 2",
        url="https://example.com/2",
        snippet="This is the 2nd mock search result"
    ),
    SearchResult(
        title="Mock result 3",
        url="https://example.com/3",
        snippet="This is the 3rd mock search result"
    ),
]

def web_search(input: WebSearchInput) -> WebSearchOutput:
    if input.max_results < 1:
        raise ValueError("max_results must be at least 1.")
    print(f"query: {input.query}, max_results: {input.max_results}")
    return WebSearchOutput(results=_MOCK_RESULTS[:input.max_results])

web_search_tool = ToolSpec(
    name="web_search",
    description="Searches the web for a query and returns matching results.",
    input_schema=WebSearchInput,
    output_schema=WebSearchOutput,
    allowed_roles=[Role.ANALYST, Role.OPERATOR, Role.ADMIN],
    rate_limit=10,
    risk_level=RiskLevel.MEDIUM
)