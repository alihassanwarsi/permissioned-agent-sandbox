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