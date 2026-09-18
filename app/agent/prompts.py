from app.tools.registry import ToolRegistry

def get_tools_list(registry: ToolRegistry) -> str:
    return "\n".join(
        f"{tool.name}: {tool.description}" for tool in registry.all_tools()
    )

def build_planning_prompt(user_message: str, registry: ToolRegistry) -> str:
    tools_list = get_tools_list(registry)

    return f"""You are deciding which tool (if any) should handle a user's request.

Available tools:
{tools_list}

User request: "{user_message}"

Respond with ONLY valid JSON in this exact shape, nothing else:
{{"tool": "<tool_name or null>", "input": {{<input fields for that tool>}}, "reasoning": "<short explanation>"}}

If no tool is needed (e.g. it's just a question you can answer directly), set "tool" to null and "input" to {{}}.
"""

def build_reflection_prompt(tool_result, tool_error: str | None) -> str:
    return f"""A tool call failed with this error: {tool_error}

Should we retry with a different tool or different arguments, or give up?
Respond with ONLY one word: "retry" or "stop".
"""

def build_result_prompt(user_message: str, tool_result: object) -> str:
    return f"""The user asked: "{user_message}"

A tool was run and produced this result: {tool_result}

Write a short, clear, natural language response explaining this result.
Do not mention that a "tool" was used, just answer naturally.
"""

def build_direct_answer_prompt(user_message: str) -> str:
    return f"""The user asked: "{user_message}"

No tool is needed. Write a short, clear response answering directly.
"""