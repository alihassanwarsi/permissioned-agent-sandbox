def get_explicit_tool_request(message: str) -> str | None:
    message = message.strip().lower()

    web_search_phrases = (
        "search ",
        "search for ",
        "search the web",
        "web search",
        "look up ",
        "look up online",
        "find online",
        "browse the web"
    )

    if any(
        message.startswith(phrase)
        for phrase in web_search_phrases
    ):
        return "web_search"

    return None