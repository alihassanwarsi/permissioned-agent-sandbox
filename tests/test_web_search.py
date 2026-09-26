import pytest
from unittest.mock import patch
from app.tools.web_search import WebSearchInput, web_search

@patch("app.tools.web_search.TavilyClient")
def test_returns_requested_number_results(mock_client, monkeypatch):
    monkeypatch.setattr(
        "app.tools.web_search.settings.tavily_api_key",
        "test-key"
    )

    mock_client.return_value.search.return_value = {
        "results": [
            {
                "title": "Result 1",
                "url": "https://example.com/1",
                "content": "First result"
            },
            {
                "title": "Result 2",
                "url": "https://example.com/2",
                "content": "Second result"
            }
        ]
    }

    result = web_search(
        WebSearchInput(
            query="test",
            max_results=2
        )
    )

    assert len(result.results) == 2
    assert result.results[0].title == "Result 1"

    mock_client.return_value.search.assert_called_once_with(
        query="test",
        max_results=2,
        search_depth="basic"
    )

@patch("app.tools.web_search.TavilyClient")
def test_defaults_to_five_results(mock_client, monkeypatch):
    monkeypatch.setattr(
        "app.tools.web_search.settings.tavily_api_key",
        "test-key"
    )

    mock_client.return_value.search.return_value = {
        "results": []
    }

    web_search(
        WebSearchInput(query="test")
    )

    mock_client.return_value.search.assert_called_once_with(
        query="test",
        max_results=5,
        search_depth="basic"
    )

def test_rejects_non_positive_max_results():
    with pytest.raises(ValueError):
        WebSearchInput(
            query="test",
            max_results=0
        )