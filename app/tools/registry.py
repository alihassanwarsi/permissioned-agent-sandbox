from app.models.tool_spec import ToolSpec

class ToolRegistry:
    """Holds all registered tools and lets us register or look them up."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> None:
        if tool.name in self._tools:
            raise ValueError(f"A tool named '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(f"No tool named '{name}' is registered.")
        return self._tools[name]

    def all_tools(self) -> list[ToolSpec]:
        return list(self._tools.values())