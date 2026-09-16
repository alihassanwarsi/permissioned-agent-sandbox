from app.tools.registry import ToolRegistry
from app.tools.file_reader import file_reader_tool
from app.tools.web_search import web_search_tool
from app.tools.send_email import send_email_tool

def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(file_reader_tool)
    registry.register(web_search_tool)
    registry.register(send_email_tool)
    return registry