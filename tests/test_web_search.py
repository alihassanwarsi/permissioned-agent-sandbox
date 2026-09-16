import pytest
from app.tools.web_search import WebSearchInput, web_search

def test_returns_requested_number_results():
    result = web_search(WebSearchInput(query="test", max_results=2))
    assert len(result.results) == 2

def test_defaults_to_five_results():
    result = web_search(WebSearchInput(query="test"))
    assert len(result.results) <= 5

def test_rejects_non_positive_max_results():
    with pytest.raises(ValueError):
        web_search(WebSearchInput(query="test", max_results=0))