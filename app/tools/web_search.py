from pydantic import BaseModel, ConfigDict, Field
from tavily import TavilyClient
from app.config import settings
from app.models.tool_spec import RiskLevel, ToolSpec
from app.models.user import Role

class WebSearchInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str
    max_results: int = Field(default=5, ge=1, le=10)

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str

class WebSearchOutput(BaseModel):
    results: list[SearchResult]

def web_search(input: WebSearchInput) -> WebSearchOutput:
    if not settings.tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY is required to perform web searches.")

    client = TavilyClient(api_key=settings.tavily_api_key)

    response = client.search(
        query=input.query,
        max_results=input.max_results,
        search_depth="basic"
    )

    results = [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("content", ""),
        )
        for item in response.get("results", [])
    ]

    return WebSearchOutput(results=results)

web_search_tool = ToolSpec(
    name="web_search",
    description="Searches the live web for current information and returns relevant results.",
    input_schema=WebSearchInput,
    output_schema=WebSearchOutput,
    handler=web_search,
    allowed_roles=[Role.ANALYST, Role.OPERATOR, Role.ADMIN],
    rate_limit=10,
    risk_level=RiskLevel.MEDIUM
)