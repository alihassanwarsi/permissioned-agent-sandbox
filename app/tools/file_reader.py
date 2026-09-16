from pathlib import Path
from pydantic import BaseModel
from app.models.user import Role
from app.models.tool_spec import RiskLevel, ToolSpec

SANDBOX_DIR = Path("sandbox_files").resolve()

class FileReaderInput(BaseModel):
    path: str

class FileReaderOutput(BaseModel):
    content: str

def read_files(input: FileReaderInput) -> FileReaderOutput:
    requested_path = (SANDBOX_DIR/input.path).resolve()

    if not requested_path.is_relative_to(SANDBOX_DIR):
        raise PermissionError(f"{input.path} is outside of the sandbox directory.")

    if not requested_path.exists():
        raise FileNotFoundError(f"{input.path} does not exists.")

    if not requested_path.is_file():
        raise ValueError(f"{input.path} is not a file.")

    return FileReaderOutput(content=requested_path.read_text())

file_reader_tool = ToolSpec(
    name="file_reader",
    description="Reads a text file from within the sandbox directory.",
    input_schema=FileReaderInput,
    output_schema=FileReaderOutput,
    allowed_roles=[Role.VIEWER, Role.ANALYST, Role.OPERATOR, Role.ADMIN],
    rate_limit=30,
    risk_level=RiskLevel.LOW
)